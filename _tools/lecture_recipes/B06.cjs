// B06 체험: 두 절차로 카드 찾기 견주기
// z_start 처음 · z_pick 예측 고른 뒤 · z_result 카드 줄 + 세 수 칸(확인한 수·빠뜨린 수)이 함께 보이는 컷
module.exports = async (p, { shot, shotEl, sleep }) => {
  await p.setViewport({ width: 780, height: 900, deviceScaleFactor: 2 }); await sleep(500);
  await p.addStyleTag({ content: 'nav,header,.fun-stamp,.fun-guide,.fun-say{display:none!important}' });
  const hide0 = await p.addStyleTag({ content: '#guess,#say{display:none!important}' }); await sleep(300);
  const r0 = await p.evaluate(() => { const a = document.querySelectorAll('section')[0].getBoundingClientRect(), b = document.querySelector('.cbox').parentElement.getBoundingClientRect(); return { x: a.left, y: a.top + scrollY, width: a.width, height: b.bottom - a.top + 6 }; });
  await p.screenshot({ path: 'lecture/_shots/B06/z_start.png', clip: r0 }); console.log('z_start');
  await hide0.evaluate(n => n.remove()); await sleep(200);
  await p.click('[data-g="1"]'); await sleep(300);
  await shotEl(p, 'section', 1, 'z_pick');
  await p.click('#run'); await sleep(4500);
  await shotEl(p, 'section', 1, 'z_count');
  await p.addStyleTag({ content: '#guess,#say{display:none!important}' }); await sleep(300);
  const r = await p.evaluate(() => { const a = document.querySelectorAll('section')[0].getBoundingClientRect(), b = document.querySelector('.cbox').parentElement.getBoundingClientRect(); return { x: a.left, y: a.top + scrollY, width: a.width, height: b.bottom - a.top + 6 }; });
  await p.screenshot({ path: 'lecture/_shots/B06/z_result.png', clip: r }); console.log('z_result');
};
