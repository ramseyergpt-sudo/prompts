#!/usr/bin/env python3
"""Recompute ancestor numbers for every person from the father/mother links.

Updates these properties on every note in People/: ancestor, ahnentafel,
generation, relationship. Run after changing any father or mother link:

    python3 "_System/tools/recompute.py" "/path/to/Family Tree"
"""
import os, re, sys, math, collections

V = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import settings as S
P = os.path.join(V, "People")
ROOTS = S.ANCHORS

notes = {f[:-3]: open(os.path.join(P, f), encoding="utf-8").read() for f in os.listdir(P) if f.endswith(".md")}
def prop(s, k):
    m = re.search(r'^%s: "\[\[(.+?)\]\]"' % k, s, re.M); return m.group(1) if m else None
def sex(s):
    m = re.search(r'^sex: "?([MF])', s, re.M); return m.group(1) if m else None

AH = collections.defaultdict(set); stack = list(ROOTS.items())
while stack:
    t, n = stack.pop()
    if t not in notes: continue
    AH[t].add(n)
    for k, c in (("father", 2 * n), ("mother", 2 * n + 1)):
        par = prop(notes[t], k)
        if par: stack.append((par, c))

def rel(n, sx):
    g = int(math.log2(n)) + 1; noun = {"M": "father", "F": "mother"}.get(sx, "parent")
    if g == 3: return "grand" + noun
    k = g - 3
    if k == 1: return "great-grand" + noun
    suf = "th" if 11 <= k % 100 <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(k % 10, "th")
    return "%d%s great-grand%s" % (k, suf, noun)

changed = 0
for t, s in notes.items():
    if t == S.ROOT_PERSON: continue
    nums = sorted(AH.get(t, []))
    end = s.index("\n---\n", 4); fm, body = s[:end + 1], s[end + 1:]
    fm = re.sub(r"^ahnentafel:.*\n((?:  - .*\n)*)", "", fm, flags=re.M)
    for k in ("ancestor", "generation", "relationship"):
        fm = re.sub(r"^%s:.*\n" % k, "", fm, flags=re.M)
    add = "ancestor: %s\n" % ("true" if nums else "false")
    if nums:
        add += "ahnentafel:\n" + "".join("  - %d\n" % n for n in nums)
        add += "generation: %d\n" % (int(math.log2(nums[0])) + 1)
        add += 'relationship: "%s"\n' % "; ".join(sorted(set(rel(n, sex(s)) for n in nums)))
    fm = fm + add
    new = fm + body
    if new != s:
        open(os.path.join(P, t + ".md"), "w", encoding="utf-8").write(new); changed += 1
print("ancestors", sum(1 for t in notes if AH.get(t)), "notes updated", changed)
