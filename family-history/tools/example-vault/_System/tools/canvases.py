#!/usr/bin/env python3
"""Rebuild the ancestor canvases, one per side (Canvas/*.canvas) from the vault.

Reads each person's `ahnentafel` numbers and `evidence`, and lays out one tree
per side in settings.SIDES, coloured by evidence level. Run after recompute.py:

    python3 "_System/tools/canvases.py" "/path/to/Family Tree"
"""
import os, re, sys, json, math

V = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import settings as S
P = os.path.join(V, "People")
W, H, GAP = 420, 300, 40   # box size; Obsidian never resizes canvas boxes itself
COL = {"documented": "4", "strong inference": "5", "family compilation": "3", "compiled lead": "2", "unresolved": "1"}
nums, ev = {}, {}
for f in os.listdir(P):
    if not f.endswith(".md"): continue
    s = open(os.path.join(P, f), encoding="utf-8").read(); t = f[:-3]
    m = re.search(r"^ahnentafel:\n((?:  - \d+\n)+)", s, re.M)
    if m:
        for n in re.findall(r"\d+", m.group(1)): nums[int(n)] = t
    e = re.search(r'^evidence: "?([a-z ]+)', s, re.M); ev[t] = e.group(1).strip() if e else ""

def canvas(root, title):
    sub = {}
    for n, t in nums.items():
        m = n
        while m > root: m //= 2
        if m == root: sub[n] = t
    Y, slot = {}, [0]
    def lay(n):
        kids = [c for c in (2 * n, 2 * n + 1) if c in sub]
        for c in kids: lay(c)
        if kids: Y[n] = sum(Y[c] for c in kids) / len(kids)
        else: Y[n] = slot[0] * (H + GAP); slot[0] += 1
    lay(root)
    nodes, edges = [], []
    for n, t in sub.items():
        d = int(math.log2(n)) - int(math.log2(root))
        node = dict(id="a%d" % n, type="file", file="People/%s.md" % t, x=d * (W + 60), y=int(Y[n]), width=W, height=H)
        if COL.get(ev.get(t)): node["color"] = COL[ev[t]]
        nodes.append(node)
        for c in (2 * n, 2 * n + 1):
            if c in sub: edges.append(dict(id="e%d_%d" % (n, c), fromNode="a%d" % n, fromSide="right", toNode="a%d" % c, toSide="left"))
    nodes.append(dict(id="legend", type="text", x=-(W + 60), y=0, width=W, height=230,
        text="**%s**\n\nAncestors of the grandparent at left, parents to the right.\n\nColors: green = documented · cyan = strong inference · yellow = family compilation · orange = compiled lead · red = unresolved · grey = not set" % title))
    json.dump(dict(nodes=nodes, edges=edges), open(os.path.join(V, "Canvas", title + ".canvas"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

os.makedirs(os.path.join(V, "Canvas"), exist_ok=True)
for n, side in S.SIDES.items(): canvas(n, side + " side")
print("canvases rebuilt")
