# -*- coding: utf-8 -*-
"""누리집 쪽(홈·plan·topics·lessons·tools·play)을 점검한다. 체험 게임 쪽은 audit.py가 본다.

  python _tools/site_check.py            점검만
  python _tools/site_check.py --online   바깥 링크가 열리는지도 본다(느림)

보는 것
  S1 쪽 있음   : 홈·네 갈래·차시 28쪽·PDF 28개가 있다
  S2 안 링크   : 쪽 안의 상대 링크·그림이 실제 파일을 가리킨다
  S3 과정안 일치: 차시 쪽 제목 = _data/lessons.json 학습 주제, 성취기준 코드가 들어 있다
  S4 개인정보  : 전화번호·전자우편·생년월일 꼴, '개발자' 칸이 없다
  S5 도구 링크 : 바깥 링크는 https, tools.json·links.json 주소는 모두 https
  S6 게임 짝   : 체험 게임이 있는 차시는 차시 쪽에서 게임으로, 게임 쪽에서 차시 쪽으로 이어진다
  S7 규격      : lang="ko", viewport, 바깥 스크립트·스타일 없음
  S8 공개용 PDF: 개발자 칸이 연구회 이름이고 문서 정보의 작성자가 비어 있다(creator는 한글 프로그램 이름이라 둔다), 드라이브 원본 링크 없음
"""
from __future__ import annotations

import json
import re
import sys
import urllib.request
from pathlib import Path
from urllib.parse import unquote

sys.path.insert(0, str(Path(__file__).resolve().parent))
from blocks import LESSON  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
for s in (sys.stdout, sys.stderr):
    try:
        s.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

PII = [(r'01[016789]-?\d{3,4}-?\d{4}', '전화번호'), (r'[\w.+-]+@[\w-]+\.[\w.]+', '전자우편'),
       (r'(19|20)\d\d\.\s?\d\d\.\s?\d\d\.\s*생|생년월일', '생년월일'), (r'>개발자<', '개발자 칸')]


def pages():
    out = [ROOT / 'index.html']
    for d in ('plan', 'topics', 'lessons', 'tools', 'play'):
        out += sorted((ROOT / d).rglob('index.html'))
    return out


def main(argv):
    bad = []
    L = json.loads((ROOT / '_data/lessons.json').read_text(encoding='utf-8'))
    std = json.loads((ROOT / '_data/standards.json').read_text(encoding='utf-8'))['lessons']
    # S1
    for p in ['index.html', 'plan/index.html', 'topics/index.html', 'lessons/index.html', 'tools/index.html', 'play/index.html']:
        if not (ROOT / p).exists():
            bad.append(('S1', p, '쪽 없음'))
    for c in LESSON:
        if not (ROOT / 'lessons' / c / 'index.html').exists():
            bad.append(('S1', c, '차시 쪽 없음'))
        if not (ROOT / 'assets/pdf' / (c + '.pdf')).exists():
            bad.append(('S1', c, 'PDF 없음'))
    ext = set()
    for f in pages():
        h = f.read_text(encoding='utf-8')
        rel = f.relative_to(ROOT).as_posix()
        # S7
        if 'lang="ko"' not in h or 'name="viewport"' not in h:
            bad.append(('S7', rel, 'lang·viewport'))
        if re.search(r'<script[^>]+src=|<link[^>]+stylesheet', h):
            bad.append(('S7', rel, '바깥 스크립트·스타일'))
        # S2
        for m in re.finditer(r'(?:href|src)="([^"#]+)(#[^"]*)?"', h):
            u = m.group(1)
            if re.match(r'^(https?:|mailto:)', u):
                if u.startswith('http:'):
                    bad.append(('S5', rel, 'https 아님: ' + u))
                ext.add(u)
                continue
            t = (f.parent / unquote(u)).resolve()
            if t.is_dir():
                t = t / 'index.html'
            if not t.exists():
                bad.append(('S2', rel, '없는 곳: ' + u))
        # S4
        txt = re.sub(r'<script[\s\S]*?</script>|<style[\s\S]*?</style>', ' ', h)
        for pat, name in PII:
            for m in re.finditer(pat, txt):
                bad.append(('S4', rel, '%s 꼴: %s' % (name, m.group(0)[:30])))
    # S3·S6
    for c in LESSON:
        f = ROOT / 'lessons' / c / 'index.html'
        if not f.exists():
            continue
        h = f.read_text(encoding='utf-8')
        topic = L[c]['overview'].get('학습 주제', [''])[0]
        h1 = re.search(r'<h1>([\s\S]*?)</h1>', h)
        import html as H
        if not h1 or H.unescape(h1.group(1)).strip() != topic:
            bad.append(('S3', c, '제목이 학습 주제와 다름'))
        if std.get(c) and std[c] not in H.unescape(h):
            bad.append(('S3', c, '성취기준 코드 없음'))
        g = ROOT / c / 'index.html'
        if g.exists():
            if 'href="../../%s/"' % c not in h:
                bad.append(('S6', c, '차시 쪽 → 게임 링크 없음'))
            if 'href="../lessons/%s/"' % c not in g.read_text(encoding='utf-8'):
                bad.append(('S6', c, '게임 쪽 → 차시 쪽 링크 없음'))
    # S8
    try:
        import fitz
        for c in LESSON:
            f = ROOT / 'assets/pdf' / (c + '.pdf')
            if not f.exists():
                continue
            d = fitz.open(f)
            t = ''.join(pg.get_text() for pg in d)
            m = re.search(r'개발자\s*\n\s*([^\n]+)', t)
            if not m or m.group(1).strip() != '경기 AI 융합교육 에듀다움 교사연구회':
                bad.append(('S8', c, 'PDF 개발자 칸이 공개용이 아님'))
            if any((d.metadata or {}).get(k) for k in ('author', 'subject', 'keywords')):
                bad.append(('S8', c, 'PDF 문서 정보에 작성자 등이 남음'))
    except ImportError:
        print('  (PyMuPDF 없음 — S8 PDF 검사 건너뜀)')
    for f in pages():
        if 'drive.google.com' in f.read_text(encoding='utf-8'):
            bad.append(('S8', f.relative_to(ROOT).as_posix(), '드라이브 원본 링크'))
    # S5
    for name in ('tools.json', 'links.json'):
        for u in re.findall(r'"url":\s*"([^"]+)"', (ROOT / '_data' / name).read_text(encoding='utf-8')):
            if not u.startswith('https://'):
                bad.append(('S5', name, 'https 아님: ' + u))
    if '--online' in argv:
        for u in sorted(ext):
            try:
                req = urllib.request.Request(u, method='GET', headers={'User-Agent': 'Mozilla/5.0'})
                code = urllib.request.urlopen(req, timeout=15).status
            except Exception as ex:  # noqa: BLE001
                code = getattr(ex, 'code', str(ex)[:40])
            if code != 200 and code != 403:   # canva는 자동 요청에 403
                bad.append(('S5', 'online', '%s → %s' % (u, code)))
    n = len(pages())
    print('누리집 %d쪽 점검, 지적 %d건' % (n, len(bad)))
    for k, w, m in bad:
        print('  [%s] %s — %s' % (k, w, m))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
