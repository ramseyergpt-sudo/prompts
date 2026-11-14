"""Fine-tune a TrOCR model on the verified training lines, optionally with the base model's own lines mixed in.

Our lines:   training/<page>.tsv (verified only) -> lines/<page>/L###.png. Whole pages in
             config.VALIDATION_PAGES are held out.
Mix-in:      config.MIX_FILES in config.MIX_DIR (parquet, image + text). Each epoch draws a fresh sample
             so they make up about config.MIX_SHARE of the training lines, to limit forgetting.
Test pages:  selection.json pages and volumes are refused.
Output:      checkpoints/<run>/best (lowest validation CER) and /last, log in checkpoints/<run>/train.log.

Usage: python finetune.py BASE_MODEL RUN_NAME [EPOCHS] [SELECTION.json ...]   (selections limit the pages; default all)
"""
import csv, io, json, os, random, re, sys, time, unicodedata
import torch
from PIL import Image, ImageEnhance
from transformers import TrOCRProcessor, VisionEncoderDecoderModel, get_linear_schedule_with_warmup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C
ST = C.HERE
BASE, RUN = sys.argv[1], sys.argv[2]
EPOCHS = int(sys.argv[3]) if len(sys.argv) > 3 else C.EPOCHS
ONLY = {x["id"] for s in sys.argv[4:] for x in json.load(open(os.path.join(ST, s)))} or None
VAL = C.VALIDATION_PAGES
MIX, POOL, BATCH, LR, SEED = C.MIX_SHARE, C.MIX_POOL, C.BATCH, C.LEARNING_RATE, C.SEED
MIXFILES = C.MIX_FILES
OUT = os.path.join(ST, "checkpoints", RUN); os.makedirs(OUT, exist_ok=True)
logf = open(os.path.join(OUT, "train.log"), "a")
def log(*a):
    s = time.strftime("%H:%M:%S ") + " ".join(str(x) for x in a); print(s, flush=True); logf.write(s + "\n"); logf.flush()
random.seed(SEED); torch.manual_seed(SEED)

# --- our verified lines, split by whole page; refuse test pages and volumes
test = {x["id"] for x in json.load(open(os.path.join(ST, "selection.json")))}
vol = lambda p: p.split("_")[0]
ours = {"train": [], "val": []}
for f in sorted(os.listdir(os.path.join(ST, "training"))):
    if not f.endswith(".tsv"): continue
    page = f[:-4]
    if ONLY and page not in ONLY: continue
    assert page not in test and vol(page) not in {vol(t) for t in test}, f"test page or volume in training: {page}"
    for r in csv.DictReader(open(os.path.join(ST, "training", f), encoding="utf-8"), delimiter="\t", quoting=csv.QUOTE_NONE):
        if r["status"] != "verified" or "[?]" in r["text"] or not r["text"].strip(): continue
        img = os.path.join(ST, "lines", page, f"L{int(r['line']):03d}.png")
        assert os.path.exists(img), img
        ours["val" if page in VAL else "train"].append({"image": img, "text": r["text"].strip(), "page": page})
for k, v in ours.items():
    with open(os.path.join(ST, "training", f"{RUN}-{k}.jsonl"), "w", encoding="utf-8") as fo:
        for x in v: fo.write(json.dumps({**x, "image": os.path.relpath(x["image"], ST)}, ensure_ascii=False) + "\n")
log(f"run {RUN} base {BASE}: train {len(ours['train'])} lines from {len({x['page'] for x in ours['train']})} pages, "
    f"val {len(ours['val'])} lines {VAL}")

# --- mix-in pool from the base model's own data (image bytes kept in memory)
pool = []
if MIXFILES:
    import pyarrow.parquet as pq
for mf in MIXFILES:
    t = pq.read_table(os.path.join(C.MIX_DIR, mf), columns=["image", "text"]).to_pylist()
    t = [r for r in t if r["text"] and r["text"].strip() and 2 <= len(r["text"]) <= 120]
    pool += [{"bytes": r["image"]["bytes"], "text": r["text"].strip()} for r in random.sample(t, min(POOL, len(t)))]
n_mix = round(len(ours["train"]) * MIX / (1 - MIX)) if pool else 0
log(f"mix-in pool {len(pool)} lines from {MIXFILES}; {n_mix} drawn per epoch ({MIX:.0%} of the epoch)")

dev = C.device()
proc = TrOCRProcessor.from_pretrained(BASE)
model = VisionEncoderDecoderModel.from_pretrained(BASE).to(dev)
tok = proc.tokenizer

def load_img(x, aug):
    im = Image.open(io.BytesIO(x["bytes"]) if "bytes" in x else x["image"]).convert("RGB")
    if aug:   # mild: slight rotation and contrast (the Bern scans are bilevel microfilm)
        im = im.rotate(random.uniform(-1.5, 1.5), expand=True, fillcolor=(255, 255, 255))
        im = ImageEnhance.Contrast(im).enhance(random.uniform(0.8, 1.2))
    return im

def batch_tensors(xs, aug):
    pv = proc(images=[load_img(x, aug) for x in xs], return_tensors="pt").pixel_values.to(dev)
    lab = tok([x["text"] for x in xs], padding=True, truncation=True, max_length=128, return_tensors="pt").input_ids
    lab[lab == tok.pad_token_id] = -100
    return pv, lab.to(dev)

def norm(s, strict=True):   # as in score.py
    s = re.sub(r"\s+", " ", unicodedata.normalize("NFC", s or "")).strip()
    if not strict:
        s = s.lower().replace("ÿ", "y").replace("ß", "ss").replace("ů", "u"); s = re.sub(r"[.,:;]", "", s); s = re.sub(r"\s+", " ", s).strip()
    return s
def lev(a, b):
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1): cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]

def evaluate():
    model.eval(); e = {True: 0, False: 0}; n = {True: 0, False: 0}
    with torch.no_grad():
        for i in range(0, len(ours["val"]), BATCH):
            xs = ours["val"][i:i + BATCH]
            pv = proc(images=[load_img(x, False) for x in xs], return_tensors="pt").pixel_values.to(dev)
            hyp = proc.batch_decode(model.generate(pv, max_new_tokens=96), skip_special_tokens=True)
            for x, h in zip(xs, hyp):
                for s in (True, False): e[s] += lev(norm(x["text"], s), norm(h, s)); n[s] += len(norm(x["text"], s))
    model.train(); return e[True] / n[True], e[False] / n[False]

steps_per_epoch = -(-(len(ours["train"]) + n_mix) // BATCH)
opt = torch.optim.AdamW(model.parameters(), lr=LR, weight_decay=0.01)
sched = get_linear_schedule_with_warmup(opt, int(0.1 * steps_per_epoch * EPOCHS), steps_per_epoch * EPOCHS)
best = evaluate(); log(f"epoch 0 (base): val CER strict {best[0]:.2%} loose {best[1]:.2%}")
model.save_pretrained(os.path.join(OUT, "best")); proc.save_pretrained(os.path.join(OUT, "best"))
model.train(); t0 = time.time()
for ep in range(1, EPOCHS + 1):
    items = [dict(x) for x in ours["train"]] + random.sample(pool, n_mix); random.shuffle(items)
    tot = 0.0
    for s in range(0, len(items), BATCH):
        pv, lab = batch_tensors(items[s:s + BATCH], aug=True)
        loss = model(pixel_values=pv, labels=lab).loss
        loss.backward(); torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0); opt.step(); sched.step(); opt.zero_grad()
        tot += loss.item()
    cer = evaluate()
    log(f"epoch {ep}: loss {tot / steps_per_epoch:.3f}  val CER strict {cer[0]:.2%} loose {cer[1]:.2%}  ({(time.time() - t0) / 60:.0f} min)")
    if cer[0] < best[0]:
        best = cer; model.save_pretrained(os.path.join(OUT, "best")); proc.save_pretrained(os.path.join(OUT, "best")); log("  saved best")
model.save_pretrained(os.path.join(OUT, "last")); proc.save_pretrained(os.path.join(OUT, "last"))
log(f"done: best val CER strict {best[0]:.2%} loose {best[1]:.2%}")
