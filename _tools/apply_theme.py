# -*- coding: utf-8 -*-
"""체험 게임 쪽에 누리집과 같은 디자인 토큰을 입힌다 — 여러 번 돌려도 같다.

  python _tools/apply_theme.py            게임 28쪽 전부
  python _tools/apply_theme.py B07 B12    지정한 쪽만

바꾸는 것 (_공통기준.md 6-3, 2026. 9. 27. 통일안)
  바탕 크림·점무늬 → 흰 바탕, 먹 #141414 → #222222
  굵은 먹 테두리(1.5~3px) → 1px. 누르는 것(버튼·돌아가기·선택지)은 먹색, 틀·카드는 옅은 회색(#DDDDDD)
  하드 그림자(5px 5px 0) → 그림자 한 단계(rgba) 하나, 작은 하드 그림자 → 없음에 가까운 얇은 그림자
  차시별 포인트색 → 강조색 하나(#FF385C), 노랑(amber) → 옅은 강조색, 주 단추는 강조색 바탕에 흰 글자
  모서리 18~20px → 14px, 작은 모서리 → 8px, 글자 굵기 900 → 700, 800 → 600
화면의 짜임·글·동작은 바꾸지 않는다.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from blocks import LESSON  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
MARK = '/* 에듀다움 통일 테마 2026-09-27 */'
SHADOW = 'rgba(0,0,0,.02) 0 0 0 1px,rgba(0,0,0,.04) 0 2px 6px 0,rgba(0,0,0,.1) 0 4px 8px 0'
SHADOW_SM = '0 1px 2px rgba(0,0,0,.08)'
CONTROL = re.compile(r'btn|button|\.back|\.opt|\.pick|\.tab\b|topnav a|thumb|\.gbtn|\.pbtn|\.mark|\.x\b|\.key|\.choice')
BORDER = re.compile(r'(border(?:-top|-bottom|-left|-right)?)\s*:\s*[\d.]+px (solid|dashed) var\(--ink\)')

TOKENS = [
    (r'--paper\s*:\s*#[0-9A-Fa-f]{6}', '--paper:#FFFFFF'),
    (r'--ink\s*:\s*#141414', '--ink:#222222'),
    (r'--hard\s*:\s*[^;}]+', '--hard:' + SHADOW),
    (r'--hard-sm\s*:\s*[^;}]+', '--hard-sm:' + SHADOW_SM),
    (r'--r\s*:\s*\d+px', '--r:14px'),
    (r'--r-sm\s*:\s*\d+px', '--r-sm:8px'),
    (r'--point\s*:\s*#[0-9A-Fa-f]{3,6}', '--point:#FF385C'),
    (r'--point-soft\s*:\s*#[0-9A-Fa-f]{3,6}', '--point-soft:#FFF0F3'),
    (r'--amber\s*:\s*#[0-9A-Fa-f]{3,6}', '--amber:#FFE3E9'),
    (r'--muted\s*:\s*#[0-9A-Fa-f]{6}', '--muted:#6A6A6A'),
]


def restyle_css(css: str) -> str:
    for a, b in TOKENS:
        css = re.sub(a, b, css)
    if '--line:' not in css:
        css = re.sub(r':root\s*\{', ':root{--line:#DDDDDD;--line-strong:#C1C1C1;', css, count=1)
    css = re.sub(r'background-image\s*:\s*radial-gradient\(var\(--ink\)[^;}]*\)\s*;?', '', css)
    css = re.sub(r'background-size\s*:\s*22px 22px\s*;?', '', css)

    def rule(m):
        sel, dec = m.group(1), m.group(2)
        ctl = bool(CONTROL.search(sel))

        def bd(x):
            if x.group(2) == 'dashed':
                return '%s:1.5px dashed var(--line-strong)' % x.group(1)
            return '%s:1px solid %s' % (x.group(1), 'var(--ink)' if ctl else 'var(--line)')
        dec = BORDER.sub(bd, dec)
        dec = re.sub(r'([45])px \1px 0 var\(--ink\)', SHADOW, dec)
        dec = re.sub(r'([123])px \1px 0 var\(--ink\)', SHADOW_SM, dec)
        dec = re.sub(r'font-weight\s*:\s*900', 'font-weight:700', dec)
        dec = re.sub(r'font-weight\s*:\s*800', 'font-weight:600', dec)
        return sel + '{' + dec + '}'
    css = re.sub(r'([^{}]+)\{([^{}]*)\}', rule, css)
    return css


def theme(h: str) -> str:
    if MARK in h:
        return h
    # <style> 안은 규칙 단위로, 밖(스크립트·style 속성)은 굵은 먹 테두리·하드 그림자만 바꾼다
    parts = re.split(r'(<style>[\s\S]*?</style>)', h)
    for i, part in enumerate(parts):
        if part.startswith('<style>'):
            parts[i] = '<style>' + restyle_css(part[7:-8]) + '</style>'
        else:
            part = re.sub(r'(?<![\d.])(?:1\.5|2|2\.5|3)px (solid) var\(--ink\)', r'1px \1 var(--line)', part)
            part = re.sub(r'([45])px \1px 0 var\(--ink\)', SHADOW, part)
            parts[i] = re.sub(r'([123])px \1px 0 var\(--ink\)', SHADOW_SM, part)
    h = ''.join(parts).replace('#141414', '#222222')
    extra = [MARK]
    if '.btn.main' in h:
        extra.append('.btn.main{background:var(--point);border-color:var(--point);color:#fff}')
    h = h.replace('</style>', '\n' + '\n'.join(extra) + '\n</style>', 1)
    return h


def main(argv):
    want = [a for a in argv if a.startswith('B')]
    n = 0
    for c in sorted(LESSON):
        if want and c not in want:
            continue
        f = ROOT / c / 'index.html'
        if not f.exists():
            continue
        h = f.read_text(encoding='utf-8')
        h2 = theme(h)
        if h2 != h:
            f.write_text(h2, encoding='utf-8')
            n += 1
    print('통일 테마를 입힌 게임 쪽 %d개' % n)


if __name__ == '__main__':
    main(sys.argv[1:])
