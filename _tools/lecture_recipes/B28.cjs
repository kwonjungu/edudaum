// B28 체험: 학습 데이터 손 사진 짜기 — z_start(처음) · z_pick(세 사람·추가 사진·예측 고른 뒤) · z_result(넣어 보기 뒤)
// 세 구역(사람·추가 사진·확인)을 .wrap 하나로 가로 컷. 오른손(맨손)·왼손·어두운 곳 오른손을 고르고 왼손 사진을 더해 본다.
module.exports = async (p, { shot, shotEl, sleep }) => {
  await p.setViewport({ width: 1000, height: 900, deviceScaleFactor: 2 });
  await p.addStyleTag({ content: '[class*="fun-"]{display:none!important} nav,header,.note{display:none!important} .wrap{max-width:960px;padding:10px;display:grid;grid-template-columns:1fr 1fr;gap:12px;align-items:start} .wrap>section{margin-top:0} .wrap>section:first-of-type{grid-row:span 2}' });
  const clk = sel => p.evaluate(s => document.querySelector(s).click(), sel);
  const grab = async n => { await sleep(500); await shotEl(p, '.wrap', 0, n); };
  await grab('z_start');
  for (const i of [1, 2, 4]) { await clk('#people .pick:nth-child(' + i + ')'); await sleep(150); }
  await clk('#wheres .pick:nth-child(1)'); await sleep(150);
  await clk('#people .pick:nth-child(2)'); await sleep(150);
  await grab('z_pick');
  await clk('#go'); await sleep(2500);
  await grab('z_result');
};
