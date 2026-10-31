// B24 체험: 기준 바꿔 다시 나누기 — 왼쪽 표 칸만 4줄씩 둘로 나눠 크게 찍는다.
// 산출: z_{start|pick|result}_{a|b}.png (표 위 4줄·아래 4줄), z_chart.png (결과 막대 차트). PIL로 16:9 가까운 틀에 얹는다.
module.exports = async (p, { shot, shotEl, sleep }) => {
  const fs = require('fs'), path = require('path');
  const OUT = path.resolve('lecture/_shots/B24');
  await p.setViewport({ width: 560, height: 900, deviceScaleFactor: 2 });
  const info = async () => p.evaluate(() => {
    const t = id => document.getElementById(id).textContent;
    const c1 = t('c1'), c2 = t('c2');
    const rows = [...document.querySelectorAll('#tbl button.tr')].map(b => ({
      t: b.querySelector('.nt') ? b.querySelector('.nt').textContent.trim() : '', x: b.querySelector('.nx') ? b.querySelector('.nx').textContent.trim() : '' }));
    return { c1, c2, rows };
  });
  // 기준에 쓰인 시간과 같은 값의 줄이 있고 달라질 줄이 2~5줄인 판이 나올 때까지 새로 연다(말풍선 '기준값과 같은 줄'과 맞추려고)
  let ok = false;
  for (let k = 0; k < 120 && !ok; k++) {
    if (k) { await p.reload({ waitUntil: 'load' }); await sleep(250); }
    const v = await p.evaluate(() => {
      const t = id => document.getElementById(id).textContent;
      const c1 = t('c1'), c2 = t('c2');
      const rs = [...document.querySelectorAll('#tbl button.tr')].map(b => { const tt = b.querySelector('.nt').textContent; return { w: b.querySelector('.w').textContent.trim(), t: tt === '—' ? null : parseInt(tt), x: parseInt(b.querySelector('.nx').textContent) }; });
      const mk = s => { let m;
        if ((m = s.match(/시간이 (\d+)분/))) return { f: r => r.t === null ? null : r.t > +m[1], v: +m[1] };
        if ((m = s.match(/횡단보도를 (\d+)개/))) return { f: r => r.x > +m[1], v: null };
        return { f: r => r.w === '걸어서', v: null }; };
      const a = mk(c1), b = mk(c2);
      const ch = rs.filter(r => { const p = a.f(r), q = b.f(r); return p !== null && q !== null && p !== q; }).length;
      const vals = [a.v, b.v].filter(x => x !== null);
      const same = vals.some(v => rs.some(r => r.t === v));
      return { c1, c2, ch, same, t: /시간이/.test(c2) };
    });
    ok = v.same && v.t && v.ch >= 2 && v.ch <= 5;
    if (ok) console.log('판', JSON.stringify(v));
  }
  console.log('판 조건 맞음:', ok);
  const rows = await p.evaluate(() => {
    const t = id => document.getElementById(id).textContent;
    const mk = s => { let m;
      if ((m = s.match(/시간이 (\d+)분/))) return r => r.t === null ? null : r.t > +m[1];
      if ((m = s.match(/횡단보도를 (\d+)개/))) return r => r.x > +m[1];
      return r => r.w === '걸어서'; };
    const f1 = mk(t('c1')), f2 = mk(t('c2'));
    return [...document.querySelectorAll('#tbl button.tr')].map((b, i) => {
      const tt = b.querySelector('.nt').textContent;
      const r = { w: b.querySelector('.w').textContent.trim(), t: tt === '—' ? null : parseInt(tt), x: parseInt(b.querySelector('.nx').textContent) };
      const a = f1(r), c = f2(r); return a !== null && c !== null && a !== c ? i : -1; }).filter(i => i >= 0);
  });
  console.log('달라질 줄', JSON.stringify(rows));
  const half = async (state, which) => {
    await p.evaluate(w => { document.querySelectorAll('#tbl button.tr').forEach((b, i) => { b.style.display = (w === 'a' ? i < 4 : i >= 4) ? '' : 'none'; }); }, which);
    await sleep(200);
    const sec = (await p.$$('section'))[0];
    await sec.screenshot({ path: `${OUT}/z_${state}_${which}.png` }); console.log(`z_${state}_${which}`);
  };
  const both = async state => { await half(state, 'a'); await half(state, 'b'); await p.evaluate(() => document.querySelectorAll('#tbl button.tr').forEach(b => { b.style.display = ''; })); };
  await p.addStyleTag({ content: '*{animation:none!important;transition:none!important} [class*="fun-"]{display:none!important} nav,header,.foot,#s1 h2,section:first-of-type h2,.hint,.acts{display:none!important} .wrap{padding:8px} section{margin:0!important} .crit{font-size:17px!important;gap:6px!important} .crit .k{font-size:15px!important} .tr{font-size:18px!important} .th{font-size:17px!important} .tr .g{font-size:17px!important} .tr .tag2{font-size:16px!important} .bline{font-size:18px!important} .say{font-size:19px!important} #s2 h2{display:block!important;font-size:19px!important}' });
  await sleep(600);
  await both('start');
  for (const i of rows) { await p.evaluate(n => document.querySelectorAll('#tbl button.tr')[n].click(), i); await sleep(120); }
  await sleep(300);
  await both('pick');
  await p.evaluate(() => document.getElementById('checkBtn').click());
  await sleep(2500);
  await both('result');
  await p.evaluate(() => { document.querySelectorAll('.acts').forEach(a => { a.style.display = 'none'; }); });
  const s2 = await p.$('#s2'); await s2.screenshot({ path: `${OUT}/z_chart.png` }); console.log('z_chart');
};
