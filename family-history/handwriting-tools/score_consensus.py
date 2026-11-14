"""Score model readings on the consensus test pages: CER on lines both AI readers agreed on (no [?]).

A weaker check than the verified pages: agreed lines are the easier lines, and both readers can be wrong.
Usage: python3 score_consensus.py MODEL [MODEL ...]    (pages: selection.json minus config.VERIFIED_PAGES)
"""
import csv, json, os, re, sys, unicodedata
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from conventions import conventions

import config as C
ST = C.HERE
VERIFIED = set(C.VERIFIED_PAGES)

def load(p):
    return {int(r["line"]): r for r in csv.DictReader(open(p, encoding="utf-8"), delimiter="\t", quoting=csv.QUOTE_NONE)
            if r.get("line", "").isdigit()}
def norm(s, strict=True):   # as in score.py
    s = conventions(s).replace("[noise]", "").replace("[?]", "").replace("[", "").replace("]", "")
    s = re.sub(r"\s+", " ", s).strip()
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

pages = [x["id"] for x in json.load(open(os.path.join(ST, "selection.json"))) if x["id"] not in VERIFIED]
models = sys.argv[1:]
tot = {(m, s): [0, 0] for m in models for s in (True, False)}
print(f"{'page':20}{'lines':>6}" + "".join(f"{m[:22]:>24}" for m in models) + "   (CER strict / loose)")
for p in pages:
    ref = load(os.path.join(ST, "reference", p + ".consensus.tsv"))
    gold = [k for k, r in ref.items() if r["status"] == "agreed" and "[?]" not in r["text"] and r["text"].strip()]
    row = f"{p:20}{len(gold):>6}"
    for m in models:
        f = os.path.join(ST, "model-readings", p, m + ".tsv")
        h = load(f) if os.path.exists(f) else {}
        cell = []
        for s in (True, False):
            e = sum(lev(norm(ref[k]["text"], s), norm(h.get(k, {}).get("text", ""), s)) for k in gold)
            n = sum(len(norm(ref[k]["text"], s)) for k in gold)
            tot[(m, s)][0] += e; tot[(m, s)][1] += n; cell.append(f"{e / n:.1%}" if n else "-")
        row += f"{' / '.join(cell):>24}"
    print(row)
print(f"{'all pages':26}" + "".join(f"{tot[(m, True)][0] / tot[(m, True)][1]:.1%} / {tot[(m, False)][0] / tot[(m, False)][1]:.1%}".rjust(24) for m in models))
