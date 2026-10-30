module.exports = async (p, { shot, shotEl, sleep }) => {
  await shotEl(p, 'section', 0, 'z_start');
  await p.click('#plus').catch(() => {}); await sleep(100);
  for (let i = 0; i < 5; i++) { await p.click('#plus'); await sleep(60); }
  await sleep(300);
  await shotEl(p, 'section', 1, 'z_pick');
  await p.click('#pick'); await sleep(300);
  for (let i = 0; i < 5; i++) { await p.click('#shake').catch(() => {}); await sleep(900); }
  await sleep(900);
  await shotEl(p, 'section', 1, 'z_result');
  await shotEl(p, 'section', 0, 'z_led');
};
