# -*- coding: utf-8 -*-
"""있는 차시 폴더를 훑어 허브 index.html을 만든다.

  python _tools/make_hub.py

차시 폴더의 index.html에서 제목(h1), 부제, 포인트색(--point)을 읽어 카드로 세운다.
만들지 않기로 한 블록은 폴더가 없으므로 저절로 빠진다.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'index.html'

GRADE = {**{'B%02d' % i: 5 for i in range(1, 15)},
         **{'B%02d' % i: 6 for i in range(15, 29)}}


def strip(s: str) -> str:
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', s)).strip()


def read(d: Path) -> dict | None:
    f = d / 'index.html'
    if not f.exists():
        return None
    h = f.read_text(encoding='utf-8')
    title = re.search(r'<h1[^>]*>([\s\S]*?)</h1>', h)
    lead = re.search(r'class="lead"[^>]*>([\s\S]*?)</', h) or \
        re.search(r'<h1[^>]*>[\s\S]*?</h1>\s*<p[^>]*>([\s\S]*?)</p>', h)
    point = re.search(r'--point\s*:\s*(#[0-9A-Fa-f]{3,6})', h)
    return {'id': d.name,
            'title': strip(title.group(1)) if title else d.name,
            'lead': strip(lead.group(1))[:40] if lead else '',
            'point': point.group(1) if point else '#F59E0B'}


CSS = """
:root{--ink:#141414;--paper:#FBF7EC;--surface:#fff;--amber:#FFB800;--muted:#6B6B6B;
--r:20px;--hard:5px 5px 0 var(--ink);--hard-sm:3px 3px 0 var(--ink)}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);font-size:17px;line-height:1.6;
font-family:'Pretendard','Malgun Gothic',system-ui,sans-serif;
background-image:radial-gradient(var(--ink) .5px,transparent .5px);background-size:22px 22px}
.wrap{max-width:1040px;margin:0 auto;padding:28px 18px 56px}
.kick{display:inline-block;border:2.5px solid var(--ink);background:var(--amber);
border-radius:999px;padding:5px 14px;font-weight:800;font-size:13px;letter-spacing:.04em}
h1{font-size:clamp(28px,6vw,46px);font-weight:900;letter-spacing:-.035em;margin:14px 0 6px}
.lead{color:var(--muted);font-weight:600;margin:0 0 26px}
.gradelabel{margin:30px 0 12px;font-weight:900;font-size:19px}
.grid{display:grid;gap:16px;grid-template-columns:repeat(auto-fill,minmax(250px,1fr))}
.card{display:block;text-decoration:none;color:inherit;background:var(--surface);
border:3px solid var(--ink);border-radius:var(--r);box-shadow:var(--hard);padding:18px;
transition:transform .12s,box-shadow .12s}
.card:hover{transform:translate(-2px,-2px);box-shadow:7px 7px 0 var(--ink)}
.card:active{transform:translate(3px,3px);box-shadow:0 0 0 var(--ink)}
.card:focus-visible{outline:3px solid var(--pt);outline-offset:3px}
.num{display:inline-block;border:2px solid var(--ink);border-radius:999px;
background:var(--pt);color:#fff;font-weight:800;font-size:12px;padding:3px 10px}
.card h2{font-size:19px;font-weight:800;margin:10px 0 4px;letter-spacing:-.02em}
.card p{margin:0;color:var(--muted);font-size:14px;font-weight:600}
.note{margin-top:34px;border:3px solid var(--ink);border-radius:var(--r);
background:var(--ink);color:var(--paper);padding:16px 18px;font-weight:700;font-size:15px}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
"""


def main() -> None:
    cards = [c for c in (read(d) for d in sorted(ROOT.glob('B*')) if d.is_dir()) if c]
    if not cards:
        print('차시 폴더가 없습니다.')
        return

    body = []
    for g in (5, 6):
        mine = [c for c in cards if GRADE.get(c['id']) == g]
        if not mine:
            continue
        body.append('<h2 class="gradelabel">%d학년</h2>\n<div class="grid">' % g)
        for c in mine:
            body.append(
                '  <a class="card" href="%s/" style="--pt:%s">'
                '<span class="num">%s</span><h2>%s</h2><p>%s</p></a>'
                % (c['id'], c['point'], c['id'], c['title'], c['lead']))
        body.append('</div>')

    html = ('<!doctype html>\n<html lang="ko">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
            '<title>에듀다움 체험 — 학교자율시간</title>\n<style>%s</style>\n</head>\n'
            '<body>\n<div class="wrap">\n'
            '<span class="kick">학교자율시간 · 5~6학년</span>\n'
            '<h1>수업 중에<br>잠깐 만져 보는 체험</h1>\n'
            '<p class="lead">과정안의 활동 하나를 짧게 미리 겪어 보거나 견주어 봐요.</p>\n'
            '%s\n'
            '<p class="note">카메라와 마이크는 화면에만 쓰이고 저장되지 않아요. '
            '밖으로 보내는 것도 없어요.</p>\n'
            '</div>\n</body>\n</html>\n') % (CSS, '\n'.join(body))

    OUT.write_text(html, encoding='utf-8')
    print('허브 %d개 카드 → index.html' % len(cards))
    for c in cards:
        print('  %s %s' % (c['id'], c['title']))


if __name__ == '__main__':
    main()
