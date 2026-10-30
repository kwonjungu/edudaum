# 블록 강의교안: python _tools/make_lecture.py B01
# lecture/_src/B01.json(원고) → lecture/B01/index.html(모션) + lecture/B01/B01_강의교안.pdf(모든 단계 펼침)
# 설계: _설계/_강의교안_설계_2026-10-30.md, 감수: _설계/_강의교안_감수기준_2026-10-30.md
import json, sys, os, io, html, subprocess
import qrcode, qrcode.image.svg

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://edudaum.vercel.app/'
NAME = {'c1': '새싹쌤', 'c2': '순서쌤', 'c3': '비트쌤', 'c4': '말랑쌤', 'c5': '규칙쌤', 'c6': '데이터쌤', 'c7': '지킴쌤'}
e = lambda x: html.escape(str(x))


def qr(url):
    img = qrcode.make(url, image_factory=qrcode.image.svg.SvgPathImage, box_size=10, border=1)
    s = img.to_string(encoding='unicode')
    return s[s.index('<svg'):]


def ai(src):  # 생성형 AI 그림 표시: 코덱스가 만든 lecture/_assets/Bxx/*.webp(orig 제외)
    return ('/_assets/B' in src and '/orig/' not in src and '/chars/' not in src) or ('../../B' in src and '/assets/' in src)   # 체험 활동 그림도 코덱스 생성


AIX = set()   # 과정안이 'AI 생성 삽화'라고 밝힌 원본 그림(원고의 ai_orig)
NOAI = set()  # _assets에 있어도 AI 그림이 아닌 것(코드·화면 캡처, 영상 썸네일: 원고의 not_ai)


USED_AI = [False]   # 이 장에 생성형 AI 그림이 있으면 장 맨 아래에 한 줄로 밝힌다
USED_ORIG = [False]  # 교수학습 과정안의 원본 그림


def img(src, cls='', style=''):
    if (ai(src) and src not in NOAI) or src in AIX: USED_AI[0] = True
    if '/orig/' in src: USED_ORIG[0] = True
    return f'<figure class="pic {cls}" style="{style}"><img src="{src}" alt="" loading="lazy"></figure>'


def bubble(b, step=None):
    st = f' data-step="{step}"' if step else ''
    side = ' r' if b.get('side') == 'r' else ''
    return (f'<div class="bub{side}"{st}><img class="face" src="../_assets/chars/{b["c"]}.webp" alt="">'
            f'<div class="talk"><b class="nm">{NAME[b["c"]]}</b>{b["t"]}</div></div>')


def bubbles(bs, start=1, row=False):
    h = ''.join(bubble(b, start + i if b.get('step', True) else None) for i, b in enumerate(bs or []))
    return f'<div class="bubrow">{h}</div>' if row and h else h


def tag(s):
    t = s.get('tag', '')
    return f'<span class="ktag">{e(t)}</span>' if t else ''   # 시간은 선생님마다 달라 표시하지 않는다(2026-10-30)


def head(s):
    return f'{tag(s)}<h2 class="h">{s["title"]}</h2>'


def slide(s, d):
    t = s['type']; body = ''
    if t == 'cover':
        body = (f'<div class="cover">{img(s["img"], "bg")}<div class="ctext"><span class="kick">{e(d["grade"])}학년 {e(d["cha"])} · 블록 수업</span>'
                f'<h1 class="h">{d["title"]}</h1><p class="lead">{e(d["mission"])}</p></div>'
                f'<div class="crew"><img src="../_assets/chars/c1.webp" alt=""><img src="../_assets/chars/{d["lead"]}.webp" alt=""></div></div>')
    elif t == 'mission':
        body = (f'<div class="two">{img(s["img"], "contain")}<div class="mcard"><span class="stamp">{e(d["mission"])}</span>'
                f'<p class="mq">{e(d["problem"])}</p>{bubbles(s.get("bubbles"))}</div></div>')
    elif t == 'path':
        cells = ''.join(f'<li class="{"cha" if it[1] == "" else ""}"><b>{e(it[0])}</b><span>{e(it[1])}</span></li>' for it in s['items'])
        body = f'{head(s)}<ol class="path">{cells}</ol><div class="pathrow">{img(s["img"], "contain") if s.get("img") else ""}{bubbles(s.get("bubbles"))}</div>'
    elif t == 'scene':
        body = f'{head(s)}<div class="two wide">{img(s["img"], "contain" if s.get("contain") else "")}<div class="col">{bubbles(s.get("bubbles"))}{note(s)}</div></div>'
    elif t == 'open':
        body = (f'{head(s)}<div class="two wide">{img(s["img"], "contain" if s.get("contain") else "")}<div class="col"><p class="todo">{s["todo"]}</p>'
                f'{note(s)}{link(s)}{bubbles(s.get("bubbles"))}</div></div>')
    elif t == 'predict':
        opts = ''.join(f'<button class="opt">{e(o)}</button>' for o in s['options'])
        after = img(s['after'], 'after contain' if s.get('contain') else 'after', '') if s.get('after') else ''
        body = (f'{head(s)}<div class="two wide"><div class="col"><p class="q">{s["q"]}</p><div class="opts">{opts}</div>'
                f'{bubbles(s.get("bubbles"))}</div><div class="col" data-step="{len(s.get("bubbles") or []) + 1}">{after}{note(s)}</div></div>')
    elif t == 'hunt':
        spots = ''.join(f'<i class="spot" data-step="{i + 1}" style="left:{x}%;top:{y}%;width:{r}%;"><em>{e(lb)}</em></i>' for i, (x, y, r, lb) in enumerate(s['spots']))
        body = (f'{head(s)}<div class="huntwrap"><div class="hunt">{img(s["img"])}{spots}</div>'
                f'<div class="col">{bubbles([dict(b, step=False) for b in s.get("bubbles", [])])}{note(s)}</div></div>')
    elif t == 'flip':
        cards = ''.join(f'<button class="flip"><span class="fr">{img(c["img"], "contain" if c.get("contain") else "")}<b>{e(c["front"])}</b></span><span class="bk">{c["back"]}</span></button>' for c in s['cards'])
        body = f'{head(s)}<div class="flips">{cards}</div>{bubbles(s.get("bubbles"), row=True)}'
    elif t == 'pair':
        body = (f'{head(s)}<div class="pair"><button class="side">{img(s["a"]["img"], "contain" if s["a"].get("contain") else "")}<b>{e(s["a"]["label"])}</b></button>'
                f'<span class="vs">?</span><button class="side">{img(s["b"]["img"], "contain" if s["b"].get("contain") else "")}<b>{e(s["b"]["label"])}</b></button></div>{bubbles(s.get("bubbles"), row=True)}')
    elif t == 'ws':
        ptrs = ''.join(f'<i class="ptr" data-step="{i + 1}" style="left:{x}%;top:{y}%;width:{w}%;height:{h}%"><b>{i + 1}</b></i>' for i, (x, y, w, h) in enumerate(s.get('point', [])))
        if s.get('side'):   # 세로로 긴 활동지 컷: 말풍선은 오른쪽 칸, 캡처는 장 높이 가득
            body = (f'{head(s)}<div class="wsside"><div class="zoom ws"><div class="zin"><img src="{s["img"]}" alt="">{ptrs}</div></div>'
                    f'<div class="col">{bubbles(s.get("bubbles"))}</div></div>{note(s, "top")}')
        else:
          body = (f'{head(s)}<div class="zoom ws"><div class="zin"><img src="{s["img"]}" alt="">{ptrs}</div>'
                f'</div>{note(s, "top")}{bubbles(s.get("bubbles"), row=True)}')
    elif t == 'app':
        shots = ''.join(f'<img src="{x}" alt="" class="{"on" if i == 0 else ""}"><span class="lb{" on" if i == 0 else ""}">{e(l)}</span>' for i, (x, l) in enumerate(s['shots']))
        url = SITE + s['url']
        body = (f'{head(s)}<div class="appz"><div class="zoom scr">{shots}</div>'
                f'<div class="col"><div class="go"><span class="qr">{qr(url)}</span><a href="{url}" target="_blank" class="btn">체험 열기 ↗</a><small>{e(url)}</small></div>{bubbles(s.get("bubbles"))}</div></div>')
    elif t == 'video':
        url = s['url']
        body = (f'{head(s)}<div class="two wide">{img(s["thumb"])}<div class="col">{bubbles(s.get("bubbles"))}'
                f'<div class="go"><a href="{url}" target="_blank" class="btn">▶ 영상 보기 ↗</a><span class="qr">{qr(url)}</span></div></div></div>')
    elif t == 'prep':
        items = ''.join(f'<li><b>{e(a)}</b><span>{e(b)}</span></li>' for a, b in s['items'])
        body = f'{head(s)}<div class="two wide">{img(s["img"], "contain" if s.get("contain") else "")}<div class="col"><ul class="prep">{items}</ul>{bubbles(s.get("bubbles"))}</div></div>'
    elif t == 'order':
        cards = ''.join(f'<button class="oc" data-k="{k}"><b class="n"></b>{img(c["img"], "contain" if c.get("contain") else "") if c.get("img") else ""}<span>{e(c["t"])}</span><em class="k" data-step="{len(s.get("bubbles") or []) + 1}">수업 순서 {k}</em></button>' for k, c in s['cards'])
        body = f'{head(s)}<p class="q">{s["q"]}</p><div class="order">{cards}</div>{bubbles(s.get("bubbles"), row=True)}'
    elif t == 'break':
        body = f'<div class="brk">{img(s["img"])}<div class="col"><h2 class="h">{s["title"]}</h2>{bubbles(s.get("bubbles"))}</div></div>'
    elif t == 'wrap':
        items = ''.join(f'<li data-step="{i + 1}">{x}</li>' for i, x in enumerate(s['items']))
        body = f'{head(s)}<div class="zoom ws"><img src="{s["img"]}" alt=""></div>{note(s, "top")}<ul class="wraprow">{items}</ul>'
    elif t == 'done':
        body = (f'<div class="done">{img(s["img"])}<div class="col"><span class="seal">미션 해결!</span><h2 class="h">{e(d["mission"])} 해결 보고</h2>'
                f'{bubbles(s.get("bubbles"))}<p class="next">다음 미션 · {e(d["next"])}</p></div></div>')
    return body


def link(s):   # 바로가기 단추 + QR (원고의 link: [이름, 주소])
    if not s.get('link'): return ''
    nm, url = s['link']
    return f'<div class="go"><span class="qr">{qr(url)}</span><a href="{url}" target="_blank" class="btn">{e(nm)} ↗</a><small>{e(url)}</small></div>'


def note(s, cls=''):
    return f'<div class="memo {cls}">{s["note"]}</div>' if s.get('note') else ''


CSS = open(os.path.join(ROOT, '_tools', 'lecture.css'), encoding='utf-8').read()
JS = open(os.path.join(ROOT, '_tools', 'lecture.js'), encoding='utf-8').read()


def build(B):
    d = json.load(open(os.path.join(ROOT, 'lecture', '_src', B + '.json'), encoding='utf-8'))
    out = os.path.join(ROOT, 'lecture', B); os.makedirs(out, exist_ok=True)
    N = len(d['slides']); parts = []
    AIX.clear(); AIX.update(d.get('ai_orig', [])); NOAI.clear(); NOAI.update(d.get('not_ai', []))
    mins = {s['tag']: s['min'] for s in d['slides'] if s.get('tag') and s.get('min')}
    for s in d['slides']:
        if s.get('tag') in mins and not s.get('min'): s['min'] = mins[s['tag']]
    for i, s in enumerate(d['slides']):
        USED_AI[0] = False; USED_ORIG[0] = False; body = slide(s, d)
        src = ([f'그림: {B} 교수학습 과정안'] if USED_ORIG[0] else []) + (['생성형 AI로 만든 그림이 있어요'] if USED_AI[0] else [])
        aim = f'<span class="aisl">{" · ".join(src)}</span>' if src else ''
        parts.append(f'<section class="s t-{s["type"]}" data-i="{i}">{body}'
                     f'<div class="grass"></div>{aim}<span class="pn">{B} · {i + 1} / {N}</span></section>')
    doc = (f'<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
           f'<title>{B} 강의교안 — {html.escape(d["title_plain"])} — 에듀다움</title><style>{CSS}</style></head>'
           f'<body><main class="deck">{"".join(parts)}</main><nav class="ctl"><button id="prev" title="앞 장">←</button><span id="pg"></span><button id="nextb" title="다음">→</button><button id="fs" title="전체 화면 (F)">⛶ 전체 화면</button>'
           f'<a href="{B}_강의교안.pdf">PDF</a></nav><script>{JS}</script></body></html>')
    open(os.path.join(out, 'index.html'), 'w', encoding='utf-8').write(doc)
    pdf = os.path.join(out, f'{B}_강의교안.pdf')
    subprocess.run(['node', os.path.join(ROOT, '_tools', 'lecture_pdf.cjs'), os.path.join(out, 'index.html'), pdf], check=True)
    print(B, N, '장 →', out)


if __name__ == '__main__':
    for B in sys.argv[1:]:
        build(B)
