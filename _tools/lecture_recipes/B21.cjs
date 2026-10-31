// B21 체험: 질문 다섯 번에 동물 찾기 — z_start(처음, 예측 앞) · z_pick(예측하고 질문 두 번) · z_result(끝)
// 위 예측 줄 아래로 후보 구역(왼쪽)과 질문·지나온 길(오른쪽)을 두 열로 바꿔 가로 컷으로 찍는다.
const AT = { '강아지':[0,0,1,0,1,0],'상어':[0,1,0,0,0,1],'나비':[1,0,0,1,0,0],'기린':[0,0,1,0,0,1],'닭':[1,0,0,0,1,0],'여우':[0,0,1,0,0,0],'고래':[0,1,0,0,0,1],'고양이':[0,0,1,0,1,0],'벌':[1,0,0,1,1,0],'코끼리':[0,0,1,0,0,1],'문어':[0,1,0,0,0,0],'말':[0,0,1,0,1,1],'독수리':[1,0,0,0,0,0],'다람쥐':[0,0,1,0,0,0],'열대어':[0,1,0,0,1,0],'소':[0,0,1,0,1,1] };
module.exports = async (p, { shot, shotEl, sleep }) => {
  await p.setViewport({ width: 1180, height: 900, deviceScaleFactor: 1.6 });
  await p.addStyleTag({ content: '[class*="fun-"]{display:none!important} nav,header,.tools{display:none!important} body{background:#fff} .wrap{max-width:1140px;display:grid;grid-template-columns:1.25fr 1fr;gap:12px;padding:10px} #predBox{grid-column:1/3;margin-top:0} .wrap>section{margin-top:0} .wrap>section:nth-of-type(2){grid-row:2/4} .pool{grid-template-columns:repeat(4,1fr)} .an .em{width:64px;height:64px} .an{font-size:15px} .q{min-height:42px;padding:6px 12px} h2{font-size:17px}' });
  const clk = sel => p.evaluate(s => document.querySelector(s).click(), sel);
  // 후보가 많은 판(11~12마리)이 나올 때까지 다음 판
  for (let i = 0; i < 40; i++) { const n = await p.$$eval('#pool .an', e => e.length); if (n >= 11) break; await clk('#next'); await sleep(120); }
  const grab = async n => {
    await sleep(500);
    const r = await p.evaluate(() => { const w = document.querySelector('.wrap'); const x = w.getBoundingClientRect(); return { x: x.left + scrollX, y: x.top + scrollY, width: x.width, height: x.height }; });
    await p.screenshot({ path: `lecture/_shots/B21/${n}.png`, clip: r, captureBeyondViewport: true }); console.log(n);
  };
  await grab('z_start');
  await clk('#pred .btn:nth-child(4)'); await sleep(200);
  const step = async () => {
    const info = await p.evaluate(() => ({
      alive: [...document.querySelectorAll('#pool .an')].filter(e => !e.classList.contains('gone')).map(e => e.querySelector('.nm').textContent),
      qs: [...document.querySelectorAll('#qs .q')].map(b => b.disabled)
    }));
    const n = info.alive.length; const map = [1, 2, 3, 4, 5, 6]; // 질문 순서 = 날개·물속·다리4·다리6·기름·큼 → AT 열 0~5
    let best = -1, bd = 1e9;
    info.qs.forEach((dis, k) => { if (dis) return; const y = info.alive.filter(nm => AT[nm][k]).length; if (y === 0 || y === n) return; const d = Math.abs(y - n / 2); if (d < bd) { bd = d; best = k; } });
    if (best < 0) return false;
    await clk(`#qs .q:nth-child(${best + 1})`); await sleep(250); return true;
  };
  await step(); await step();
  await grab('z_pick');
  for (let i = 0; i < 4; i++) { if (!(await step())) break; }
  await sleep(600);
  await grab('z_result');
};
