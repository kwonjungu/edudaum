# 강의교안 PDF를 쪽 그림 모음으로: python _tools/lecture_pages.py B07 [dpi=28] → lecture/_shots/B07/_pages.png
import sys, os, fitz
from PIL import Image
B = sys.argv[1]; dpi = int(sys.argv[2]) if len(sys.argv) > 2 else 28
d = fitz.open(f'lecture/{B}/{B}_강의교안.pdf'); ims = []
for p in d:
    pm = p.get_pixmap(dpi=dpi); ims.append(Image.frombytes('RGB', (pm.width, pm.height), pm.samples))
w, h = ims[0].size; cols = 4; rows = (len(ims) + cols - 1) // cols
W = Image.new('RGB', (cols * (w + 6), rows * (h + 6)), '#333')
for k, im in enumerate(ims): W.paste(im, ((k % cols) * (w + 6), (k // cols) * (h + 6)))
out = f'lecture/_shots/{B}/_pages.png'; W.save(out); print(out, len(ims), '쪽')
