"""Make numbered review sheets of the real lines (drop specks and fragments)."""
import json,os,glob,sys
from PIL import Image,ImageDraw,ImageFont
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import config as C
ST=C.HERE; tot=0
SEL=sys.argv[1] if len(sys.argv)>1 else None   # optional selection file: only its pages
IDS={s["id"] for s in json.load(open(SEL))} if SEL else None
for d in sorted(glob.glob(os.path.join(ST,"lines","*"))):
    if IDS and os.path.basename(d) not in IDS: continue
    meta=json.load(open(os.path.join(d,"lines.json")))
    keep=[]
    for L in meta["lines"]:
        im=Image.open(os.path.join(d,L["file"]))
        if im.width<C.MIN_LINE_WIDTH or im.height<C.MIN_LINE_HEIGHT: L["kept"]=False; continue
        L["kept"]=True; keep.append((L,im))
    json.dump(meta,open(os.path.join(d,"lines.json"),"w"))
    sd=os.path.join(d,"sheets"); os.makedirs(sd,exist_ok=True)
    N=C.LINES_PER_SHEET
    for k in range(0,len(keep),N):
        chunk=keep[k:k+N]; W=1700
        ims=[]
        for L,im in chunk:
            s=min(1.0,(W-90)/im.width); ims.append((L,im.resize((int(im.width*s),int(im.height*s)))))
        H=sum(i.height+14 for _,i in ims)+10
        sh=Image.new("RGB",(W,H),"white"); dr=ImageDraw.Draw(sh); y=5
        f=ImageFont.load_default(size=26) if hasattr(ImageFont,"load_default") else None
        for L,i in ims:
            dr.text((5,y+i.height//2-12),f"{L['line']}",fill=(200,0,0),font=f); sh.paste(i,(85,y)); y+=i.height+14
        sh.save(os.path.join(sd,f"sheet{k//N+1:02d}.png"))
    print(os.path.basename(d),len(keep),"real lines",-(-len(keep)//N),"sheets"); tot+=len(keep)
print("total",tot)
