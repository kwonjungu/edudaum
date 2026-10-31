// B16 체험: 짝 가르기 — z_start(처음) · z_pick(두 장 칸 짚은 뒤) · z_result(확인 뒤)
// start·pick은 카드 두 장(.pair)부터 아래 안내 줄(.key)까지, result는 카드 두 장부터 확인 칸(#msg)까지(단추 줄은 뺌). 화면 폭 600에 글자를 키워 장 틀에서 18px 이상.
module.exports = async (p, { shot, shotEl, sleep }) => {
  await p.setViewport({ width: 600, height: 900, deviceScaleFactor: 2.5 });
  await p.addStyleTag({ content: '[class*="fun-"]{display:none!important} .note,nav,header,.lead{display:none} main{max-width:none} .ask{display:none} .name{font-size:21px} .sensor{font-size:14px} .bin{font-size:21px;min-height:48px} .key{font-size:19px} .case{font-size:18px} .fb,.why{font-size:18px} #msg{font-size:18px} #confirmBtn{font-size:19px}' });
  const grab = async (n, endSel) => {
    await sleep(600);
    const r = await p.evaluate(e => { const a = document.querySelector('.pair').getBoundingClientRect(), b = document.querySelector(e).getBoundingClientRect(); return { x: 0, y: a.top + scrollY - 14, width: innerWidth, height: b.bottom - a.top + 28 }; }, endSel);
    await p.screenshot({ path: `lecture/_shots/B16/${n}.png`, clip: r, captureBeyondViewport: true }); console.log(n);
  };
  await grab('z_start', '.key');
  await p.click('.case:nth-child(1) .bin[data-k="m"]'); await sleep(200);
  await p.click('.case:nth-child(2) .bin[data-k="a"]'); await sleep(200);
  await grab('z_pick', '.key');
  await p.click('#confirmBtn'); await sleep(2500);
  await p.addStyleTag({ content: '.key{display:none} #confirmBtn{display:none} .btn{display:none}' }); await grab('z_result', 'section:nth-of-type(2)');
};
