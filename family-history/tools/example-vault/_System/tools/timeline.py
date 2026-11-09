#!/usr/bin/env python3
"""Build Canvas/Timeline.canvas: everyone in People/ laid out by lifetime.

x = birth year, box width = lifespan. One horizontal lane per grandparent
side (settings.SIDES). Direct ancestors are coloured
by evidence level; relatives who are not ancestors are grey and marked "↳".
Years that are only estimated (fl., d., c., centuries, from a child's birth)
are shown with "~". A strip of History events runs along the top.

    python3 "_System/tools/timeline.py" "/path/to/Family Tree"
"""
import os, re, sys, json, hashlib

V = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import settings as S
P, H = os.path.join(V, "People"), os.path.join(V, "History")
START, PX, ROW, BOXH, GAP = S.TIMELINE_START, 40, 110, 90, 20   # px per year; row pitch; box height
COL = {"documented": "4", "strong inference": "5", "family compilation": "3", "compiled lead": "2", "unresolved": "1"}
LANES = list(S.SIDES.values()) + ["Other"]

def fm(s, key):
    m = re.search(r'^%s:\s*"?([^"\n]*)"?\s*$' % key, s, re.M)
    if m and m.group(1).strip(): return m.group(1).strip()
    m = re.search(r'^%s:\n\s+- "?([^"\n]+)"?' % key, s, re.M)
    return m.group(1).strip() if m else ""

def year(v):
    m = re.search(r"(\d{4})", v or "")
    return int(m.group(1)) if m else None

people = {}
for f in os.listdir(P):
    if not f.endswith(".md"): continue
    t = f[:-3]; s = open(os.path.join(P, f), encoding="utf-8").read()
    born, died = fm(s, "born"), fm(s, "died")
    label = re.search(r"\(([^)]*)\)$", t)
    label = label.group(1) if label else ""
    if not died and not re.search(r"\d{4}|c\.", label) and year(born) and year(born) > S.LIVING_BORN_AFTER:
        continue                                  # living person: never shown
    if t == S.ROOT_PERSON: continue
    p = dict(t=t, side=fm(s, "side"), ev=fm(s, "evidence"), anc=fm(s, "ancestor") == "true",
             father=fm(s, "father").strip("[]"), mother=fm(s, "mother").strip("[]"),
             b=year(born), d=year(died), est=False)
    exact = bool(p["b"]) and not re.search(r"^(c\.|bapt)", born)
    if p["b"] is None:
        m = re.search(r"fl\. (\d{4})|m\. (\d{4})|arr\. (\d{4})|emigrated (\d{4})|killed (\d{4})|b\. (\d{4})", label)
        if m:
            y = int(next(g for g in m.groups() if g)); p["b"] = y - (0 if "b. " in label else 25)
            if "killed" in label: p["d"] = y
        elif re.search(r"(\d{2})th c\.", label):
            p["b"] = (int(re.search(r"(\d{2})th", label).group(1)) - 1) * 100 + 40
        m = re.search(r"d\. (?:before )?(\d{4})", label)
        if m: p["d"] = int(m.group(1)); p["b"] = p["b"] or p["d"] - 60
    p["est"] = not exact or p["d"] is None
    m = re.search(r"^ahnentafel:\n\s+- (\d+)", s, re.M)   # ancestors: lane from their number
    if m:
        n = int(m.group(1))
        while n > 7: n //= 2
        if n in S.SIDES: p["side"] = S.SIDES[n]
    people[t] = p

# fill missing births from a child's birth (parent born about 30 years earlier)
for _ in range(4):
    for p in people.values():
        if p["b"]: continue
        kids = [c["b"] for c in people.values() if c["b"] and p["t"] in (c["father"], c["mother"])]
        if kids: p["b"] = min(kids) - 30; p["est"] = True
for p in people.values():
    if p["b"] and not p["d"]: p["d"] = p["b"] + 60
    if p["side"] not in LANES: p["side"] = "Other"

nodes, edges, lane_top = [], [], 0
for lane in LANES:
    rows = []                                     # right edge of last box in each row
    nodes.append(dict(id="lane-" + lane, type="text", x=-900, y=lane_top, width=800, height=BOXH,
                      text="## %s side" % lane, color="6"))
    members = sorted([p for p in people.values() if p["side"] == lane and p["b"]], key=lambda p: (p["b"], not p["anc"]))
    for p in members:
        x = (p["b"] - START) * PX; w = max((p["d"] - p["b"]) * PX, 360)
        r = next((i for i, right in enumerate(rows) if right + GAP <= x), None)
        if r is None: rows.append(0); r = len(rows) - 1
        rows[r] = x + w
        node = dict(id="p-" + hashlib.md5(p["t"].encode()).hexdigest()[:12], type="file", file="People/%s.md" % p["t"],
                    x=x, y=lane_top + r * ROW, width=w, height=BOXH)
        if p["anc"] and COL.get(p["ev"]): node["color"] = COL[p["ev"]]
        nodes.append(node); p["node"] = node["id"]
    lane_top += (len(rows) + 1) * ROW + 200

for p in people.values():                        # parent → child links, ancestors only
    for par in (p["father"], p["mother"]):
        q = people.get(par)
        if p.get("node") and q and q.get("node") and q["anc"] and p["anc"]:
            edges.append(dict(id="e-%s-%s" % (q["node"], p["node"]), fromNode=q["node"], fromSide="right",
                              toNode=p["node"], toSide="left"))

# century ruler and History events along the top
for y in range(START, 2051, 50):
    nodes.append(dict(id="yr%d" % y, type="text", x=(y - START) * PX, y=-420, width=300, height=70,
                      text="**%d**" % y, color="6" if y % 100 == 0 else None))
ev_rows = []
for f in (sorted(os.listdir(H)) if os.path.isdir(H) else []):
    s = open(os.path.join(H, f), encoding="utf-8").read(); y = year(fm(s, "date"))
    if not y: continue
    x = (y - START) * PX
    r = next((i for i, right in enumerate(ev_rows) if right + GAP <= x), None)
    if r is None: ev_rows.append(0); r = len(ev_rows) - 1
    ev_rows[r] = x + 700
    nodes.append(dict(id="h-" + hashlib.md5(f.encode()).hexdigest()[:12], type="file", file="History/" + f,
                      x=x, y=-560 - (r + 1) * ROW, width=700, height=BOXH))
nodes = [{k: v for k, v in n.items() if v is not None} for n in nodes]
nodes.append(dict(id="legend", type="text", x=-900, y=-560 - (len(ev_rows) + 1) * ROW, width=800, height=360,
                  text="**Timeline**\n\nEach box spans a lifetime (left edge = birth). Lanes = grandparent sides.\n\n"
                       "Coloured = direct ancestor (green documented · cyan strong inference · yellow family compilation · "
                       "orange compiled lead · red unresolved). Grey = relative, not an ancestor.\n\nEstimated dates "
                       "(fl., c., centuries) are approximate. Living people are never shown. Events along the top. "
                       "A few links cross lanes where one ancestor appears on two sides (see Double ancestors).\n\n"
                       "Rebuild: `python3 _System/tools/timeline.py`"))
os.makedirs(os.path.join(V, "Canvas"), exist_ok=True)
json.dump(dict(nodes=nodes, edges=edges), open(os.path.join(V, "Canvas", "Timeline.canvas"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("timeline: %d people, %d events, %d links" % (sum(1 for p in people.values() if p.get("node")), len(ev_rows) and sum(1 for n in nodes if n["id"].startswith("h-")), len(edges)))
