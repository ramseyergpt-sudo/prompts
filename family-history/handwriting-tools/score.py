"""Score model readings against the reference: character error rate (CER) on 'sure'+'verified' lines."""
import csv,os,sys,re,unicodedata,itertools
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from conventions import conventions
ST=os.path.dirname(os.path.abspath(__file__)); page=sys.argv[1]; refname=sys.argv[2] if len(sys.argv)>2 else page+".tsv"
def load(p):
    d={}
    for r in csv.DictReader(open(p,encoding="utf-8"),delimiter="\t", quoting=csv.QUOTE_NONE):
        try: d[int(r["line"])]=r
        except: pass
    return d
def norm(s,strict=True):
    s=conventions(s)   # GUIDELINES.md character conventions, applied to reference and reading alike
    s=s.replace("[noise]","").replace("[?]","").replace("[","").replace("]","")
    s=re.sub(r"\s+"," ",s).strip()
    if not strict:
        s=s.lower().replace("ÿ","y").replace("ß","ss").replace("ů","u")
        s=re.sub(r"[.,:;]","",s); s=re.sub(r"\s+"," ",s).strip()
    return s
def lev(a,b):
    if a==b: return 0
    prev=list(range(len(b)+1))
    for i,ca in enumerate(a,1):
        cur=[i]
        for j,cb in enumerate(b,1): cur.append(min(prev[j]+1,cur[j-1]+1,prev[j-1]+(ca!=cb)))
        prev=cur
    return prev[-1]
ref=load(os.path.join(ST,"reference",refname))
gold=[k for k,r in ref.items() if r["status"] in("sure","verified")]
models=sorted(f[:-4] for f in os.listdir(os.path.join(ST,"model-readings",page)) if f.endswith(".tsv"))
print(f"page {page}: {len(gold)} scored lines (sure+verified), {sum(len(norm(ref[k]['text'])) for k in gold)} characters\n")
print(f"{'model':24}{'CER strict':>11}{'CER loose':>11}{'exact lines':>13}{'missing':>9}")
res={}
for m in models:
    h=load(os.path.join(ST,"model-readings",page,m+".tsv"))
    for strict in (True,False):
        e=n=0; ex=0; miss=0
        for k in gold:
            r=norm(ref[k]["text"],strict); t=norm(h[k]["text"],strict) if k in h else ""
            if k not in h: miss+=1
            e+=lev(r,t); n+=len(r); ex+=(r==t)
        res[(m,strict)]=(e/n,ex,miss)
    print(f"{m:24}{res[(m,True)][0]*100:10.1f}%{res[(m,False)][0]*100:10.1f}%{res[(m,False)][1]:>8}/{len(gold)}{res[(m,True)][2]:>9}")
# agreement on the reference's 'unsure' lines: mean pairwise similarity
uns=[k for k,r in ref.items() if r["status"] in("unsure","verified-partial")]
H={m:load(os.path.join(ST,"model-readings",page,m+".tsv")) for m in models}
print(f"\nAgreement on {len(uns)} uncertain lines (1 - normalised edit distance, loose):")
for a,b in itertools.combinations(["claude-ref"]+models,2):
    sims=[]
    for k in uns:
        ta=norm(ref[k]["text"] if a=="claude-ref" else H[a].get(k,{}).get("text",""),False)
        tb=norm(H[b].get(k,{}).get("text",""),False)
        if ta or tb: sims.append(1-lev(ta,tb)/max(len(ta),len(tb),1))
    print(f"  {a:22} vs {b:22} {sum(sims)/len(sims):.2f}")
