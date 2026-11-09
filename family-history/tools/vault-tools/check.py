#!/usr/bin/env python3
"""Health check for the vault. Run last in the rebuild; read every warning.

Checks: properties that do not parse, broken links, notes whose names differ only
by capital letters (the Mac treats them as one file), untagged tasks, malformed
search_log entries, person notes missing key fields, possible living people, and
hand edits left inside generated sections.

    python3 "_System/tools/check.py" "/path/to/Family Tree"
"""
import os, re, sys, collections
try:
    import yaml
except ImportError:
    yaml = None

V = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import settings as S
notes, files = {}, set()
for r, _, fs in os.walk(V):
    if ".git" in r or "/.obsidian" in r or "/.trash" in r:
        continue
    for f in fs:
        files.add(f)
        if f.endswith(".md"):
            notes.setdefault(f[:-3], []).append(os.path.join(r, f))

W = collections.defaultdict(list)
low = collections.defaultdict(list)
for n in notes:
    low[n.lower()].append(n)
for k, v in low.items():
    if len(v) > 1 or len(notes[v[0]]) > 1:
        W["Name clash (same name, different folder or capitals)"].append(", ".join(v))

for n, paths in notes.items():
    p = paths[0]
    if "/Templates/" in p or "/Private/" in p:
        continue
    s = open(p, encoding="utf-8").read()
    rel = os.path.relpath(p, V)
    fm = ""
    if s.startswith("---"):
        parts = s.split("---", 2)
        if len(parts) < 3:
            W["Properties block not closed"].append(rel); continue
        fm = parts[1]
        if yaml:
            try:
                yaml.safe_load(fm)
            except Exception as e:
                W["Properties do not parse (YAML)"].append("%s: %s" % (rel, str(e).splitlines()[0]))
    for l in set(re.findall(r"\[\[([^\]|#]+)", s)):
        l = l.strip().rstrip("\\")
        base = l.split("/")[-1]
        if base not in notes and base not in files and base + ".md" not in files and not re.search(r"\.(canvas|base)$", base):
            if base not in ("Note title", "AGENTS.md"):
                W["Broken link"].append("%s → [[%s]]" % (rel, l))
    for t in re.findall(r"^\s*- \[ \] (.*)$", s, re.M):
        if "#task/" not in t and not rel.startswith("Research/To-do"):
            W["Open task without #task/ai or #task/human"].append("%s: %s" % (rel, t[:80]))
    if rel.startswith("People/"):
        for e in re.findall(r'^\s+- "(.*)"$', (re.search(r"^search_log:\n((?:  - .*\n?)+)", fm, re.M) or [None, ""])[1], re.M):
            if not re.match(r"\d{4}-\d{2}-\d{2}|undated", e):
                W["search_log entry without a date"].append("%s: %s" % (rel, e[:60]))
        for k in ("type", "side", "evidence"):
            if not re.search(r"^%s:\s*\S" % k, fm, re.M):
                W["Person note missing '%s'" % k].append(rel)
        b = re.search(r"^born:\s*\"?(\d{4})", fm, re.M)
        d = re.search(r"^died:\s*\S", fm, re.M)
        if b and int(b.group(1)) > S.LIVING_BORN_AFTER and not d and n != S.ROOT_PERSON:
            W["Possible living person (born after %d, no death)" % S.LIVING_BORN_AFTER].append(rel)
    m = re.search(r"<!-- backlinks:start.*?-->(.*?)<!-- backlinks:end -->", s, re.S)
    if m and re.search(r"^(?!- \*\*|\s*$).+", m.group(1).strip(), re.M):
        W["Hand edit inside a generated Narratives section (will be lost)"].append(rel)

if not W:
    print("check: all clear")
for k, v in W.items():
    print("\n%s (%d)" % (k, len(v)))
    for x in sorted(v)[:15]:
        print("  - " + x)
    if len(v) > 15:
        print("  … and %d more" % (len(v) - 15))
