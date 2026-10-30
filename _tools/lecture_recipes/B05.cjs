// B05 체험: 순서도 따라가며 끝 맞히기 — z_start(처음) · z_pick(짚은 뒤) · z_result(굴린 결과) · z_swap(글자가 뒤바뀐 판) · z_swapd(뒤바뀐 판의 순서도만)
// '이번 책' 칸부터 '순서도·버튼' 칸까지 한 컷으로 찍는다(이번 책 칩이 함께 보이게)
module.exports = async (p, { shot, shotEl, sleep }) => {
  await p.setViewport({ width: 780, height: 700, deviceScaleFactor: 2 }); await sleep(500);
  const grab = async n => {
    await sleep(400);
    const r = await p.evaluate(() => { const a = document.querySelector('section.face').getBoundingClientRect(), b = document.querySelector('.wrap').getBoundingClientRect(); return { x: 0, y: a.top + scrollY - 4, width: innerWidth, height: b.bottom - a.top + 8 }; });
    await p.screenshot({ path: `lecture/_shots/B05/${n}.png`, clip: r }); console.log(n);
  };
  // 같은 책(동화책)으로 원래 판과 글자가 바뀐 판을 찍는다
  const want = async (book, sw) => { for (let i = 0; i < 80; i++) { const bk = await p.$eval('.chip', e => e.textContent); const t = await p.$eval('#ynL', e => e.textContent); if (bk === book && (t === '아니요') === sw) return; await p.click('#next'); await sleep(150); } };
  await want('동화책', false);
  await grab('z_start');
  await p.click('#guessHand'); await sleep(200);
  await grab('z_pick');
  await p.click('#run'); await sleep(5200);
  await grab('z_result');
  await want('동화책', true);
  await p.click('#guessHand'); await sleep(200);
  await p.click('#run'); await sleep(5200);
  await grab('z_swap');
  await shotEl(p, '.diagram', 0, 'z_swapd');
};
