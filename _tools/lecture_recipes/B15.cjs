// B15 체험: 세 칸으로 나누기 — z_start(처음) · z_pick(두 장 놓은 뒤) · z_result(확인 뒤)
// 세 칸 구역만 크게(폭 560, 2배) 찍는다. 단추 줄·머리·안내는 숨기고 단추는 evaluate로 누른다.
module.exports = async (p, { shot, shotEl, sleep }) => {
  await p.setViewport({ width: 560, height: 900, deviceScaleFactor: 2 });
  await p.addStyleTag({ content: '[class*="fun-"]{display:none!important} nav,header,.note,.acts{display:none!important} .wrap{padding:6px} .wrap>section:first-child{position:absolute;left:-9999px;top:0;width:520px}' });
  const clk = sel => p.evaluate(s => document.querySelector(s).click(), sel);
  for (let i = 0; i < 40; i++) { const t = await p.$eval('#scene', e => e.textContent); if (t.includes('음성 비서')) break; await clk('#nextBtn'); await sleep(150); }
  const grab = async n => { await shotEl(p, '.wrap > section:last-child', 0, n); };
  await grab('z_start');
  await clk('#cards .card:nth-child(1)'); await sleep(200);
  await clk('#cards .card:nth-child(2)'); await sleep(200);
  await grab('z_pick');
  await clk('#cards .card:nth-child(3)'); await sleep(200);
  await clk('#checkBtn'); await sleep(700);
  await grab('z_result');
};
