# -*- coding: utf-8 -*-
"""공통기준을 지켰는지 정적으로 감사한다.

  python _tools/audit.py             모든 차시
  python _tools/audit.py B07         지정한 차시만
  python _tools/audit.py --json      기계가 읽을 결과도 남긴다

보는 것: 규격(단일 파일·CDN·저장), 글자 양, 금지 표현, 직관성·사용성,
개인정보, 연습 모드. 브라우저를 띄우는 검사는 headless.mjs가 한다.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / '_tools' / '_감사결과.json'

CDN_OK = ('https://cdn.jsdelivr.net/', 'https://storage.googleapis.com/mediapipe-models/')
TEXT_CAP = 250          # 한 화면 글자 수 상한
LIMITS = {'제목': 20, '부제': 35, '버튼': 10}

# 개념 정의문 냄새
DEFINE = [r'[가-힣]{2,}(?:이)?란\s', r'[가-힣]{2,}(?:은|는)\s+[^.]{0,40}(?:입니다|이다)\.',
          r'뜻합니다', r'말합니다', r'의미합니다']
# 설명체·AI 티
SMELL = ['이를 통해', '뿐만 아니라', '나아가', '다양한', '살펴봅시다', '알아봅시다',
         '학습 목표', '성취기준', '~란?']


def strip_tags(html: str) -> str:
    h = re.sub(r'<script[\s\S]*?</script>|<style[\s\S]*?</style>|<!--[\s\S]*?-->', ' ', html)
    h = re.sub(r'<[^>]+>', ' ', h)
    return re.sub(r'\s+', ' ', h).strip()


def screens(html: str) -> list:
    """<section> 또는 data-screen 단위를 한 화면으로 본다."""
    parts = re.findall(r'<section\b[^>]*>([\s\S]*?)</section>', html)
    if not parts:
        parts = re.findall(r'<div\b[^>]*data-screen[^>]*>([\s\S]*?)</div>', html)
    return parts or [html]


def audit(path: Path) -> list:
    name = path.parent.name if path.parent != ROOT else 'index'
    html = path.read_text(encoding='utf-8')
    body = strip_tags(html)
    bad = []
    hub = (name == 'index')

    # ── 규격
    if not re.search(r'<html[^>]+lang="ko"', html):
        bad.append('html lang="ko" 없음')
    if 'name="viewport"' not in html:
        bad.append('viewport 메타 없음')
    for m in re.finditer(r'<(?:script|link)[^>]+(?:src|href)="(https?://[^"]+)"', html):
        url = m.group(1)
        if not url.startswith(CDN_OK):
            bad.append('허용하지 않은 외부 주소: %s' % url[:70])
    for m in re.finditer(r'<script[^>]+src="(?!https?://)([^"]+)"', html):
        bad.append('외부 js 파일로 쪼갬: %s (단일 파일이어야 함)' % m.group(1))
    for m in re.finditer(r'<link[^>]+rel="stylesheet"[^>]+href="(?!https?://)([^"]+)"', html):
        bad.append('외부 css 파일로 쪼갬: %s' % m.group(1))
    if re.search(r'\bfetch\s*\(\s*[\'"`]https?://', html):
        for m in re.finditer(r'fetch\s*\(\s*[\'"`](https?://[^\'"`]+)', html):
            if not m.group(1).startswith(CDN_OK):
                bad.append('허용하지 않은 fetch: %s' % m.group(1)[:70])
    if re.search(r'sessionStorage|document\.cookie|indexedDB', html):
        bad.append('localStorage 말고 다른 저장소를 씀')

    if hub:
        return bad

    # ── 글자 양
    for i, s in enumerate(screens(html)):
        t = strip_tags(s)
        if len(t) > TEXT_CAP:
            bad.append('화면[%d] 글자 %d자 (상한 %d자)' % (i + 1, len(t), TEXT_CAP))
    h1 = re.search(r'<h1[^>]*>([\s\S]*?)</h1>', html)
    if h1 and len(strip_tags(h1.group(1))) > LIMITS['제목']:
        bad.append('제목 %d자 (상한 %d자)' % (len(strip_tags(h1.group(1))), LIMITS['제목']))
    for m in re.finditer(r'<button[^>]*>([\s\S]*?)</button>', html):
        label = strip_tags(m.group(1))
        if len(label) > LIMITS['버튼']:
            bad.append('버튼 글자 %d자: %r (상한 %d자)' % (len(label), label[:24], LIMITS['버튼']))

    # ── 금지 표현
    for pat in DEFINE:
        m = re.search(pat, body)
        if m:
            bad.append('개념 정의문으로 읽힘: %r' % body[max(0, m.start() - 12):m.start() + 34])
            break
    for w in SMELL:
        if w in body:
            bad.append('설명체·금지 낱말: %r' % w)
    if re.search(r'퀴즈|정답을 고르|맞혀 보', body):
        bad.append('퀴즈 화면으로 마무리함 (공통기준 4절에서 금지)')
    if re.search(r'<(?:button|h1|h2|h3)[^>]*>[^<]*[\U0001F300-\U0001FAFF]', html):
        bad.append('버튼·제목에 이모지를 아이콘으로 씀')

    # ── 직관성·사용성
    if 'prefers-reduced-motion' not in html:
        bad.append('prefers-reduced-motion 대응 없음')
    if ':focus-visible' not in html:
        bad.append(':focus-visible 테두리 없음')
    if not re.search(r'min-(?:height|width)\s*:\s*4[4-9]px|min-height\s*:\s*[5-9]\d px', html):
        bad.append('44px 터치 영역 규칙이 안 보임')
    # 낱말 목록이다. 되돌리는 버튼의 이름은 차시마다 과정안 말을 따르므로
    # '다시 하기' 말고도 '다시 보기'(B07)·'다시 시작'(B08) 같은 이름이 나온다.
    # 2026-09-17에 그 둘을 더했다. 있는 것을 못 찾던 것을 고친 것이지,
    # 없는 것을 통과시키려고 느슨하게 한 것이 아니다.
    if not re.search(r'다시\s*(?:하기|보기|시작)|되돌리|처음으로|초기화', body):
        bad.append('되돌리기·다시 하기가 없음')
    n_btn = len(re.findall(r'<button', html))
    if n_btn > 14:
        bad.append('버튼이 %d개 — 화면당 5개 이하인지 확인 필요' % n_btn)

    # ── 카메라·마이크
    if 'getUserMedia' in html:
        if not re.search(r'저장되지\s*않', body):
            bad.append('카메라·마이크를 쓰는데 "저장되지 않아요" 문구가 없음')
        if 'getTracks' not in html:
            bad.append('스트림을 끄는 track.stop 처리가 없음')
        if 'visibilitychange' not in html and 'pagehide' not in html:
            bad.append('화면을 벗어날 때 끄는 처리가 없음')
        if re.search(r'얼굴|face', body, re.I) and '얼굴은 비추지' not in body:
            bad.append('얼굴을 다루는 낌새 — 공통기준 6-4에서 금지')
    # ── 연습 모드
    if re.search(r'getUserMedia|cdn\.jsdelivr', html) and '연습 모드' not in body:
        bad.append('막혔을 때의 연습 모드가 없음')

    # ── 개인정보·경쟁
    if re.search(r'<input[^>]+(?:name|placeholder)="[^"]*이름', html):
        bad.append('학생 이름을 입력받음')
    if re.search(r'순위|등수|랭킹|점수판', body):
        bad.append('학생끼리 견주는 순위·점수판이 있음')

    # ── 미리 채운 값
    for m in re.finditer(r'<input[^>]*value="([^"]+)"[^>]*>', html):
        if re.match(r'^\s*[\d.]+\s*$', m.group(1)) and 'range' not in m.group(0):
            bad.append('학생이 채울 칸에 값이 미리 들어 있음: %r' % m.group(1))
            break
    return bad


def main(argv: list) -> int:
    want = [a for a in argv if a.startswith('B')]
    targets = []
    if (ROOT / 'index.html').exists() and not want:
        targets.append(ROOT / 'index.html')
    for d in sorted(ROOT.glob('B*')):
        if d.is_dir() and (d / 'index.html').exists() and (not want or d.name in want):
            targets.append(d / 'index.html')
    if not targets:
        print('감사할 페이지가 없습니다.')
        return 0

    report, total = {}, 0
    for p in targets:
        name = p.parent.name if p.parent != ROOT else 'index'
        msgs = audit(p)
        report[name] = msgs
        total += len(msgs)
        print('%-6s %s' % (name, 'OK' if not msgs else '%d건' % len(msgs)))
        for m in msgs:
            print('   -', m)
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('\n%d쪽 / 감사 지적 %d건 → %s' % (len(targets), total, OUT.name))
    return 1 if total else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
