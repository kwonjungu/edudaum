// B27 체험: 약속한 조건대로 자료 담기 — z_start(약속 읽기) · z_pick(조건 맞춰 몇 장 담은 뒤) · z_result(다른 조건이 섞인 줄)
// 위(조건·카메라)·아래(담은 장수) 두 section을 2열로 놓고 .wrap 한 컷. 카메라는 가짜 장치(캡처 인자).
module.exports = async (p, { shot, shotEl, sleep }) => {
  await p.setViewport({ width: 1100, height: 700, deviceScaleFactor: 2 });
  await p.addStyleTag({ content: '[class*="fun-"]{display:none!important} nav,header,.foot,.acts #next,.acts #reset,.note:last-child{display:none!important} .wrap{max-width:1040px;display:grid;grid-template-columns:1fr 1fr;gap:12px;padding:10px;align-items:start} .wrap>section{margin-top:0}' });
  await sleep(1500);
  const clk = sel => p.evaluate(s => document.getElementById(s).click(), sel);
  const o = await p.evaluate(() => document.getElementById('order').textContent);
  const a = /위/.test(o) ? 'oTop' : 'oSide', b = /흰/.test(o) ? 'oWhite' : 'oDesk';
  const n = ['세', '네', '다섯', '여섯'].findIndex(w => o.includes(w + ' 장')) + 3;
  console.log(o, a, b, n);
  await shotEl(p, '.wrap', 0, 'z_start');
  await clk(a); await clk(b); await sleep(700);
  await clk('grab'); await sleep(250); await clk('grab'); await sleep(400);
  await shotEl(p, '.wrap', 0, 'z_pick');
  for (let i = 2; i < n; i++) { await clk('grab'); await sleep(250); }
  await clk(a === 'oTop' ? 'oSide' : 'oTop'); await sleep(300); await clk('grab'); await sleep(900);
  await shotEl(p, '.wrap', 0, 'z_result');
};
