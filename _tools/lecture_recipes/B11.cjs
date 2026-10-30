// B11 체험: 흔들어 목표 수에 딱 멈추기 — 처음(목표·예상 고르기) · 예측 뒤(예상 고르고 몇 번 흔듦) · 결과(목표에서 멈춤)
// 폰 모양 세로 화면이라 안내 말풍선·도장을 숨기고, 두 구역(목표·손)을 가로 두 칸으로 놓아 핵심만 찍는다.
module.exports = async (p, { shot, shotEl, sleep }) => {
  await p.addStyleTag({ content: 'nav.nav,header,.fun-stamp,.fun-guide,.fun-say,.safe{display:none!important}.wrap{max-width:1040px!important;display:grid;grid-template-columns:1.25fr 1fr;gap:14px;padding:12px!important;align-items:start}.wrap>section{margin:0!important}.chip{font-size:20px!important}.btn{font-size:22px!important}.note,.say,.practice{font-size:20px!important}h2{font-size:22px!important}.goal b{font-size:44px!important}' });
  await p.setViewport({ width: 1100, height: 760, deviceScaleFactor: 2 });
  await sleep(500);
  await shotEl(p, '.wrap', 0, 'z_start');
  await p.click('[data-g="exact"]'); await sleep(200);
  for (let i = 0; i < 4; i++) { await p.click('#shake'); await sleep(120); }
  await shotEl(p, '.wrap', 0, 'z_pick');
  const goal = parseInt(await p.$eval('#goal', e => e.textContent), 10);
  for (let i = 4; i < goal; i++) { await p.click('#shake'); await sleep(120); }
  await sleep(300);
  await p.click('#stop'); await sleep(700);
  await shotEl(p, '.wrap', 0, 'z_result');
};
