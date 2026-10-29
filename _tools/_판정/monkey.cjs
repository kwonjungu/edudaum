// 남은 블록 직접 판정용 점검: node _tools/_판정/monkey.cjs BXX  → JSON 한 줄(오류·넘침·금지말·외부요청·도장) + 430px 사진
const puppeteer = require('C:/Users/권준구/projects/edudaum/node_modules/puppeteer-core');
const B = process.argv[2]; const OUT = 'C:/Users/권준구/projects/edudaum/_tools/_판정/shots';
const BAN = /맞았어요|틀렸어요|잘했어요|정답|오답|대단해요|점수|등수/;
(async () => {
  const b = await puppeteer.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe',
    args: ['--use-fake-ui-for-media-stream', '--use-fake-device-for-media-stream'] });
  const res = { block: B, errors: [], external: [], overflow: {}, banned: [], fun: false, stamped: false, clicks: 0 };
  try {
    for (const w of [360, 430, 1280]) {
      const p = await b.newPage(); await p.setViewport({ width: w, height: 900 });
      p.on('pageerror', e => res.errors.push(`${w}:${e.message}`.slice(0, 160)));
      p.on('console', m => { if (m.type() === 'error') res.errors.push(`${w}:${m.text()}`.slice(0, 160)); });
      p.on('request', r => { const u = r.url(); if (!u.startsWith('http://127.0.0.1') && !u.startsWith('data:') && !u.startsWith('blob:')) res.external.push(u.slice(0, 80)); });
      await p.goto(`http://127.0.0.1:8790/${B}/`, { waitUntil: 'networkidle0' });
      res.fun = res.fun || await p.evaluate(() => !!document.querySelector('.fun-guide') && !!window.Fun);
      for (let i = 0; i < 60; i++) {                      // 보이는 단추·칸을 무작위로 누른다
        const ok = await p.evaluate(() => {
          const els = [...document.querySelectorAll('button:not([disabled]):not(.topnav *), [role=button], input[type=range]')].filter(e => e.offsetParent && !e.closest('.topnav, nav, a'));
          if (!els.length) return false; const e = els[Math.floor(Math.random() * els.length)];
          if (e.type === 'range') { e.value = Math.floor(Math.random() * (+e.max || 10)); e.dispatchEvent(new Event('input', { bubbles: true })); }
          else e.click(); return true;
        });
        if (!ok) break; res.clicks++; await new Promise(r => setTimeout(r, 120));
      }
      await new Promise(r => setTimeout(r, 1500));
      res.overflow[w] = await p.evaluate(() => document.documentElement.scrollWidth - innerWidth);
      const txt = await p.evaluate(() => document.body.innerText);
      const m = txt.match(BAN); if (m) res.banned.push(`${w}:${m[0]}`);
      res.stamped = res.stamped || await p.evaluate(() => !!(localStorage.getItem('edudaum.stamps') || '').includes(location.pathname.match(/B\d\d/)[0]));
      if (w === 430) await p.screenshot({ path: `${OUT}/${B}_me_430.png`, fullPage: true });
      await p.close();
    }
  } finally { await b.close(); }
  res.external = [...new Set(res.external)]; console.log(JSON.stringify(res));
})();
