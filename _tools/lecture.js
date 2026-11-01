(function () {
  'use strict';
  var S = [].slice.call(document.querySelectorAll('.s:not(.exp)')), cur = 0, pg = document.getElementById('pg');
  var start = parseInt((location.hash.match(/\d+/) || [1])[0], 10) - 1;
  function fit() {
    var k = Math.min(innerWidth / 1280, innerHeight / 720);
    S.forEach(function (s) { s.style.transform = 'translate(-50%,-50%) scale(' + k + ')'; });
  }
  function steps(s) { return [].slice.call(s.querySelectorAll('[data-step]')).sort(function (a, b) { return a.dataset.step - b.dataset.step; }); }
  function reset(s) { steps(s).forEach(function (x) { x.classList.add('hide'); }); }
  var cycle = null;
  // 「예시 보기」: 같은 자리에서 빈 활동지와 예시 답 판을 바꿔 보여 준다
  function exSet(b, on) {
    var im = b.parentNode.querySelector('.zoom.ws img'); if (!im) return;
    im.src = on ? b.dataset.ex : b.dataset.blank; b.setAttribute('aria-pressed', on ? 'true' : 'false');
    b.querySelector('.t').textContent = on ? '빈 활동지' : '예시 보기';
  }
  function exOff(s) { [].forEach.call(s.querySelectorAll('.exbtn[aria-pressed="true"]'), function (b) { exSet(b, false); }); }
  [].forEach.call(document.querySelectorAll('.exbtn'), function (b) {
    new Image().src = b.dataset.ex;
    b.addEventListener('click', function (ev) { ev.stopPropagation(); exSet(b, b.getAttribute('aria-pressed') !== 'true'); });
  });
  function show(i) {
    if (i < 0 || i >= S.length) return;
    S[cur].classList.remove('cur'); exOff(S[cur]); cur = i; S[cur].classList.add('cur'); reset(S[cur]);
    pg.textContent = (cur + 1) + ' / ' + S.length; history.replaceState(null, '', '#' + (cur + 1));
    clearInterval(cycle);
    var shots = S[cur].querySelectorAll('.scr img'), lbs = S[cur].querySelectorAll('.scr .lb');
    if (shots.length > 1) { var k = 0; cycle = setInterval(function () { shots[k].classList.remove('on'); if (lbs[k]) lbs[k].classList.remove('on'); k = (k + 1) % shots.length; shots[k].classList.add('on'); if (lbs[k]) lbs[k].classList.add('on'); }, 2600); }
  }
  function next() { var h = S[cur].querySelector('[data-step].hide'); if (h) h.classList.remove('hide'); else show(cur + 1); }
  function prev() { show(cur - 1); }
  document.addEventListener('keydown', function (ev) {
    if (ev.target.closest && ev.target.closest('.exbtn') && (ev.key === ' ' || ev.key === 'Enter')) return;   // 단추는 스페이스·엔터로 누른다
    if (ev.key === 'ArrowRight' || ev.key === ' ' || ev.key === 'PageDown') { ev.preventDefault(); next(); }
    if (ev.key === 'ArrowLeft' || ev.key === 'PageUp') { ev.preventDefault(); prev(); }
    if (ev.key === 'f' || ev.key === 'F') toggleFs();
  });
  document.getElementById('nextb').onclick = next; document.getElementById('prev').onclick = prev;
  // 전체 화면: 단추나 F 키로 켜고 끈다
  var fsb = document.getElementById('fs');
  function toggleFs() { if (document.fullscreenElement) document.exitFullscreen(); else if (document.documentElement.requestFullscreen) document.documentElement.requestFullscreen(); }
  fsb.onclick = toggleFs;
  document.addEventListener('fullscreenchange', function () { fsb.textContent = document.fullscreenElement ? '⛶ 창으로' : '⛶ 전체 화면'; fit(); });
  document.querySelector('.deck').addEventListener('click', function (ev) {
    var t = ev.target.closest('button, a, .qr, .qrbig'); if (t) return; next();
  });
  // 게임 부품
  document.querySelectorAll('.opts').forEach(function (g) { g.addEventListener('click', function (ev) { var b = ev.target.closest('.opt'); if (!b) return; g.querySelectorAll('.opt').forEach(function (x) { x.classList.toggle('pick', x === b); }); }); });
  document.querySelectorAll('.flip').forEach(function (b) { b.onclick = function () { b.classList.toggle('on'); }; });
  document.querySelectorAll('.pair').forEach(function (g) { g.addEventListener('click', function (ev) { var b = ev.target.closest('.side'); if (!b) return; g.querySelectorAll('.side').forEach(function (x) { x.classList.toggle('pick', x === b); }); }); });
  document.querySelectorAll('.hunt').forEach(function (h) { h.addEventListener('click', function (ev) { ev.stopPropagation(); var x = h.querySelector('.spot.hide'); if (x) x.classList.remove('hide'); }); });
  // QR을 누르면 화면 가득 크게, 다시 누르거나 Esc로 닫기
  document.querySelectorAll('.qr').forEach(function (q) {
    q.addEventListener('click', function (ev) {
      ev.stopPropagation();
      var o = document.createElement('div'); o.className = 'qrbig';
      var a = q.parentNode.querySelector('a');
      o.innerHTML = q.innerHTML + '<p>' + (a ? a.getAttribute('href') : '') + '</p>';
      o.onclick = function (e) { e.stopPropagation(); o.remove(); };
      document.body.appendChild(o);
    });
  });
  document.addEventListener('keydown', function (ev) { if (ev.key === 'Escape') document.querySelectorAll('.qrbig').forEach(function (o) { o.remove(); }); });
  document.querySelectorAll('.order').forEach(function (g) {
    var n = 0; g.addEventListener('click', function (ev) { var b = ev.target.closest('.oc'); if (!b) return; ev.stopPropagation();
      if (b.classList.contains('done')) { g.querySelectorAll('.oc').forEach(function (x) { x.classList.remove('done'); }); n = 0; return; }
      n++; b.classList.add('done'); b.querySelector('.n').textContent = n; });
  });
  document.querySelectorAll('.timer').forEach(function (t) {
    var id = null; t.onclick = function () {
      if (id) { clearInterval(id); id = null; t.classList.remove('run'); return; }
      var left = parseInt(t.dataset.min, 10) * 60, sp = t.querySelector('span'); t.classList.add('run');
      id = setInterval(function () { left--; sp.textContent = Math.floor(left / 60) + ':' + ('0' + left % 60).slice(-2); if (left <= 0) { clearInterval(id); id = null; t.classList.remove('run'); } }, 1000);
    };
  });
  addEventListener('resize', fit); fit();
  S.forEach(reset); S[0].classList.add('cur'); show(Math.max(0, Math.min(start, S.length - 1)));
})();
