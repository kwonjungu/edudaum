// B19 체험: 카드 한 장 빼서 다음 말 바꾸기 — z_start(처음 표) · z_pick(예상·카드 고른 뒤) · z_result(확인 뒤)
// 처음부터 1등이 둘인 판(같아요 · 주사위)이 나올 때까지 '다음 판'을 눌러 '바뀜' 결과를 찍는다
module.exports = async (p, { shot, shotEl, sleep }) => {
  await p.setViewport({ width: 900, height: 760, deviceScaleFactor: 2 });
  await p.addStyleTag({ content: '[class^="fun-"],[class*=" fun-"]{display:none!important} .nav,header,.note{display:none!important} body{background:#fff!important} .wrap{display:grid!important;grid-template-columns:1fr 1fr;gap:14px;max-width:none!important}' });
  for (let i = 0; i < 40; i++) { const r = await p.$eval('#result', e => e.textContent); if (r.startsWith('같아요')) break; await p.click('#nextBtn'); await sleep(150); }
  const grab = async n => {
    await sleep(500);
    const r = await p.evaluate(() => { const s = document.querySelectorAll('section'); const x = s[0].getBoundingClientRect(), y = s[1].getBoundingClientRect(); const t = Math.min(x.top, y.top) + scrollY, b = Math.max(x.bottom, y.bottom) + scrollY; return { x: Math.max(0, x.left - 8), y: t - 8, width: y.right - x.left + 16, height: b - t + 16 }; });
    await p.screenshot({ path: `lecture/_shots/B19/${n}.png`, clip: r, captureBeyondViewport: true }); console.log(n);
  };
  await grab('z_start');
  await p.click('#bets button[data-g="changed"]'); await sleep(200);
  const w = await p.evaluate(() => { const rows = [...document.querySelectorAll('.barrow')]; const cs = rows.map(r => +r.querySelector('.barcount').textContent); const m = Math.max(...cs); return rows[cs.indexOf(m)].querySelector('.barname').textContent; });
  const idx = await p.evaluate(w => [...document.querySelectorAll('#cards .card')].findIndex(c => c.querySelector('u').textContent === w), w);
  await p.click(`#cards .card:nth-child(${idx + 1})`); await sleep(200);
  await grab('z_pick');
  await p.click('#confirmBtn'); await sleep(1200);
  await grab('z_result');
  // 연계 활동: 말 알아듣기 실험실(lab/voice) — lab_card · lab_pick
  const { pathToFileURL } = require('url'); const path = require('path');
  await p.goto(pathToFileURL(path.resolve('lab/voice/index.html')).href, { waitUntil: 'load' }); await sleep(1000);
  await p.setViewport({ width: 760, height: 1000, deviceScaleFactor: 2 });
  await p.addStyleTag({ content: '[class^="fun-"],[class*=" fun-"]{display:none!important} .nav{display:none!important}' });
  await sleep(300);
  await p.evaluate(() => { const g = document.getElementById('gate'); if (g) g.hidden = true; document.getElementById('s1').hidden = false; });
  const el = await p.$('#s1'); await el.screenshot({ path: 'lecture/_shots/B19/lab_card.png' }); console.log('lab_card');
  await p.click('.pick[data-b="1"]').catch(() => {}); await sleep(300);
  await el.screenshot({ path: 'lecture/_shots/B19/lab_pick.png' }); console.log('lab_pick');
};
