// B22 체험: 날씨 카드로 판단 도우미 시험 — z_start(처음) · z_pick(결론 짚은 뒤) · z_result(확인 뒤)
// 두 section을 2열로 놓고 .wrap 전체를 한 컷으로. 첫 카드는 기본 순서(원래 순서)가 나올 때까지 #next.
module.exports = async (p, { shot, shotEl, sleep }) => {
  await p.setViewport({ width: 1100, height: 700, deviceScaleFactor: 2 });
  await p.addStyleTag({ content: '[class*="fun-"]{display:none!important} nav,header,.note{display:none!important} .wrap{max-width:1040px;display:grid;grid-template-columns:1.1fr 1fr;gap:12px;padding:10px} .wrap>section{margin-top:0}' });
  const clk = sel => p.evaluate(s => document.querySelector(s).click(), sel);
  const info = () => p.evaluate(() => ({ ord: document.getElementById('ord').textContent, w: document.getElementById('vw').textContent, d: document.getElementById('vd').textContent, t: parseFloat(document.getElementById('vt').textContent), cn: document.getElementById('cn').textContent }));
  for (let i = 0; i < 30; i++) { const o = await info(); if (!/기온/.test(o.ord) && /날씨 카드/.test(o.cn) && o.w !== '비') break; await clk('#next'); await sleep(150); }
  const o = await info();
  let ans = 4;
  if (o.w === '비') ans = 0; else if (o.d === '나쁨' || o.d === '매우나쁨') ans = 1; else if (o.t >= 33) ans = 2; else if (o.t >= 28) ans = 3;
  console.log(JSON.stringify(o), ans);
  const grab = async n => { await sleep(500); await shotEl(p, '.wrap', 0, n); };
  await grab('z_start');
  await clk('#opts .opt:nth-child(' + (ans + 1) + ')'); await sleep(250);
  await grab('z_pick');
  await clk('#check'); await sleep(2500);
  await grab('z_result');
  await sleep(300); await shotEl(p, '#rows', 0, 'z_rules'); await shotEl(p, '#say', 0, 'z_say'); await shotEl(p, '#opts', 0, 'z_opts');
};
