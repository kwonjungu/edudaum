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
  S9 게임 테마  : 통일 테마 표시가 있고, 하드 그림자·크림 바탕·굵은 먹 테두리가 없다(초점 테두리는 둔다)
  S8 공개용 PDF: 개발자 칸이 연구회 이름이고 문서 정보의 작성자가 비어 있다(creator는 한글 프로그램 이름이라 둔다),
               드라이브 링크는 forms.json에 등록된 공개 서식 주소만(과정안 원본 등 다른 드라이브 링크는 지적)
  S10 서식 파일 : forms.json의 파일·미리보기·묶음(zip)이 assets/forms에 있고 크기가 기록과 같다
  S11 서식 딱지 : 서식마다 구분(공식/연구회 참고)·단계·갈래·근거가 있고, 서식 파일 안에는 안내 문구(공식 양식 아님 등)가 없다 — 안내는 누리집에서만
  S12 공지      : 날짜 꼴, 고정 3건 이하, 첨부 서식·관련 Q&A가 실제로 있다
  S13 Q&A·가이드: 문항 번호 겹침 없음, 문항마다 근거, 근거 문서가 refs.json에 있다, 이어진 서식이 있다
  S14 지난 규칙 : 세특 예시에 시간·기간이 없다, 빈 양식 제목에 연도를 박아 두지 않았다(20○○학년도)
  S15 서식 개인정보: 서식 파일 안 전화·전자우편 꼴 없음, 문서 정보 작성자 비어 있음
  S16 두 곳 일치: 누리집 assets/forms 와 구글 드라이브 「서식 자료실(공개용)」의 파일 목록·크기·해시가 같다
               (드라이브 폴더가 없는 곳 — 예: GitHub Actions — 에서는 건너뛴다. 경로: 환경변수 EDUDAUM_DRIVE_FORMS)
"""
from __future__ import annotations

import json
import os
import re
import sys
import zipfile
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
    for d in ('plan', 'topics', 'lessons', 'tools', 'play', 'notice', 'about', 'guide', 'qna', 'forms', 'search'):
        out += sorted((ROOT / d).rglob('index.html'))
    return out


FORMS_DIR = ROOT / 'assets/forms'
# 공식·참고 여부 안내는 누리집에서만 한다 — 서식 파일 안에 이런 문구가 있으면 지적(2026. 9. 28.)
NOTICE = re.compile(r'공식 양식이 아닙니다|연구회 작성 예시\s*—|원 양식\s*:|공식 양식 아님')
ORGS = {'에듀다움 연구회', '경기 AI 융합교육 에듀다움 교사연구회'}   # 문서 정보 작성자로 허용하는 이름
DRIVE_FORMS = Path(os.environ.get('EDUDAUM_DRIVE_FORMS', r'G:\내 드라이브\경기 에듀다움 - 학교자율시간 AI 교육과정 개발·검증\서식 자료실(공개용)'))


def jload(name, default):
    f = ROOT / '_data' / name
    return json.loads(f.read_text(encoding='utf-8')) if f.exists() else default


def public_drive_ids():
    fm = jload('forms.json', {})
    ids = set(re.findall(r'(?:/d/|folders/|id=)([\w-]{20,})', json.dumps(fm)))
    for f in fm.get('forms', []):
        ids |= {x['drive'] for x in f.get('files', []) if x.get('drive')}
    return ids


def hwpx_text(p: Path) -> str:
    try:
        z = zipfile.ZipFile(p)
        return ' '.join(re.sub(r'<[^>]+>', ' ', z.read(n).decode('utf-8', 'ignore'))
                        for n in z.namelist() if re.match(r'Contents/section\d+\.xml', n))
    except Exception:  # noqa: BLE001
        return ''


def check_forms():
    bad = []
    fm = jload('forms.json', {'forms': [], 'sets': []})
    qids = {q['id'] for q in jload('qna.json', {'items': []}).get('items', [])}
    fids = {f['id'] for f in fm['forms']}
    refs = jload('refs.json', {})
    # S10·S11·S14·S15
    for f in fm['forms']:
        if f.get('kind') not in ('공식', '연구회 참고'):
            bad.append(('S11', f['id'], '구분 없음'))
        if not f.get('stage') or not f.get('track'):
            bad.append(('S11', f['id'], '단계·갈래 없음'))
        if f.get('kind') == '공식' and not (f.get('refs') or f.get('source')):
            bad.append(('S11', f['id'], '공식 양식인데 근거 없음'))
        for x in f.get('files', []) + ([{'file': f['preview']}] if f.get('preview') else []):
            p = FORMS_DIR / x['file']
            if not p.exists():
                bad.append(('S10', f['id'], '파일 없음: ' + x['file']))
                continue
            if x.get('bytes') and p.stat().st_size != x['bytes']:
                bad.append(('S10', f['id'], '크기가 기록과 다름: ' + x['file']))
            if p.suffix == '.hwpx':
                t = hwpx_text(p)
                if NOTICE.search(t):
                    bad.append(('S11', f['id'], '서식 파일 안에 안내 문구가 남음(안내는 누리집에서만): ' + x['file']))
                if x.get('role') == '빈 양식' and re.search(r'20\d\d학년도\s*초등\s*학교자율시간', t):
                    bad.append(('S14', f['id'], '빈 양식 제목에 연도 고정: ' + x['file']))
                if f['id'] == 'F15' and x.get('role') != '빈 양식':
                    for m in re.finditer(r'\d+시간|\d{4}\.\s?\d{1,2}\.\s?\d{1,2}\.', t):
                        bad.append(('S14', f['id'], '세특 예시에 시간·기간: ' + m.group(0)))
                for pat, name in PII[:2]:
                    for m in re.finditer(pat, t):
                        bad.append(('S15', f['id'], '%s 꼴: %s' % (name, m.group(0)[:30])))
                try:
                    hpf = zipfile.ZipFile(p).read('Contents/content.hpf').decode('utf-8', 'ignore')
                    who = [v for v in re.findall(r'name="(?:creator|lastsaveby)" content="text">([^<]*)<', hpf) if v and v not in ORGS]
                    if who:
                        bad.append(('S15', f['id'], '문서 정보에 작성자 남음: ' + x['file']))
                except KeyError:
                    pass
    for s_ in fm.get('sets', []):
        p = FORMS_DIR / s_['zip']
        if not p.exists():
            bad.append(('S10', s_['id'], '묶음 없음: ' + s_['zip']))
        elif s_.get('bytes') and p.stat().st_size != s_['bytes']:
            bad.append(('S10', s_['id'], '묶음 크기가 기록과 다름'))
    # S12
    ns = jload('notices.json', {'notices': []})['notices']
    if sum(1 for n in ns if n.get('pinned')) > 3:
        bad.append(('S12', 'notices.json', '고정 공지 3건 초과'))
    for n in ns:
        if not re.match(r'^\d{4}-\d\d-\d\d$', n.get('date', '')):
            bad.append(('S12', n['id'], '날짜 꼴'))
        for x in n.get('forms', []):
            if x not in fids:
                bad.append(('S12', n['id'], '없는 서식: ' + x))
        for x in n.get('qna', []):
            if x not in qids:
                bad.append(('S12', n['id'], '없는 Q&A: ' + x))
    # S13
    items = jload('qna.json', {'items': []}).get('items', [])
    seen = set()
    for q in items:
        if q['id'] in seen:
            bad.append(('S13', q['id'], '문항 번호 겹침'))
        seen.add(q['id'])
        if not q.get('refs'):
            bad.append(('S13', q['id'], '근거 없음'))
        for x in q.get('forms', []):
            if x not in fids:
                bad.append(('S13', q['id'], '없는 서식: ' + x))
    g = jload('guide.json', {'tracks': {}, 'topics': []})
    for name, b in (('qna', items), ('guide', g), ('about', jload('about.json', {})), ('notices', ns)):
        for d in set(re.findall(r'"doc":\s*"([^"]+)"', json.dumps(b, ensure_ascii=False))):
            if d not in refs:
                bad.append(('S13', name, 'refs.json에 없는 근거 문서: ' + d))
    for x in set(re.findall(r'"(F\d\d)"', json.dumps(g))):
        if x not in fids:
            bad.append(('S13', 'guide', '없는 서식: ' + x))
    # S16 — 드라이브 배치 계획(forms_pack.drive_plan)과 실제 폴더를 대조한다
    if DRIVE_FORMS.exists():
        import hashlib
        import forms_pack
        h = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()  # noqa: E731
        plan = forms_pack.drive_plan(fm)
        have = {p.relative_to(DRIVE_FORMS).as_posix(): p for p in DRIVE_FORMS.rglob('*') if p.is_file() and p.name != 'desktop.ini'}
        for rel in sorted(set(plan) - set(have)):
            bad.append(('S16', rel, '드라이브에 없음'))
        for rel in sorted(set(have) - set(plan)):
            bad.append(('S16', rel, '계획에 없는 파일이 드라이브에 있음'))
        for rel in sorted(set(plan) & set(have)):
            if plan[rel].stat().st_size != have[rel].stat().st_size or h(plan[rel]) != h(have[rel]):
                bad.append(('S16', rel, '두 곳 내용이 다름'))
    else:
        print('  (드라이브 서식 폴더 없음 — S16 건너뜀)')
    return bad


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
    ok_drive = public_drive_ids()
    for f in pages():
        for m in re.finditer(r'drive\.google\.com/[^"\s<]*', f.read_text(encoding='utf-8')):
            ids = re.findall(r'(?:/d/|folders/|id=)([\w-]{20,})', m.group(0))
            if not ids or any(i not in ok_drive for i in ids):
                bad.append(('S8', f.relative_to(ROOT).as_posix(), '등록되지 않은 드라이브 링크(과정안 원본일 수 있음): ' + m.group(0)[:80]))
    bad += check_forms()
    # S9 게임 통일 테마
    for c in LESSON:
        g = ROOT / c / 'index.html'
        if not g.exists():
            continue
        h = g.read_text(encoding='utf-8')
        if '에듀다움 통일 테마' not in h:
            bad.append(('S9', c, '통일 테마 없음 — python _tools/apply_theme.py %s' % c))
        for pat, name in ((r'\dpx \dpx 0 var\(--ink\)', '하드 그림자'), (r'#FBF7EC|#141414', '옛 크림·먹색'),
                          (r'(?:2|2\.5|3)px (?:solid|dashed) var\(--ink\)(?![^{]*outline)', '굵은 먹 테두리')):
            for m in re.finditer(pat, h):
                line = h[h.rfind('\n', 0, m.start()) + 1:h.find('\n', m.end())]
                if 'outline' in line:
                    continue
                bad.append(('S9', c, '%s: %s' % (name, m.group(0))))
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
