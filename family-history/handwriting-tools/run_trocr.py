"""Read the kept line crops of a page with a TrOCR model -> model-readings/<page>/<name>.tsv

Usage: python3 run_trocr.py PAGE MODEL NAME     (MODEL: a Hugging Face id or a checkpoint folder)
"""
import json,os,sys,torch
from PIL import Image
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import config as C
ST=C.HERE; page=sys.argv[1]; model=sys.argv[2]; name=sys.argv[3]
meta=json.load(open(os.path.join(ST,"lines",page,"lines.json")))
lines=[L for L in meta["lines"] if L.get("kept")]
dev=C.device(); p=TrOCRProcessor.from_pretrained(model); m=VisionEncoderDecoderModel.from_pretrained(model).to(dev).eval()
out=["line\ttext\tconfidence"]
for i in range(0,len(lines),8):
    ch=lines[i:i+8]; ims=[Image.open(os.path.join(ST,"lines",page,L["file"])).convert("RGB") for L in ch]
    with torch.no_grad(): ids=m.generate(p(images=ims,return_tensors="pt").pixel_values.to(dev),max_new_tokens=96,no_repeat_ngram_size=3)
    for L,t in zip(ch,p.batch_decode(ids,skip_special_tokens=True)): out.append(f"{L['line']}\t{t.strip()}\t-")
os.makedirs(os.path.join(ST,"model-readings",page),exist_ok=True)
open(os.path.join(ST,"model-readings",page,name+".tsv"),"w").write("\n".join(out)+"\n"); print(name,len(lines))
