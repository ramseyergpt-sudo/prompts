"""Cut each rendered page into numbered line images (kraken blla) and draw an overlay for checking."""
import json,os,glob,sys
from PIL import Image,ImageDraw
from kraken import blla
from kraken.lib.segmentation import extract_polygons
ST=os.path.dirname(os.path.abspath(__file__))
SEL=sys.argv[1] if len(sys.argv)>1 else None   # optional selection file: only its pages
IDS={s["id"] for s in json.load(open(SEL))} if SEL else None
for p in sorted(glob.glob(os.path.join(ST,"pages","*.png"))):
    if IDS and os.path.basename(p)[:-4] not in IDS: continue
    pid=os.path.basename(p)[:-4]; od=os.path.join(ST,"lines",pid)
    if os.path.exists(os.path.join(od,"lines.json")): continue
    os.makedirs(od,exist_ok=True)
    im=Image.open(p).convert("RGB"); seg=blla.segment(im)
    items=[]
    for li,(lim,line) in enumerate(extract_polygons(im,seg)):
        bl=line.baseline; x=min(q[0] for q in bl); y=sum(q[1] for q in bl)/len(bl)
        items.append({"x":int(x),"y":int(y),"baseline":[list(map(int,q)) for q in bl],"boundary":[list(map(int,q)) for q in line.boundary],"img":lim})
    W=im.width; items.sort(key=lambda d:(d["x"]>W*0.5, d["y"]))   # left column/page first, then top to bottom
    meta=[]; ov=im.copy(); dr=ImageDraw.Draw(ov)
    for n,d in enumerate(items,1):
        name=f"L{n:03d}.png"; d["img"].save(os.path.join(od,name))
        dr.line([tuple(q) for q in d["boundary"]]+[tuple(d["boundary"][0])],fill=(255,0,0),width=3)
        dr.text((d["x"]-60,d["y"]-30),str(n),fill=(0,0,255))
        meta.append({"line":n,"file":name,"x":d["x"],"y":d["y"],"baseline":d["baseline"],"boundary":d["boundary"]})
    json.dump({"page":pid,"lines":meta},open(os.path.join(od,"lines.json"),"w"))
    ov.thumbnail((1800,1800)); ov.save(os.path.join(od,"overlay.jpg"),quality=80)
    print(pid,len(meta),"lines",flush=True)
