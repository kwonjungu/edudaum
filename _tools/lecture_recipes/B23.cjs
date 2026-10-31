// B23 체험: 기록 간격 비교하기 — z_start(처음) · z_pick(막대 짚은 뒤) · z_result(30초 기록 확인 뒤)
// 누리집 체험 쪽 첫 판(7칸, 0~60초)과 같은 판이 나올 때까지 #nextBtn. 막대 칸만 크게(글 20px 이상), 결과 문장은 막대 아래에 같이.
module.exports = async (p, { shot, shotEl, sleep }) => {
  await p.setViewport({ width: 720, height: 700, deviceScaleFactor: 2 });
  const CSS = '[class*="fun-"]{display:none!important} nav,header,.foot,.acts,#h3t,#s2>h2{display:none!important} .wrap{max-width:720px;padding:46px 10px 8px;background:#fff} section{margin-top:0;box-shadow:none;border:0;padding:2px 0} section.off{opacity:1} #s3{margin-top:2px} #s3.hid{visibility:hidden} .hint{font-size:22px;font-weight:600;color:#222;line-height:1.3} .t{font-size:21px;font-weight:700;color:#222} .key{font-size:20px;color:#222;margin-top:4px} .key span::before{width:20px;height:14px} .walk{font-size:20px;color:#222;margin-top:4px} .walk svg{height:26px} .chart{margin-top:4px;gap:3px} .bar{height:32px;min-height:32px} .say{font-size:25px;line-height:1.3;margin-top:2px} .rowb{grid-template-columns:2.6em 1fr}';
  await p.addStyleTag({ content: CSS });
  const clk = sel => p.evaluate(s => document.querySelector(s).click(), sel);
  const vals = () => p.evaluate(() => [...document.querySelectorAll('#chart10 .bar')].map(b => parseFloat(b.querySelector('i').style.width)));
  // 7칸이면서 가운데가 눈에 띄게 튀는 판(30초 기록이 크게 놓치는 곳이 있는 판)을 찾는다
  let best = -1;
  for (let i = 0; i < 80; i++) {
    const v = await vals(); const n = v.length; let m = -1, bi = -1;
    for (let k = 0; k < n; k++) { if (k % 3 === 0) continue; const a = k - (k % 3), b = a + 3; const l = b < n ? v[a] + (v[b] - v[a]) * (k - a) / 3 : v[a]; const d = Math.abs(v[k] - l); if (d > m) { m = d; bi = k; } }
    if (m > 18 && n === 7) { best = bi; break; }
    await p.reload({ waitUntil: 'load' }); await sleep(300); await p.addStyleTag({ content: CSS });
  }
  if (best < 0) throw new Error('7칸 판을 못 찾음');
  await p.evaluate(() => document.getElementById('s3').classList.add('hid'));
  const grab = async n => { await sleep(500); await shotEl(p, '.wrap', 0, n); };
  await grab('z_start');
  await p.evaluate(k => document.querySelectorAll('#chart10 .bar')[k].click(), best); await sleep(250);
  await grab('z_pick');
  await clk('#checkBtn'); await sleep(1200);
  await p.evaluate(() => document.getElementById('s3').classList.remove('hid')); await sleep(200);
  await grab('z_result');
};
