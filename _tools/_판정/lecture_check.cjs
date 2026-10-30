// 강의교안 점검: node _tools/_판정/lecture_check.cjs B01 → 오류·바깥 요청·장 수·말풍선 최소 글자·넘침
const puppeteer = require('C:/Users/권준구/projects/edudaum/node_modules/puppeteer-core');
const path = require('path'); const { pathToFileURL } = require('url');
(async () => {
  const B = process.argv[2]; const res = { block: B, errors: [], external: [], slides: 0, small: [], overflow: [] };
  const b = await puppeteer.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', args: ['--allow-file-access-from-files'] });
  const p = await b.newPage(); await p.setViewport({ width: 1280, height: 720 });
  p.on('pageerror', e => res.errors.push(e.message.slice(0, 120)));
  p.on('console', m => { if (m.type() === 'error') res.errors.push(m.text().slice(0, 120)); });
  p.on('requestfailed', r => res.errors.push('없는 파일: ' + decodeURIComponent(r.url()).split('/').slice(-3).join('/')));
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
  // 금지어·시간 표시(분·초)
  // 활동지 쪽: 새 판 PDF 쪽 수(ws_pages.json)보다 큰 쪽을 가리키면 잡는다
  const wsN = (JSON.parse(require('fs').readFileSync(__dirname + '/ws_pages.json', 'utf8')))[B];
  res.wspage = wsN ? await p.evaluate(n => [...document.querySelectorAll('.s')].flatMap((s, i) => [...s.textContent.matchAll(/활동지\s*(\d+)\s*쪽/g)].filter(m => +m[1] > n).map(m => (i + 1) + ':' + m[0])), wsN) : [];
  res.words = await p.evaluate(() => [...document.querySelectorAll('.s')].flatMap((s, i) => (s.textContent.match(/맞았어요|틀렸어요|잘했어요|정답|오답|대단해요|점수|등수|(?<![가-힣])[한두세네]\s*시간(?![표씩])|\d+\s*(?:분|초)\s*(?:동안|간\b|안에|이내|만에|씩|짜리|발표|말하기|인터뷰|설명|토의|활동)|\(\s*\d+\s*분\s*\)/g) || []).map(w => (i + 1) + ':' + w)));
  // 원고의 words_ok: 학습 내용 속 값(과정안 예시 등)은 예외로 둔다
  try { const ok = JSON.parse(require('fs').readFileSync(`lecture/_src/${B}.json`, 'utf8')).words_ok || []; res.words = res.words.filter(w => !ok.some(o => w.endsWith(':' + o) || w.split(':')[1] && o.includes(w.split(':')[1]))); } catch (e) {}
  console.log(JSON.stringify(res)); await b.close();
})();
