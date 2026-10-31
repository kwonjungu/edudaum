// B20 체험: 규칙 순서 바꾸면 옮길 카드 짚기 — z_start(처음) · z_pick(짚은 뒤) · z_result(순서 바꾼 뒤)
// 규칙표 구역과 카드 구역을 가로 두 칸으로 놓고 한 장으로 찍는다. 옮겨가는 카드가 1~4장인 판이 나올 때까지 '다음 판'을 돌린다.
module.exports = async (p, { shot, shotEl, sleep }) => {
  await p.setViewport({ width: 1000, height: 700, deviceScaleFactor: 2 });
  await p.addStyleTag({ content: '[class*="fun-"]{display:none!important} nav,header,.acts,.hint{display:none!important} .wrap{max-width:1000px!important;display:grid;grid-template-columns:1fr 1fr;gap:12px;padding:8px} .wrap>section{margin-top:0!important} .card svg.shape{max-width:70px} .card .v{font-size:15px}' });
  const clk = sel => p.evaluate(s => document.querySelector(s).click(), sel);
  for (let i = 0; i < 60; i++) {
    await clk('#nextBtn'); await sleep(150);
    await clk('#gstrip .gc:nth-child(3)'); await sleep(100);
    await clk('#swapBtn'); await sleep(900);
    const n = await p.$$eval('.card.diff', e => e.length);
    if (n >= 1 && n <= 4) { await clk('#reset'); await sleep(500); break; }
  }
  const grab = async n => { await shotEl(p, '.wrap', 0, n); };
  await grab('z_start');
  await clk('#gstrip .gc:nth-child(3)'); await sleep(300);
  await grab('z_pick');
  await clk('#swapBtn'); await sleep(1200);
  await grab('z_result');
};
