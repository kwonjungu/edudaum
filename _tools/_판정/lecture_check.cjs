// 강의교안 점검: node _tools/_판정/lecture_check.cjs B01 → 오류·바깥 요청·장 수·말풍선 최소 글자·넘침
const puppeteer = require('C:/Users/권준구/projects/edudaum/node_modules/puppeteer-core');
const path = require('path'); const { pathToFileURL } = require('url');
(async () => {
  const B = process.argv[2]; const res = { block: B, errors: [], external: [], slides: 0, small: [], overflow: [] };
  const b = await puppeteer.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', args: ['--allow-file-access-from-files'] });
  const p = await b.newPage(); await p.setViewport({ width: 1280, height: 720 });
  p.on('pageerror', e => res.errors.push(e.message.slice(0, 120)));
  p.on('console', m => { if (m.type() === 'error') res.errors.push(m.text().slice(0, 120)); });
  p.on('request', r => { const u = r.url(); if (!u.startsWith('file:') && !u.startsWith('data:')) res.external.push(u.slice(0, 80)); });
  await p.goto(pathToFileURL(path.resolve(`lecture/${B}/index.html`)).href, { waitUntil: 'networkidle0' });
  res.slides = await p.$$eval('.s', x => x.length);
  for (let i = 0; i < 200; i++) { await p.keyboard.press('ArrowRight'); }
  const r = await p.evaluate(() => {
    const out = { small: [], overflow: [] };
    document.querySelectorAll('.s').forEach((s, i) => {
      s.style.display = 'flex'; s.style.transform = 'none'; s.style.position = 'relative'; s.style.left = '0'; s.style.top = '0';
      s.querySelectorAll('[data-step]').forEach(x => x.classList.remove('hide'));
      const R = s.getBoundingClientRect();
      s.querySelectorAll('.talk, .todo, .q, .memo, .wrapq li, .mq').forEach(t => { const fs = parseFloat(getComputedStyle(t).fontSize); if (fs < 24) out.small.push((i + 1) + ':' + fs); });
      s.querySelectorAll('.bub, .memo, .col, .mcard, .opts, .go, .pic, .zoom, .flip, .oc, .side, .sheet').forEach(t => { const b = t.getBoundingClientRect(); if (b.bottom > R.bottom - 50 || b.right > R.right + 1) out.overflow.push((i + 1) + ':' + t.className); });
      s.querySelectorAll('.memo, .prep li, .talk, .wraprow li, .mq, .todo, .q').forEach(t => { if (t.scrollHeight > t.clientHeight + 2 || (!t.classList.contains('talk') && t.scrollWidth > t.clientWidth + 2)) out.overflow.push((i + 1) + ':clip:' + t.className); });
      const bubs = [...s.querySelectorAll('.bub')].map(x => x.querySelector('.talk').getBoundingClientRect());
      s.querySelectorAll('.zoom, .flip, .pic, .sheet, .oc, .side').forEach(t => { const r = t.getBoundingClientRect(); bubs.forEach(q => { const ox = Math.min(r.right, q.right) - Math.max(r.left, q.left), oy = Math.min(r.bottom, q.bottom) - Math.max(r.top, q.top); if (ox > 8 && oy > 8) out.overflow.push((i + 1) + ':cover:' + t.className); }); });
      [...s.children].forEach(ch => { if (ch.scrollHeight > ch.clientHeight + 4 && getComputedStyle(ch).overflow === 'visible' && !ch.classList.contains('grass')) out.overflow.push((i + 1) + ':shrunk:' + ch.className); });
      s.querySelectorAll('.col, .mcard').forEach(c => { const cb = c.getBoundingClientRect(); [...c.children].forEach(ch => { const b = ch.getBoundingClientRect(); if (b.bottom > cb.bottom + 2) out.overflow.push((i + 1) + ':outofcol:' + ch.className); }); });
      s.style.display = ''; s.style.position = ''; s.style.left = ''; s.style.top = '';
    });
    return out;
  });
  res.small = r.small; res.overflow = [...new Set(r.overflow)];
  console.log(JSON.stringify(res)); await b.close();
})();
