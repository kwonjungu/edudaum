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
AREA_OF = {b: a for a in SITE['areas'] for b in a['blocks']}
CODES = sorted(LESSON)

e = html.escape


# ───────────────────────── 공통 모양
CSS = """
:root{--ink:#141414;--paper:#FBF7EC;--surface:#fff;--amber:#FFB800;--muted:#5E5E5E;--line:#141414;
--g5:#F59E0B;--g6:#3D5AFE;--soft:#F3EEDD;--r:16px;--hard:4px 4px 0 var(--ink);--hard-sm:2px 2px 0 var(--ink)}
*{box-sizing:border-box}
html{scroll-padding-top:72px}
body{margin:0;background:var(--paper);color:var(--ink);font-size:16px;line-height:1.7;
font-family:'Pretendard','Malgun Gothic','Apple SD Gothic Neo',system-ui,sans-serif;word-break:keep-all;overflow-wrap:anywhere}
a{color:inherit}
.top{position:sticky;top:0;z-index:10;background:var(--paper);border-bottom:2.5px solid var(--ink)}
.top .in{max-width:1120px;margin:0 auto;padding:8px 16px;display:flex;gap:6px 14px;align-items:center;flex-wrap:wrap}
.brand{font-weight:900;font-size:18px;text-decoration:none;letter-spacing:-.02em;margin-right:6px;display:flex;align-items:center;gap:8px}
.brand i{display:inline-block;width:14px;height:14px;border:2.5px solid var(--ink);border-radius:4px;background:var(--amber)}
.top nav{display:flex;flex-wrap:wrap;gap:4px}
.top nav a{text-decoration:none;font-weight:700;font-size:14.5px;padding:8px 10px;border-radius:10px;min-height:40px;display:inline-flex;align-items:center}
.top nav a:hover{background:var(--soft)}
.top nav a[aria-current]{background:var(--ink);color:var(--paper)}
main{max-width:1120px;margin:0 auto;padding:24px 16px 64px}
h1{font-size:clamp(26px,4.6vw,40px);line-height:1.25;font-weight:900;letter-spacing:-.03em;margin:8px 0 10px}
h2{font-size:clamp(20px,3vw,26px);font-weight:900;letter-spacing:-.02em;margin:40px 0 12px;padding-top:4px}
h3{font-size:18px;font-weight:800;margin:24px 0 8px}
.lead{color:var(--muted);font-weight:600;margin:0 0 18px;font-size:17px}
.kick{display:inline-block;border:2px solid var(--ink);background:var(--amber);border-radius:999px;padding:3px 12px;font-weight:800;font-size:13px}
.chip{display:inline-block;border:2px solid var(--ink);border-radius:999px;padding:1px 10px;font-weight:800;font-size:12.5px;background:#fff;white-space:nowrap}
.chip.g5{background:var(--g5)}.chip.g6{background:var(--g6);color:#fff}
.box{background:var(--surface);border:2.5px solid var(--ink);border-radius:var(--r);box-shadow:var(--hard);padding:18px 20px;margin:14px 0}
.grid{display:grid;gap:14px;grid-template-columns:repeat(auto-fill,minmax(260px,1fr))}
.card{display:block;text-decoration:none;background:var(--surface);border:2.5px solid var(--ink);border-radius:var(--r);box-shadow:var(--hard);padding:16px;transition:transform .1s,box-shadow .1s}
a.card:hover{transform:translate(-2px,-2px);box-shadow:6px 6px 0 var(--ink)}
.card h3{margin:8px 0 4px;font-size:17px}
.card p{margin:0;color:var(--muted);font-size:14.5px;font-weight:600}
.btn{display:inline-flex;align-items:center;gap:6px;min-height:44px;padding:8px 14px;border:2.5px solid var(--ink);border-radius:12px;background:#fff;
box-shadow:var(--hard-sm);font-weight:800;text-decoration:none;font-size:15px;cursor:pointer;font-family:inherit;color:var(--ink)}
.btn.pri{background:var(--amber)}
.btn:hover{transform:translate(-1px,-1px)}
.btns{display:flex;flex-wrap:wrap;gap:10px;margin:12px 0}
.tw{overflow-x:auto;margin:12px 0;border:2.5px solid var(--ink);border-radius:12px;background:#fff}
table{border-collapse:collapse;width:100%;font-size:15px}
th,td{border-bottom:1.5px solid #D9D2BE;padding:9px 10px;text-align:left;vertical-align:top}
th{background:var(--soft);font-weight:800;white-space:nowrap}
tr:last-child td{border-bottom:0}
.muted{color:var(--muted)}
.small{font-size:13.5px}
.note{border-left:5px solid var(--amber);background:#fff;padding:10px 14px;border-radius:0 10px 10px 0;margin:12px 0;font-size:15px}
:focus-visible{outline:3px solid var(--g6);outline-offset:2px}
footer{border-top:2.5px solid var(--ink);margin-top:40px}
footer .in{max-width:1120px;margin:0 auto;padding:18px 16px;font-size:13.5px;color:var(--muted)}
/* 64차시 지도 */
.map{display:grid;grid-template-columns:repeat(16,minmax(0,1fr));gap:4px;margin:8px 0 18px}
.map a{display:flex;align-items:center;justify-content:center;min-height:44px;border:2px solid var(--ink);border-radius:8px;text-decoration:none;font-weight:800;font-size:13px;background:#fff}
.map a:hover{transform:translate(-1px,-1px);box-shadow:var(--hard-sm)}
@media (max-width:720px){.map{grid-template-columns:repeat(8,minmax(0,1fr))}}
.legend{display:flex;flex-wrap:wrap;gap:6px 12px;font-size:13.5px;font-weight:700}
.legend span{display:inline-flex;align-items:center;gap:6px}
.legend i{width:14px;height:14px;border:2px solid var(--ink);border-radius:4px;display:inline-block}
/* 과정안 */
.flow{display:flex;flex-wrap:wrap;gap:8px;margin:10px 0}
.flow a{text-decoration:none;border:2px solid var(--ink);border-radius:10px;padding:6px 10px;background:#fff;font-weight:700;font-size:14px}
.flow b{font-weight:900}
.act h4{margin:14px 0 4px;font-size:16px;font-weight:900}
.act h4:first-child{margin-top:0}
.act ul{margin:0 0 6px;padding-left:20px}
.act li{margin:2px 0}
.act p{margin:4px 0}
figure{margin:10px 0;max-width:560px}
figure img{width:100%;height:auto;border:2px solid var(--ink);border-radius:10px;background:#fff}
figcaption{font-size:13px;color:var(--muted);font-weight:600;margin-top:4px}
.res div{margin:3px 0;font-size:14.5px}
.res .k{display:inline-block;min-width:44px;font-weight:900;font-size:12px;border:1.5px solid var(--ink);border-radius:6px;padding:0 5px;margin-right:6px;background:var(--soft);text-align:center}
.stage{font-weight:900;white-space:nowrap}
.rowcard{border:2.5px solid var(--ink);border-radius:var(--r);background:#fff;margin:14px 0;overflow:hidden}
.rowhead{display:flex;flex-wrap:wrap;gap:8px 14px;align-items:center;background:var(--soft);border-bottom:2px solid var(--ink);padding:8px 14px;font-weight:900}
.rowbody{display:grid;grid-template-columns:minmax(0,1.7fr) minmax(0,1fr);gap:0}
.rowbody>div{padding:12px 16px}
.rowbody>.res{border-left:2px dashed #CFC6AE;background:#FFFDF6}
@media (max-width:760px){.rowbody{grid-template-columns:1fr}.rowbody>.res{border-left:0;border-top:2px dashed #CFC6AE}}
.lv td:first-child{white-space:nowrap;font-weight:800}
.toolgrid{display:grid;gap:10px;grid-template-columns:repeat(auto-fill,minmax(240px,1fr))}
.tool{display:block;border:2px solid var(--ink);border-radius:12px;padding:10px 12px;background:#fff;text-decoration:none}
.tool b{display:block;font-size:15px}
.tool span{display:block;font-size:13px;color:var(--muted);font-weight:600}
.tool:hover{box-shadow:var(--hard-sm);transform:translate(-1px,-1px)}
.mine form{display:flex;flex-wrap:wrap;gap:8px;margin-top:10px}
.mine input{min-height:44px;border:2px solid var(--ink);border-radius:10px;padding:6px 10px;font:inherit;flex:1 1 180px;min-width:0}
.mine li{display:flex;gap:8px;align-items:center;margin:6px 0;flex-wrap:wrap}
.mine ul{list-style:none;padding:0;margin:8px 0 0}
.x{min-height:36px;padding:2px 10px;border:2px solid var(--ink);border-radius:8px;background:#fff;cursor:pointer;font:inherit;font-weight:700}
.pn{display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap;margin-top:28px}
.toc{display:flex;flex-wrap:wrap;gap:6px;margin:6px 0 4px}
.toc a{font-size:14px;font-weight:700;text-decoration:none;border-bottom:2px solid var(--amber)}
@media (prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important}}
@media print{.top,footer,.btns,.mine,.pn{display:none}body{background:#fff}.box,.rowcard{box-shadow:none}}
"""

NAV = [('', '홈'), ('plan/', '계획서·성취기준'), ('topics/', '주제별 활동'), ('lessons/', '차시별 과정안'),
       ('tools/', '연동 도구'), ('play/', '체험 게임')]


def page(path: str, title: str, body: str, cur: str, extra_js: str = '') -> None:
    depth = path.count('/') + 1 if path else 0
    up = '../' * depth
    nav = ''.join('<a href="%s%s"%s>%s</a>' % (up, h, ' aria-current="page"' if h == cur else '', t) for h, t in NAV)
    doc = ('<!doctype html>\n<html lang="ko">\n<head>\n<meta charset="utf-8">\n'
           '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
           '<title>%s</title>\n<style>%s</style>\n</head>\n<body>\n'
           '<header class="top"><div class="in"><a class="brand" href="%s"><i></i>에듀다움</a><nav aria-label="누리집 메뉴">%s</nav></div></header>\n'
           '<main>\n%s\n</main>\n'
           '<footer><div class="in">%s · %s · 과정안 기준일 %s<br>'
           '학생 이름·점수를 받지 않고, 체험 게임의 카메라·마이크는 화면에만 쓰며 저장하지 않습니다.</div></footer>\n'
           '%s</body>\n</html>\n') % (e(title), CSS, up or './', nav, body, e(SITE['org']), e(SITE['title']),
                                      e(SITE['updated']), extra_js)
    out = ROOT / path / 'index.html' if path else ROOT / 'index.html'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc, encoding='utf-8')


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


def gchip(code):
    g = grade(code)
    return '<span class="chip g%d">%d학년 %s차시</span>' % (g, g, label(code))


AREA_COLOR = {'sw1': '#FDE68A', 'sw2': '#FDBA74', 'sw3': '#FCA5A5', 'sw4': '#F9A8D4',
              'ai1': '#BFDBFE', 'ai2': '#A5B4FC', 'ai3': '#C4B5FD', 'ai4': '#99F6E4', 'ai5': '#BBF7D0'}


def lesson_nums(code):
    a, _, b = label(code).partition('~')
    return list(range(int(a), int(b or a) + 1))


# ───────────────────────── 홈
def build_home():
    maps = []
    for g in (5, 6):
        cells = []
        for c in CODES:
            if grade(c) != g:
                continue
            col = AREA_COLOR[AREA_OF[c]['id']]
            for n in lesson_nums(c):
                cells.append('<a href="lessons/%s/" style="background:%s" title="%d학년 %d차시 · %s">%d</a>'
                             % (c, col, g, n, e(topic(c)), n))
        crs = SITE['courses'][str(g)]
        legend = ''.join('<span><i style="background:%s"></i>%s</span>' % (AREA_COLOR[a['id']], e(a['name']))
                         for a in SITE['areas'] if a['grade'] == g)
        maps.append('<h3>%d학년 · %s <span class="muted small">%s</span></h3><div class="map">%s</div><div class="legend">%s</div>'
                    % (g, e(crs['name']), e(crs['tools']), ''.join(cells), legend))
    body = f"""
<span class="kick">{e(SITE['org'])}</span>
<h1>{e(SITE['title'])}</h1>
<p class="lead">{e(SITE['subtitle'])} — 학교자율시간에 바로 쓰는 교수학습 과정안, 연동 도구, 수업 중 체험 게임을 한곳에 모았습니다.</p>
<div class="grid">
 <a class="card" href="plan/"><span class="chip">1</span><h3>계획서·성취기준</h3><p>개발 배경과 목표, 운영 구조, 자체 성취기준과 2022 개정 연계, 평가 설계</p></a>
 <a class="card" href="topics/"><span class="chip">2</span><h3>주제별 활동 내용</h3><p>9개 영역마다 성취기준, 핵심 활동, 대표 산출물, 도구</p></a>
 <a class="card" href="lessons/"><span class="chip">3</span><h3>차시별 교수학습 과정안</h3><p>28편 64차시 전문, 평가 계획, PDF, 차시에 걸린 도구·링크</p></a>
 <a class="card" href="play/"><span class="chip">4</span><h3>체험 게임</h3><p>과정안 활동 앞뒤에 붙는 5~10분 짜리 웹 조각 28개</p></a>
</div>
<h2>64차시 한눈에 보기</h2>
<p class="muted small">칸을 누르면 그 차시의 과정안으로 갑니다. 색은 영역입니다.</p>
{''.join(maps)}
<h2>이렇게 운영합니다</h2>
<div class="grid">
 <div class="box"><h3>학년마다 32차시 전체</h3><p class="small">5·6학년 각 2학급이 학년 32차시를 모두 운영합니다. 주 2차시 블록 수업으로 약 16주, 비교 학급은 선택입니다.</p></div>
 <div class="box"><h3>이야기로 잇는 수업</h3><p class="small">5학년은 「{e(SITE['courses']['5']['story'])}」, 6학년은 「{e(SITE['courses']['6']['story'])}」 이야기 틀로 차시가 이어집니다.</p></div>
 <div class="box"><h3>만들고 재고 고친다</h3><p class="small">마이크로비트·엔트리·CreateAI로 실제로 만들고, 공식 통계와 실측 자료로 확인하며, 한 가지만 바꾸어 다시 시험합니다.</p></div>
</div>
"""
    page('', '에듀다움 — 학교자율시간 SW·AI 교육과정', body, '')


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
<span class="kick">1 · 계획서·성취기준</span>
<h1>학교자율시간 연계 초등 SW·AI 융합 프로그램</h1>
<p class="lead">연구 계획서와 고도화 심층 설계서의 요점을 옮겼습니다.</p>
<div class="toc"><a href="#why">배경과 목표</a><a href="#run">운영 구조</a><a href="#course">과정 구성</a><a href="#std">성취기준</a><a href="#link">교과 연계</a><a href="#eval">평가·검증</a><a href="#safe">안전·개인정보</a><a href="#time">추진 일정</a></div>

<h2 id="why">배경과 목표</h2>
<div class="box">
<p><b>연구 주제</b> 학교자율시간 연계 초등 SW·AI 융합 프로그램 개발 및 적용 <span class="muted small">(AI 활용 — AI·데이터 기반 교과 융합 수업모델 개발)</span></p>
<ul>
<li>2022 개정 교육과정은 초등 정보교육을 34시간 이상으로 늘렸으나, 실과 「디지털 사회와 인공지능」 17차시만으로는 SW·데이터·인공지능을 프로젝트로 넓히기 어렵고, 학교자율시간에 쓸 검증된 자료가 부족합니다.</li>
<li>실과 정보 영역 [6실05-01]~[6실05-05]와 학교자율시간 정보 교육 [06자율-1]~[06자율-7]을 재구조화하여 5학년 32차시, 6학년 32차시(합 64차시)를 개발합니다.</li>
<li>5학년은 SW 기초를 교과와 잇는 교과 융합 프로젝트, 6학년은 데이터와 AI로 학교·가정·지역 문제를 푸는 실생활 문제해결 프로젝트입니다.</li>
<li>고가 장비 없이 학교 보유 기기, 무료 교육용 도구, 학교 주변에서 모을 수 있는 자료로 운영합니다.</li>
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
<p class="note">연구 계획서의 1차 파일럿 → 2차 확대 적용 구조를, 고도화 과정에서 학년별 2학급 전체 운영으로 바꾸었습니다. 이야기 흐름과 누적 산출물을 한 학생 집단 안에서 볼 수 있게 하려는 것입니다.</p>

<h2 id="course">과정 구성 — 영역과 차시</h2>
<div class="tw"><table><tr><th>학년</th><th>영역</th><th>차시</th><th>과정안</th></tr>{area_rows}</table></div>

<h2 id="std">성취기준</h2>
<p class="small muted">학교자율시간 과목을 위해 연구회가 자체 개발한 성취기준입니다. [5실소프트웨어…]·[6실인공지능…]은 국가 실과 성취기준 코드가 아니며, ‘연계’ 칸이 2022 개정 실과·학교자율시간 정보 교육 성취기준입니다.</p>
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
<li>사진·영상에 사람 얼굴을 넣지 않고 손·물건으로 대신합니다. 웹캠 자료는 저장하지 않고 수업 끝에 지웁니다.</li>
<li>생성형 AI는 학생용 <b>우리아이AI</b>만 쓰며, 개인정보는 입력하지 않고 학생 계정은 만들지 않습니다.</li>
<li>무선으로 보낸 정보는 다른 사람도 받을 수 있음을 실험으로 겪고, 교사가 정한 그룹 번호만 씁니다.</li>
<li>작품에 쓴 그림·소리는 허락·출처·이용 조건(CCL)을 확인해 밝힙니다.</li>
<li>설문은 이름 없이 반·번호로만 받으며, 연구 종료 후 기관 기준에 따라 보관·폐기합니다.</li>
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
    page('plan', '계획서·성취기준 — 에듀다움', body, 'plan/')


# ───────────────────────── 2) 주제별
def build_topics():
    parts = []
    for g in (5, 6):
        crs = SITE['courses'][str(g)]
        parts.append('<h2>%d학년 · %s</h2><p class="muted">이야기 틀: %s · 주 도구: %s</p>' % (g, e(crs['name']), e(crs['story']), e(crs['tools'])))
        for a in SITE['areas']:
            if a['grade'] != g:
                continue
            stds = ''.join('<p class="small"><b>%s</b> %s</p>' % (e(s), e(STD['standards'].get(s, ''))) for s in a['std'])
            cards = []
            for c in a['blocks']:
                acts = ''.join('<li>%s</li>' % e(x) for x in activities(c))
                tl = ' '.join('<span class="chip">%s</span>' % e(t['name']) for t in tools_of(c))
                gm = game(c)
                gl = ('<a class="btn" href="../%s/">체험 게임: %s</a>' % (c, e(gm['title']))) if gm else ''
                cards.append(
                    '<div class="box"><div>%s</div><h3><a href="../lessons/%s/">%s</a></h3>'
                    '<ul class="small">%s</ul><div class="small" style="margin:6px 0">%s</div>'
                    '<div class="btns"><a class="btn pri" href="../lessons/%s/">과정안 보기</a>%s</div></div>'
                    % (gchip(c), c, e(topic(c)), acts, tl, c, gl))
            parts.append('<section id="%s"><h3 style="font-size:21px;margin-top:30px"><span class="chip" style="background:%s">%s차시</span> %s</h3>'
                         '<p>%s</p>%s<div class="grid">%s</div></section>'
                         % (a['id'], AREA_COLOR[a['id']], a['range'], e(a['name']), e(a['summary']), stds, ''.join(cards)))
    toc = ''.join('<a href="#%s">%d학년 %s</a>' % (a['id'], a['grade'], e(a['name'])) for a in SITE['areas'])
    body = ('<span class="kick">2 · 주제별 활동 내용</span><h1>영역별로 보는 활동</h1>'
            '<p class="lead">영역마다 성취기준과 차시별 핵심 활동, 연동 도구, 체험 게임을 모았습니다.</p>'
            '<div class="toc">%s</div>%s') % (toc, ''.join(parts))
    page('topics', '주제별 활동 내용 — 에듀다움', body, 'topics/')


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


def build_lesson(code, prev, nxt):
    d = L[code]
    g = grade(code)
    a = AREA_OF[code]
    s = std_code(code)
    # 활동 흐름 띠
    flow = []
    for i, r in enumerate(d['rows']):
        heads = [x[1:].strip() for x in r['body'] if isinstance(x, str) and x.startswith('◎')]
        flow.append('<a href="#r%d"><b>%s차시 %s</b> %s</a>' % (i, e(r['lesson']), e(r['stage']), e(' · '.join(re.sub(r'\s*\(\d+분\)', '', h) for h in heads)[:60])))
    rows = []
    for i, r in enumerate(d['rows']):
        rows.append('<div class="rowcard" id="r%d"><div class="rowhead"><span>%s차시</span><span class="stage">%s</span><span class="chip">%s</span></div>'
                    '<div class="rowbody"><div class="act">%s</div><div class="res">%s</div></div></div>'
                    % (i, e(r['lesson']), e(r['stage']), e(r['time']), render_body(r['body']), render_res(r['res'])))
    # 개요
    ovr = []
    for k in ('성취기준', '핵심 역량', '핵심 기능', '가치 태도'):
        v = ov(code, k)
        if v:
            ovr.append('<tr><th>%s</th><td>%s</td></tr>' % (e(k), '<br>'.join(e(x) for x in v)))
    # 평가
    evs = []
    for ev in d['eval']:
        lv = ''.join('<tr><td>%s</td><td>%s</td></tr>' % (e(l['level']), e(l['desc'])) for l in ev['levels'])
        evs.append('<div class="box"><p><b>%s</b></p><p>%s</p><div class="tw"><table class="lv"><tr><th>수준</th><th>평가 기준</th></tr>%s</table></div>'
                   '<p class="small"><b>평가 방법</b> %s</p></div>'
                   % (e(' · '.join(ev['aspect'])), e(ev['goal']), lv, e(' · '.join(ev['method']))))
    # 도구·링크
    tl = []
    for t in tools_of(code):
        tl.append('<a class="tool" href="%s" target="_blank" rel="noopener"><b>%s ↗</b><span>%s</span><span>계정: %s</span></a>'
                  % (e(t['url']), e(t['name']), e(t['use']), e(t['account'])))
        for m in t.get('more', []):
            tl.append('<a class="tool" href="%s" target="_blank" rel="noopener"><b>%s ↗</b><span>%s 안내</span></a>' % (e(m['url']), e(m['name']), e(t['name'])))
    for x in LINKS.get(code, {}).get('extra', []):
        tl.append('<a class="tool" href="%s" target="_blank" rel="noopener"><b>%s ↗</b><span>%s</span></a>' % (e(x['url']), e(x['name']), e(x.get('note', ''))))
    gm = game(code)
    gbox = ('<div class="box" style="border-left:10px solid %s"><p class="small muted">수업 중 5~10분 체험</p><h3 style="margin-top:2px">%s</h3><p>%s</p>'
            '<div class="btns"><a class="btn pri" href="../../%s/">체험 게임 열기</a></div></div>' % (gm['point'], e(gm['title']), e(gm['lead']), code)) if gm else ''
    # 원본 hwpx(드라이브)에는 개발자 이름이 있어 공개 쪽에 걸지 않는다. PDF는 공개용 사본(public_copy.py)에서 뽑는다.
    dl = '<a class="btn" href="../../assets/pdf/%s.pdf" target="_blank" rel="noopener">과정안 PDF</a>' % code
    pn = '<div class="pn">%s%s</div>' % (
        ('<a class="btn" href="../%s/">← %d학년 %s차시</a>' % (prev, grade(prev), label(prev))) if prev else '<span></span>',
        ('<a class="btn" href="../%s/">%d학년 %s차시 →</a>' % (nxt, grade(nxt), label(nxt))) if nxt else '')
    body = f"""
<p class="small"><a href="../">차시별 과정안</a> › <a href="../../topics/#{a['id']}">{e(a['name'])}</a></p>
<div>{gchip(code)} <span class="chip">{e(a['name'])}</span> <span class="chip">{e(s)}</span></div>
<h1>{e(topic(code))}</h1>
<p class="lead">학습 문제 — {e(problem(code))}</p>
<div class="btns">{dl}{'<a class="btn" href="#game">체험 게임</a>' if gm else ''}<a class="btn" href="#tools">연동 도구·링크</a></div>
<div class="toc"><a href="#ov">개요</a><a href="#flow">교수학습 활동</a><a href="#eval">평가 계획</a><a href="#tools">연동 도구·링크</a>{'<a href="#game">체험 게임</a>' if gm else ''}</div>

<h2 id="ov">개요</h2>
<div class="tw"><table>{''.join(ovr)}</table></div>

<h2 id="flow">교수학습 활동</h2>
<div class="flow">{''.join(flow)}</div>
{''.join(rows)}

<h2 id="eval">평가 계획</h2>
{''.join(evs)}

<h2 id="tools">연동 도구·링크</h2>
<p class="small muted">과정안에 나오는 도구가 저절로 걸립니다. 수업 전에 학교망에서 열리는지, 블록·메뉴 이름이 바뀌지 않았는지 확인하세요.</p>
<div class="toolgrid">{''.join(tl) or '<p class="muted">이 차시는 외부 도구 없이 종이·실물로 운영합니다.</p>'}</div>
<div class="box mine" data-code="{code}">
<h3 style="margin-top:0">내 수업 링크</h3>
<p class="small muted">학급 패들렛, 엔트리 작품, 활동지 주소처럼 이 차시에 쓸 링크를 걸어 둡니다. 이 브라우저에만 저장되고 밖으로 보내지 않습니다. 학생 이름이 든 주소는 넣지 마세요.</p>
<ul></ul>
<form><label class="small" for="mn-{code}">이름</label><input id="mn-{code}" name="n" maxlength="40" required placeholder="예: 우리 반 패들렛">
<label class="small" for="mu-{code}">주소</label><input id="mu-{code}" name="u" type="url" required placeholder="https://">
<button class="btn" type="submit">걸어 두기</button></form>
</div>
{('<h2 id="game">체험 게임</h2>' + gbox) if gm else ''}
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
    if(!a.length){var p=document.createElement('li');p.className='small muted';p.textContent='아직 걸어 둔 링크가 없습니다.';ul.appendChild(p);return}
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
    parts = []
    for g in (5, 6):
        rows = []
        for c in CODES:
            if grade(c) != g:
                continue
            gm = game(c)
            rows.append('<tr><td><b>%s</b></td><td><a href="%s/">%s</a><br><span class="small muted">%s</span></td><td class="small">%s</td><td class="small">%s</td><td>%s</td></tr>' % (
                label(c), c, e(topic(c)), e(AREA_OF[c]['name']),
                '<br>'.join(e(re.sub(r'\s*\(\d+분\)', '', x)) for x in activities(c)),
                ', '.join(e(t['name']) for t in tools_of(c)) or '종이·실물',
                ('<a href="../%s/">%s</a>' % (c, e(gm['title']))) if gm else '—'))
        parts.append('<h2>%d학년 · %s</h2><div class="tw"><table><tr><th>차시</th><th>학습 주제</th><th>활동</th><th>연동 도구</th><th>체험 게임</th></tr>%s</table></div>'
                     % (g, e(SITE['courses'][str(g)]['name']), ''.join(rows)))
    body = ('<span class="kick">3 · 차시별 교수학습 과정안</span><h1>28편 64차시 과정안</h1>'
            '<p class="lead">학습 주제를 누르면 과정안 전문(개요·교수학습 활동·평가 계획)과 PDF, 연동 도구, 체험 게임으로 이어집니다.</p>%s') % ''.join(parts)
    page('lessons', '차시별 교수학습 과정안 — 에듀다움', body, 'lessons/')


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
            cards.append('<div class="box"><h3 style="margin-top:0"><a href="%s" target="_blank" rel="noopener">%s ↗</a></h3><p class="small">%s</p>'
                         '<p class="small muted">계정: %s%s</p><div>%s</div></div>'
                         % (e(t['url']), e(t['name']), e(t['use']), e(t['account']), (' · ' + more) if more else '', ls or '<span class="small muted">직접 쓰는 차시 없음</span>'))
        groups.append('<h2>%s</h2><div class="grid">%s</div>' % (grp, ''.join(cards)))
    body = ('<span class="kick">연동 도구</span><h1>차시에 걸린 외부 도구</h1>'
            '<p class="lead">모두 무료이며 학생 계정 없이 쓸 수 있게 골랐습니다. 칩을 누르면 그 도구를 쓰는 차시로 갑니다.</p>'
            '<p class="note">도구를 더하거나 차시에 링크를 더 걸려면 <code>_data/tools.json</code>·<code>_data/links.json</code>을 고친 뒤 <code>python _tools/make_site.py</code>를 돌립니다. 교사 개인 링크는 차시 쪽 「내 수업 링크」에 걸 수 있습니다.</p>%s') % ''.join(groups)
    page('tools', '연동 도구 — 에듀다움', body, 'tools/')


# ───────────────────────── 체험 게임 목록
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
            cards.append('<a class="card" href="../%s/" style="border-top:10px solid %s"><span class="chip">%s</span><h3>%s</h3><p>%s</p></a>'
                         % (c, gm['point'], label(c), e(gm['title']), e(gm['lead'])))
        parts.append('<h2>%d학년</h2><div class="grid">%s</div>' % (g, ''.join(cards)))
    body = ('<span class="kick">체험 게임</span><h1>수업 중에 잠깐 만져 보는 체험</h1>'
            '<p class="lead">과정안의 활동 하나를 짧게 미리 겪어 보거나 견주어 봐요. 마이크로비트·엔트리·실제 측정을 대신하지 않습니다.</p>%s'
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
    n = len(list((ROOT / 'lessons').glob('B*/index.html')))
    print('누리집: 홈·계획서·주제별·도구·체험 + 차시 %d쪽' % n)
    for c in CODES:
        print('  %s %-6s 도구 %s' % (c, label(c), ', '.join(t['id'] for t in tools_of(c))))


if __name__ == '__main__':
    main()
