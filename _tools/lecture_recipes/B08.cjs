module.exports = async (p, { shot, shotEl, sleep }) => {
  for (let k = 0; k < 40; k++) { const t = await p.$eval('#rule', e => e.textContent); if (t.includes('10과 같거나')) break; await p.click('#next'); await sleep(60); }
  await shotEl(p, 'section', 0, 'z_start');
  await p.click('#strip .c:nth-child(11)').catch(() => {}); await sleep(300);
  await shotEl(p, 'section', 0, 'z_pick');
  for (let i = 0; i < 9; i++) { await p.click('#left'); await sleep(60); }
  await p.click('#right'); await sleep(250);
  await p.click('#left'); await sleep(60); await p.click('#right'); await sleep(900);
  await shotEl(p, 'section', 0, 'z_result');
  await shotEl(p, 'section', 1, 'z_led');
};
