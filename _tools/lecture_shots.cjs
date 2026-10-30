// 강의교안용 체험 화면 캡처: node _tools/lecture_shots.cjs B01  → lecture/_shots/B01/{start,pick,result}.png (1280×800)
const puppeteer = require('C:/Users/권준구/projects/edudaum/node_modules/puppeteer-core');
const path = require('path'); const { pathToFileURL } = require('url');
const RECIPE = {
  B01: async p => { await shotEl(p, 'section', 0, 'z_start'); await p.click('[data-g="both"]'); await shot(p, 'pick'); await shotEl(p, 'section', 0, 'z_pick');
    for (let i = 0; i < 12; i++) { const t = await p.$('#tray button, #tray [role="button"], #tray .piece'); if (!t) break; await t.click(); await p.click(i % 2 ? '#drop-sw' : '#drop-hw').catch(() => {}); await sleep(120); }
    await p.click('#check').catch(() => {}); await sleep(900); await shotEl(p, 'section', 1, 'z_result'); },
};
const B = process.argv[2], OUT = path.resolve(`lecture/_shots/${B}`);
const sleep = ms => new Promise(r => setTimeout(r, ms));
let shot;
const shotEl = async (p, sel, i, n) => { await sleep(400); const els = await p.$$(sel); if (els[i]) { await els[i].screenshot({ path: `${OUT}/${n}.png` }); console.log(n); } };
(async () => {
  const b = await puppeteer.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', args: ['--allow-file-access-from-files', '--use-fake-ui-for-media-stream', '--use-fake-device-for-media-stream'] });
  const p = await b.newPage(); await p.setViewport({ width: 560, height: 980, deviceScaleFactor: 2 });
  shot = async (pg, n) => { await sleep(500); await pg.screenshot({ path: `${OUT}/${n}.png`, fullPage: true }); console.log(n); };
  await p.goto(pathToFileURL(path.resolve(`${B}/index.html`)).href, { waitUntil: 'load' }); await sleep(1200);
  await shot(p, 'start');
  if (RECIPE[B]) { await RECIPE[B](p); await shot(p, 'result'); }
  await b.close();
})();
