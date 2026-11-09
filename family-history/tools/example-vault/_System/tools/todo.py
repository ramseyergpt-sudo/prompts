#!/usr/bin/env python3
"""Build Research/To-do.md: the single to-do hub for the vault.

Collects, from the notes themselves (never edit the hub by hand):
  1. Questions   - the curated list in Research/Open questions.md, plus every
                   person's `conflicts`.
  2. AI actions  - every open checkbox tagged #task/ai.
  3. Human actions - every open checkbox tagged #task/human, plus the blockers
                   table in Research/Human tasks and blockers.md.
  4. Edges       - every ancestor with an unknown parent, with what has been
                   tried (`search_log`) and the next open task on their note.

    python3 "_System/tools/todo.py" "/path/to/Family Tree"
"""
import os, re, sys, collections

V = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import settings as S
OUT = os.path.join(V, "Research", "To-do.md")
os.makedirs(os.path.dirname(OUT), exist_ok=True)
SIDES = list(S.SIDES.values())
# Lists that only copy tasks from other notes; skip them to avoid duplicates.
SKIP = set(S.BOOKKEEPING_NOTES) | {"To-do", "Template - Person"}

def split(s):
    p = s.split("---", 2)
    return (p[1], p[2]) if len(p) > 2 and s.startswith("---") else ("", s)

def get(fm, k):
    m = re.search(r"^%s:\s*(.*)$" % k, fm, re.M)
    return m.group(1).strip().strip('"') if m else ""

def getlist(fm, k):
    m = re.search(r"^%s:\s*\n((?:  - .*\n?)+)" % k, fm, re.M)
    return [x.strip()[2:].strip().strip('"') for x in m.group(1).splitlines()] if m else []

def empty(v): return v in ("", "[]", "''")

notes = {}
for r, _, fs in os.walk(V):
    if ".git" in r or "Private" in r or "/Templates" in r or "/.obsidian" in r:
        continue
    for f in fs:
        if f.endswith(".md"):
            notes[f[:-3]] = (os.path.relpath(r, V), open(os.path.join(r, f), encoding="utf-8").read())

def side_of(n):
    fm, _ = split(notes[n][1]) if n in notes else ("", "")
    s = get(fm, "side") or " ".join(getlist(fm, "side"))
    for x in SIDES:
        if x in s:
            return x
    return "General"

# ---- tasks
TASK = re.compile(r"^\s*- \[ \] (.*)$", re.M)
tasks = {"ai": [], "human": []}
for n, (d, s) in notes.items():
    if n in SKIP:
        continue
    for m in TASK.finditer(s):
        t = m.group(1)
        kind = "ai" if "#task/ai" in t else "human" if "#task/human" in t else None
        if not kind:
            continue
        t = re.sub(r"\s*#task/\w+", "", t).strip()
        tasks[kind].append((n, d, t))

AI_CATS = S.AI_TASK_GROUPS
HUMAN_CATS = S.HUMAN_TASK_GROUPS

def cat(t, cats):
    for name, rx in cats:
        if re.search(rx, t, re.I):
            return name
    return "Other"

def task_line(n, t):
    link = "" if ("[[%s" % n) in t else " — [[%s]]" % n
    return "- [ ] %s%s" % (t, link)

# ---- blockers table (manual) from Human tasks and blockers
blockers = []
hb = notes.get("Human tasks and blockers", ("", ""))[1]
for row in re.findall(r"^\|\s*(\d+)\s*\|(.*)\|\s*$", hb, re.M):
    cells = [c.strip() for c in row[1].split("|")]
    if cells and not cells[0].startswith("~~"):
        blockers.append(cells)

# ---- questions
oq = notes.get("Open questions", ("", ""))[1]
_, oq_body = split(oq)
oq_sections = re.split(r"^## ", oq_body, flags=re.M)[1:]
conflicts = collections.defaultdict(list)
for n, (d, s) in notes.items():
    if d != "People":
        continue
    fm, _ = split(s)
    for c in getlist(fm, "conflicts"):
        conflicts[side_of(n)].append((n, c))

# ---- edges
people = {n: split(s)[0] for n, (d, s) in notes.items() if d == "People"}
edges = []
for n, fm in people.items():
    if get(fm, "ancestor") != "true":
        continue
    miss = [x for x in ("father", "mother") if empty(get(fm, x))]
    if not miss:
        continue
    gen = get(fm, "generation")
    log = getlist(fm, "search_log")
    j = " ".join(log).lower()
    real = [x for x in log if not re.search(r"(?:parents|mother|father)[^;]{0,25}not yet searched", x, re.I)]
    if not real:
        status = "never looked"
    elif "blocked" in j:
        status = "blocked"
    elif re.search(r"\blead\b|candidate", j):
        status = "lead"
    else:
        status = "searched"
    nxt = next((t for (m, d, t) in tasks["ai"] + tasks["human"] if m == n), "")
    edges.append((int(gen) if gen.isdigit() else 99, side_of(n), n, " and ".join(miss), status, log, nxt))
edges.sort(key=lambda e: (e[0], e[1], e[2]))

# ---- write
L = ["---", 'type: "research"', 'title: "To-do"', "generated: true", "---", "",
     "# To-do: questions, actions and edges", "",
     "> [!info] Generated file: do not edit",
     "> Built by `_System/tools/todo.py` from the notes themselves. To change an item, edit the note it links to: tick or add a checkbox tagged `#task/ai` or `#task/human`, add a `conflicts` line, add a question to [[Open questions]], or add a `search_log` entry on the person. Then run the rebuild (`_System/tools/rebuild.sh`).", ""]
st = collections.Counter(e[4] for e in edges)
L += ["| | Count |", "|---|---|",
      "| Open questions | %d curated + %d conflicts |" % (sum(len(re.findall(r"^\d+\.", sct, re.M)) for sct in oq_sections), sum(len(v) for v in conflicts.values())),
      "| AI actions | %d |" % len(tasks["ai"]), "| Human actions | %d tasks + %d blockers |" % (len(tasks["human"]), len(blockers)),
      "| Edges (ancestors with an unknown parent) | %d: %s |" % (len(edges), ", ".join("%d %s" % (st[k], k) for k in ("never looked", "searched", "lead", "blocked") if st[k])), ""]

L += ["## 1. Questions", "", "### Curated (from [[Open questions]])", ""]
for sct in oq_sections:
    title, _, rest = sct.partition("\n")
    L += ["#### " + title.strip(), "", rest.strip(), ""]
L += ["### Conflicts recorded on person notes", ""]
for sd in SIDES + ["General"]:
    if conflicts.get(sd):
        L += ["#### %s side" % sd if sd != "General" else "#### Other", ""]
        L += ["- [[%s]]: %s" % (n, c) for n, c in sorted(conflicts[sd])]
        L.append("")

def emit(kind, cats, title):
    out = ["## %s" % title, ""]
    groups = collections.defaultdict(list)
    for n, d, t in tasks[kind]:
        groups[cat(t, cats)].append((side_of(n), n, t))
    for name in [c[0] for c in cats] + ["Other"]:
        if groups.get(name):
            out += ["### %s (%d)" % (name, len(groups[name])), ""]
            out += [task_line(n, t) for sd, n, t in sorted(groups[name], key=lambda x: (SIDES.index(x[0]) if x[0] in SIDES else 9, x[1]))]
            out.append("")
    return out

L += emit("ai", AI_CATS, "2. AI actions")
L += emit("human", HUMAN_CATS, "3. Human actions")
L += ["### Blockers (from [[Human tasks and blockers]])", "", "| # | Blocker | What's needed | What it would unlock |", "|---|---|---|---|"]
L += ["| %s | %s |" % (i + 1, " | ".join(c[:3])) for i, c in enumerate(blockers)]
L.append("")

L += ["## 4. Edges: where each line stops", "",
      "Every ancestor with an unknown father or mother. **Status** comes from their `search_log`: *never looked* (no recorded search), *searched* (looked, nothing yet), *lead* (a candidate found), *blocked* (needs a paid site, login or archive request).", ""]
for sd in SIDES:
    rows = [e for e in edges if e[1] == sd]
    if not rows:
        continue
    c = collections.Counter(e[4] for e in rows)
    L += ["### %s side (%d edges: %s)" % (sd, len(rows), ", ".join("%d %s" % (c[k], k) for k in ("never looked", "searched", "lead", "blocked") if c[k])), "",
          "| Gen | Ancestor | Missing | Status | What has been tried | Next |", "|---|---|---|---|---|---|"]
    for gen, _, n, miss, status, log, nxt in rows:
        tried = ("%d: " % len(log) + log[-1][:140].replace("|", "/")) if log else "—"
        L.append("| %s | [[%s]] | %s | **%s** | %s | %s |" % (gen if gen != 99 else "?", n, miss, status, tried, nxt[:110].replace("|", "/") or "—"))
    L.append("")

open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("to-do: %d AI, %d human, %d blockers, %d edges (%s)" % (len(tasks["ai"]), len(tasks["human"]), len(blockers), len(edges), dict(st)))
