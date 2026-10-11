# -*- coding: utf-8 -*-
"""에듀다움 누리집을 만든다 — 과정안 데이터(_data)와 체험 게임 폴더(BXX)를 이어 붙인다.

  python _tools/make_site.py

만드는 쪽
  index.html              홈 (64차시 지도, 네 갈래 입구)
  plan/index.html         1) 계획서 및 성취기준
  topics/index.html       2) 주제(영역)별 활동 내용
  lessons/index.html      3) 차시별 교수학습 과정안 목록
  lessons/BXX/index.html     차시 쪽 — 과정안 전문 + 연동 도구·링크 + 체험 게임 + PDF
  tools/index.html        연동 도구 모음
  play/index.html         체험 게임 목록 (예전 허브)

근거 데이터
  _data/lessons.json   export_plans.py가 hwpx에서 뽑은 과정안 (손으로 고치지 않는다)
  _data/site.json      과정 이름·영역·연계 성취기준
  _data/standards.json 자체 성취기준 확정 문장
  _data/tools.json     외부 도구 목록 (match 낱말로 차시에 저절로 붙는다)
  _data/links.json     차시별로 더 걸 링크·숨길 도구·드라이브 원본 id

체험 게임 쪽(BXX/index.html)은 이 스크립트가 만들지 않는다. 제목·부제·포인트색만 읽어 온다.
"""
from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from blocks import LESSON, grade, label  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / '_data'
L = json.loads((D / 'lessons.json').read_text(encoding='utf-8'))
SITE = json.loads((D / 'site.json').read_text(encoding='utf-8'))
STD = json.loads((D / 'standards.json').read_text(encoding='utf-8'))
TOOLS = json.loads((D / 'tools.json').read_text(encoding='utf-8'))['tools']
LINKS = json.loads((D / 'links.json').read_text(encoding='utf-8'))
EASY = json.loads((D / 'easy.json').read_text(encoding='utf-8'))['lessons']
AREA_OF = {b: a for a in SITE['areas'] for b in a['blocks']}
CODES = sorted(LESSON)

e = html.escape


# ───────────────────────── 공통 모양
CSS = (Path(__file__).resolve().parent / 'site.css').read_text(encoding='utf-8')

BRAND = ('<svg viewBox="0 0 32 32" aria-hidden="true"><path fill="currentColor" d="M16 3c7.2 0 13 5.8 13 13s-5.8 13-13 13S3 23.2 3 16 8.8 3 16 3zm0 6.5a6.5 6.5 0 1 0 0 13 6.5 6.5 0 0 0 0-13z"/>'
         '<circle cx="16" cy="16" r="2.6" fill="currentColor"/></svg>')


# 윗줄 메뉴 — 넷만 둔다(2026. 10. 11.). 예전 쪽은 지우지 않고 펼침 항목으로 묶는다.
# (주소, 이름, 아이콘, 펼침 항목[(주소, 이름)])
MENU = [
    ('lessons/', '수업 자료', 'book-open', [('lessons/', '차시별 수업 꾸러미'), ('topics/', '단원별로 보기'), ('tools/', '연동 도구')]),
    ('play/', '체험 게임', 'game', []),
    ('about/', '도입 안내', 'lightbulb', [('about/', '학교자율시간이란?'), ('guide/', '도입 절차'), ('forms/', '서식 받기'),
                                     ('forms/set/', '채운 서식 한 벌'), ('qna/', '자주 묻는 질문')]),
    ('plan/', '연구회', 'people-team', [('plan/', '연구회 소개'), ('notice/', '알림')]),
]
# 펼침에 없고 바닥 사이트맵에만 두는 쪽
MORE = [('forms/list/', '서식 목록·검색'), ('forms/versions/', '판본 차이·정오표'), ('search/', '검색')]

NAV_JS = """<script>
(function(){
  var dd=[].slice.call(document.querySelectorAll('.menu details'));
  document.addEventListener('click',function(ev){dd.forEach(function(d){if(!d.contains(ev.target))d.removeAttribute('open')})});
  dd.forEach(function(d){d.addEventListener('focusout',function(ev){if(!d.contains(ev.relatedTarget))d.removeAttribute('open')})});
  document.addEventListener('keydown',function(ev){if(ev.key==='Escape')dd.forEach(function(d){if(d.open){d.removeAttribute('open');d.querySelector('summary').focus()}})});
  dd.forEach(function(d){d.addEventListener('toggle',function(){if(d.open)dd.forEach(function(o){if(o!==d)o.removeAttribute('open')})})});
  var m=document.querySelector('.menu'), c=m&&m.querySelector('.m[aria-current]');
  if(c&&m.scrollWidth>m.clientWidth) m.scrollLeft=c.offsetLeft-16;
})();
</script>
"""


def menu_top(cur: str) -> str:
    """지금 쪽이 어느 메뉴 아래에 있는지 — 가장 길게 맞는 주소를 고른다."""
    best, n = '', 0
    for href, _, _, sub in MENU:
        for h in [href] + [s for s, _ in sub]:
            if cur.startswith(h) and len(h) > n:
                best, n = href, len(h)
    return best


def icon(name: str, up: str, cls: str = 'ic') -> str:
    return '<img class="%s" src="%sassets/icons/%s.svg" alt="" width="24" height="24">' % (cls, up, name)


def nav(up: str, cur: str) -> str:
    top = menu_top(cur)
    out = []
    for href, name, ic, sub in MENU:
        here = ' aria-current="page"' if href == top else ''
        if not sub:
            out.append('<a class="m" href="%s%s"%s>%s<span>%s</span></a>' % (up, href, here, icon(ic, up), e(name)))
            continue
        items = ''.join('<a href="%s%s"%s>%s</a>' % (up, h, ' aria-current="page"' if h == cur else '', e(t)) for h, t in sub)
        out.append('<details class="dd"><summary class="m"%s>%s<span>%s</span></summary><div class="panel">%s</div></details>'
                   % (here, icon(ic, up), e(name), items))
    return '<nav class="menu" aria-label="누리집 메뉴">%s</nav>' % ''.join(out)


def page(path: str, title: str, body: str, cur: str, extra_js: str = '') -> None:
    depth = path.count('/') + 1 if path else 0
    up = '../' * depth
    doc = ('<!doctype html>\n<html lang="ko">\n<head>\n<meta charset="utf-8">\n'
           '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
           '<title>%s</title>\n<link rel="icon" href="%sassets/icons/book-open.svg">\n<style>%s</style>\n</head>\n<body>\n'
           '<a class="skip" href="#main">본문 바로가기</a>\n'
           '<header class="top"><div class="in"><a class="brand" href="%s">%s에듀다움</a>%s'
           '<a class="find" href="%ssearch/" aria-label="누리집 검색"%s>%s<span>검색</span></a></div></header>\n'
           '<main id="main">\n%s\n</main>\n'
           '<footer><div class="in">%s<p><b>%s</b><br>%s · %s · 과정안 기준일 %s<br>'
           '학교자율시간 안내·서식은 경기도교육청 자료를 재구성했어요. 원문과 최신 공문을 함께 확인하세요.<br>'
           '학생 이름·점수를 받지 않고, 체험 게임의 카메라·마이크는 화면에만 쓰며 저장하지 않아요.</p></div></footer>\n'
           '%s%s</body>\n</html>\n') % (e(title), up, CSS, up or './', BRAND, nav(up, cur), up,
                                        ' aria-current="page"' if cur == 'search/' else '', SEARCH_ICON, body, sitemap(up),
                                        e(SITE['org']), e(SITE['title']), e(SITE['subtitle']), e(SITE['updated']), NAV_JS, extra_js)
    out = ROOT / path / 'index.html' if path else ROOT / 'index.html'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc, encoding='utf-8')


SEARCH_ICON = ('<svg viewBox="0 0 32 32" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round">'
               '<circle cx="14" cy="14" r="8.5"/><path d="M20.5 20.5l6.5 6.5"/></svg>')


def sitemap(up: str) -> str:
    """바닥 사이트맵 — 윗줄 메뉴와 같은 항목."""
    cols = []
    for href, name, _, sub in MENU:
        links = sub or [(href, name)]
        cols.append('<div><b>%s</b>%s</div>' % (e(name), ''.join('<a href="%s%s">%s</a>' % (up, h, e(t)) for h, t in links)))
    cols.append('<div><b>더 보기</b>%s</div>' % ''.join('<a href="%s%s">%s</a>' % (up, h_, e(t)) for h_, t in MORE))
    return '<nav class="smap" aria-label="사이트맵">%s</nav>' % ''.join(cols)


# ───────────────────────── 데이터 도우미
def ov(code, key):
    return L[code]['overview'].get(key, [])


def topic(code):
    return (ov(code, '학습 주제') or [''])[0]


def problem(code):
    return (ov(code, '학습 문제') or [''])[0]


def std_code(code):
    return STD['lessons'].get(code, '')


def activities(code):
    """◎ 활동 제목(시간 포함)만 뽑는다."""
    out = []
    for r in L[code]['rows']:
        for it in r['body']:
            if isinstance(it, str) and it.startswith('◎'):
                t = it[1:].strip()
                if re.match(r'^활동\s*\d', t):
                    out.append(t)
    return out


def all_text(code):
    parts = []
    for r in L[code]['rows']:
        parts += [x for x in r['body'] if isinstance(x, str)] + r['res']
    for v in L[code]['overview'].values():
        parts += v
    return '\n'.join(parts)


def tools_of(code):
    t = all_text(code).lower()
    cfg = LINKS.get(code, {})
    hide, add = set(cfg.get('hide', [])), set(cfg.get('add', []))
    return [x for x in TOOLS if x['id'] not in hide and
            (x['id'] in add or any(m.lower() in t for m in x['match']))]


def game(code):
    f = ROOT / code / 'index.html'
    if not f.exists():
        return None
    h = f.read_text(encoding='utf-8')
    strip = lambda s: re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', s)).strip()
    t = re.search(r'<h1[^>]*>([\s\S]*?)</h1>', h)
    ld = re.search(r'class="lead"[^>]*>([\s\S]*?)</', h)
    pt = re.search(r'--point\s*:\s*(#[0-9A-Fa-f]{3,6})', h)
    return {'title': strip(t.group(1)) if t else code, 'lead': strip(ld.group(1)) if ld else '',
            'point': pt.group(1) if pt else '#F59E0B'}


def thumb(code):
    """과정안 첫 그림(대개 도입 상황 그림)을 카드 사진으로 쓴다."""
    for r in L[code]['rows']:
        for it in r['body']:
            if isinstance(it, dict):
                return it['img']
    return ''


def easy(code, key):
    """카드 한 줄 제목(title)·한 줄 요약(summary) — _data/easy.json. 없으면 학습 주제·학습 문제를 쓴다."""
    v = EASY.get(code, {}).get(key)
    return v or (topic(code) if key == 'title' else problem(code))


def sheet_href(code):
    """활동지 PDF — 올라오면(assets/sheets/BXX.pdf) 저절로 걸린다. 없으면 빈 문자열."""
    return 'assets/sheets/%s.pdf' % code if (ROOT / 'assets/sheets' / ('%s.pdf' % code)).exists() else ''


def res_icons(code, up):
    """카드 아래 아이콘 셋 — 지도안·활동지·게임. 아직 없는 자료는 흐리게 두고 누르지 않는다."""
    out = []
    items = [('plan', '지도안', 'assets/pdf/%s.pdf' % code, True),
             ('sheet', '활동지', sheet_href(code), True),
             ('game', '게임', '%s/' % code if game(code) else '', False)]
    for ic, name, href, newtab in items:
        if href:
            out.append('<a href="%s%s"%s aria-label="%d학년 %s차시 %s">%s<span>%s</span></a>' % (
                up, href, ' target="_blank" rel="noopener"' if newtab else '', grade(code), label(code), name, icon(ic, up), name))
        else:
            out.append('<span class="off" title="%s 준비 중">%s<span>%s</span></span>' % (name, icon(ic, up), name))
    return '<div class="lico">%s</div>' % ''.join(out)


def lcard(code, up, extra=''):
    """차시 카드 — 그림 · 차시 꼬리표 · 한 줄 제목 · 아이콘 셋(지도안·활동지·게임)."""
    img = thumb(code)
    ph = '<img src="%s%s" alt="" loading="lazy">' % (up, img) if img else ''
    return ('<div class="lcard g%d"><a class="lmain" href="%slessons/%s/">'
            '<span class="ph">%s<span class="tag">%s차시</span></span><b class="lt">%s</b></a>%s</div>'
            % (grade(code), up, code, ph, label(code), e(easy(code, 'title')), res_icons(code, up)))


def units(up, g, open_all=False):
    """학년 하나의 단원 묶음 — 접고 펴는 칸 안에 차시 카드."""
    out = []
    for i, a in enumerate([a for a in SITE['areas'] if a['grade'] == g], 1):
        cards = ''.join(lcard(c, up) for c in a['blocks'])
        out.append('<details class="unit" id="u-%s"%s><summary><span class="no c%d">%d</span>%s<b>%s</b>'
                   '<span class="rng">%s차시</span></summary><div class="lgrid">%s</div></details>'
                   % (a['id'], ' open' if open_all else '', (i - 1) % 4 + 1, i, icon(a['id'], up), e(a['name']), a['range'], cards))
    return ''.join(out)


def grade_tabs(up, open_all=False):
    tabs = ''.join('<button type="button" role="tab" class="g%d" id="t%d" aria-controls="p%d" aria-selected="%s">%s<span>%d학년 %s</span></button>'
                   % (g, g, g, 'true' if g == 5 else 'false', icon('g%d' % g, up), g, 'SW' if g == 5 else 'AI') for g in (5, 6))
    panels = ''.join('<section class="gpanel g%d" id="p%d" role="tabpanel" aria-labelledby="t%d"><p class="crs">%s · %s</p>%s</section>'
                     % (g, g, g, e(SITE['courses'][str(g)]['name']), e(SITE['courses'][str(g)]['tools']), units(up, g, open_all)) for g in (5, 6))
    return '<div class="gtabs" role="tablist" aria-label="학년">%s</div>%s' % (tabs, panels)


TABS_JS = """<script>
(function(){
  var tabs=[].slice.call(document.querySelectorAll('.gtabs [role=tab]'));
  function pick(g,keep){tabs.forEach(function(t){var on=t.id==='t'+g;t.setAttribute('aria-selected',on?'true':'false');t.tabIndex=on?0:-1;
    document.getElementById(t.getAttribute('aria-controls')).hidden=!on});
    if(!keep){try{history.replaceState(null,'','#g'+g)}catch(_){}}}
  tabs.forEach(function(t,i){t.onclick=function(){pick(t.id.slice(1))};
    t.onkeydown=function(ev){if(ev.key==='ArrowRight'||ev.key==='ArrowLeft'){var n=tabs[(i+1)%tabs.length];n.focus();pick(n.id.slice(1))}}});
  var h=location.hash, m=/^#g([56])$/.exec(h), u=/^#u-(sw|ai)[0-9]$/.exec(h);
  pick(m?m[1]:(u&&u[1]==='ai')?'6':'5',true);
  if(u){var d=document.getElementById(h.slice(1));if(d){d.open=true;d.scrollIntoView()}}
})();
</script>
"""


def gchip(code):
    g = grade(code)
    return '<span class="chip g%d">%d학년 %s차시</span>' % (g, g, label(code))


def lesson_nums(code):
    a, _, b = label(code).partition('~')
    return list(range(int(a), int(b or a) + 1))


# ───────────────────────── 홈
SEARCH_SVG = ('<svg viewBox="0 0 32 32" aria-hidden="true" fill="none" stroke="#fff" stroke-width="4" stroke-linecap="round">'
              '<circle cx="14" cy="14" r="9"/><path d="M21 21l7 7"/></svg>')


def search_bar(action):
    areas = ''.join('<option value="%s">%d학년 · %s</option>' % (a['id'], a['grade'], e(a['name'])) for a in SITE['areas'])
    return ('<form class="search" action="%s" role="search">'
            '<label><span>학년</span><select name="g"><option value="">5·6학년 모두</option><option value="5">5학년</option><option value="6">6학년</option></select></label>'
            '<label><span>영역</span><select name="a"><option value="">모든 영역</option>%s</select></label>'
            '<label><span>찾을 말</span><input name="q" placeholder="예: 마이크로비트, 챗봇, 무선"></label>'
            '<button class="orb" type="submit" aria-label="과정안 찾기">%s</button></form>') % (action, areas, SEARCH_SVG)


def build_home():
    quick = [('about/', 'about', '학교자율시간이란?', '한 쪽으로 알아봐요'), ('guide/', 'steps', '도입 절차', '누가·언제·무엇을 내는지'),
             ('forms/', 'forms', '서식 받기', '채운 서식과 빈 양식')]
    q = ''.join('<a href="%s">%s<b>%s</b><span>%s</span></a>' % (u, icon(ic, ''), e(t), e(d)) for u, ic, t, d in quick)
    body = f"""
<section class="hello"><h1>학교자율시간 SW·AI 수업 자료</h1>
<p class="lead">학년을 고르고, 단원을 펴고, 차시를 눌러요. 지도안·활동지·체험 게임이 한곳에 있어요.</p></section>
{grade_tabs('')}
<h2 class="sub">{icon('lightbulb', '')}도입 안내</h2>
<div class="quick">{q}</div>
<p class="small muted">모든 자료는 무료이고, 학생 이름·점수를 받지 않아요. <a href="play/">체험 게임 모아 보기</a> · <a href="plan/">연구회 소개</a></p>
"""
    page('', '에듀다움 — 학교자율시간 SW·AI 수업 자료', body, '', TABS_JS)


# ───────────────────────── 1) 계획서·성취기준
def build_plan():
    rows = []
    for a in SITE['areas']:
        for s in a['std']:
            blocks = [c for c in a['blocks'] if std_code(c) == s]
            rows.append('<tr><td>%d학년</td><td>%s</td><td><b>%s</b><br>%s</td><td>%s</td><td>%s</td></tr>' % (
                a['grade'], e(a['name']), e(s), e(STD['standards'].get(s, '')),
                ' '.join(e(x) for x in SITE['links_std'].get(s, [])),
                ' '.join('<a href="../lessons/%s/">%s</a>' % (c, label(c)) for c in blocks)))
    area_rows = ''.join('<tr><td>%d학년</td><td><a href="../topics/#%s">%s</a></td><td>%s</td><td>%d편</td></tr>' % (
        a['grade'], a['id'], e(a['name']), a['range'], len(a['blocks'])) for a in SITE['areas'])
    body = f"""
<span class="kick">연구회 소개</span>
<h1>경기 AI 융합교육 에듀다움 교사연구회</h1>
<p class="lead">경기도 초등 교사들이 학교자율시간에 바로 쓰는 SW·AI 교육과정을 만들고 교실에서 검증해요. 2026년 연구 주제는 「학교자율시간 연계 초등 SW·AI 융합 프로그램 개발 및 적용」 — 5학년 SW 32차시, 6학년 AI 32차시예요.</p>
<div class="toc"><a href="#why">배경과 목표</a><a href="#run">운영 구조</a><a href="#course">과정 구성</a><a href="#std">성취기준</a><a href="#link">교과 연계</a><a href="#eval">평가·검증</a><a href="#safe">안전·개인정보</a><a href="#time">추진 일정</a></div>

<h2 id="why">배경과 목표</h2>
<div class="box">
<p><b>연구 주제</b> 학교자율시간 연계 초등 SW·AI 융합 프로그램 개발 및 적용 <span class="muted small">(AI 활용 — AI·데이터 기반 교과 융합 수업모델 개발)</span></p>
<ul>
<li>2022 개정 교육과정은 초등 정보교육을 34시간 이상으로 늘렸으나, 실과 「디지털 사회와 인공지능」 17차시만으로는 SW·데이터·인공지능을 프로젝트로 넓히기 어렵고, 학교자율시간에 쓸 검증된 자료가 부족해요.</li>
<li>실과 정보 영역 [6실05-01]~[6실05-05]와 학교자율시간 정보 교육 [06자율-1]~[06자율-7]을 재구조화하여 5학년 32차시, 6학년 32차시(합 64차시)를 개발해요.</li>
<li>5학년은 SW 기초를 교과와 잇는 교과 융합 프로젝트, 6학년은 데이터와 AI로 학교·가정·지역 문제를 푸는 실생활 문제해결 프로젝트예요.</li>
<li>고가 장비 없이 학교 보유 기기, 무료 교육용 도구, 학교 주변에서 모을 수 있는 자료로 운영해요.</li>
</ul></div>

<h2 id="run">운영 구조 (고도화안)</h2>
<div class="tw"><table>
<tr><th>구분</th><th>5학년</th><th>6학년</th></tr>
<tr><td>과정</td><td>{e(SITE['courses']['5']['name'])}</td><td>{e(SITE['courses']['6']['name'])}</td></tr>
<tr><td>과정안</td><td>B01~B14 (14편, 32차시)</td><td>B15~B28 (14편, 32차시)</td></tr>
<tr><td>주 도구</td><td>{e(SITE['courses']['5']['tools'])}</td><td>{e(SITE['courses']['6']['tools'])}</td></tr>
<tr><td>수업 학급</td><td>2학급이 32차시 전체</td><td>2학급이 32차시 전체</td></tr>
<tr><td>비교 학급</td><td>선택 1학급</td><td>선택 1학급</td></tr>
<tr><td>편성</td><td colspan="2">주 2차시 블록 수업, 한 학기 약 16주. 한 차시 40분, 대부분 2차시(80분) 묶음, B11·B12·B25·B27은 4차시 묶음</td></tr>
</table></div>
<p class="note">연구 계획서의 1차 파일럿 → 2차 확대 적용 구조를, 고도화 과정에서 학년별 2학급 전체 운영으로 바꾸었어요. 이야기 흐름과 누적 산출물을 한 학생 집단 안에서 볼 수 있게 하려는 것이에요.</p>

<h2 id="course">과정 구성 — 영역과 차시</h2>
<div class="tw"><table><tr><th>학년</th><th>영역</th><th>차시</th><th>과정안</th></tr>{area_rows}</table></div>

<h2 id="std">성취기준</h2>
<p class="small muted">학교자율시간 과목을 위해 연구회가 자체 개발한 성취기준이에요. [5실SW…]·[6실인공지능…]은 국가 실과 성취기준 코드가 아니며, ‘연계’ 칸이 2022 개정 실과·학교자율시간 정보 교육 성취기준이에요.</p>
<div class="tw"><table><tr><th>학년</th><th>영역</th><th>자체 성취기준</th><th>연계</th><th>차시</th></tr>{''.join(rows)}</table></div>

<h2 id="link">교과 연계</h2>
<div class="grid">
<div class="box"><h3>5학년</h3><p class="small">국어(설명하는 글쓰기·발표), 수학(규칙과 대응, 자료의 정리), 과학(온도와 열, 몸의 구조 — 센서·측정), 미술(디자인과 소통, 산출물 시각화), 실과(생활 속 문제 해결)</p></div>
<div class="box"><h3>6학년</h3><p class="small">사회(정보사회와 미디어 리터러시), 과학(자료의 수집과 해석), 수학(자료와 가능성 — 평균, 그래프), 실과(인공지능과 로봇, 발명과 문제해결)</p></div>
</div>

<h2 id="eval">평가와 검증</h2>
<div class="tw"><table>
<tr><th>무엇을</th><th>어떻게</th></tr>
<tr><td>수업 중 평가</td><td>과정안마다 매우 잘함·잘함·보통·노력요함·미관찰 5수준 기준. 미관찰은 낮은 성취로 적지 않고 보충 확인</td></tr>
<tr><td>사전·사후 설문</td><td>학년별 구글 폼(5학년 42문항, 6학년 47문항), 비교 학급은 공통 22문항. 사후 문항 순서 무선화</td></tr>
<tr><td>산출물 분석</td><td>미션 포스터·근거 카드·오류 도감·모델 카드 등을 공통 코딩 루브릭으로 분석</td></tr>
<tr><td>내용타당도</td><td>전문가 CVR(Lawshe) 검토, 수정 이력 관리, 과정안 점검 하네스(H1~H10)</td></tr>
</table></div>

<h2 id="safe">안전·개인정보 원칙</h2>
<ul>
<li>사진·영상에 사람 얼굴을 넣지 않고 손·물건으로 대신해요. 웹캠 자료는 저장하지 않고 수업 끝에 지워요.</li>
<li>생성형 AI는 학생용 <b>우리아이AI</b>만 쓰며, 개인정보는 입력하지 않고 학생 계정은 만들지 않아요.</li>
<li>무선으로 보낸 정보는 다른 사람도 받을 수 있음을 실험으로 겪고, 교사가 정한 그룹 번호만 써요.</li>
<li>작품에 쓴 그림·소리는 허락·출처·이용 조건(CCL)을 확인해 밝혀요.</li>
<li>설문은 이름 없이 반·번호로만 받으며, 연구 종료 후 기관 기준에 따라 보관·폐기해요.</li>
</ul>

<h2 id="time">추진 일정 (2026)</h2>
<div class="tw"><table>
<tr><th>활동</th><th>6월</th><th>7월</th><th>8월</th><th>9월</th><th>10월</th><th>11월</th><th>12월</th><th>'27. 1월</th></tr>
<tr><td>자료 조사·연구 기획</td><td>●</td><td>●</td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
<tr><td>교육과정 분석·수업모델 설계</td><td></td><td>●</td><td>●</td><td></td><td></td><td></td><td></td><td></td></tr>
<tr><td>교수학습자료 협력 개발</td><td></td><td>●</td><td>●</td><td>●</td><td>●</td><td></td><td></td><td></td></tr>
<tr><td>5·6학년 32차시 적용</td><td></td><td></td><td></td><td>●</td><td>●</td><td>●</td><td></td><td></td></tr>
<tr><td>효과성 조사·결과 분석</td><td></td><td></td><td></td><td></td><td>●</td><td>●</td><td>●</td><td></td></tr>
<tr><td>공개수업·참관 협의회(4회 이상)</td><td></td><td></td><td></td><td></td><td></td><td>●</td><td>●</td><td></td></tr>
<tr><td>이슈페이퍼·결과보고서</td><td></td><td></td><td></td><td></td><td></td><td></td><td>●</td><td>●</td></tr>
</table></div>
"""
    page('plan', '연구회 소개 — 에듀다움', body, 'plan/')


# ───────────────────────── 2) 주제별
def build_topics():
    parts = []
    for g in (5, 6):
        crs = SITE['courses'][str(g)]
        parts.append('<h2 style="margin-top:56px;font-size:24px">%d학년 · %s</h2><p class="muted">이야기 틀: %s · 주 도구: %s</p>' % (g, e(crs['name']), e(crs['story']), e(crs['tools'])))
        for a in SITE['areas']:
            if a['grade'] != g:
                continue
            stds = ''.join('<p class="small muted" style="margin:0 0 16px"><b style="color:var(--ink);font-weight:600">%s</b> %s</p>' % (e(s), e(STD['standards'].get(s, ''))) for s in a['std'])
            cards = []
            for c in a['blocks']:
                acts = ''.join('<li>%s</li>' % e(re.sub(r'\s*\(\d+분\)', '', x)) for x in activities(c))
                tl = ' '.join('<span class="chip">%s</span>' % e(t['name']) for t in tools_of(c))
                gm = game(c)
                gl = (' · <a href="../%s/">체험 게임</a>' % c) if gm else ''
                img = thumb(c)
                cards.append(
                    '<div class="card"><a href="../lessons/%s/" class="ph" style="display:block">%s<span class="badge">%d학년 %s차시</span></a>'
                    '<div class="meta"><h3><a href="../lessons/%s/" style="text-decoration:none">%s</a></h3>'
                    '<ul class="small muted" style="padding-left:18px;margin:6px 0">%s</ul><div style="display:flex;flex-wrap:wrap;gap:4px;margin:8px 0">%s</div>'
                    '<p class="small"><a href="../lessons/%s/">과정안 보기</a>%s</p></div></div>'
                    % (c, ('<img src="../%s" alt="" loading="lazy">' % img) if img else '', grade(c), label(c), c, e(topic(c)), acts, tl, c, gl))
            parts.append('<section id="%s"><h2 style="font-size:20px;margin-top:48px">%s <span class="muted" style="font-weight:400;font-size:15px">%d학년 %s차시</span></h2>'
                         '<p class="lead" style="margin-bottom:8px">%s</p>%s<div class="grid">%s</div></section>'
                         % (a['id'], e(a['name']), a['grade'], a['range'], e(a['summary']), stds, ''.join(cards)))
    toc = ''.join('<a href="#%s">%d학년 %s</a>' % (a['id'], a['grade'], e(a['name'])) for a in SITE['areas'])
    body = ('<span class="kick">수업 자료</span><h1>단원별로 보기</h1>'
            '<p class="lead">영역마다 성취기준과 차시별 핵심 활동, 연동 도구, 체험 게임을 모았어요.</p>'
            '<nav class="cats" aria-label="영역">%s</nav>%s') % (toc, ''.join(parts))
    page('topics', '영역별 교수학습 과정안 — 에듀다움', body, 'topics/')


# ───────────────────────── 3) 차시별 과정안
def render_body(items):
    out, ul = [], []

    def flush():
        if ul:
            out.append('<ul>%s</ul>' % ''.join('<li>%s</li>' % x for x in ul))
            ul.clear()
    for it in items:
        if isinstance(it, dict):
            flush()
            cap = it.get('caption', '')
            cap = re.sub(r'^\[(사진|그림) ?\d+\]\s*-?\s*', '', cap)
            out.append('<figure><img src="../../%s" alt="%s" loading="lazy">%s</figure>'
                       % (it['img'], e(cap or '과정안 그림'), ('<figcaption>%s</figcaption>' % e(cap)) if cap else ''))
        elif not it:
            flush()
        elif it.startswith('◎'):
            flush()
            out.append('<h4>%s</h4>' % e(it[1:].strip()))
        elif re.match(r'^\s*[-·•]\s', it):
            ul.append(e(re.sub(r'^\s*[-·•]\s*', '', it)))
        elif re.match(r'^\[(사진|그림) ?\d+\]', it):
            flush()
            out.append('<p class="small muted">%s</p>' % e(it))
        else:
            flush()
            out.append('<p>%s</p>' % e(it))
    flush()
    return ''.join(out)


RES_KIND = {'☆': '준비물', '★': '자료', '△': '유의점'}


def render_res(lines):
    out = []
    for x in lines:
        k = RES_KIND.get(x[:1])
        if k:
            out.append('<div><span class="k">%s</span>%s</div>' % (k, e(x[1:].strip())))
        else:
            out.append('<div>%s</div>' % e(x))
    return ''.join(out)


STAGE_IC = {'도입': 'start', '전개': 'do', '정리': 'end'}
PREP_IC = [(r'태블릿|노트북|컴퓨터|크롬북', 'tablet'), (r'마이크로비트|USB|배터리', 'device'), (r'웹캠|카메라', 'camera'),
           (r'마이크|소리', 'mic'), (r'헤드폰|이어폰|스피커', 'headphones'), (r'온도계', 'thermo'), (r'무선', 'wifi'),
           (r'카드', 'card'), (r'필기구|연필|펜|사인펜|색연필', 'pen'), (r'붙임쪽지|스티커|쪽지|테이프', 'note'),
           (r'기록지|활동지|학습지|기록표|점검표', 'sheet'), (r'클립보드', 'clipboard'), (r'종이|전지|도화지|평면도|판', 'paper'),
           (r'그림|사진', 'image'), (r'차트|그래프', 'chart')]


def core_lines(r):
    """수업 흐름 표 한 칸 — 전개는 ◎활동 제목, 도입·정리는 ◎ 아래 첫 줄. 과정안 문장을 그대로 쓴다."""
    groups, cur = [], None
    for it in r['body']:
        if isinstance(it, str) and it.startswith('◎'):
            cur = [it[1:].strip(), []]
            groups.append(cur)
        elif isinstance(it, str) and cur and re.match(r'^\s*[-·•]\s', it):
            cur[1].append(re.sub(r'^\s*[-·•]\s*', '', it))
    out = []
    for h, b in groups:
        if re.match(r'^활동\s*\d', h):
            out.append(h)
        elif '학습문제' in h.replace(' ', ''):
            continue
        else:
            out.append(b[0] if b else h)
    return out


def flow_rows(d):
    """같은 차시·같은 단계가 이어지면 한 줄로 묶는다."""
    rows = []
    for r in d['rows']:
        m = re.match(r'(\d+)', r['time'] or '')
        mins = int(m.group(1)) if m else 0
        if rows and rows[-1]['lesson'] == r['lesson'] and rows[-1]['stage'] == r['stage']:
            rows[-1]['mins'] += mins
            rows[-1]['lines'] += core_lines(r)
        else:
            rows.append({'lesson': r['lesson'], 'stage': r['stage'], 'mins': mins, 'lines': core_lines(r)})
    return rows


def flow_line(t):
    m = re.match(r'^활동\s*(\d+)\.\s*(.*?)\s*(?:\((\d+분)\))?$', t)
    if m:
        return '<li><span class="ano">활동%s</span>%s%s</li>' % (m.group(1), e(m.group(2)), (' <span class="min">%s</span>' % m.group(3)) if m.group(3) else '')
    return '<li>%s</li>' % e(t)


def flow_table(d, up):
    out = []
    for r in flow_rows(d):
        lines = r['lines'][:3]
        more = len(r['lines']) - len(lines)
        ic = STAGE_IC.get(r['stage'], 'do')
        out.append('<tr class="st-%s"><th scope="row">%s<span>%s</span><small>%s차시</small></th><td class="tm">%s분</td><td><ul>%s%s</ul></td></tr>'
                   % (ic, icon(ic, up), e(r['stage']), e(r['lesson']), r['mins'],
                      ''.join(flow_line(x) for x in lines), ('<li class="muted small">그 밖에 %d가지 — 맨 아래 과정안 전문</li>' % more) if more > 0 else ''))
    return '<div class="tw flowt"><table><tr><th>단계</th><th>시간</th><th>핵심 활동</th></tr>%s</table></div>' % ''.join(out)


def split_items(line):
    parts, depth, buf = [], 0, ''
    for ch in line:
        depth += ch in '(（'
        depth -= ch in ')）'
        if ch == ',' and depth == 0:
            parts.append(buf.strip())
            buf = ''
        else:
            buf += ch
    parts.append(buf.strip())
    return [x for x in parts if x]


def prep_chips(d, up):
    seen, out = set(), []
    for r in d['rows']:
        for x in r['res']:
            if x[:1] != '☆':
                continue
            for it in split_items(x[1:].strip()):
                short = re.sub(r'\s*[(（][^)）]*[)）]', '', it).strip()
                if not short or short in seen:
                    continue
                seen.add(short)
                ic = next((n for pat, n in PREP_IC if re.search(pat, short)), 'kit')
                out.append('<span class="pchip"%s>%s%s</span>' % ((' title="%s"' % e(it)) if it != short else '', icon(ic, up), e(short)))
    return ''.join(out)


def eval_block(d):
    if not d['eval']:
        return ''
    det = []
    for ev in d['eval']:
        lv = ''.join('<tr><td>%s</td><td>%s</td></tr>' % (e(x['level']), e(x['desc'])) for x in ev['levels'])
        det.append('<p><b>%s</b> — %s</p><div class="tw"><table class="lv"><tr><th>수준</th><th>평가 기준</th></tr>%s</table></div>'
                   '<p class="small"><b>평가 방법</b> %s</p>' % (e(' · '.join(ev['aspect'])), e(ev['goal']), lv, e(' · '.join(ev['method']))))
    return '<p class="evone">%s</p><details class="more"><summary>평가 기준 자세히</summary>%s</details>' % (e(d['eval'][0]['goal']), ''.join(det))


def kit_buttons(code, up, gm, has_tools):
    b = ['<a class="kb" href="%sassets/pdf/%s.pdf" target="_blank" rel="noopener">%s<b>지도안 받기</b><span>PDF</span></a>' % (up, code, icon('plan', up))]
    sh = sheet_href(code)
    b.append(('<a class="kb" href="%s%s" target="_blank" rel="noopener">%s<b>활동지</b><span>PDF</span></a>' % (up, sh, icon('sheet', up)))
             if sh else '<span class="kb off" title="활동지는 곧 올려요">%s<b>활동지</b><span>준비 중</span></span>' % icon('sheet', up))
    b.append(('<a class="kb" href="%s%s/">%s<b>체험 게임</b><span>5~10분</span></a>' % (up, code, icon('game', up)))
             if gm else '<span class="kb off">%s<b>체험 게임</b><span>없음</span></span>' % icon('game', up))
    b.append('<a class="kb" href="#tools">%s<b>연동 도구</b><span>%s</span></a>' % (icon('tool', up), '바로 열기' if has_tools else '종이·실물'))
    return '<div class="kit">%s</div>' % ''.join(b)


def build_lesson(code, prev, nxt):
    d = L[code]
    g = grade(code)
    a = AREA_OF[code]
    up = '../../'
    rows = []
    for i, r in enumerate(d['rows']):
        rows.append('<div class="rowcard" id="r%d"><div class="rowhead"><span>%s차시</span><span class="stage">%s</span><span class="chip">%s</span></div>'
                    '<div class="rowbody"><div class="act">%s</div><div class="res">%s</div></div></div>'
                    % (i, e(r['lesson']), e(r['stage']), e(r['time']), render_body(r['body']), render_res(r['res'])))
    ovr = []
    for k in ('성취기준', '핵심 역량', '핵심 기능', '가치 태도'):
        v = ov(code, k)
        if v:
            ovr.append('<tr><th>%s</th><td>%s</td></tr>' % (e(k), '<br>'.join(e(x) for x in v)))
    tl = []
    for t in tools_of(code):
        tl.append('<a class="tool" href="%s" target="_blank" rel="noopener"><b>%s ↗</b><span>%s</span><span>계정: %s</span></a>'
                  % (e(t['url']), e(t['name']), e(t['use']), e(t['account'])))
        for m in t.get('more', []):
            tl.append('<a class="tool" href="%s" target="_blank" rel="noopener"><b>%s ↗</b><span>%s 안내</span></a>' % (e(m['url']), e(m['name']), e(t['name'])))
    for x in LINKS.get(code, {}).get('extra', []):
        tl.append('<a class="tool" href="%s" target="_blank" rel="noopener"><b>%s ↗</b><span>%s</span></a>' % (e(x['url']), e(x['name']), e(x.get('note', ''))))
    gm = game(code)
    gbox = ('<a class="gcard" href="%s%s/">%s<span><b>%s</b><span>%s</span></span><span class="go">열기</span></a>'
            % (up, code, icon('game', up, 'ic big'), e(gm['title']), e(gm['lead']))) if gm else ''
    chips = prep_chips(d, up)
    # 원본 hwpx(드라이브)에는 개발자 이름이 있어 공개 쪽에 걸지 않는다. PDF는 공개용 사본(public_copy.py)에서 뽑는다.
    pn = '<div class="pn">%s%s</div>' % (
        ('<a class="btn" href="../%s/">← %d학년 %s차시</a>' % (prev, grade(prev), label(prev))) if prev else '<span></span>',
        ('<a class="btn" href="../%s/">%d학년 %s차시 →</a>' % (nxt, grade(nxt), label(nxt))) if nxt else '')
    prep = ('<h2 class="sub">%s준비물</h2><div class="pchips">%s</div>' % (icon('kit', up), chips)) if chips else ''
    gsec = ('<h2 class="sub" id="game">%s체험 게임</h2>%s' % (icon('game', up), gbox)) if gm else ''
    body = f"""
<p class="crumb"><a href="../">수업 자료</a> › <a href="../#u-{a['id']}">{g}학년 {e(a['name'])}</a></p>
<div class="kband g{g}">
<span class="ktag">{icon('g%d' % g, up)}{g}학년 {label(code)}차시 · {e(easy(code, 'title'))}</span>
<h1>{e(topic(code))}</h1>
<p class="ksum">{e(easy(code, 'summary'))}</p>
</div>
{kit_buttons(code, up, gm, bool(tl))}
<div class="g{g}">
<h2 class="sub">{icon('clock', up)}수업 흐름</h2>
{flow_table(d, up)}
<div class="goal">{icon('goal', up)}<span><b>학습 문제</b> {e(problem(code))}</span></div>
{prep}
<h2 class="sub">{icon('eval', up)}평가</h2>
{eval_block(d)}
{gsec}
<h2 class="sub" id="tools">{icon('tool', up)}연동 도구</h2>
<p class="small muted">과정안에 나온 도구예요. 수업 전에 학교망에서 열리는지 확인해 주세요.</p>
<div class="toolgrid">{''.join(tl) or '<p class="muted">이 차시는 외부 도구 없이 종이·실물로 해요.</p>'}</div>
<details class="more mine" data-code="{code}"><summary>내 수업 링크 걸어 두기</summary>
<p class="small muted">학급 패들렛, 엔트리 작품처럼 이 차시에 쓸 링크를 걸어 둬요. 이 브라우저에만 저장돼요. 학생 이름이 든 주소는 넣지 마세요.</p>
<ul></ul>
<form><div class="f"><label for="mn-{code}">이름</label><input id="mn-{code}" name="n" maxlength="40" required placeholder="예: 우리 반 패들렛"></div>
<div class="f"><label for="mu-{code}">주소</label><input id="mu-{code}" name="u" type="url" required placeholder="https://"></div>
<button class="btn pri" type="submit">걸어 두기</button></form>
</details>
<details class="more full" id="full"><summary>{icon('plan', up)}과정안 전문 펼치기 <span class="small muted">개요·교수학습 활동·그림</span></summary>
<h3>개요</h3>
<div class="tw"><table>{''.join(ovr)}</table></div>
<h3>교수학습 활동</h3>
{''.join(rows)}
</details>
</div>
{pn}
"""
    page('lessons/%s' % code, '%d학년 %s차시 %s — 에듀다움' % (g, label(code), topic(code)), body, 'lessons/', MINE_JS)


MINE_JS = """<script>
(function(){
  var box=document.querySelector('.mine'); if(!box) return;
  var key='edudaum.links.'+box.dataset.code, ul=box.querySelector('ul'), f=box.querySelector('form');
  function load(){try{return JSON.parse(localStorage.getItem(key)||'[]')}catch(_){return []}}
  function save(a){try{localStorage.setItem(key,JSON.stringify(a))}catch(_){}}
  function draw(){
    var a=load(); ul.textContent='';
    if(!a.length){var p=document.createElement('li');p.className='small muted';p.textContent='아직 걸어 둔 링크가 없어요.';ul.appendChild(p);return}
    a.forEach(function(x,i){
      var li=document.createElement('li'),l=document.createElement('a'),b=document.createElement('button');
      l.href=x.u;l.textContent=x.n+' ↗';l.target='_blank';l.rel='noopener';l.style.fontWeight='800';
      b.type='button';b.className='x';b.textContent='빼기';b.setAttribute('aria-label',x.n+' 빼기');
      b.onclick=function(){var z=load();z.splice(i,1);save(z);draw()};
      li.appendChild(l);li.appendChild(b);ul.appendChild(li)});
  }
  f.addEventListener('submit',function(ev){
    ev.preventDefault(); var n=f.n.value.trim(), u=f.u.value.trim();
    if(!/^https:\\/\\//.test(u)){f.u.setCustomValidity('https:// 로 시작하는 주소만 걸 수 있어요');f.u.reportValidity();f.u.setCustomValidity('');return}
    var a=load(); a.push({n:n,u:u}); save(a); f.reset(); draw();
  });
  draw();
})();
</script>
"""


def build_lessons():
    for i, c in enumerate(CODES):
        prev = CODES[i - 1] if i > 0 else None
        nxt = CODES[i + 1] if i + 1 < len(CODES) else None
        build_lesson(c, prev, nxt)
    body = ('<span class="kick">수업 자료</span><h1>차시별 수업 꾸러미</h1>'
            '<p class="lead">5·6학년 28묶음 64차시예요. 카드를 누르면 한 줄 요약, 수업 흐름 표, 자료 단추가 나와요.</p>%s') % grade_tabs('../', open_all=True)
    page('lessons', '차시별 수업 꾸러미 — 에듀다움', body, 'lessons/', TABS_JS)


# ───────────────────────── 도구 모음
def build_tools():
    used = {t['id']: [c for c in CODES if t in tools_of(c)] for t in TOOLS}
    groups = []
    for grp in ('코딩', '인공지능', '데이터', '제작', '안전'):
        cards = []
        for t in TOOLS:
            if t['group'] != grp:
                continue
            ls = ' '.join('<a class="chip" href="../lessons/%s/">%d-%s</a>' % (c, grade(c), label(c)) for c in used[t['id']])
            more = ' · '.join('<a href="%s" target="_blank" rel="noopener">%s ↗</a>' % (e(m['url']), e(m['name'])) for m in t.get('more', []))
            cards.append('<div class="box" style="margin:0"><h3 style="margin-top:0"><a href="%s" target="_blank" rel="noopener">%s ↗</a></h3><p class="small">%s</p>'
                         '<p class="small muted">계정: %s%s</p><div>%s</div></div>'
                         % (e(t['url']), e(t['name']), e(t['use']), e(t['account']), (' · ' + more) if more else '', ls or '<span class="small muted">직접 쓰는 차시 없음</span>'))
        groups.append('<h2>%s</h2><div class="grid">%s</div>' % (grp, ''.join(cards)))
    body = ('<span class="kick">연동 도구</span><h1>차시에 걸린 외부 도구</h1>'
            '<p class="lead">모두 무료이며 학생 계정 없이 쓸 수 있게 골랐어요. 칩을 누르면 그 도구를 쓰는 차시로 가요.</p>'
            '<p class="note">도구를 더하거나 차시에 링크를 더 걸려면 <code>_data/tools.json</code>·<code>_data/links.json</code>을 고친 뒤 <code>python _tools/make_site.py</code>를 돌려요. 교사 개인 링크는 차시 쪽 「내 수업 링크」에 걸 수 있어요.</p>%s') % ''.join(groups)
    page('tools', '연동 도구 — 에듀다움', body, 'tools/')


# ───────────────────────── 체험 게임 목록
def needs(code):
    """체험 게임 카드의 꼬리표 — 걸리는 시간과 필요한 것(게임 쪽 코드에서 읽는다)."""
    h = (ROOT / code / 'index.html').read_text(encoding='utf-8')
    tags = [('clock', '교사 준비용' if code == 'B03' else '5~10분')]
    if 'devicemotion' in h:
        tags.append(('motion', '흔들기(태블릿)'))
    if 'getUserMedia' in h and re.search(r'video\s*:\s*\{', h):
        tags.append(('camera', '카메라'))
    if 'getUserMedia' in h and 'audio:false' not in h.replace(' ', ''):
        tags.append(('mic', '마이크'))
    if len(tags) == 1:
        tags.append(('tablet', '누르기만'))
    return ''.join('<i>%s%s</i>' % (icon(ic, '../'), e(t)) for ic, t in tags)


def build_play():
    parts = []
    for g in (5, 6):
        cards = []
        for c in CODES:
            if grade(c) != g:
                continue
            gm = game(c)
            if not gm:
                continue
            cards.append('<a class="gcard g%d" href="../%s/">%s<span><small class="gtag">%d학년 %s차시</small><b>%s</b><span>%s</span>'
                         '<span class="needs">%s</span></span></a>'
                         % (g, c, icon('game', '../', 'ic big'), g, label(c), e(gm['title']), e(gm['lead']), needs(c)))
        parts.append('<h2 class="sub">%s%d학년 %s</h2><div class="ggrid">%s</div>' % (icon('g%d' % g, '../'), g, 'SW' if g == 5 else 'AI', ''.join(cards)))
    body = ('<span class="kick">체험 게임</span><h1>수업 중 5~10분 체험 게임</h1>'
            '<p class="lead">활동 하나를 짧게 미리 해 보거나 견주어 봐요. 설치 없이 브라우저로 열어요. 실물 활동을 대신하지는 않아요.</p>%s'
            '<p class="note">카메라와 마이크는 화면에만 쓰이고 저장되지 않아요. 밖으로 보내는 것도 없어요.</p>') % ''.join(parts)
    page('play', '체험 게임 — 에듀다움', body, 'play/')


def main():
    import link_games
    link_games.main()
    build_home()
    build_plan()
    build_topics()
    build_lessons()
    build_tools()
    build_play()
    import make_hub
    make_hub.main()
    n = len(list((ROOT / 'lessons').glob('B*/index.html')))
    print('누리집: 홈·계획서·주제별·도구·체험 + 차시 %d쪽' % n)
    for c in CODES:
        print('  %s %-6s 도구 %s' % (c, label(c), ', '.join(t['id'] for t in tools_of(c))))


if __name__ == '__main__':
    main()
