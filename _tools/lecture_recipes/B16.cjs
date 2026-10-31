// B16 체험: 짝 가르기 — z_start(처음) · z_pick(두 장 칸 짚은 뒤) · z_result(확인 뒤)
// 질문 줄(.ask)부터 안내 줄(#msg)까지만 찍는다. 이름표·진행 줄·단추 줄은 뺀다. 화면 폭을 좁혀 글자를 키운다.
module.exports = async (p, { shot, shotEl, sleep }) => {
  await p.setViewport({ width: 760, height: 900, deviceScaleFactor: 2.5 });
  await p.addStyleTag({ content: '.fun-stamp,.fun-guide,.fun-say,[class*="fun-"]{display:none!important} .note,nav,header,.lead{display:none} main{max-width:none} .key{font-size:15px}' });
  const grab = async n => {
    await sleep(600);
    const r = await p.evaluate(() => { const a = document.querySelector('.ask').getBoundingClientRect(), b = document.querySelector('#msg').getBoundingClientRect(); return { x: 0, y: a.top + scrollY - 4, width: innerWidth, height: b.bottom - a.top + 8 }; });
    await p.screenshot({ path: `lecture/_shots/B16/${n}.png`, clip: r, captureBeyondViewport: true }); console.log(n);
  };
  await grab('z_start');
  await p.click('.case:nth-child(1) .bin[data-k="m"]'); await sleep(200);
  await p.click('.case:nth-child(2) .bin[data-k="a"]'); await sleep(200);
  await grab('z_pick');
  await p.click('#confirmBtn'); await sleep(2500);
  await grab('z_result');
};
