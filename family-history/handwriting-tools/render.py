"""Render the selected register pages to grayscale PNG (pages/<id>.png).

A selection file lists pages as JSON: [{"id": "parish01_i116", "file": "Parish/Parish_01*", "image": 116, "note": "..."}]
"file" is a glob pattern inside config.REGISTERS_DIR; "image" is the 1-based PDF page number.

Usage: python3 render.py [selection.json]      (needs: pip install pypdfium2 pillow)
"""
import glob, json, os, sys
import pypdfium2 as pdfium
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C

ST = C.HERE
SEL = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ST, "selection.json")
os.makedirs(os.path.join(ST, "pages"), exist_ok=True)
for s in json.load(open(SEL)):
    out = os.path.join(ST, "pages", s["id"] + ".png")
    if os.path.exists(out):
        continue
    f = sorted(glob.glob(os.path.join(C.REGISTERS_DIR, s["file"])))[0]
    page = pdfium.PdfDocument(f)[s["image"] - 1]
    w, h = page.get_size()
    im = page.render(scale=C.RENDER_LONG_SIDE / max(w, h)).to_pil().convert("L")
    im.save(out)
    print(s["id"], os.path.basename(f), im.size)
