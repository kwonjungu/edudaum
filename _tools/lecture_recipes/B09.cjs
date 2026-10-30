// B09 체험: 몇 번 나타날까요 — 처음(반복 블록과 LED) · 예측 뒤(띠에서 짚음) · 결과(돌려 본 뒤 나타난 수)
// 과정안 활동3(횟수 3과 8 바꾸기)에 맞춰 반복 안에 ♥ 묶음 하나뿐인 홑 판(m=1, 겹침 없음)이 나올 때까지 '다음 판'을 누른다
module.exports = async (p, { shot, shotEl, sleep }) => {
  const want = async (n, nested) => {
    for (let k = 0; k < 800; k++) {
      const t = await p.$$eval('#code .blkline', e => e.map(x => x.textContent));
      const nn = parseInt((t[0].match(/\d+/) || [0])[0]);
      const isN = t.length === 3 && /^\[\d 번 반복\]/.test(t[1]);
      if (t.length === 2 && !isN && (n === 0 || nn === n)) return nn;
      await p.click('#next'); await sleep(30);
    }
    throw new Error('판을 못 찾음');
  };
  const N = await want(3);
  console.log('판', N);
  await shotEl(p, 'section', 0, 'z_start');
  await p.click(`#strip .c:nth-child(${N})`); await sleep(300);
  await shotEl(p, 'section', 1, 'z_pick');
  await p.click('#go'); await sleep(Math.ceil(N * 480 + 1500));
  await shotEl(p, 'section', 1, 'z_result');
  // 둘 중 하나용: [3 번 반복] 묶음, [8 번 반복] 묶음(체험 판은 5회까지라 글줄만 8로 바꾸어 찍는다)
  await want(3); await shotEl(p, '#code', 0, 'z_three');
  await p.$eval('#code .blkline', el => { el.textContent = '[8 번 반복]'; });
  await shotEl(p, '#code', 0, 'z_eight');
};
