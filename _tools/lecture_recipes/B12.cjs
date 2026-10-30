// B12 체험: 보내기 전 수신 화면 맞히기 — 처음(약속표·코드·수신 화면) · 예측 뒤(보기 고름) · 결과(A 누른 뒤 수신 화면과 확인 말)
module.exports = async (p, { shot, shotEl, sleep }) => {
  await shotEl(p, 'section', 0, 'z_start');
  await p.click('#picks .pk'); await sleep(300);
  await shotEl(p, 'section', 1, 'z_pick');
  await p.click('#send'); await sleep(1800);
  await shotEl(p, 'section', 0, 'z_result');
  await shotEl(p, 'section', 1, 'z_result2');
};
