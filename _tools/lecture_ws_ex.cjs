// 활동지 예시 답 판 만들기: node _tools/lecture_ws_ex.cjs B01 [--noshot]
// 원본 활동지 html(읽기만)에 lecture/_src/ans/BXX.json 답을 넣고, lecture_ws.cjs와 같은 요소·같은 크기로
// ws_actK_ex.png, ws_actK_J_ex.png를 찍는다. 넘침·빈칸·금지어를 함께 점검해 _ex_check.json에 남긴다.
const puppeteer = require('C:/Users/권준구/projects/edudaum/node_modules/puppeteer-core');
const path = require('path'); const fs = require('fs'); const { pathToFileURL } = require('url');
const B = process.argv[2]; const NOSHOT = process.argv.includes('--noshot');
const SRC = `C:/Users/권준구/Desktop/에듀다움_책만들기/work/ws/html/${B}.html`;
const ROOT = 'C:/Users/권준구/projects/edudaum';
const OUT = path.resolve(`${ROOT}/lecture/_shots/${B}`); fs.mkdirSync(OUT, { recursive: true });
const ANS = JSON.parse(fs.readFileSync(`${ROOT}/lecture/_src/ans/${B}.json`, 'utf8'));
const FIND = fs.readFileSync(path.join(__dirname, 'ws_cells_find.js'), 'utf8');
(async () => {
  const b = await puppeteer.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', args: ['--allow-file-access-from-files'] });
  const p = await b.newPage(); await p.emulateMediaType('print'); await p.setViewport({ width: 680, height: 983, deviceScaleFactor: 2.5 });
  await p.goto(pathToFileURL(SRC).href, { waitUntil: 'networkidle0' }); await p.evaluate(() => document.fonts.ready);
  await p.addScriptTag({ content: FIND });
  const res = await p.evaluate((ans) => {
    const st = document.createElement('style');
    st.textContent = `.ans{color:#1d4ed8;font-weight:600;font-size:10.5pt;line-height:1.35;letter-spacing:-0.2px;word-break:keep-all}
      td>.ans{display:block;padding:0.6mm 1mm;text-align:left}
      .lines>.ans{display:block;padding:0 1.5mm;line-height:var(--lh,8.6mm)}
      .blank>.ans{white-space:nowrap;padding-left:1mm;position:relative;top:-0.8mm}
      .pick i.ansp{outline:0.6mm solid #1d4ed8;outline-offset:0.4mm;border-radius:2mm;color:#1d4ed8;font-weight:700}
      .exbadge{position:absolute;right:16mm;top:1.5mm;background:#1d4ed8;color:#fff;font-size:9pt;font-weight:700;padding:0.5mm 2.2mm;border-radius:2mm;z-index:5}
      .exbadge.open{background:#fff;color:#1d4ed8;border:0.35mm solid #1d4ed8;right:36mm}`;
    document.head.appendChild(st);
    const cells = window.__wsCells(); const miss = [], over = [], bad = [];
    const BAN = /정답|오답|맞았어요|틀렸어요|·|→|\[확인 필요\]/;
    for (const c of cells) {
      const id = c.info.id; const v = ans.cells[id];
      if (v === undefined) { miss.push(id); continue; }
      if (v === '') continue;
      if (BAN.test(v) && c.kind !== 'pick') bad.push(id + ' ' + v);
      if (c.kind === 'pick') {
        for (const one of String(v).split('|')) {
          const opt = [...c.el.querySelectorAll('i')].find(i => i.innerText.trim() === one.trim());
          if (opt) opt.classList.add('ansp'); else bad.push(id + ' 고르기에 없는 값: ' + one);
        }
        continue;
      }
      const sp = document.createElement('span'); sp.className = 'ans'; sp.textContent = v;
      const host = c.el;
      const mode = c.info.mode;
      if (mode === 'prefix') { sp.style.display = 'inline'; sp.style.padding = '0 1mm 0 0'; host.insertBefore(sp, host.firstChild); continue; }
      if (mode === 'suffix') { sp.style.display = 'inline'; sp.style.padding = '0 0 0 1mm'; host.appendChild(sp); continue; }
      if (mode === 'replace') { sp.style.whiteSpace = 'pre-line'; sp.style.lineHeight = '7.2mm'; sp.style.padding = '0'; host.innerHTML = ''; host.appendChild(sp); }
      else if (c.info.keep) { sp.style.display = 'inline'; sp.style.padding = '0 0 0 1mm'; const f = host.querySelector('span'); if (f) host.insertBefore(sp, f); else host.appendChild(sp); }
      else if (host.matches('td')) { host.innerHTML = ''; host.appendChild(sp); }
      else if (host.matches('.blank')) { host.innerHTML = ''; host.appendChild(sp); }
      else { host.innerHTML = ''; host.appendChild(sp); }
      const r = host.getBoundingClientRect(), s = sp.getBoundingClientRect();
      const cs = getComputedStyle(host);
      const limH = host.matches('td') ? parseFloat(c.info.hmm) * 3.78 + 2 : r.height + 2;
      if ((!host.matches('.blank') && s.height > limH + 1) || s.width > r.width + 2 || sp.scrollWidth > sp.clientWidth + 2) over.push(`${id} 칸 ${Math.round(r.width)}×${Math.round(limH)} 글 ${Math.round(s.width)}×${Math.round(s.height)}: ${v}`);
    }
    // 섹션마다 예시 띠
    const secs = [...document.querySelectorAll('section.act, section.review')];
    secs.forEach((s, i) => { s.style.position = 'relative'; const t = document.createElement('span'); t.className = 'exbadge'; t.textContent = '예시 답'; s.appendChild(t);
      if ((ans.open || []).includes(i + 1)) { const o = document.createElement('span'); o.className = 'exbadge open'; o.textContent = '다른 답도 돼요'; s.appendChild(o); } });
    return { n: cells.length, filled: cells.filter(c => ans.cells[c.info.id]).length, miss, over, bad };
  }, ANS);
  // 표 줄 높이가 늘었는지(원본 대비) 확인: 빈 판 목록과 견준다
  const list = [];
  if (!NOSHOT) {
    const secs = await p.$$('section.act, section.review'); let k = 0;
    for (const s of secs) {
      k++; await s.screenshot({ path: `${OUT}/ws_act${k}_ex.png` });
      const parts = await s.$$(':scope > table, :scope > .box, :scope > .two, :scope > div.lines, :scope > ul, :scope > table + p.say');
      let j = 0; for (const el of parts) { j++; await el.screenshot({ path: `${OUT}/ws_act${k}_${j}_ex.png` }); }
      list.push(k);
    }
  }
  fs.writeFileSync(`${OUT}/_ex_check.json`, JSON.stringify(res, null, 1));
  console.log(B, `칸 ${res.n} / 채움 ${res.filled} / 빠짐 ${res.miss.length} / 넘침 ${res.over.length} / 금지 ${res.bad.length}`);
  for (const x of res.miss) console.log('  빠짐', x);
  for (const x of res.over) console.log('  넘침', x);
  for (const x of res.bad) console.log('  금지', x);
  await b.close();
  await toWebp();
})();

// 빈 판(ws_actK*.webp)과 같은 설정: 너비 1500px, 높이는 원본 비율로 반올림, webp 품질 82.
// 빈 판 webp가 이미 있으면 그 크기에 정확히 맞춘다(겹침 보장). _12처럼 두 컷을 위아래로 이은 빈 판은 _ex도 같은 방식으로 잇는다.
async function toWebp() {
  const sharp = require(`${ROOT}/node_modules/sharp`);
  const dim = (f) => fs.existsSync(f) ? sharp(f).metadata().then(m => [m.width, m.height]) : null;
  const made = {};
  for (const f of fs.readdirSync(OUT).filter(x => /^ws_act\d+(_\d+)?_ex\.png$/.test(x))) {
    const base = f.replace(/_ex\.png$/, ''); const png = `${OUT}/${f}`; const m = await sharp(png).metadata();
    let [w, h] = (await dim(`${OUT}/${base}.webp`)) || [1500, Math.round(m.height * 1500 / m.width)];
    const buf = await sharp(png).resize(w, h, { fit: 'fill' }).webp({ quality: 82, effort: 6 }).toBuffer();
    fs.writeFileSync(`${OUT}/${base}_ex.webp`, buf); made[base] = { w, h, buf };
  }
  for (const f of fs.readdirSync(OUT)) {
    const m = f.match(/^(ws_act\d+)_(\d)(\d)\.webp$/); if (!m) continue;   // 빈 판 ws_act2_12.webp = _1 + _2 위아래
    const a = made[`${m[1]}_${m[2]}`], c = made[`${m[1]}_${m[3]}`]; if (!a || !c) continue;
    const [W, H] = await dim(`${OUT}/${f}`);
    const A = await sharp(a.buf).resize(W, a.h).toBuffer(), C = await sharp(c.buf).resize(W, H - a.h).toBuffer();
    await sharp({ create: { width: W, height: H, channels: 3, background: '#fff' } }).composite([{ input: A, top: 0, left: 0 }, { input: C, top: a.h, left: 0 }]).webp({ quality: 82, effort: 6 }).toFile(`${OUT}/${f.replace('.webp', '_ex.webp')}`);
  }
  console.log(B, '예시 webp', fs.readdirSync(OUT).filter(x => /_ex\.webp$/.test(x)).join(' '));
}
