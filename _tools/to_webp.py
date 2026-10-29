# 코덱스가 만든 PNG를 누리집용 webp로 줄인다: python _tools/to_webp.py 폴더 [긴변px]
# contact.png(모아 보기)는 건너뛴다. 원본 PNG는 지우지 않고 _png/로 옮긴다(커밋에서 뺀다).
import sys, pathlib
from PIL import Image
d = pathlib.Path(sys.argv[1]); size = int(sys.argv[2]) if len(sys.argv) > 2 else 512
(d / '_png').mkdir(exist_ok=True)
for p in sorted(d.glob('*.png')):
    if p.stem == 'contact': continue
    im = Image.open(p); im.thumbnail((size, size)); im.save(p.with_suffix('.webp'), 'WEBP', quality=82, method=6)
    p.rename(d / '_png' / p.name)
    print(p.stem, p.with_suffix('.webp').stat().st_size // 1024, 'KB')
