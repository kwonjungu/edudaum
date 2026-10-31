// B17 체험: 하나만 바꿔 알아보게 하기 — z_start(처음) · z_pick(조건 하나 고르고 예상) · z_result(확인한 뒤)
module.exports = async (p, { shot, shotEl, sleep }) => {
  await p.setViewport({ width: 720, height: 1000, deviceScaleFactor: 2 });
  await p.addStyleTag({ content: '[class*="fun-"]{display:none!important} nav,.topnav,header,h1,.lead{display:none!important} body{background:#fff!important} main{padding-top:8px!important}' });
  const grab = async n => {
    await sleep(500);
    const r = await p.evaluate(() => { const x = document.querySelector('main section').getBoundingClientRect(); return { x: Math.max(0, x.left - 6), y: x.top + scrollY - 6, width: x.width + 12, height: x.height + 12 }; });
    await p.screenshot({ path: `lecture/_shots/B17/${n}.png`, clip: r }); console.log(n);
  };
  await grab('z_start');
  await p.click('.tab[data-c="dist"]'); await sleep(300);
  await p.evaluate(() => { const r = document.getElementById('rng'); r.value = 3; r.dispatchEvent(new Event('input', { bubbles: true })); r.dispatchEvent(new Event('change', { bubbles: true })); });
  await p.click('.gbtn[data-g="short"]'); await sleep(300);
  await grab('z_pick');
  await p.click('#confirmBtn'); await sleep(900);
  await grab('z_result');
};
