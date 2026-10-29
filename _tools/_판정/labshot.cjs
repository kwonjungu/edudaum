// 실험실 쪽 점검: node _tools/_판정/labshot.cjs chart "스크립트(JS, 쪽 안에서 실행)"  → 오류·넘침·금지말 JSON + 430/1280 사진
const puppeteer = require('C:/Users/권준구/projects/edudaum/node_modules/puppeteer-core');
const [,, P, ACT = ''] = process.argv; const OUT = 'C:/Users/권준구/projects/edudaum/_tools/_판정/shots';
const BAN = /맞았어요|틀렸어요|잘했어요|정답|오답|대단해요|점수|등수/;
(async () => {
  const b = await puppeteer.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe',
    args: ['--allow-file-access-from-files', '--use-fake-ui-for-media-stream', '--use-fake-device-for-media-stream'] });
  const res = { page: P, errors: [], external: [], overflow: {}, banned: [] };
  try {
    for (const w of [360, 1280]) {
      const p = await b.newPage(); await p.setViewport({ width: w, height: 900 });
      p.on('pageerror', e => res.errors.push(`${w}:${e.message}`.slice(0, 200)));
      p.on('console', m => { if (m.type() === 'error') res.errors.push(`${w}:${m.text()}`.slice(0, 200)); });
      p.on('requestfailed', r => res.errors.push(`${w}:FAIL ${r.url().slice(-60)}`));
      p.on('request', r => { const u = r.url(); if (!/^(file|data|blob):/.test(u)) res.external.push(u.slice(0, 80)); });
      await p.goto('file:///C:/Users/권준구/projects/edudaum/lab/' + P + '/index.html', { waitUntil: 'load' });
      await new Promise(r => setTimeout(r, 600));
      if (ACT) { try { res['act' + w] = await p.evaluate(ACT); } catch (e) { res.errors.push(`${w}:ACT ${e.message}`.slice(0, 200)); } }
      await new Promise(r => setTimeout(r, 900));
      res.overflow[w] = await p.evaluate(() => document.documentElement.scrollWidth - innerWidth);
      const m = (await p.evaluate(() => document.body.innerText)).match(BAN); if (m) res.banned.push(`${w}:${m[0]}`);
      await p.screenshot({ path: `${OUT}/lab_${P}_${w}.png`, fullPage: true });
      await p.close();
    }
  } finally { await b.close(); }
  res.external = [...new Set(res.external)]; console.log(JSON.stringify(res));
})();
