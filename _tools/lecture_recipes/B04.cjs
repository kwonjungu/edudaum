// B04 로봇 셰프 레시피 고치기: 처음(z_start) → 동그라미 친 뒤(z_pick) → 로봇이 멈춘 곳(z_stop) → 고쳐서 완성(z_result)
module.exports = async (p, { shot, shotEl, sleep }) => {
  await shotEl(p, '#sheet', 0, 'z_start');
  await p.click('#cut-2'); await sleep(300); await shotEl(p, '#sheet', 0, 'z_pick');
  await p.click('#run'); await sleep(4500);
  await shotEl(p, '#sheet', 0, 'z_stop');
  const out0 = await p.$('#out'); if (out0) await out0.screenshot({ path: 'lecture/_shots/B04/z_stop_msg.png' });
  const done = () => p.$eval('#sheet', e => e.classList.contains('cooked'));
  const pairs = [[0,1],[1,2],[2,3],[0,2],[1,3],[0,3]];
  for (let r = 0; r < 40 && !(await done()); r++) {
    const [a, b] = pairs[r % pairs.length];
    await p.click('#cut-' + a).catch(()=>{}); await p.click('#cut-' + b).catch(()=>{}); await sleep(250);
    await p.click('#run').catch(()=>{}); await sleep(4200);
  }
  await sleep(600); await shotEl(p, '#sheet', 0, 'z_result');
  const out = await p.$('#out'); if (out) await out.screenshot({ path: 'lecture/_shots/B04/z_result_msg.png' });
};
