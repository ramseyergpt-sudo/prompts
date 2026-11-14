"""Look up surnames and place names in online name references, gently and with a local cache.

Swiss example: it queries Swiss name references. For another country, replace place() and surname()
with your own gazetteer and surname dictionary, and keep the gentle fetch() and the cache.

Places  -> ortsnamen.ch (its own UI search API); for hits from the Ortsnamenbuch des Kantons Bern (BEnb)
           also fetch the record's historical spellings. BEnb data: CC BY-SA 4.0.
Surnames -> Familiennamenbuch der Schweiz (familiennamenbuch.ch, HLS): communes with citizenship before 1800 ("a").

One request at a time, PAUSE seconds apart, long timeouts (the sites can be slow), every answer cached in
name-cache/ so a name is never asked twice.

Usage: python3 lookup_names.py IN.tsv OUT.tsv    (IN needs columns kind, as_written, lookup_form, parish)
"""
import csv, hashlib, html, json, os, re, sys, time, urllib.parse, urllib.request

ST = os.path.dirname(os.path.abspath(__file__)); CACHE = os.path.join(ST, "name-cache"); os.makedirs(CACHE, exist_ok=True)
PAUSE, TIMEOUT, UA = 5, 120, "HTR study name check (genealogy research; slow, cached, one request at a time)"
last = [0.0]

def fetch(url, data=None):
    key = hashlib.sha1((url + "|" + (data or "")).encode()).hexdigest()
    p = os.path.join(CACHE, key + ".txt")
    if os.path.exists(p): return open(p, encoding="utf-8").read()
    for attempt in (1, 2):
        wait = PAUSE - (time.time() - last[0])
        if wait > 0: time.sleep(wait)
        try:
            req = urllib.request.Request(url, data=data.encode() if data else None, headers={"User-Agent": UA})
            body = urllib.request.urlopen(req, timeout=TIMEOUT).read().decode("utf-8", "replace")
            last[0] = time.time(); open(p, "w", encoding="utf-8").write(body); return body
        except Exception as e:
            last[0] = time.time(); err = e; time.sleep(PAUSE * 4)
    return "ERROR " + str(err)

def text(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s or ""))).strip()

def place(name, parish):
    res = []
    # parish commune first, then Bern, then anywhere: common names have more hits than one page holds
    for q in ([f"{name} gemeinde:{parish}"] if parish else []) + [name + " kanton:BE", name]:
        body = fetch("https://ortsnamen.ch/de/api/ui/search?" + urllib.parse.urlencode({"q": q, "limit": 50}))
        if body.startswith("ERROR"): return {"status": body}
        res = [r for r in json.loads(body).get("results", []) if r.get("name", "").lower() == name.lower()]
        if res: break
    be = [r for r in res if r.get("kantonKey") == "BE"]
    best = next((r for r in be if parish and parish in r.get("gemeindeKey", "")), None) or (be or res or [None])[0]
    out = {"status": "found" if res else "not found", "exact_hits": len(res), "hits_BE": len(be)}
    if best:
        out["best"] = f"{best['name']}, {', '.join(best.get('municipalities', []))} ({', '.join(best.get('types', []))})"
        out["providers"] = ", ".join(p["label"] for p in best.get("providers", []))
        if "BEnb" in out["providers"]:
            d = fetch(f"https://ortsnamen.ch/de/api/ui/onchplace/{best['id']}/BEnb")
            if not d.startswith("ERROR"):
                rec = json.loads(d)[0]
                out["historical"] = " / ".join(text(x["text"]).replace("<br>", "; ") for h in rec.get("historical_records", []) for x in h.get("data", []))
                out["dialect"] = ", ".join(x["data"] for x in rec.get("phonetics", []))
    return out

def surname(name):
    form = urllib.parse.urlencode({"famname": name, "famncomm": "", "famncanton": "", "exactm": "on",
                                   "perioda": "on", "periodb": "on", "periodc": "on", "lg": "d"})
    body = fetch("https://familiennamenbuch.ch/index.php", form)
    if body.startswith("ERROR"): return {"status": body}
    cells = [text(c) for c in re.findall(r"<td[^>]*>(.*?)</td>", body, re.S)]
    rows = [cells[i:i + 5] for i in range(0, len(cells) - 4) if cells[i] == name and len(cells[i + 1]) == 2]
    old = sorted({r[2] for r in rows if r[1] == "BE" and r[3] == "a"})
    return {"status": "found" if rows else "not found", "entries": len(rows), "BE_before_1800": ", ".join(old)}

inp, outp = sys.argv[1], sys.argv[2]
rows = list(csv.DictReader(open(inp, encoding="utf-8"), delimiter="\t"))
cols = ["kind", "as_written", "lookup_form", "parish", "source", "status", "result", "historical_or_detail"]
with open(outp, "w", encoding="utf-8") as f:
    f.write("\t".join(cols) + "\n")
    for r in rows:
        t0 = time.time()
        if r["kind"] == "place":
            o = place(r["lookup_form"], r["parish"]); src = "ortsnamen.ch"
            res = f"{o.get('exact_hits', 0)} exact ({o.get('hits_BE', 0)} BE); best: {o.get('best', '')} [{o.get('providers', '')}]"
            det = "; ".join(x for x in (o.get("historical", ""), ("dialect " + o["dialect"]) if o.get("dialect") else "") if x)
        else:
            o = surname(r["lookup_form"]); src = "familiennamenbuch.ch"
            res = f"{o.get('entries', 0)} entries"; det = ("BE citizenship before 1800: " + o["BE_before_1800"]) if o.get("BE_before_1800") else ""
        f.write("\t".join([r["kind"], r["as_written"], r["lookup_form"], r["parish"], src, o["status"], res, det]) + "\n"); f.flush()
        print(f"{r['lookup_form']:15} {o['status']:10} {time.time() - t0:5.1f}s  {res[:90]}", flush=True)
