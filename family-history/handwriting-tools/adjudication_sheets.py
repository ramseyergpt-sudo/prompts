"""Enlarged sheets of the lines to settle (close/disputed/agreed-uncertain), 6 per sheet."""
import csv,os,sys
from PIL import Image,ImageDraw,ImageFont
ST=os.path.dirname(os.path.abspath(__file__)); page=sys.argv[1]
rows=[r for r in csv.DictReader(open(os.path.join(ST,"reference",page+".consensus.tsv"),encoding="utf-8"),delimiter="\t", quoting=csv.QUOTE_NONE) if r["status"] in("close","disputed","agreed-uncertain")]
od=os.path.join(ST,"review",page+"_sheets"); os.makedirs(od,exist_ok=True)
f=ImageFont.load_default(size=30)
for k in range(0,len(rows),6):
    ims=[]
    for r in rows[k:k+6]:
        im=Image.open(os.path.join(ST,"lines",page,f"L{int(r['line']):03d}.png")).convert("RGB")
        s=min(1.8,1600/im.width); ims.append((r["line"],im.resize((int(im.width*s),int(im.height*s)))))
    W=1700; H=sum(i.height+20 for _,i in ims)+10; sh=Image.new("RGB",(W,H),"white"); d=ImageDraw.Draw(sh); y=5
    for n,i in ims: d.text((5,y+i.height//2-15),n,fill=(200,0,0),font=f); sh.paste(i,(90,y)); y+=i.height+20
    sh.save(os.path.join(od,f"adj{k//6+1:02d}.png"))
print(page,len(rows),"lines,",(len(rows)+5)//6,"sheets")
