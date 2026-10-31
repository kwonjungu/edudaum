// B26 체험: 원인 짚고 한 부분만 고치기 — z_start(처음) · z_pick(원인 카드 짚은 뒤) · z_result(다시 시험 뒤)
// 위(시험 기록)·아래(원인 카드) 두 section을 2열로 놓고 .wrap 한 컷. 원인은 근거 세 줄을 읽고 고른다.
module.exports = async (p, { shot, shotEl, sleep }) => {
  await p.setViewport({ width: 1100, height: 700, deviceScaleFactor: 2 });
  await p.addStyleTag({ content: '[class*="fun-"]{display:none!important} nav,header,.foot,.acts #next,.acts #reset,.note:last-child{display:none!important} .wrap{max-width:1040px;display:grid;grid-template-columns:1.1fr 1fr;gap:12px;padding:10px;align-items:start} .wrap>section{margin-top:0}' });
  await sleep(900);
  await shotEl(p, '.wrap', 0, 'z_start');
  const idx = await p.evaluate(() => {
    const rows = [...document.querySelectorAll('#ev .row')].map(r => r.textContent);
    if (/샘플 0개/.test(rows[0])) return 0;
    if (!/헷갈림 없음/.test(rows[1])) return 1;
    return 2;
  });
  console.log('pick', idx);
  await p.evaluate(i => document.querySelectorAll('#fix .btn')[i].click(), idx);
  await sleep(400);
  await shotEl(p, '.wrap', 0, 'z_pick');
  await p.evaluate(() => document.getElementById('retest').click());
  await sleep(1500);
  await shotEl(p, '.wrap', 0, 'z_result');
};
