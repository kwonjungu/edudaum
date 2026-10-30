// B02 체험: 가장 자주 걸린 기준 짚기 (표 9칸 채우기 → ✕ 많을 기준 예측 → 세로로 보기)
module.exports = async (p, { shot, shotEl, sleep }) => {
  await shotEl(p, 'section', 0, 'z_start');
  // 표시: 기준1(순서를 말할 수 있나)에 ✕가 두 칸 모이게. 칸을 누를 때마다 빈칸→O→△→✕
  const X = { '0,0': 1, '0,1': 2, '0,2': 1, '1,0': 3, '1,1': 3, '1,2': 1, '2,0': 1, '2,1': 2, '2,2': 3 };
  // 값: 1=O 2=△ 3=✕ (누른 횟수)
  for (const [k, n] of Object.entries(X)) {
    const [c, d] = k.split(',');
    for (let i = 0; i < n; i++) { await p.click(`button.mark[data-crit="${c}"][data-cand="${d}"]`); await sleep(40); }
  }
  await p.click('#guess .gb:nth-child(2)'); await sleep(300);
  await shotEl(p, 'section', 0, 'z_pick');
  await p.click('#flip'); await sleep(900);
  await shotEl(p, 'section', 0, 'z_result');
};
