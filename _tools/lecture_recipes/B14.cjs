// B14 체험: 드러난 개인정보 찾기 — 처음(예시 네 칸) · 예측 뒤(칸 고름) · 결과(확인 말)
module.exports = async (p, { shot, shotEl, sleep }) => {
  await p.addStyleTag({ content: 'nav.nav,header{display:none!important}.wrap{max-width:1040px!important;display:grid;grid-template-columns:1fr 1fr;gap:12px;padding:12px!important;align-items:start}.wrap>section{margin:0!important}#scene{max-width:420px!important}.zlabel{font-size:12px!important}.zval{font-size:15px!important}.pk,.btn{font-size:20px!important}.status{font-size:20px!important}h2{font-size:18px!important}.note{font-size:17px!important}.fun-stamp,.fun-guide,.fun-say{display:none!important}' });
  await p.setViewport({ width: 1100, height: 700, deviceScaleFactor: 2 });
  await sleep(500);
  await shotEl(p, '.wrap', 0, 'z_start');
  await p.click('#picks .pk:nth-child(2)'); await sleep(300);
  await shotEl(p, '.wrap', 0, 'z_pick');
  await p.click('#checkBtn'); await sleep(900);
  await p.addStyleTag({ content: '.fun-stamp,.fun-guide,.fun-say,[class*=fun-]{visibility:hidden!important}' });
  await shotEl(p, '.wrap', 0, 'z_result');
};
