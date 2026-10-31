// B25 체험: 샘플 3개로 학습 → 시도 그래프 짚기 → 확인(헷갈림 판)
// z_start(빈 샘플 칸) · z_pick(그래프 세 장 중 고르기) · z_samples(샘플이 찬 모습) · z_result(시험 결과: 막대+헷갈림 판)
module.exports = async (p, { shot, shotEl, sleep }) => {
  await p.setViewport({ width: 760, height: 900, deviceScaleFactor: 2 });
  await p.addStyleTag({ content: '[class*="fun-"]{display:none!important} nav,header,.foot,.row2{display:none!important} .wrap{max-width:720px!important;padding:8px} .wrap>section{margin-top:0!important}' });
  const clk = sel => p.evaluate(s => document.querySelector(s).click(), sel);
  await sleep(500);
  await shotEl(p, 'section', 0, 'z_start');
  await clk('#rec'); await sleep(400);
  await shotEl(p, 'section', 0, 'z_pick');
  // 샘플 9개 채우기(각 동작 3개, 첫 번째 그래프 고르기)
  for (let i = 0; i < 9; i++) {
    await clk('#pick .cand:nth-child(1)'); await sleep(200);
    if (i < 8) { await clk('#rec'); await sleep(250); }
  }
  await sleep(400);
  await shotEl(p, 'section', 0, 'z_samples');
  // 시험 6장
  for (let i = 0; i < 6; i++) {
    await clk('#try'); await sleep(900);
    const card = await p.evaluate(() => document.getElementById('card').textContent);
    const k = /손바닥/.test(card) ? 1 : /손등/.test(card) ? 2 : 3;
    if (i === 5) { /* 마지막 시도는 짚기까지만 */ }
    await clk('#guess .gb:nth-child(' + k + ')'); await sleep(150);
    if (i === 0) { await sleep(200); await p.evaluate(() => { document.querySelector('table.cf').style.display = 'none'; document.getElementById('bars').style.display = 'none'; }); await shotEl(p, '#sec2', 0, 'z_try'); await p.evaluate(() => { document.querySelector('table.cf').style.display = ''; document.getElementById('bars').style.display = ''; }); }
    await clk('#ok'); await sleep(900);
  }
  await sleep(1000);
  await p.addStyleTag({ content: '#big,.legend,#guess,#ok,#try{display:none!important}' });
  await shotEl(p, '#sec2', 0, 'z_result');
  // 샘플 8개로 늘리기(③ 구역): 6번 가운데 몇 번 예측 → 5개씩 더 → 2회차 확인
  await p.evaluate(() => { const h = document.getElementById('sec3'); h.hidden = false; });
  await clk('#g7 .gb:nth-child(5)'); await sleep(200);
  await shotEl(p, '#sec3', 0, 'z_more_pre');
  await clk('#more'); await sleep(300); await clk('#r2'); await sleep(1500);
  await shotEl(p, '#sec3', 0, 'z_more');
  // 연계 활동: 나만의 이미지 모델(lab/camera) — 실험 카드 '한 무리에만 예시를 많이'와 예측 고르기
  const { pathToFileURL } = require('url'); const path = require('path');
  await p.goto(pathToFileURL(path.resolve('lab/camera/index.html')).href, { waitUntil: 'load' }); await sleep(1500);
  await p.setViewport({ width: 760, height: 1000, deviceScaleFactor: 2 });
  await p.addStyleTag({ content: '[class^="fun-"],[class*=" fun-"]{display:none!important} .nav{display:none!important}' });
  for (let i = 0; i < 30; i++) { const t = await p.$eval('#task', e => e.textContent); if (/예시를 많이/.test(t)) break; await clk('#nexttask'); await sleep(150); }
  await sleep(300);
  const sec = (await p.$$('section'))[2];
  await sec.screenshot({ path: 'lecture/_shots/B25/lab_card.png' }); console.log('lab_card');
  await clk('#bets .pick[data-b="0"]'); await sleep(300);
  await sec.screenshot({ path: 'lecture/_shots/B25/lab_pick.png' }); console.log('lab_pick');
};
