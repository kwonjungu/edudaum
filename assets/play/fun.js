/* 에듀다움 체험 활동 공통 재미 장치 (2026-10-29)
   게임 쪽 </body> 바로 앞에 <script src="../assets/play/fun.js" data-block="B01"></script>
   - 캐릭터 안내 띠를 h1·.lead 아래에 넣는다. 첫 말은 data-mission(없으면 .lead).
   - Fun.say(글, 기분)  기분: 'cheer'(한 판 끝) | 'think'(빗나감·다시) | 없음
   - Fun.stamp()        한 판을 끝까지 했을 때. 도장을 찍고 이 블록에 도장 표시를 남긴다(누리집 지도에 보임).
   - Fun.burst(요소)    도형 조각이 터진다. Fun.shake(요소) 살짝 흔든다.
   점수·등수·맞힌 판 수를 세지 않는다. 칭찬·판정 낱말(맞았어요·틀렸어요·잘했어요)을 쓰지 않는다(_공통기준.md). */
(function () {
  'use strict';
  var me = document.currentScript;
  var B = (me && me.dataset.block) || (location.pathname.match(/B\d\d/) || [''])[0];
  var n = +B.slice(1);
  // 블록마다 안내하는 캐릭터(책 「캐릭터 소개」와 같다)
  var CAST = [
    [1, 6, 'c2', '순서쌤'], [7, 14, 'c3', '비트쌤'], [15, 19, 'c4', '말랑쌤'],
    [20, 22, 'c5', '규칙쌤'], [23, 26, 'c6', '데이터쌤'], [27, 28, 'c7', '지킴쌤']
  ];
  var who = CAST.filter(function (c) { return n >= c[0] && n <= c[1]; })[0] || [0, 0, 'c1', '새싹쌤'];
  var base = me ? me.src.replace(/play\/fun\.js.*$/, '') : '../assets/';
  var KEY = 'edudaum.stamps';

  function el(t, cls, html) { var e = document.createElement(t); if (cls) e.className = cls; if (html != null) e.innerHTML = html; return e; }
  function esc(s) { return String(s).replace(/[&<>]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]; }); }

  var guide, say, stampEl;
  function mount() {
    var h1 = document.querySelector('main h1, h1');
    if (!h1 || document.querySelector('.fun-guide')) return;
    var lead = h1.nextElementSibling && h1.nextElementSibling.classList.contains('lead') ? h1.nextElementSibling : null;
    var first = (me && me.dataset.mission) || (lead ? lead.textContent.trim() : '');
    guide = el('div', 'fun-guide');
    guide.setAttribute('aria-live', 'polite');
    var img = el('img'); img.src = base + 'chars/' + who[2] + '.webp'; img.alt = ''; img.width = 78; img.height = 78;
    say = el('div', 'fun-say');
    guide.appendChild(img); guide.appendChild(say);
    (lead || h1).insertAdjacentElement('afterend', guide);
    if (lead && !(me && me.dataset.keepLead)) lead.hidden = true;   // 같은 말이 두 번 보이지 않게
    setSay(first ? '<span class="fun-mission">' + esc(first) + '</span>' : '', true);
    stampEl = el('div', 'fun-stamp', B + '<br>미션<small>도장</small>');
    stampEl.setAttribute('aria-hidden', 'true');
    document.body.appendChild(stampEl);
  }
  function setSay(html, raw) {
    if (!say) return;
    say.innerHTML = '<b>' + who[3] + '</b>' + (raw ? html : esc(html));
    say.classList.remove('pop'); void say.offsetWidth; say.classList.add('pop');
  }
  function mood(m) {
    if (!guide) return;
    guide.classList.remove('cheer', 'think'); void guide.offsetWidth;
    if (m) guide.classList.add(m);
  }
  function save() {
    try {
      var s = JSON.parse(localStorage.getItem(KEY) || '{}');
      if (!s[B]) { s[B] = new Date().toISOString().slice(0, 10); localStorage.setItem(KEY, JSON.stringify(s)); }
    } catch (e) { /* 저장이 막힌 브라우저에서도 화면은 그대로 */ }
  }
  var COLORS = ['#5aa9e6', '#4cbf9a', '#ffc845', '#9b8cf2', '#ff8fa3', '#2f78b5'];
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;

  window.Fun = {
    block: B, guide: who[3],
    say: function (text, m) { setSay(text); mood(m); },
    stamp: function () {
      save(); mood('cheer');
      if (!stampEl) return;
      stampEl.classList.remove('on'); void stampEl.offsetWidth; stampEl.classList.add('on');
      clearTimeout(stampEl._t); stampEl._t = setTimeout(function () { stampEl.classList.remove('on'); }, 2600);
    },
    burst: function (target) {
      if (reduce) return;
      var r = target && target.getBoundingClientRect ? target.getBoundingClientRect() : { left: innerWidth / 2, top: innerHeight / 2, width: 0, height: 0 };
      var cx = r.left + r.width / 2, cy = r.top + r.height / 2, box = el('div', 'fun-burst');
      for (var i = 0; i < 22; i++) {
        var p = el('i'), a = Math.random() * Math.PI * 2, d = 60 + Math.random() * 110;
        p.style.left = cx + 'px'; p.style.top = cy + 'px'; p.style.background = COLORS[i % COLORS.length];
        if (i % 3 === 0) p.style.borderRadius = '50%';
        p.style.setProperty('--dx', Math.cos(a) * d + 'px'); p.style.setProperty('--dy', Math.sin(a) * d - 40 + 'px');
        p.style.setProperty('--rot', (Math.random() * 540 - 270) + 'deg');
        box.appendChild(p);
      }
      document.body.appendChild(box); setTimeout(function () { box.remove(); }, 1000);
    },
    shake: function (target) {
      if (!target || reduce) return;
      target.classList.remove('fun-shake'); void target.offsetWidth; target.classList.add('fun-shake');
      setTimeout(function () { target.classList.remove('fun-shake'); }, 400);
    }
  };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', mount); else mount();
})();
