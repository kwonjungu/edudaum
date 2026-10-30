// B07 체험: 순서 바꾸면 남는 그림 맞히기 — 처음 · 예측 뒤(보기 고름) · 결과
// 강의 장의 컷 틀이 820×430(가로세로비 1.907)이라 같은 비율로 찍는다. 다른 칸은 가려 빈 칸이 흰색으로 남게 한다.
const path = require('path');
module.exports = async (p, { shotEl, sleep }) => {
  const OUT = path.resolve('lecture/_shots/B07');
  const cap = async (i, name, padTop) => {
    await sleep(400);
    await p.evaluate(k => document.querySelectorAll('section').forEach((s, j) => { s.style.visibility = j === k ? 'visible' : 'hidden'; }), i);
    const b = await (await p.$$('section'))[i].boundingBox();
    const h = Math.round(b.width / 1.907);
    await p.screenshot({ path: `${OUT}/${name}.png`, clip: { x: b.x, y: b.y - padTop, width: b.width, height: h } });
    await p.evaluate(() => document.querySelectorAll('section').forEach(s => { s.style.visibility = 'visible'; }));
    console.log(name);
  };
  await cap(0, 'z_start', 0);
  await p.click('[data-g="heart"]'); await sleep(300);
  await cap(1, 'z_pick', 44);
  await p.click('#go'); await sleep(5200);
  await cap(0, 'z_result', 0);
};
