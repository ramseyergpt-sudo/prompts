"""Build a consensus reference for a page from two independent strong readings (config.READER_A and config.READER_B).

For each line:
  agreed    - the two readings match after loose normalisation -> reference text
  close     - similar (>= 0.75) but differ in some words -> needs adjudication on the image
  disputed  - the readings differ a lot -> needs a human check
  noise     - both readers found no text
Writes reference/<page>.consensus.tsv and review/<page>.md (the lines to adjudicate, word by word).

Usage: python3 build_reference.py PAGE [PAGE ...]
"""
import csv, difflib, os, re, sys, unicodedata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C
ST = C.HERE
A, B = C.READER_A, C.READER_B

def load(p):
    d = {}
    if not os.path.exists(p): return d
    for r in csv.DictReader(open(p, encoding="utf-8"), delimiter="\t", quoting=csv.QUOTE_NONE):
        if (r.get("line") or "").strip().isdigit(): d[int(r["line"])] = r
    return d

def loose(s):
    s = unicodedata.normalize("NFC", s or "").replace("[noise]", "").replace("[?]", "")
    s = s.lower().replace("ÿ", "y").replace("ß", "ss").replace("ů", "u").replace("ſ", "s")
    s = re.sub(r"[.,:;()\[\]]", "", s)
    return re.sub(r"\s+", " ", s).strip()

def clean(s):
    return re.sub(r"\s+", " ", (s or "").replace("[noise]", "")).strip()

for page in sys.argv[1:]:
    ha = load(os.path.join(ST, "model-readings", page, A + ".tsv"))
    hb = load(os.path.join(ST, "model-readings", page, B + ".tsv"))
    lines = sorted(set(ha) | set(hb))
    rows, review, counts = [], [], {}
    for k in lines:
        ta, tb = (ha.get(k) or {}).get("text", ""), (hb.get(k) or {}).get("text", "")
        la, lb = loose(ta), loose(tb)
        if not la and not lb:
            st, text = "noise", ""
        elif la == lb:
            # prefer the reading without uncertainty marks
            text = clean(ta) if "[?]" not in ta else clean(tb)
            st = "agreed" if "[?]" not in text else "agreed-uncertain"
        else:
            sim = difflib.SequenceMatcher(None, la, lb).ratio()
            st = "close" if sim >= 0.75 else "disputed"
            text = ""
            wa, wb = clean(ta).split(), clean(tb).split()
            diff = []
            for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, [loose(w) for w in wa], [loose(w) for w in wb]).get_opcodes():
                if op != "equal": diff.append(f"`{' '.join(wa[i1:i2]) or '∅'}` ↔ `{' '.join(wb[j1:j2]) or '∅'}`")
            review.append(f"- **L{k}** ({st}, {sim:.2f})  \n  {A}: {clean(ta)}  \n  {B}: {clean(tb)}  \n  differs: {'; '.join(diff)}")
        counts[st] = counts.get(st, 0) + 1
        rows.append((k, text, st, clean(ta), clean(tb)))
    os.makedirs(os.path.join(ST, "reference"), exist_ok=True); os.makedirs(os.path.join(ST, "review"), exist_ok=True)
    with open(os.path.join(ST, "reference", page + ".consensus.tsv"), "w", encoding="utf-8") as f:
        f.write(f"line\ttext\tstatus\t{A}\t{B}\n")
        for r in rows: f.write("\t".join(str(x) for x in r) + "\n")
    with open(os.path.join(ST, "review", page + ".md"), "w", encoding="utf-8") as f:
        f.write(f"# Review: {page}\n\n{counts}\n\nLines where {A} and {B} disagree. Settle each on the line image (`lines/{page}/L###.png`).\n\n" + "\n".join(review) + "\n")
    print(page, counts)
