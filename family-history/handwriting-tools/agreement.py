"""Agreement between the two AI readers per page: character disagreement and share of consensus words.

Page labels come from the "note" field of selection.json.
Usage: python3 agreement.py
"""
import csv,os,glob,difflib,re,sys,unicodedata,json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import config as C
ST=C.HERE
def loose(s):
    s=unicodedata.normalize("NFC",s or "").replace("[noise]","").replace("[?]","")
    s=s.lower().replace("ÿ","y").replace("ß","ss").replace("ů","u").replace("ſ","s")
    s=re.sub(r"[.,:;()\[\]]","",s); return re.sub(r"\s+"," ",s).strip()
def lev(a,b):
    prev=list(range(len(b)+1))
    for i,ca in enumerate(a,1):
        cur=[i]
        for j,cb in enumerate(b,1): cur.append(min(prev[j]+1,cur[j-1]+1,prev[j-1]+(ca!=cb)))
        prev=cur
    return prev[-1]
sel=os.path.join(ST,"selection.json")
meta={x["id"]:x.get("note",x["id"]) for x in json.load(open(sel))} if os.path.exists(sel) else {}
rows=[]; T=[0,0,0,0]
for f in sorted(glob.glob(os.path.join(ST,"reference","*.consensus.tsv"))):
    page=os.path.basename(f).split(".")[0]; e=n=wa=wt=0
    for r in csv.DictReader(open(f,encoding="utf-8"),delimiter="\t", quoting=csv.QUOTE_NONE):
        if r["status"]=="noise": continue
        a,b=loose(r[C.READER_A]),loose(r[C.READER_B])
        e+=lev(a,b); n+=max(len(a),len(b),1)
        A,B=a.split(),b.split(); sm=difflib.SequenceMatcher(None,A,B)
        wa+=sum(bl.size for bl in sm.get_matching_blocks()); wt+=max(len(A),len(B))
    rows.append((page,e/n,wa/max(wt,1))); T[0]+=e;T[1]+=n;T[2]+=wa;T[3]+=wt
print(f"{'page':40}{'char disagreement':>18}{'words agreed':>14}")
for p,c,w in sorted(rows,key=lambda x:x[1]): print(f"{meta.get(p,p):40}{c*100:17.0f}%{w*100:13.0f}%")
print(f"{'ALL pages':40}{T[0]/T[1]*100:17.0f}%{T[2]/T[3]*100:13.0f}%")
