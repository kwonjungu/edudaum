// B18 체험: 소리 크기 수 → 글자 — z_start(처음) · z_pick(예측하고 첫 수 담기) · z_result(두 번째 수 담은 뒤 같은 글자·다른 수)
// 가짜 마이크는 늘 같은 소리라, AnalyserNode 값을 직접 정해 소리 크기를 흉내 낸다
module.exports = async (p, { shot, shotEl, sleep }) => {
  await p.setViewport({ width: 760, height: 1000, deviceScaleFactor: 2 });
  await p.addStyleTag({ content: '[class^="fun-"],[class*=" fun-"]{display:none!important} .nav,header{display:none!important} body{background:#fff!important}' });
  await p.evaluate(() => {
    window.__v = 20;
    AnalyserNode.prototype.getByteTimeDomainData = function (a) {
      const rms = Math.pow(10, (window.__v / 99 * 50 - 60) / 20);
      for (let i = 0; i < a.length; i++) a[i] = Math.round(128 + (i % 2 ? 1 : -1) * rms * 128);
    };
  });
  const setV = async v => { await p.evaluate(v => { window.__v = v; }, v); await sleep(1200); };
  for (let i = 0; i < 30; i++) { const w = await p.$eval('#want', e => e.textContent); if (w === '다') break; await p.click('#next'); await sleep(150); }
  await setV(20);
  const grab = async n => {
    await sleep(400);
    const r = await p.evaluate(() => { const s = document.querySelectorAll('section'); const x = s[0].getBoundingClientRect(), y = s[1].getBoundingClientRect(); return { x: Math.max(0, x.left - 6), y: x.top + scrollY - 6, width: x.width + 12, height: y.bottom - x.top + 12 }; });
    await p.screenshot({ path: `lecture/_shots/B18/${n}.png`, clip: r }); console.log(n);
  };
  await grab('z_start');
  await p.click('.chip[data-g="60"]'); await setV(55);
  await p.click('#keep'); await sleep(300);
  await grab('z_pick');
  await setV(70);
  await p.click('#keep'); await sleep(900);
  await grab('z_result');
  // 연계 활동: 말 알아듣기 실험실(lab/voice) — lab_card(실험 카드와 예측)
  const { pathToFileURL } = require('url'); const path = require('path');
  await p.goto(pathToFileURL(path.resolve('lab/voice/index.html')).href, { waitUntil: 'load' }); await sleep(1000);
  await p.setViewport({ width: 760, height: 1000, deviceScaleFactor: 2 });
  await p.addStyleTag({ content: '[class^="fun-"],[class*=" fun-"]{display:none!important} .nav{display:none!important}' });
  await sleep(300);
  await p.evaluate(() => { const g = document.getElementById('gate'); if (g) g.hidden = true; document.getElementById('s1').hidden = false; });
  const el = await p.$('#s1'); await el.screenshot({ path: 'lecture/_shots/B18/lab_card.png' }); console.log('lab_card');
  await p.click('.pick[data-b="1"]').catch(() => {}); await sleep(300);
  await el.screenshot({ path: 'lecture/_shots/B18/lab_pick.png' }); console.log('lab_pick');
};
