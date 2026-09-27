# -*- coding: utf-8 -*-
"""교수학습 과정안(hwpx)을 웹 데이터로 옮긴다 — 홈페이지 과정안 쪽의 단 하나의 근거.

  python _tools/export_plans.py "<과정안 hwpx 폴더>"

hwpx 28개를 읽어 아래를 만든다.
  _data/lessons.json     차시별 개요·교수학습 활동·평가 계획 (문단 순서 그대로, 그림 자리 포함)
  assets/plan/BXX_n.jpg  과정안에 든 그림 (가로 960px로 줄여 jpg)

과정안이 바뀌면 hwpx를 고친 뒤 이 스크립트와 make_site.py를 다시 돌린다.
웹에서 과정안 문장을 따로 고치지 않는다(과정안이 원본이다).

개발자 칸(개요 '개발자')은 공개 누리집에 싣지 않는다. 필요하면 SHOW_DEV를 True로 바꾼다.
"""
from __future__ import annotations

import io
import json
import re
import sys
import zipfile
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from blocks import LESSON  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / '_data' / 'lessons.json'
IMG = ROOT / 'assets' / 'plan'
SHOW_DEV = False
MAXW = 960

P_RE = re.compile(r'<hp:p\b[\s\S]*?</hp:p>')


def para_items(p: str) -> list:
    """문단 하나 → [('text', s)] 또는 [('img', binId)]"""
    out = []
    for m in re.finditer(r'binaryItemIDRef="([^"]+)"', p):
        out.append(('img', m.group(1)))
    # 표 안의 표는 쓰지 않는다. 글자는 hp:t 안에서만 모은다.
    t = ''.join(re.findall(r'<hp:t>([\s\S]*?)</hp:t>', p))
    t = re.sub(r'<[^>]+>', '', t)
    t = (t.replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"')
         .replace('&apos;', "'").replace('&amp;', '&'))
    if not out:
        out.append(('text', t.strip()))
    elif t.strip():
        out.append(('text', t.strip()))
    return out


def cells(tbl: str) -> dict:
    res = {}
    for tc in re.finditer(r'<hp:tc\b[\s\S]*?</hp:tc>', tbl):
        x = tc.group(0)
        a = re.search(r'<hp:cellAddr colAddr="(\d+)" rowAddr="(\d+)"', x)
        span = re.search(r'<hp:cellSpan colSpan="(\d+)" rowSpan="(\d+)"', x)
        items = []
        for p in P_RE.findall(x):
            items += para_items(p)
        # 끝의 빈 줄 정리, 빈 줄 연속은 하나로
        clean = []
        for k, v in items:
            if k == 'text' and not v and (not clean or clean[-1] == ('text', '')):
                continue
            clean.append((k, v))
        while clean and clean[-1] == ('text', ''):
            clean.pop()
        res[(int(a.group(2)), int(a.group(1)))] = {
            'items': clean, 'rowspan': int(span.group(2)) if span else 1}
    return res


def texts(c) -> list:
    return [v for k, v in c['items'] if k == 'text' and v] if c else []


def export(path: Path, bins: dict, code: str) -> dict:
    z = zipfile.ZipFile(path)
    x = z.read('Contents/section0.xml').decode('utf-8')
    tbls = re.findall(r'<hp:tbl\b[\s\S]*?</hp:tbl>', x)
    t0, t1, t2 = (cells(t) for t in tbls[:3])

    # 그림: 문서 순서대로 BXX_1, BXX_2 …
    hpf = z.read('Contents/content.hpf').decode('utf-8')
    href = dict(re.findall(r'<opf:item id="([^"]+)" href="([^"]+)"', hpf))
    img_no = [0]

    def conv(items):
        out = []
        for k, v in items:
            if k == 'img':
                img_no[0] += 1
                name = '%s_%d.jpg' % (code, img_no[0])
                im = Image.open(io.BytesIO(z.read(href[v]))).convert('RGB')
                if im.width > MAXW:
                    im = im.resize((MAXW, round(im.height * MAXW / im.width)), Image.LANCZOS)
                im.save(IMG / name, 'JPEG', quality=80, optimize=True)
                out.append({'img': 'assets/plan/' + name})
            else:
                out.append(v)
        # 그림 바로 뒤 '[사진 N] …' 줄을 캡션으로 붙인다
        res = []
        for it in out:
            if isinstance(it, str) and re.match(r'^\[(사진|그림) ?\d+\]', it) and res and isinstance(res[-1], dict):
                res[-1]['caption'] = it
            else:
                res.append(it)
        return res

    # 개요 (표1): 왼쪽 라벨 → 오른쪽 값
    ov = {}
    for r in sorted({r for r, _ in t1}):
        lab = (texts(t1.get((r, 1))) or texts(t1.get((r, 0))) or [''])[-1]
        val = texts(t1.get((r, 3)))
        if lab and val:
            ov[lab] = val
    if not SHOW_DEV:
        ov.pop('개발자', None)

    # 활동 (표0)
    rows = []
    r = 1
    while (r, 3) in t0:
        rows.append({
            'lesson': ' '.join(texts(t0.get((r, 0)))) or (rows[-1]['lesson'] if rows else ''),
            'stage': ' '.join(texts(t0.get((r, 1)))),
            'time': ' '.join(texts(t0.get((r, 2)))),
            'body': conv(t0[(r, 3)]['items']),
            'res': texts(t0.get((r, 4))),
        })
        r += 1

    # 평가 (표2)
    ev = []
    r, cur = 1, None
    while (r, 2) in t2:
        if (r, 0) in t2:
            cur = {'aspect': texts(t2[(r, 0)]), 'goal': ' '.join(texts(t2.get((r, 1)))),
                   'method': texts(t2.get((r, 4))), 'levels': []}
            ev.append(cur)
        cur['levels'].append({'level': ' '.join(texts(t2[(r, 2)])),
                              'desc': ' '.join(texts(t2.get((r, 3))))})
        r += 1

    g, n = LESSON[code]
    return {'code': code, 'grade': g, 'lessons': n, 'file': path.name,
            'overview': ov, 'rows': rows, 'eval': ev, 'images': img_no[0]}


def main() -> None:
    src = Path(sys.argv[1])
    IMG.mkdir(parents=True, exist_ok=True)
    for f in IMG.glob('*.jpg'):
        f.unlink()
    out = {}
    for f in sorted(src.glob('B*.hwpx')):
        code = f.name[:3]
        if code in LESSON:
            out[code] = export(f, {}, code)
            print(code, len(out[code]['rows']), '행', out[code]['images'], '그림')
    DATA.parent.mkdir(exist_ok=True)
    DATA.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding='utf-8')
    print('→', DATA, len(out))


if __name__ == '__main__':
    main()
