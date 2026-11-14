"""Write training/<page>.tsv (line, text, status) from the consensus plus settled lines.

Agreed lines (both readers match, no [?]) enter as they are. Close/disputed lines enter only when settled on
the enlarged crop in review/<page>.decisions.tsv (columns line, text, note); an empty text means the line is
left out. A decision also overrides an agreed line. Lines with [?] never enter.

Usage: python3 make_training.py PAGE [PAGE ...]
"""
import csv, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from conventions import conventions

ST = os.path.dirname(os.path.abspath(__file__))


for page in sys.argv[1:]:
    rows = list(csv.DictReader(open(os.path.join(ST, "reference", page + ".consensus.tsv"), encoding="utf-8"), delimiter="\t", quoting=csv.QUOTE_NONE))
    dp = os.path.join(ST, "review", page + ".decisions.tsv")
    dec = {int(r["line"]): r for r in csv.DictReader(open(dp, encoding="utf-8"), delimiter="\t", quoting=csv.QUOTE_NONE)} if os.path.exists(dp) else {}
    out = []
    for r in rows:
        k = int(r["line"])
        if k in dec:   # a decision overrides, also for an agreed line both readers got wrong
            if not dec[k]["text"].strip(): continue
            text, basis = dec[k]["text"].strip(), "settled on crop"
        elif r["status"] == "agreed": text, basis = r["text"], "agreed"
        else: continue
        text = conventions(text)
        if "[?]" not in text: out.append((k, text, basis))
    os.makedirs(os.path.join(ST, "training"), exist_ok=True)
    with open(os.path.join(ST, "training", page + ".tsv"), "w", encoding="utf-8") as f:
        f.write("line\ttext\tstatus\tbasis\n")
        for k, text, basis in out: f.write(f"{k}\t{text}\tverified\t{basis}\n")
    print(f"{page}: {len(out)} verified of {len(rows)} lines ({sum(b == 'agreed' for *_, b in out)} agreed, "
          f"{sum(b != 'agreed' for *_, b in out)} settled; {len(dec)} decisions)")
