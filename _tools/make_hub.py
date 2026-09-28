# -*- coding: utf-8 -*-
"""학교자율시간 도입 지원 쪽을 만든다 — 공지사항·학교자율시간이란?·도입 가이드·Q&A·서식 자료실·검색.

  make_site.py가 부른다(따로 돌리지 않는다).

만드는 쪽
  notice/  notice/NXXXX/      공지사항 게시판·상세
  about/                      학교자율시간이란?
  guide/  guide/<주제>/        도입 가이드(한눈에 보는 절차)·주제별 가이드
  qna/                        Q&A
  forms/                      서식 자료실 — 방법 ① 절차로 찾기
  forms/list/                 방법 ② 목록·검색으로 찾기
  forms/FXX/                  서식 상세
  forms/set/                  종합세트(우리 과정을 그대로 도입하는 묶음)
  forms/versions/             판본 차이·정오표
  search/                     누리집 통합 검색

근거 데이터 (모두 사람이 고친다. forms.json의 파일 크기·쪽수만 forms 빌드가 채운다)
  _data/notices.json  _data/about.json  _data/guide.json  _data/qna.json
  _data/forms.json    _data/errata.json _data/refs.json
서식 파일은 assets/forms/ 에 있고, 같은 파일이 구글 드라이브 「서식 자료실(공개용)」에도 있다(site_check S16).
"""
from __future__ import annotations

import datetime
import json
import re

import make_site as M

e = M.e
D = M.D
ROOT = M.ROOT


def load(name, default):
    f = D / name
    return json.loads(f.read_text(encoding='utf-8')) if f.exists() else default


NOTICES = load('notices.json', {'notices': []})['notices']
ABOUT = load('about.json', {'sections': []})
GUIDE = load('guide.json', {'tracks': {}, 'topics': [], 'calendar': []})
QNA = load('qna.json', {'cats': [], 'items': []})
FORMS = load('forms.json', {'forms': [], 'sets': [], 'stages': {}, 'tracks': {}})
ERRATA = load('errata.json', [])
REFS = load('refs.json', {})

FORM = {f['id']: f for f in FORMS['forms']}
QITEM = {q['id']: q for q in QNA['items']}
STAGES = FORMS.get('stages') or {'01': '사전 준비', '02': '설계', '03': '자체 점검', '04': '컨설팅·승인 신청',
                                 '05': '학운위 심의·결재', '06': '나이스 입력·기록', '07': '성찰·보완'}
TRACKS = FORMS.get('tracks') or {'activity': '활동 개설', 'subject': '새 과목 개설', 'approved': '기승인 과목 활용', 'common': '공통'}
TOPIC_ORDER = ['activity', 'subject', 'approved', 'hours', 'standards', 'assess', 'books']
FMT = {'hwpx': '한글', 'pdf': 'PDF', 'xlsx': '엑셀', 'docx': '워드', 'zip': '묶음'}
TODAY = datetime.date(2026, 9, 28)


# ───────────────────────── 글 도우미
def inline(t: str) -> str:
    t = e(t)
    t = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t)
    return t


def md(text: str) -> str:
    """작은 마크다운: 빈 줄 문단, '- ' 목록, **굵게**, |표|."""
    if not text:
        return ''
    out, buf = [], []

    def flush():
        if not buf:
            return
        kind = buf[0][0]
        lines = [x[1] for x in buf]
        if kind == 'li':
            out.append('<ul>%s</ul>' % ''.join('<li>%s</li>' % inline(x) for x in lines))
        elif kind == 'tb':
            rows = [[c.strip() for c in x.strip().strip('|').split('|')] for x in lines if not re.match(r'^\|?\s*:?-{2,}', x.strip())]
            if rows:
                head = ''.join('<th>%s</th>' % inline(c) for c in rows[0])
                body = ''.join('<tr>%s</tr>' % ''.join('<td>%s</td>' % inline(c) for c in r) for r in rows[1:])
                out.append('<div class="tw"><table><tr>%s</tr>%s</table></div>' % (head, body))
        else:
            out.append('<p>%s</p>' % '<br>'.join(inline(x) for x in lines))
        buf.clear()
    for ln in text.split('\n'):
        s = ln.rstrip()
        if not s.strip():
            flush()
            continue
        kind = 'li' if re.match(r'^\s*[-·•]\s', s) else 'tb' if s.strip().startswith('|') else 'p'
        if buf and buf[0][0] != kind:
            flush()
        buf.append((kind, re.sub(r'^\s*[-·•]\s*', '', s) if kind == 'li' else s))
    flush()
    return '<div class="md">%s</div>' % ''.join(out)


def refs_html(refs) -> str:
    if not refs:
        return ''
    parts = []
    for r in refs:
        doc = r.get('doc', '')
        meta = REFS.get(doc, {})
        name = meta.get('short') or doc
        p = (' p.%s' % r['p']) if r.get('p') else (' %s' % r['sec']) if r.get('sec') else ''
        title = ' — '.join(x for x in (meta.get('title', ''), meta.get('issuer', ''), meta.get('date', '')) if x)
        parts.append('<span title="%s">%s%s</span>' % (e(title), e(name), e(p)))
    return '<p class="refs">근거: %s</p>' % ' · '.join(parts)


def fdate(s: str) -> str:
    try:
        d = datetime.date.fromisoformat(s)
        return '%d. %d. %d.' % (d.year, d.month, d.day)
    except (ValueError, TypeError):
        return s or ''


def is_new(s: str) -> bool:
    try:
        return (TODAY - datetime.date.fromisoformat(s)).days <= 7
    except (ValueError, TypeError):
        return False


def kind_badge(f) -> str:
    if f.get('optional'):
        return '<span class="kind ref">선택 양식 · 제출 서류 아님</span>'
    return '<span class="kind off">공식 양식</span>' if f.get('kind') == '공식' else '<span class="kind ref">연구회 참고</span>'


def human(n) -> str:
    n = n or 0
    return '%.1fMB' % (n / 1048576) if n >= 1048576 else '%dKB' % max(1, round(n / 1024))


def file_links(f, up, roles=None, drive=True) -> str:
    """서식 파일 받기 단추 — 누리집에서 바로 받기 + 구글 드라이브."""
    out = []
    for x in f.get('files', []):
        if roles and x.get('role') not in roles:
            continue
        lab = '%s%s' % (FMT.get(x['fmt'], x['fmt'].upper()), '' if x.get('role') == '빈 양식' else ' · ' + (x.get('label') or x.get('role', '')))
        out.append('<a href="%sassets/forms/%s" download%s>⬇ %s</a>' % (up, e(x['file']), '', e(lab)))
    if drive:
        did = next((x.get('drive') for x in f.get('files', []) if x.get('drive') and (not roles or x.get('role') in roles)), None)
        url = ('https://drive.google.com/file/d/%s/view' % did) if did else FORMS.get('drive_folder')
        if url:
            out.append('<a href="%s" target="_blank" rel="noopener">구글 드라이브 ↗</a>' % e(url))
    return '<div class="dl">%s</div>' % ''.join(out)


def filled_links(f, up) -> str:
    """우리 과정으로 채운 양식(작성 예시) 받기 — 학년별로 한글(없으면 엑셀) 하나씩."""
    out = []
    for g, lab in (('5', '5학년 SW'), ('6', '6학년 AI'), ('all', '5·6학년 공통')):
        xs = [x for x in f.get('files', []) if x.get('role') == '작성 예시' and x.get('grade') == g]
        x = next((y for y in xs if y['fmt'] in ('hwpx', 'xlsx')), None)
        if x:
            out.append('<a class="pri" href="%sassets/forms/%s" download>⬇ 채운 양식 · %s</a>' % (up, e(x['file']), lab))
    return ('<div class="dl">%s</div>' % ''.join(out)) if out else ''


def form_chip(fid, up) -> str:
    f = FORM.get(fid)
    if not f:
        return ''
    return '<a class="chip tap" href="%sforms/%s/">%s %s</a>' % (up, fid, fid, e(f['name']))


def qna_chip(qid, up) -> str:
    q = QITEM.get(qid)
    if not q:
        return ''
    return '<a class="chip tap" href="%sqna/#%s">%s</a>' % (up, qid, e(q['q'][:34] + ('…' if len(q['q']) > 34 else '')))


def chips(label, items) -> str:
    items = [x for x in items if x]
    return ('<p class="small" style="margin:12px 0 4px;font-weight:600">%s</p><div style="display:flex;flex-wrap:wrap;gap:6px">%s</div>' % (label, ''.join(items))) if items else ''


def fcard(f, up) -> str:
    stg = STAGES.get(f.get('stage', ''), '')
    trk = ' · '.join(TRACKS.get(t, t) for t in f.get('track', []))
    return ('<div class="fcard" data-stage="%s" data-track="%s" data-kind="%s" data-t="%s"><span class="fno">%s · %s</span>'
            '<h3><a href="%sforms/%s/">%s</a></h3><div>%s</div><p>%s</p><p>%s%s</p>%s</div>') % (
        e(f.get('stage', '')), e(' '.join(f.get('track', []))), e(f.get('kind', '')),
        e(' '.join([f['id'], f['name'], f.get('desc', ''), f.get('who', '')] + f.get('fields', [])[:40])),
        f['id'], e(stg), up, f['id'], e(f['name']), kind_badge(f), e(f.get('desc', '')),
        e(trk), (' · ' + e(f['who'])) if f.get('who') else '', filled_links(f, up) + file_links(f, up, roles=['빈 양식']))


def head(kick, title, lead, crumb='', asof=''):
    return ('%s<div class="banner"><span class="kick">%s</span><h1>%s%s</h1><p class="lead">%s</p></div>'
            % (('<p class="crumb">%s</p>' % crumb) if crumb else '', e(kick), e(title),
               ('<span class="asof">%s 기준</span>' % e(asof)) if asof else '', lead))


# ───────────────────────── 공지사항
CAT_ORDER = ['필독', '지침변경', '일정', '서식', '정정', '안내']


def notice_sorted():
    """고정 글 먼저, 그다음 최근 날짜 순."""
    return sorted(NOTICES, key=lambda n: (0 if n.get('pinned') else 1, -int(n.get('date', '0000-00-00').replace('-', '')), n['id']))


def notice_rows(up, limit=None):
    rows, num = [], sum(1 for n in NOTICES if not n.get('pinned'))
    for n in notice_sorted()[:limit]:
        pin = n.get('pinned')
        no = '📌' if pin else str(num)
        if not pin:
            num -= 1
        att = '📎' if n.get('forms') else ''
        rows.append('<tr class="%s" data-cat="%s" data-t="%s"><td class="no">%s</td><td class="cat"><span class="chip">%s</span></td>'
                    '<td class="tt"><a href="%snotice/%s/">%s</a>%s</td><td class="at">%s</td><td class="dt">%s</td></tr>'
                    % ('pin' if pin else '', e(n.get('cat', '')), e(n['title'] + ' ' + n.get('body', '')), no, e(n.get('cat', '')),
                       up, n['id'], e(n['title']), '<span class="new">N</span>' if is_new(n.get('date')) else '', att, fdate(n.get('date'))))
    return ''.join(rows)


BOARD_JS = """<script>
(function(){
  var rows=[].slice.call(document.querySelectorAll('#board tr[data-cat]')), st={c:'',q:'',p:1}, per=10,
      inp=document.querySelector('#nq'), pg=document.querySelector('#pg'), cnt=document.querySelector('.count');
  function draw(){
    var ws=st.q.trim().toLowerCase().split(/\s+/).filter(Boolean), hit=rows.filter(function(r){var t=r.dataset.t.toLowerCase();return (!st.c||r.dataset.cat===st.c)&&ws.every(function(w){return t.indexOf(w)>=0})});
    var pages=Math.max(1,Math.ceil(hit.length/per)); if(st.p>pages) st.p=pages;
    rows.forEach(function(r){r.hidden=true});
    hit.forEach(function(r,i){r.hidden=!(i>=(st.p-1)*per&&i<st.p*per)});
    cnt.textContent=hit.length+'건'; document.getElementById('none').hidden=hit.length>0;
    pg.textContent=''; for(var i=1;i<=pages;i++){var b=document.createElement('button');b.type='button';b.textContent=i;b.setAttribute('aria-pressed',i===st.p?'true':'false');b.setAttribute('aria-label',i+'쪽');(function(n){b.onclick=function(){st.p=n;draw()}})(i);pg.appendChild(b)}
    document.querySelectorAll('button[data-c]').forEach(function(b){b.setAttribute('aria-pressed',b.dataset.c===st.c?'true':'false')});
  }
  document.querySelectorAll('button[data-c]').forEach(function(b){b.onclick=function(){st.c=b.dataset.c;st.p=1;draw()}});
  inp.oninput=function(){st.q=inp.value;st.p=1;draw()};
  draw();
})();
</script>
"""


def build_notices():
    cats = [c for c in CAT_ORDER if any(n.get('cat') == c for n in NOTICES)]
    btns = '<button type="button" data-c="" aria-pressed="true">전체</button>' + ''.join('<button type="button" data-c="%s" aria-pressed="false">%s</button>' % (e(c), e(c)) for c in cats)
    body = (head('공지사항', '공지사항', '학교자율시간 지침 변경, 일정, 서식 공개 소식을 알립니다. 📌 표시는 꼭 읽어야 할 글입니다.')
            + '<div class="filters">%s<input id="nq" type="search" aria-label="제목·내용 검색" placeholder="제목·내용 검색"><span class="count" aria-live="polite"></span></div>'
              '<div class="tw"><table class="board" id="board"><tr class="hd"><th class="no">번호</th><th class="cat">분류</th><th>제목</th><th class="at">첨부</th><th class="dt">작성일</th></tr>%s</table></div>'
              '<p class="muted" id="none" hidden>맞는 글이 없습니다.</p><div class="filters" id="pg" style="justify-content:center"></div>' % (btns, notice_rows('../')))
    M.page('notice', '공지사항 — 에듀다움', body, 'notice/', BOARD_JS)
    order = notice_sorted()
    for i, n in enumerate(order):
        prev = order[i - 1] if i > 0 else None
        nxt = order[i + 1] if i + 1 < len(order) else None
        att = []
        for fid in n.get('forms', []):
            f = FORM.get(fid)
            if f:
                att.append('<li style="margin:8px 0"><a href="../../forms/%s/"><b>%s %s</b></a> %s%s</li>' % (fid, fid, e(f['name']), kind_badge(f), file_links(f, '../../', roles=['빈 양식', '작성 예시'])))
        pn = '<div class="pn">%s%s</div>' % (
            ('<a class="btn" href="../%s/">← %s</a>' % (prev['id'], e(prev['title'][:24]))) if prev else '<span></span>',
            ('<a class="btn" href="../%s/">%s →</a>' % (nxt['id'], e(nxt['title'][:24]))) if nxt else '')
        body = ('<p class="crumb"><a href="../">공지사항</a> › %s</p><h1>%s</h1>'
                '<p class="small muted" style="margin:0 0 20px"><span class="chip">%s</span> 작성일 %s%s</p>'
                '<div class="box">%s%s</div>%s%s%s%s') % (
            e(n.get('cat', '')), e(n['title']), e(n.get('cat', '')), fdate(n.get('date')),
            (' · 📌 고정') if n.get('pinned') else '', md(n.get('body', '')), refs_html(n.get('refs')),
            ('<h2>첨부 서식</h2><ul style="list-style:none;padding:0">%s</ul>' % ''.join(att)) if att else '',
            chips('관련 Q&A', [qna_chip(q, '../../') for q in n.get('qna', [])]), '', pn)
        M.page('notice/%s' % n['id'], '%s — 공지사항 — 에듀다움' % n['title'], body, 'notice/')


# ───────────────────────── 학교자율시간이란?
def build_about():
    secs = ABOUT.get('sections', [])
    toc = ''.join('<a href="#%s">%s</a>' % (s['id'], e(s['title'])) for s in secs)
    parts = ''.join('<section id="%s"><h2>%s</h2>%s%s</section>' % (s['id'], e(s['title']), md(s.get('body', '')), refs_html(s.get('refs'))) for s in secs)
    body = (head('학교자율시간이란?', '학교자율시간, 한 쪽으로 이해하기',
                 '무엇인지, 왜 생겼는지, 활동과 과목은 무엇이 다른지, 언제 누가 얼마나 해야 하는지 정리했습니다.', asof=ABOUT.get('updated', ''))
            + '<div class="toc">%s</div>%s'
              '<div class="btns" style="margin-top:40px"><a class="btn pri" href="../guide/">도입 가이드로 →</a><a class="btn" href="../forms/set/">종합세트 받기</a></div>' % (toc, parts))
    M.page('about', '학교자율시간이란? — 에듀다움', body, 'about/')


# ───────────────────────── 도입 가이드
TRACK_JS = """<script>
(function(){
  var bs=[].slice.call(document.querySelectorAll('.segs button[data-tr]')), ps=[].slice.call(document.querySelectorAll('[data-trk]'));
  function pick(k){bs.forEach(function(b){b.setAttribute('aria-pressed',b.dataset.tr===k?'true':'false')});ps.forEach(function(p){p.hidden=p.dataset.trk!==k});
    try{history.replaceState(null,'','#'+k)}catch(_){}}
  bs.forEach(function(b){b.onclick=function(){pick(b.dataset.tr)}});
  var h=location.hash.slice(1); pick(bs.some(function(b){return b.dataset.tr===h})?h:bs[0].dataset.tr);
})();
</script>
"""


def steps_html(track, up):
    items = []
    for s in track.get('steps', []):
        pit = ''.join('<li>%s</li>' % inline(p) for p in s.get('pitfalls', []))
        items.append('<li id="%s"><h3>%s</h3><p class="who">%s%s</p>%s%s%s%s</li>' % (
            e(s.get('id', '')), e(s['title']), ('누가: ' + e(s['who'])) if s.get('who') else '',
            (' · 언제: ' + e(s['when'])) if s.get('when') else '', md(s.get('body', '')),
            ('<div class="warn"><b>⚠ 자주 틀리는 곳</b><ul>%s</ul></div>' % pit) if pit else '',
            chips('이 단계 서식', [form_chip(f, up) for f in s.get('forms', [])]), refs_html(s.get('refs'))))
    return '<ol class="steps">%s</ol>' % ''.join(items)


def build_guide():
    trs = GUIDE.get('tracks', {})
    keys = [k for k in ('activity', 'subject', 'approved') if k in trs]
    segs = ''.join('<button type="button" data-tr="%s" aria-pressed="false">%s</button>' % (k, e(trs[k]['name'])) for k in keys)
    panels = ''.join('<div data-trk="%s"><p class="lead" style="margin-top:0">%s</p>%s<div class="btns"><a class="btn" href="%s/">%s 자세히 보기 →</a></div></div>'
                     % (k, inline(trs[k].get('summary', '')), steps_html(trs[k], '../'), k, e(trs[k]['name'])) for k in keys)
    cal = ''.join('<div><b>%s</b>%s%s</div>' % (e(c['when']), inline(c['what']), ('<span class="small muted" style="display:block;margin-top:4px">%s</span>' % e(' · '.join(TRACKS.get(t, t) for t in c.get('track', [])))) if c.get('track') else '')
                  for c in GUIDE.get('calendar', []))
    tops = {t['slug']: t for t in GUIDE.get('topics', [])}
    cards = ''.join('<a class="card plain" href="%s/"><h3>%s</h3><p>%s</p></a>' % (s, e(tops[s]['title']), e(tops[s].get('lead', ''))) for s in TOPIC_ORDER if s in tops)
    body = (head('도입 가이드', '한눈에 보는 도입 절차',
                 '우리 학교가 무엇을 하려는지 고르면 단계마다 <b>누가 · 언제 · 무엇을 내는지</b>와 서식이 나옵니다.', asof='2026. 9.')
            + '<p class="small" style="margin:0 0 4px;font-weight:600">우리 학교는 무엇을 하려나요?</p><div class="segs" role="group" aria-label="갈래 고르기">%s</div>%s'
              '<h2>한 해 일정</h2><p class="small muted">해마다 공문으로 날짜가 확정됩니다. 교육지원청 안내를 함께 확인하세요.</p><div class="cal">%s</div>'
              '<h2>주제별 가이드</h2><div class="grid">%s</div>'
              '<div class="note" style="margin-top:32px">더 궁금한 것은 <a href="../qna/">자주 묻는 질문(Q&A)</a>에서 찾아보세요.</div>' % (segs, panels, cal, cards))
    M.page('guide', '도입 가이드 — 에듀다움', body, 'guide/', TRACK_JS)
    for s in TOPIC_ORDER:
        t = tops.get(s)
        if not t:
            continue
        secs = ''.join('<h2>%s</h2>%s%s' % (e(x['title']), md(x.get('body', '')), refs_html(x.get('refs'))) for x in t.get('sections', []))
        pit = ''.join('<li>%s</li>' % inline(p) for p in t.get('pitfalls', []))
        body = (head('도입 가이드', t['title'], e(t.get('lead', '')), crumb='<a href="../">도입 가이드</a> › %s' % e(t['title']))
                + secs + (('<div class="warn"><b>⚠ 자주 틀리는 곳</b><ul>%s</ul></div>' % pit) if pit else '')
                + chips('관련 서식', [form_chip(f, '../../') for f in t.get('forms', [])])
                + chips('관련 Q&A', [qna_chip(q, '../../') for q in t.get('qna', [])]))
        M.page('guide/%s' % s, '%s — 도입 가이드 — 에듀다움' % t['title'], body, 'guide/%s/' % s)


# ───────────────────────── Q&A
QNA_JS = """<script>
(function(){
  var items=[].slice.call(document.querySelectorAll('.qa details')), st={c:'',q:''}, inp=document.querySelector('#qq'), cnt=document.querySelector('.count');
  var auto=[];
  function has(t,ws){t=t.toLowerCase();return ws.every(function(w){return t.indexOf(w)>=0})}
  function draw(){var n=0,ws=st.q.trim().toLowerCase().split(/\s+/).filter(Boolean);
    auto.forEach(function(d){d.open=false});auto=[];
    items.forEach(function(d){var ok=(!st.c||d.dataset.cat===st.c)&&(!ws.length||has(d.dataset.t,ws));d.hidden=!ok;if(ok)n++;if(ws.length&&ok&&!d.open){d.open=true;auto.push(d)}});
    cnt.textContent=n+'문항';document.getElementById('none').hidden=n>0;
    document.getElementById('all').textContent=items.some(function(d){return !d.open&&!d.hidden})?'모두 펼치기':'모두 접기';
    document.querySelectorAll('button[data-c]').forEach(function(b){b.setAttribute('aria-pressed',b.dataset.c===st.c?'true':'false')})}
  document.querySelectorAll('button[data-c]').forEach(function(b){b.onclick=function(){st.c=b.dataset.c;draw()}});
  inp.oninput=function(){st.q=inp.value;draw()};
  document.getElementById('all').onclick=function(){var o=items.some(function(d){return !d.open&&!d.hidden});items.forEach(function(d){if(!d.hidden)d.open=o});this.textContent=o?'모두 접기':'모두 펼치기'};
  function hash(){var d=document.getElementById(location.hash.slice(1));if(d&&d.tagName==='DETAILS'){st.c='';st.q='';inp.value='';draw();d.open=true;d.scrollIntoView()}}
  var was=[];window.addEventListener('beforeprint',function(){was=items.filter(function(d){return !d.open});items.forEach(function(d){if(!d.hidden)d.open=true})});
  window.addEventListener('afterprint',function(){was.forEach(function(d){d.open=false})});
  window.addEventListener('hashchange',hash); draw(); hash();
})();
</script>
"""


def build_qna():
    cats = QNA.get('cats', [])
    catname = {c['id']: c['name'] for c in cats}
    btns = '<button type="button" data-c="" aria-pressed="true">전체</button>' + ''.join('<button type="button" data-c="%s" aria-pressed="false">%s</button>' % (c['id'], e(c['name'])) for c in cats)
    rows = []
    for i, q in enumerate(QNA.get('items', []), 1):
        rows.append(('<details id="%s" data-cat="%s" data-t="%s"><summary><span class="qn">Q%d</span><span>%s%s</span></summary>'
                    '<div class="ans"><p class="short">%s</p>%s%s%s<p class="refs">%s · 기준 %s · <a href="#%s">이 문항 주소</a></p></div></details>' % (
                        q['id'], e(q.get('cat', '')), e(' '.join([q['q'], q.get('short', ''), q.get('long', '')])), i, e(q['q']),
                        '<span class="chg">바뀐 안내</span>' if q.get('changed') else '',
                        inline(q.get('short', '')), md(q.get('long', '')),
                        ('<div class="warn"><b>🔁 이전 안내와 다른 점</b>%s</div>' % inline(q['changed'])) if q.get('changed') else '',
                        chips('관련 서식', [form_chip(f, '../') for f in q.get('forms', [])]),
                        e(catname.get(q.get('cat'), '')), e(q.get('since', '')), q['id'])).replace('</div></details>', refs_html(q.get('refs')) + '</div></details>'))
    body = (head('Q&A', '학교자율시간 궁금한 이야기', '경기도교육청 Q&A(2025. 9.)와 2026년 안내를 바탕으로 다시 정리했습니다. 문항마다 근거 쪽을 달았습니다.', asof='2026. 9.')
            + '<div class="filters">%s<input id="qq" type="search" aria-label="질문 검색" placeholder="질문·답 검색 — 예: 시수, 세특, 기승인"><span class="count" aria-live="polite"></span>'
              '<button type="button" id="all">모두 펼치기</button></div><div class="qa">%s</div><p class="muted" id="none" hidden>맞는 문항이 없습니다.</p>' % (btns, ''.join(rows)))
    M.page('qna', 'Q&A — 에듀다움', body, 'qna/', QNA_JS)


# ───────────────────────── 서식 자료실
STEP_JS = """<script>
(function(){
  var st={t:'activity',s:''}, cards=[].slice.call(document.querySelectorAll('.fcards .fcard')), cnt=document.querySelector('.count');
  function draw(){var n=0;
    document.querySelectorAll('.segs button[data-tr]').forEach(function(b){b.setAttribute('aria-pressed',b.dataset.tr===st.t?'true':'false')});
    document.querySelectorAll('.stepper button').forEach(function(b){b.setAttribute('aria-pressed',b.dataset.s===st.s?'true':'false');
      var has=cards.some(function(c){return c.dataset.stage===b.dataset.s&&(' '+c.dataset.track+' ').match(new RegExp(' ('+st.t+'|common) '))});b.style.opacity=has?1:.45});
    cards.forEach(function(c){var ok=(' '+c.dataset.track+' ').match(new RegExp(' ('+st.t+'|common) '))&&(!st.s||c.dataset.stage===st.s);c.hidden=!ok;if(ok)n++});
    cnt.textContent=n+'종';}
  document.querySelectorAll('.segs button[data-tr]').forEach(function(b){b.onclick=function(){st.t=b.dataset.tr;st.s='';draw()}});
  document.querySelectorAll('.stepper button').forEach(function(b){b.onclick=function(){st.s=st.s===b.dataset.s?'':b.dataset.s;draw()}});
  draw();
})();
</script>
"""

LIST_JS = """<script>
(function(){
  var st={k:'',t:'',s:'',q:''}, rows=[].slice.call(document.querySelectorAll('#flist tr[data-t]')), cnt=document.querySelector('.count'), inp=document.querySelector('#fq');
  function draw(){var n=0,ws=st.q.trim().toLowerCase().split(/\s+/).filter(Boolean);
    rows.forEach(function(r){var t=r.dataset.t.toLowerCase(),ok=(!st.k||r.dataset.kind===st.k)&&(!st.t||(' '+r.dataset.track+' ').indexOf(' '+st.t+' ')>=0)&&(!st.s||r.dataset.stage===st.s)&&ws.every(function(w){return t.indexOf(w)>=0});r.hidden=!ok;if(ok)n++});
    cnt.textContent=n+'종';document.getElementById('none').hidden=n>0}
  document.querySelectorAll('select[data-f]').forEach(function(s){s.onchange=function(){st[s.dataset.f]=s.value;draw()}});
  inp.oninput=function(){st.q=inp.value;draw()}; draw();
})();
</script>
"""

SEL = 'style="border:1px solid var(--line);border-radius:9999px;padding:8px 14px;min-height:40px;font:inherit;font-size:14px;background:#fff"'


def set_banner(up):
    ss = FORMS.get('sets', [])
    edu = [s for s in ss if s.get('edudaum')]
    if not edu:
        return ''
    return ('<div class="setcard" style="margin:8px 0 32px"><span class="kick">가져다 쓰기만 하면 되는 묶음</span><h3>에듀다움 종합세트</h3>'
            '<p>우리 연구회 5학년 SW 32차시 · 6학년 AI 32차시를 학교자율시간으로 그대로 도입할 때 필요한 서식을 <b>모두 채워</b> 두었습니다. '
            '【 】 표시한 곳을 우리 학교에 맞게 고치고, 학교 절차(학업성적관리위원회·학교운영위원회 심의, 학교장 결재)를 거쳐 확정합니다.</p><div class="btns">%s</div></div>') % ''.join(
        '<a class="btn%s" href="%sforms/set/#%s">%s</a>' % (' pri' if i == 0 else '', up, s['id'], e(s['name'])) for i, s in enumerate(edu))


def build_forms():
    forms = FORMS['forms']
    trs = [k for k in ('activity', 'subject', 'approved') if any(k in f.get('track', []) for f in forms)]
    segs = ''.join('<button type="button" data-tr="%s" aria-pressed="false">%s</button>' % (k, e(TRACKS[k])) for k in trs)
    stepper = ''.join('<button type="button" data-s="%s" aria-pressed="false"><i>%d</i>%s</button>' % (k, i, e(v)) for i, (k, v) in enumerate(sorted(STAGES.items()), 1))
    cards = ''.join(fcard(f, '../') for f in sorted(forms, key=lambda f: (f.get('stage', ''), f['id'])))
    body = (head('도입 서식', '도입 서식 — 절차로 찾기',
                 '우리 학교가 하려는 일을 고르고 단계를 누르면, 그 단계에서 쓰는 서식만 보입니다. 모든 서식은 <b>누리집에서 바로</b> 받을 수 있습니다' + (' — 같은 파일이 <b>구글 드라이브</b> 서식 폴더에도 있습니다.' if FORMS.get('drive_folder') else '.'))
            + set_banner('../')
            + '<div class="btns" style="margin-top:0"><a class="btn" href="list/">목록·검색으로 찾기 →</a>%s</div>' % (
                ('<a class="btn" href="%s" target="_blank" rel="noopener">구글 드라이브 서식 폴더 ↗</a>' % e(FORMS['drive_folder'])) if FORMS.get('drive_folder') else '')
            + '<p class="small" style="margin:24px 0 4px;font-weight:600">① 우리 학교는 무엇을 하려나요?</p><div class="segs" role="group" aria-label="갈래">%s</div>'
              '<p class="small" style="margin:8px 0 4px;font-weight:600">② 단계를 누르세요 <span class="muted" style="font-weight:400">(다시 누르면 전체)</span></p><div class="stepper" role="group" aria-label="단계">%s</div>'
              '<p class="small muted"><span class="count" aria-live="polite" style="margin:0"></span></p><div class="fcards">%s</div>' % (segs, stepper, cards))
    M.page('forms', '도입 서식 — 에듀다움', body, 'forms/', STEP_JS)

    # 방법 ② 목록·검색
    rows = []
    for f in sorted(forms, key=lambda f: f['id']):
        fm = ' · '.join(sorted({FMT.get(x['fmt'], x['fmt']) for x in f.get('files', [])}))
        rows.append('<tr data-kind="%s" data-track="%s" data-stage="%s" data-t="%s"><td>%s</td><td><a href="../%s/"><b>%s</b></a><br><span class="small muted">%s</span></td>'
                    '<td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (
                        e(f.get('kind', '')), e(' '.join(f.get('track', []))), e(f.get('stage', '')),
                        e(' '.join([f['id'], f['name'], f.get('desc', '')] + f.get('fields', [])[:40])), f['id'], f['id'], e(f['name']), e(f.get('desc', '')),
                        kind_badge(f), e(STAGES.get(f.get('stage', ''), '')), e(' · '.join(TRACKS.get(t, t) for t in f.get('track', []))), e(fm),
                        file_links(f, '../../', roles=['빈 양식'])))
    sets = ''.join('<tr><td colspan="7"><b>%s</b> <span class="small muted">%s · %s</span><div class="dl"><a href="../../assets/forms/%s" download>⬇ 한 벌 받기(zip)</a>%s</div></td></tr>' % (
        e(s['name']), e(s.get('desc', '')), human(s.get('bytes')), e(s['zip']),
        ('<a href="%s" target="_blank" rel="noopener">구글 드라이브 ↗</a>' % e(s['drive'])) if s.get('drive') else '') for s in FORMS.get('sets', []))
    opt = lambda d: ''.join('<option value="%s">%s</option>' % (k, e(v)) for k, v in d)
    body = (head('도입 서식', '도입 서식 — 목록·검색으로 찾기', '서식 이름·칸 이름으로 찾고, 구분·단계·갈래로 걸러 봅니다.', crumb='<a href="../">도입 서식</a> › 목록·검색')
            + '<div class="filters"><select data-f="k" aria-label="구분" %s><option value="">공식·참고 모두</option><option value="공식">공식 양식</option><option value="연구회 참고">연구회 참고 양식</option></select>'
              '<select data-f="s" aria-label="단계" %s><option value="">모든 단계</option>%s</select>'
              '<select data-f="t" aria-label="갈래" %s><option value="">모든 갈래</option>%s</select>'
              '<input id="fq" type="search" aria-label="서식 검색" placeholder="서식·칸 이름 — 예: 편제, 체크리스트, 세특"><span class="count" aria-live="polite"></span></div>'
              '<div class="tw"><table id="flist"><tr><th>번호</th><th>서식</th><th>구분</th><th>단계</th><th>갈래</th><th>형식</th><th>받기</th></tr>%s</table></div>'
              '<p class="muted" id="none" hidden>맞는 서식이 없습니다.</p><h2>한 번에 받기</h2><div class="tw"><table>%s</table></div>'
            % (SEL, SEL, opt(sorted(STAGES.items())), SEL, opt((k, TRACKS[k]) for k in TRACKS), ''.join(rows), sets))
    M.page('forms/list', '서식 목록·검색 — 에듀다움', body, 'forms/list/', LIST_JS)

    for f in forms:
        build_form(f)
    build_set()
    build_versions()


DOCNAME = {'GD': '안내자료(2025. 9.)', 'QA': 'Q&A(2025. 9.)', 'WS': '워크시트(2025. 9.)', 'BBS': '예시자료(2024. 7.)',
           'GG': '이것이 궁금해요(2024. 2.)', 'HWPX': '각종 양식(2025. 10.)'}
MEMO = re.compile(r'조판|자간|계정|문서 정보|작성자|머리글|머리말|HWPX|T\d+|셀 name|fill|기울임')


def teacher_change(t: str):
    """교사에게 필요한 변경만 남기고, 원문 약칭을 풀어 쓴다."""
    if MEMO.search(t):
        return None
    for k, v in DOCNAME.items():
        t = re.sub(r'\b%s\b' % k, v, t)
    return t


def linkf(text, up):
    return re.sub(r'\bF(\d\d)\b', lambda m: '<a href="%sforms/F%s/">F%s</a>' % (up, m.group(1), m.group(1)) if 'F' + m.group(1) in FORM else m.group(0), text)


def related(fid):
    pit, guides = [], []
    for k, tr in GUIDE.get('tracks', {}).items():
        for s in tr.get('steps', []):
            if fid in s.get('forms', []):
                pit += s.get('pitfalls', [])
                guides.append(('guide/#%s' % k, '%s — %s' % (tr['name'], s['title'])))
    for t in GUIDE.get('topics', []):
        if fid in t.get('forms', []):
            pit += t.get('pitfalls', [])
            guides.append(('guide/%s/' % t['slug'], t['title']))
    seen, out = set(), []
    for p in pit:
        if p not in seen:
            seen.add(p); out.append(p)
    qs = [q['id'] for q in QNA.get('items', []) if fid in q.get('forms', [])]
    return out[:6], guides, qs


def build_form(f):
    up = '../../'
    rel_pit, rel_guides, rel_q = related(f['id'])
    f = dict(f, pitfalls=f.get('pitfalls') or rel_pit)
    tips = ''.join('<tr><th>%s</th><td>%s</td></tr>' % (e(t.get('part', '')), inline(t.get('text', ''))) for t in f.get('tips', []))
    pit = ''.join('<li>%s</li>' % inline(p) for p in f.get('pitfalls', []))
    diffs = ''.join('<li>%s</li>' % inline(p) for p in (teacher_change(x) for x in f.get('diffs', []) + f.get('changes_from_source', [])) if p)
    files = ''.join('<tr><td>%s</td><td>%s</td><td>%s%s</td><td><div class="dl" style="padding:0"><a href="%sassets/forms/%s" download>⬇ 받기</a>%s</div></td></tr>' % (
        e(x.get('label') or x.get('role', '')), e(FMT.get(x['fmt'], x['fmt'])), human(x.get('bytes')), (' · %d쪽' % x['pages']) if x.get('pages') else '', up, e(x['file']),
        ('<a href="https://drive.google.com/file/d/%s/view" target="_blank" rel="noopener">드라이브 ↗</a>' % e(x['drive'])) if x.get('drive') else '')
        for x in f.get('files', []))
    flow = ' → '.join(linkf(e(x), up) for x in (f.get('who'), f.get('submit_to'), f.get('next')) if x)
    pv = ('<div class="pv"><img src="%sassets/forms/%s" alt="%s 첫 쪽 미리보기" loading="lazy"></div>' % (up, e(f['preview']), e(f['name']))) if f.get('preview') else ''
    body = ('<p class="crumb"><a href="../">도입 서식</a> › <a href="../list/">목록</a> › %s</p>'
            '<h1>%s %s</h1><p style="margin:0 0 16px">%s <span class="asof">%s</span> <span class="small muted">%s · %s</span></p>'
            '%s%s<div class="two"><div>%s%s%s%s%s</div><aside>%s<h2 style="margin-top:24px">파일</h2><div class="tw"><table><tr><th>종류</th><th>형식</th><th>크기</th><th>받기</th></tr>%s</table></div>%s</aside></div>') % (
        f['id'], f['id'], e(f['name']), kind_badge(f), e(f.get('asof', '2025. 9.') + ' 기준' if f.get('kind') == '공식' else '연구회 제작 ' + f.get('asof', '2026. 9.')),
        e(STAGES.get(f.get('stage', ''), '')), e(' · '.join(TRACKS.get(t, t) for t in f.get('track', []))),
        ('<p class="lead">%s</p>' % e(f['desc'])) if f.get('desc') else '', file_links(f, up),
        ('<p><b>흐름</b> %s</p>' % flow) if flow else '',
        ('<div class="note">경기도교육청 공식 양식이 아닙니다. 에듀다움 연구회가 현장에서 필요해 만든 참고 양식이니 학교 여건에 맞게 고쳐 쓰세요.</div>' if f.get('kind') != '공식' else ''),
        ('<h2>칸별 작성 요령</h2><div class="tw"><table>%s</table></div>' % tips) if tips else '',
        ('<div class="warn"><b>⚠ 자주 틀리는 곳</b><ul>%s</ul></div>' % pit) if pit else '',
        (('<h2>원 양식과 다른 점</h2><ul class="small">%s</ul>' % diffs) if diffs else '')
        + chips('관련 가이드', ['<a class="chip tap" href="%s%s">%s</a>' % (up, u, e(t)) for u, t in rel_guides[:6]])
        + chips('관련 Q&A', [qna_chip(q, up) for q in rel_q[:8]]),
        pv, files,
        refs_html(f.get('refs') or f.get('source')))
    M.page('forms/%s' % f['id'], '%s %s — 도입 서식 — 에듀다움' % (f['id'], f['name']), body, 'forms/list/')


def build_set():
    parts = []
    for s in FORMS.get('sets', []):
        cont = ''.join('<li>%s</li>' % inline(c) for c in s.get('contents', []))
        how = ''.join('<li>%s</li>' % inline(c) for c in s.get('howto', []))
        rows = ''.join('<tr><td>%02d</td><td><a href="../%s/"><b>%s</b></a> <span class="small muted">%s</span></td><td><div class="dl" style="padding:0">%s</div></td></tr>' % (
            it['no'], it['id'], e(it['name']), it['id'],
            ''.join('<a href="../../assets/forms/%s" download>⬇ %s</a>' % (e(x['file']), FMT.get(x['fmt'], x['fmt'])) for x in it['files']))
            for it in s.get('items', []))
        order = ('<h4 style="margin:20px 0 6px">들어 있는 채운 양식 — 쓰는 순서대로</h4><p class="small muted" style="margin:0 0 8px">zip과 구글 드라이브 폴더도 같은 번호 순서입니다. 과정안 14편(한글·PDF)과 「00_먼저읽어주세요」 안내가 함께 들어 있습니다.</p>'
                 '<div class="tw"><table><tr><th>순서</th><th>서식</th><th>한 장씩 받기</th></tr>%s</table></div>' % rows) if rows else ''
        parts.append('<section id="%s" class="setcard" style="margin:24px 0"><h3>%s</h3><p>%s</p>'
                     '<div class="btns"><a class="btn%s" href="../../assets/forms/%s" download>⬇ 한 번에 받기 (zip, %s)</a>%s</div>'
                     '%s%s</section>' % (s['id'], e(s['name']), inline(s.get('desc', '')), ' pri' if s.get('edudaum') else '', e(s['zip']), human(s.get('bytes')),
                                          ('<a class="btn" href="%s" target="_blank" rel="noopener">구글 드라이브에서 받기 ↗</a>' % e(s['drive'])) if s.get('drive') else '',
                                          order + (('<h4>이렇게 쓰세요</h4><ol class="small">%s</ol>' % how) if how else ''),
                                          ('<details><summary class="small" style="cursor:pointer;font-weight:600">묶음에 든 파일 %d개</summary><ul class="small">%s</ul></details>' % (len(s.get('contents', [])), cont)) if cont else ''))
    body = (head('도입 서식', '종합세트 — 가져다 쓰기만 하면 되는 묶음',
                 '5학년 SW·6학년 AI 32차시를 학교자율시간으로 그대로 도입할 때 필요한 서식을 <b>모두 채워</b> 두었습니다. 신청서부터 학운위 안건·결재 기안·교구 구입 품의·나이스 업로드·세특 예시까지, 쓰는 순서대로 번호를 붙였습니다. 다른 과정을 직접 만들 학교는 맨 아래 빈 양식 한 벌을 받으세요.',
                 crumb='<a href="../">도입 서식</a> › 종합세트')
            + '<div class="note">채운 서식은 <b>작성 예시</b>입니다. 【 】 표시한 곳을 우리 학교에 맞게 고치고, 학교 절차(학업성적관리위원회·학교운영위원회 심의, 학교장 결재)를 거쳐 확정합니다. 【 】에는 학교명·날짜·운영 학기·시수를 조정할 교과 등이 들어 있습니다.</div>'
            + ''.join(parts))
    M.page('forms/set', '종합세트 — 도입 서식 — 에듀다움', body, 'forms/set/')


def build_versions():
    rows = ''.join('<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td class="small muted">%s</td></tr>' % (
        e(REFS.get(x.get('doc', ''), {}).get('short') or x.get('doc', '')), e(str(x.get('p', ''))), e(x.get('wrong', '')), e(x.get('right', '')), e(x.get('note', ''))) for x in ERRATA)
    diff = []
    for f in FORMS['forms']:
        ch = f.get('diffs', []) + f.get('changes_from_source', [])
        if f.get('kind') == '공식' and ch:
            diff.append('<h3><a href="../%s/">%s %s</a></h3><ul class="small">%s</ul>' % (f['id'], f['id'], e(f['name']), ''.join('<li>%s</li>' % inline(c) for c in ch)))
    body = (head('도입 서식', '판본 차이·정오표', '같은 서식이 문서마다 조금씩 다르고, 원문에 잘못 찍힌 곳도 있습니다. 이 누리집의 서식은 2025. 9. 판과 2026년 안내를 기준으로 맞췄습니다.',
                 crumb='<a href="../">도입 서식</a> › 판본 차이·정오표')
            + '<h2>원문 정오표</h2><div class="tw"><table><tr><th>문서</th><th>쪽</th><th>원문</th><th>바로잡음</th><th>비고</th></tr>%s</table></div>'
              '<h2>공식 양식 — 원 양식과 다르게 정리한 곳</h2>%s' % (rows, ''.join(diff) or '<p class="muted">없음</p>'))
    M.page('forms/versions', '판본 차이·정오표 — 에듀다움', body, 'forms/versions/')


# ───────────────────────── 통합 검색
SEARCH_JS = """<script>
(function(){
  var IDX=JSON.parse(document.getElementById('idx').textContent), inp=document.getElementById('sq'), out=document.getElementById('hits'), cnt=document.querySelector('.count');
  function el(tag,txt){var x=document.createElement(tag);if(txt)x.textContent=txt;return x}
  function draw(){var q=inp.value.trim().toLowerCase(), ws=q.split(/\\s+/).filter(Boolean), hit=[];
    if(ws.length) IDX.forEach(function(d){var t=(d.t+' '+d.b).toLowerCase();if(ws.every(function(w){return t.indexOf(w)>=0}))hit.push(d)});
    hit.sort(function(a,b){return (b.t.toLowerCase().indexOf(ws[0])>=0)-(a.t.toLowerCase().indexOf(ws[0])>=0)});
    out.textContent='';
    hit.slice(0,80).forEach(function(d){var i=d.b.toLowerCase().indexOf(ws[0]),s=i>=0?d.b.slice(Math.max(0,i-40),i+90):d.b.slice(0,120);
      var a=el('a'),b=el('b');a.setAttribute('href',d.u);b.appendChild(el('em',d.k));b.appendChild(document.createTextNode(d.t));a.appendChild(b);a.appendChild(el('span',s));out.appendChild(a)});
    cnt.textContent=ws.length?hit.length+'건':'';
    try{history.replaceState(null,'','?q='+encodeURIComponent(inp.value))}catch(_){}}
  inp.value=new URLSearchParams(location.search).get('q')||''; inp.oninput=draw; draw(); inp.focus();
})();
</script>
"""


def plain(t):
    return re.sub(r'\s+', ' ', re.sub(r'[*|#-]+', ' ', t or '')).strip()


def build_search():
    idx = []
    for n in NOTICES:
        idx.append({'k': '공지', 't': n['title'], 'b': plain(n.get('body', ''))[:600], 'u': '../notice/%s/' % n['id']})
    for s in ABOUT.get('sections', []):
        idx.append({'k': '학교자율시간이란', 't': s['title'], 'b': plain(s.get('body', ''))[:600], 'u': '../about/#%s' % s['id']})
    for k, tr in GUIDE.get('tracks', {}).items():
        for s in tr.get('steps', []):
            idx.append({'k': '가이드', 't': '%s — %s' % (tr['name'], s['title']), 'b': plain(s.get('body', ''))[:600], 'u': '../guide/#%s' % k})
    for t in GUIDE.get('topics', []):
        idx.append({'k': '가이드', 't': t['title'], 'b': plain(' '.join([t.get('lead', '')] + [x.get('title', '') + ' ' + x.get('body', '') for x in t.get('sections', [])]))[:900], 'u': '../guide/%s/' % t['slug']})
    for q in QNA.get('items', []):
        idx.append({'k': 'Q&A', 't': q['q'], 'b': plain(q.get('short', '') + ' ' + q.get('long', ''))[:600], 'u': '../qna/#%s' % q['id']})
    for f in FORMS['forms']:
        idx.append({'k': '서식', 't': '%s %s' % (f['id'], f['name']), 'b': plain(' '.join([f.get('desc', '')] + f.get('fields', [])))[:600], 'u': '../forms/%s/' % f['id']})
    for c in M.CODES:
        idx.append({'k': '과정안', 't': '%d학년 %s차시 %s' % (M.grade(c), M.label(c), M.topic(c)), 'b': plain(' '.join(M.activities(c)) + ' ' + M.std_code(c))[:400], 'u': '../lessons/%s/' % c})
    data = json.dumps(idx, ensure_ascii=False).replace('</', '<\\/')
    body = (head('검색', '누리집 검색', '공지·가이드·Q&A·서식·과정안을 한꺼번에 찾습니다. 낱말을 띄어 쓰면 모두 들어간 것만 보여 줍니다.')
            + '<div class="filters"><input id="sq" type="search" aria-label="검색어" placeholder="예: 세특 시간, 편제표, 기승인 인정도서, 마이크로비트" style="font-size:16px;min-height:52px">'
              '<span class="count" aria-live="polite"></span></div><div class="hits" id="hits"></div>'
              '<script type="application/json" id="idx">%s</script>' % data)
    M.page('search', '검색 — 에듀다움', body, 'search/', SEARCH_JS)


# ───────────────────────── 홈에 붙는 블록
def home_hero() -> str:
    return ('<section class="hero"><span class="kick">%s</span><h1>학교자율시간, 처음부터 끝까지</h1>'
            '<p class="lead">개념·도입 절차·Q&A·서식을 한곳에서 찾고, 5학년 SW·6학년 AI 32차시 과정을 종합세트로 그대로 가져다 씁니다.</p>'
            '<form class="search one" action="search/" role="search"><label><span>찾을 말</span>'
            '<input name="q" placeholder="예: 세특 시간, 편제표, 기승인 과목, 마이크로비트 품의"></label>'
            '<button class="orb" type="submit" aria-label="누리집 검색">%s</button></form></section>') % (e(M.SITE['org']), M.SEARCH_SVG)


def home_blocks() -> str:
    """홈 — 윗줄 메뉴와 같은 여섯 칸만."""
    quick = [('plan/', '연구회 소개', '에듀다움 교사연구회와 5·6학년 SW·AI 과정'), ('about/', '학교자율시간이란?', '개념·도입 시기·활동과 과목'),
             ('guide/', '도입 가이드', '활동 개설 절차를 단계별로'), ('forms/', '도입 서식', '채운 서식 종합세트·빈 양식'),
             ('lessons/', '차시별 교수학습 과정안', '28편 64차시'), ('topics/', '영역별 교수학습 과정안', '5학년 4영역 · 6학년 5영역')]
    q = ''.join('<a href="%s"><b>%s</b><span>%s</span></a>' % (u, e(t), e(d)) for u, t, d in quick)
    return '<div class="quick">%s</div>' % q


def main():
    build_notices()
    build_about()
    build_guide()
    build_qna()
    build_forms()
    build_search()
    n = len(NOTICES) + 1 + 1 + len(GUIDE.get('topics', [])) + 1 + 1 + 2 + len(FORMS['forms']) + 2 + 1
    print('도입 지원 쪽: 공지 %d · 가이드 주제 %d · Q&A %d · 서식 %d · 묶음 %d (약 %d쪽)' % (
        len(NOTICES), len(GUIDE.get('topics', [])), len(QNA.get('items', [])), len(FORMS['forms']), len(FORMS.get('sets', [])), n))
