#!/usr/bin/env python3
"""Rebuild Dashboards/Migration routes.md from the vault.

For every direct ancestor with two or more dated residences, draws the route
(place + country for each stop) and a one-line country path, e.g.
"Germany → Netherlands → USA". Countries come from each Place note's `country`.

    python3 "_System/tools/migration.py" "/path/to/Family Tree"
"""
import os, re, sys, datetime

V = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def fm(path):
    s = open(path, encoding="utf-8").read()
    if not s.startswith("---\n"): return {}
    d, key = {}, None
    for line in s[4:s.find("\n---", 4)].splitlines():
        m = re.match(r"^([A-Za-z_]+):\s*(.*)$", line)
        if m:
            key, v = m.group(1), m.group(2).strip()
            d[key] = [] if v in ("", "[]") else v.strip('"')
        elif line.strip().startswith("- ") and key:
            if not isinstance(d.get(key), list): d[key] = []
            d[key].append(line.strip()[2:].strip('"'))
    return d

places = {f[:-3]: fm(os.path.join(V, "Places", f)) for f in os.listdir(os.path.join(V, "Places")) if f.endswith(".md")}
def country(pl):
    d = places.get(pl, {}); c = d.get("country") or ""
    return c if c else "at sea"

people = []
for f in os.listdir(os.path.join(V, "People")):
    if not f.endswith(".md"): continue
    p = fm(os.path.join(V, "People", f))
    if str(p.get("ancestor", "")).lower() != "true": continue
    stops = []
    for r in p.get("residences") or []:
        m = re.match(r"^(.*?): \[\[(.+?)\]\]$", r)
        if m: stops.append((m.group(1), m.group(2)))
    if len(stops) >= 2:
        y = re.search(r"\d{4}", str(p.get("born") or "")); people.append((int(y.group(0)) if y else 9999, f[:-3], stops))
people.sort()

def countries_path(stops):
    out = []
    for _, pl in stops:
        c = country(pl)
        if not out or out[-1] != c: out.append(c)
    return " → ".join(out)

INIT = '%%{init: {"flowchart": {"useMaxWidth": true}}}%%'
lines = ["---", "type: dashboard", "title: Migration routes", 'updated: "%s"' % datetime.date.today().isoformat(), "---", "",
         "Each direct ancestor's dated residences (from the `residences` property), oldest ancestors first. "
         "Regenerate with `_System/tools/migration.py` after adding residences.", "",
         "## Country paths at a glance", "", "| Ancestor | Born | Countries |", "|---|---|---|"]
for y, t, stops in people:
    lines.append("| [[%s]] | %s | %s |" % (t, y if y != 9999 else "?", countries_path(stops)))
lines += ["", "## Routes", ""]
for y, t, stops in people:
    ids = ["s%d" % i for i in range(len(stops))]
    lines += ["### [[%s]]" % t, "", "**%s**" % countries_path(stops), "", "```mermaid", INIT, "flowchart LR"]
    for i, (yr, pl) in enumerate(stops):
        lines.append('  %s["%s<br/>%s<br/>%s"]' % (ids[i], yr, pl, country(pl)))
    lines.append("  " + " --> ".join(ids))
    lines += ["```", ""]
os.makedirs(os.path.join(V, "Dashboards"), exist_ok=True)
open(os.path.join(V, "Dashboards", "Migration routes.md"), "w", encoding="utf-8").write("\n".join(lines))
print(len(people), "routes")
