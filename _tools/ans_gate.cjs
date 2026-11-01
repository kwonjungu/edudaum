// 예시 답 관문: node _tools/ans_gate.cjs B16 [--norebuild]
// 0건이어야 하는 것: (a) _ex_check 빠짐·넘침·금지어 (b) 빈 판과 _ex 판 webp 크기 (c) 교안 다시 만든 뒤 lecture_check
// (d) 로컬 서버(8790)에서 ws 장마다 「예시 보기」 단추 동작 (e) PDF 쪽 수 = 장 수 + 예시 판 수. 결과는 JSON으로 출력(끝 코드 0=통과).
const puppeteer = require('C:/Users/권준구/projects/edudaum/node_modules/puppeteer-core');
const sharp = require('C:/Users/권준구/projects/edudaum/node_modules/sharp');
const fs = require('fs'); const path = require('path'); const { spawnSync } = require('child_process');
const ROOT = 'C:/Users/권준구/projects/edudaum'; const B = process.argv[2]; const REBUILD = !process.argv.includes('--norebuild');
const SHOTS = `${ROOT}/lecture/_shots/${B}`; const URL = `http://127.0.0.1:8790/lecture/${B}/`;
const run = (cmd, args) => spawnSync(cmd, args, { cwd: ROOT, encoding: 'utf8', env: { ...process.env, PYTHONIOENCODING: 'utf-8' } });
(async () => {
  const R = { block: B, a: {}, b: [], c: {}, d: [], e: {}, total: 0 };
  // (a)
  const r0 = run('node', ['_tools/lecture_ws_ex.cjs', B, '--noshot']);
  try { const j = JSON.parse(fs.readFileSync(`${SHOTS}/_ex_check.json`, 'utf8')); R.a = { miss: j.miss, over: j.over, bad: j.bad }; }
  catch (e) { R.a = { error: '_ex_check.json 없음: ' + (r0.stderr || '').slice(0, 200) }; }
  // (b) 빈 판 ↔ _ex 판 크기(원고 ws 장 그림과 파일 이름 짝 모두)
  const meta = async f => { const m = await sharp(f).metadata(); return `${m.width}x${m.height}`; };
  for (const f of fs.readdirSync(SHOTS).filter(x => /_ex\.webp$/.test(x))) {
    const blank = `${SHOTS}/${f.replace('_ex.webp', '.webp')}`; if (!fs.existsSync(blank)) continue;   // 짝 없는 것(체험 결과 그림 등)은 건너뜀
    const [x, y] = [await meta(blank), await meta(`${SHOTS}/${f}`)]; if (x !== y) R.b.push(`${f} ${y} / 빈 판 ${x}`);
  }
  // (c) 교안 다시 만들기 + lecture_check
  if (REBUILD) { const m = run('python', ['_tools/make_lecture.py', B]); R.c.build = m.status === 0 ? 'ok' : 'FAIL ' + (m.stderr || '').slice(-300); }
  const lc = run('node', ['_tools/_판정/lecture_check.cjs', B]); let ck = null;
  try { ck = JSON.parse(lc.stdout.trim().split('\n').pop()); } catch (e) { R.c.error = 'lecture_check 출력 읽기 실패 ' + (lc.stderr || '').slice(0, 200); }
  if (ck) { R.c.errors = ck.errors; R.c.external = ck.external; R.c.small = ck.small; R.c.overflow = ck.overflow; R.c.wspage = ck.wspage; R.c.words = ck.words; }
  // 원고에서 기대 단추 수
  const src = JSON.parse(fs.readFileSync(`${ROOT}/lecture/_src/${B}.json`, 'utf8'));
  const want = src.slides.map((s, i) => ({ i, s })).filter(({ s }) => (s.type === 'ws' || s.type === 'wrap') && s.ex !== false && s.img && s.img.endsWith('.webp') && fs.existsSync(path.resolve(`${ROOT}/lecture/${B}`, s.img.replace(/\.webp$/, '_ex.webp'))));
  // (d) 단추 동작
  const b = await puppeteer.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe' });
  try {
    const p = await b.newPage(); await p.setViewport({ width: 1280, height: 720 });
    for (const { i, s } of want) {
      const o = { slide: i + 1, img: s.img, problems: [] };
      await p.goto(`${URL}#${i + 1}`, { waitUntil: 'networkidle0' });
      const st = async () => p.evaluate(() => { const sec = document.querySelector('.s.cur'); const bt = sec && sec.querySelector('.exbtn'); const im = sec && sec.querySelector('.zoom.ws img');
        return bt && im ? { src: decodeURIComponent(im.src), pressed: bt.getAttribute('aria-pressed'), label: bt.textContent.trim(), ok: im.complete && im.naturalWidth > 0, vis: bt.getBoundingClientRect().width > 0 } : null; });
      let a = await st(); if (!a) { o.problems.push('단추 없음'); R.d.push(o); continue; }
      if (a.src.includes('_ex.webp') || a.pressed !== 'false' || a.label !== '예시 보기') o.problems.push('처음 상태 이상 ' + JSON.stringify(a));
      await p.click('.s.cur .exbtn'); await new Promise(r => setTimeout(r, 300)); let c = await st();
      if (!c.src.endsWith('_ex.webp') || c.pressed !== 'true' || c.label !== '빈 활동지' || !c.ok) o.problems.push('누른 뒤 이상 ' + JSON.stringify(c));
      await p.click('.s.cur .exbtn'); await new Promise(r => setTimeout(r, 300)); let d = await st();
      if (d.src !== a.src || d.pressed !== 'false' || d.label !== '예시 보기') o.problems.push('되돌림 이상 ' + JSON.stringify(d));
      // 키보드(엔터와 스페이스), 장이 바뀌지 않아야 함
      await p.focus('.s.cur .exbtn'); await p.keyboard.press('Enter'); await new Promise(r => setTimeout(r, 200)); let k1 = await st();
      await p.keyboard.press('Space'); await new Promise(r => setTimeout(r, 200)); let k2 = await st();
      if (!k1 || !k1.src.endsWith('_ex.webp') || !k2 || k2.src.endsWith('_ex.webp')) o.problems.push('키보드 이상 ' + JSON.stringify([k1 && k1.pressed, k2 && k2.pressed]));
      o.ok = !o.problems.length; R.d.push(o);
    }
    // 말풍선·그림을 가리지 않는지: 단추 상자가 .bub, .pic, .zoom 과 겹치면 기록
    for (const { i } of want) {
      await p.goto(`${URL}#${i + 1}`, { waitUntil: 'networkidle0' });
      const ov = await p.evaluate(() => { const sec = document.querySelector('.s.cur'), bt = sec.querySelector('.exbtn').getBoundingClientRect(); const out = [];
        sec.querySelectorAll('.bub,.pic,.zoom,.talk,.memo,.ktag,h2.h').forEach(t => { const r = t.getBoundingClientRect(); const ox = Math.min(r.right, bt.right) - Math.max(r.left, bt.left), oy = Math.min(r.bottom, bt.bottom) - Math.max(r.top, bt.top); if (ox > 2 && oy > 2) out.push(t.className || t.tagName); }); return out; });
      if (ov.length) R.d.push({ slide: i + 1, problems: ['단추가 가림: ' + ov.join(',')] });
    }
  } finally { await b.close(); }
  // (e) PDF 쪽 수
  const pdf = `${ROOT}/lecture/${B}/${B}_강의교안.pdf`;
  const pg = run('python', ['-c', `import pypdf,sys;print(len(pypdf.PdfReader(sys.argv[1]).pages))`, pdf]);
  R.e = { slides: src.slides.length, exPages: want.length, expect: src.slides.length + want.length, pdfPages: parseInt(pg.stdout, 10) };
  // 합계
  const n = x => Array.isArray(x) ? x.length : (x ? 1 : 0);
  R.total = n(R.a.miss) + n(R.a.over) + n(R.a.bad) + n(R.a.error) + R.b.length + n(R.c.errors) + n(R.c.external) + n(R.c.small) + n(R.c.overflow) + n(R.c.wspage) + n(R.c.words) + n(R.c.error) + (R.c.build && R.c.build !== 'ok' ? 1 : 0)
    + R.d.filter(x => x.problems && x.problems.length).length + (R.d.length === 0 && want.length ? 1 : 0) + (R.e.pdfPages === R.e.expect ? 0 : 1);
  R.pass = R.total === 0;
  console.log(JSON.stringify(R, null, 1)); process.exit(R.pass ? 0 : 1);
})();
