#!/usr/bin/env python3
"""Completeness report for the Family Tree vault.

Reads every note in People/ (the vault is the master record) and writes
Dashboards/Completeness.md: how complete each field is for the root
person's direct ancestors, broken down by side and generation, plus a list of every gap.

Run from anywhere:
    python3 "_System/tools/completeness.py" "/path/to/Family Tree"
Re-run after research sessions; any AI may run it. It only writes Dashboards/Completeness.md.
"""
import os, re, sys, collections, datetime

V = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import settings as S

def parse_frontmatter(text):
    if not text.startswith("---\n"): return {}
    end = text.find("\n---", 4)
    d, key = {}, None
    for line in text[4:end].splitlines():
        m = re.match(r"^([A-Za-z_]+):\s*(.*)$", line)
        if m:
            key, val = m.group(1), m.group(2).strip()
            if val == "": d[key] = []
            elif val == "[]": d[key] = []
            else: d[key] = val.strip('"')
        elif line.strip().startswith("- ") and key is not None:
            if not isinstance(d.get(key), list): d[key] = []
            d[key].append(line.strip()[2:].strip('"'))
    return d

def link(t): return "[[%s]]" % t

people = {}
for f in os.listdir(os.path.join(V, "People")):
    if f.endswith(".md"):
        people[f[:-3]] = parse_frontmatter(open(os.path.join(V, "People", f), encoding="utf-8").read())
anc = {t: p for t, p in people.items() if str(p.get("ancestor", "")).lower() == "true"}

def date_quality(v):
    if not v: return "missing"
    v = str(v)
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", v): return "exact"
    if re.fullmatch(r"\d{4}-\d{2}", v): return "month"
    if re.search(r"\d{4}", v): return "year/approx"
    return "missing"

def has(p, k):
    v = p.get(k)
    return bool(v) and v != []

def gen(p):
    try: return int(p.get("generation") or 0)
    except ValueError: return 0

def sides(p):
    s = p.get("side")
    return s if isinstance(s, list) else ([s] if s else ["?"])

FIELDS = [
    ("Birth date (exact day)", lambda p: date_quality(p.get("born")) == "exact"),
    ("Birth date (any)", lambda p: date_quality(p.get("born")) != "missing"),
    ("Birth place", lambda p: has(p, "born_place")),
    ("Death date (exact day)", lambda p: date_quality(p.get("died")) == "exact"),
    ("Death date (any)", lambda p: date_quality(p.get("died")) != "missing"),
    ("Death place", lambda p: has(p, "died_place")),
    ("Burial", lambda p: has(p, "buried")),
    ("Father known", lambda p: has(p, "father")),
    ("Mother known", lambda p: has(p, "mother")),
    ("Occupation", lambda p: has(p, "occupation")),
    ("Religion", lambda p: has(p, "religion")),
    ("Community", lambda p: has(p, "community")),
    ("Residences (any)", lambda p: has(p, "residences")),
    ("Documented identity", lambda p: p.get("evidence") == "documented"),
    ("Documented or strong parent link", lambda p: p.get("parent_evidence") in ("documented", "strong inference")),
    ("Has a source", lambda p: has(p, "sources")),
    ("2+ sources", lambda p: isinstance(p.get("sources"), list) and len(p["sources"]) >= 2),
]

def pct(n, d): return "%d%%" % round(100 * n / d) if d else "–"
def bar(n, d):
    if not d: return ""
    k = round(10 * n / d); return "█" * k + "░" * (10 - k)

today = datetime.date.today().isoformat()
out = ["---", "type: dashboard", "title: Completeness", 'updated: "%s"' % today, "---", "",
       "How complete the data is for " + S.ROOT_LABEL + "'s **%d direct ancestors**, computed %s from the People notes by `_System/tools/completeness.py`. "
       "Re-run that script after a research session to refresh this page. Each gap list below is a ready-made target list." % (len(anc), today), ""]

# 1. overall
out += ["## Overall", "", "| Field | Have | Missing | Complete | |", "|---|---|---|---|---|"]
for name, fn in FIELDS:
    n = sum(1 for p in anc.values() if fn(p))
    out.append("| %s | %d | %d | %s | `%s` |" % (name, n, len(anc) - n, pct(n, len(anc)), bar(n, len(anc))))
out.append("")

# 2. by side
SIDES = list(S.SIDES.values())
out += ["## By side", "", "| Field | " + " | ".join(SIDES) + " |", "|---|" + "---|" * len(SIDES)]
for name, fn in FIELDS:
    row = []
    for s in SIDES:
        grp = [p for p in anc.values() if s in sides(p)]
        row.append("%s (%d/%d)" % (pct(sum(1 for p in grp if fn(p)), len(grp)), sum(1 for p in grp if fn(p)), len(grp)))
    out.append("| %s | %s |" % (name, " | ".join(row)))
out.append("")

# 3. pedigree completeness by generation
out += ["## How full is each generation?", "",
        "Generation 3 = grandparents (4 possible), 4 = great-grandparents (8), and so on. 'Found' counts distinct ancestor numbers, so a double ancestor fills two slots.", "",
        "| Generation | Relationship | Possible | Found | Complete | |", "|---|---|---|---|---|---|"]
slots = collections.Counter()
for p in anc.values():
    for n in (p.get("ahnentafel") or []):
        try: slots[int(n).bit_length()] += 1
        except ValueError: pass
names = {3: "grandparents", 4: "great-grandparents"}
for g in range(3, max(slots) + 1 if slots else 3):
    possible = 2 ** (g - 1)
    rel = names.get(g, "%s great-grandparents" % {5: "2nd", 6: "3rd"}.get(g, "%dth" % (g - 3)))
    out.append("| %d | %s | %d | %d | %s | `%s` |" % (g, rel, possible, slots[g], pct(slots[g], possible), bar(slots[g], possible)))
out.append("")

# 4. the frontier: where each line stops
front = sorted([t for t, p in anc.items() if not has(p, "father") or not has(p, "mother")], key=lambda t: (gen(anc[t]), t))
out += ["## Where the tree stops (the frontier)", "",
        "Ancestors with at least one parent unknown, nearest generations first — the best places to push the tree back.", "",
        "| Ancestor | Generation | Side | Missing | Identity evidence |", "|---|---|---|---|---|"]
for t in front:
    p = anc[t]; miss = [k for k in ("father", "mother") if not has(p, k)]
    out.append("| %s | %d | %s | %s | %s |" % (link(t), gen(p), ", ".join(sides(p)), " and ".join(miss), p.get("evidence", "")))
out.append("")

# 5. gap lists per field
out += ["## Gap lists by field", "", "Nearest generations first. Click a name, fill the property, cite the source, re-run the script."]
for name, fn in FIELDS:
    if name in ("Birth date (any)", "Death date (any)", "Has a source"): continue
    gaps = sorted([t for t, p in anc.items() if not fn(p)], key=lambda t: (gen(anc[t]), t))
    if not gaps: continue
    out += ["", "### %s — %d missing" % (name, len(gaps)), ""]
    bygen = collections.defaultdict(list)
    for t in gaps: bygen[gen(anc[t])].append(t)
    for g in sorted(bygen):
        out.append("- **Generation %d:** %s" % (g, ", ".join(link(t) for t in bygen[g])))
out.append("")

os.makedirs(os.path.join(V, "Dashboards"), exist_ok=True)
open(os.path.join(V, "Dashboards", "Completeness.md"), "w", encoding="utf-8").write("\n".join(out))
print("ancestors", len(anc), "frontier", len(front))
