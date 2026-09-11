// 헤드리스 브라우저로 차시 페이지를 실제로 열어 본다.
//
//   node _tools/headless.mjs            모든 차시
//   node _tools/headless.mjs B07 B10    지정한 차시만
//
// 설치된 Edge(크로미움)를 그대로 쓴다. 브라우저를 따로 내려받지 않는다.
// 보는 것: 콘솔 오류, 가로 스크롤, 첫 조작 요소가 접히지 않는지, 키보드 이동,
//          권한 거부 시 연습 모드, 주 버튼을 눌렀을 때 터지지 않는지.
// 화면 사진은 _tools/_shot/ 에 남긴다.

import { readdirSync, existsSync, mkdirSync, writeFileSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import puppeteer from 'puppeteer-core';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const SHOT = resolve(ROOT, '_tools/_shot');
function findBrowser() {
  if (process.env.EDUDAUM_BROWSER_PATH) return process.env.EDUDAUM_BROWSER_PATH;
  const fixed = [
    'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
    'C:/Program Files/Microsoft/Edge/Application/msedge.exe',
    'C:/Program Files/Google/Chrome/Application/chrome.exe',
    '/usr/bin/google-chrome', '/usr/bin/chromium', '/usr/bin/chromium-browser',
  ].find(p => existsSync(p));
  if (fixed) return fixed;
  // CI: npx puppeteer browsers install chrome 이 받아 둔 것
  const cache = resolve(process.env.HOME || process.env.USERPROFILE || '.', '.cache/puppeteer/chrome');
  if (existsSync(cache)) {
    for (const v of readdirSync(cache)) {
      for (const rel of ['chrome-linux64/chrome', 'chrome-win64/chrome.exe',
                         'chrome-mac-x64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing']) {
        const p = resolve(cache, v, rel);
        if (existsSync(p)) return p;
      }
    }
  }
  return null;
}

const EDGE = findBrowser();
if (!EDGE) {
  console.error('브라우저를 찾지 못했습니다. EDUDAUM_BROWSER_PATH로 알려 주세요.');
  process.exit(2);
}

const want = process.argv.slice(2).filter(a => a.startsWith('B'));
const pages = readdirSync(ROOT, { withFileTypes: true })
  .filter(d => d.isDirectory() && /^B\d\d$/.test(d.name))
  .map(d => d.name)
  .filter(n => !want.length || want.includes(n))
  .filter(n => existsSync(resolve(ROOT, n, 'index.html')));

if (!pages.length) { console.log('열어 볼 차시가 없습니다.'); process.exit(0); }
mkdirSync(SHOT, { recursive: true });

const browser = await puppeteer.launch({
  executablePath: EDGE,
  headless: 'new',
  args: ['--no-sandbox', '--disable-dev-shm-usage', '--use-fake-ui-for-media-stream'],
});

const report = {};
let total = 0;

for (const name of pages) {
  const bad = [];
  const url = pathToFileURL(resolve(ROOT, name, 'index.html')).href;
  const page = await browser.newPage();
  const errors = [];
  page.on('console', m => { if (m.type() === 'error') errors.push(m.text().slice(0, 200)); });
  page.on('pageerror', e => errors.push(String(e).slice(0, 200)));

  try {
    // ── 1) 태블릿 크기에서 열기
    await page.setViewport({ width: 1024, height: 800 });
    await page.goto(url, { waitUntil: 'networkidle2', timeout: 30000 });
    await new Promise(r => setTimeout(r, 1200));

    if (errors.length) bad.push(`콘솔 오류 ${errors.length}건: ${errors[0]}`);

    // ── 2) 첫 조작 요소가 스크롤 없이 보이는가
    const first = await page.evaluate(() => {
      const sel = 'button, input[type=range], input[type=checkbox], select, [role=button]';
      for (const el of document.querySelectorAll(sel)) {
        const r = el.getBoundingClientRect();
        const st = getComputedStyle(el);
        if (r.width > 0 && r.height > 0 && st.visibility !== 'hidden' && st.display !== 'none') {
          return { tag: el.tagName, top: Math.round(r.top), h: Math.round(r.height),
                   w: Math.round(r.width), text: (el.textContent || '').trim().slice(0, 20) };
        }
      }
      return null;
    });
    if (!first) bad.push('조작할 수 있는 요소가 하나도 없음');
    else {
      if (first.top > 800) bad.push(`첫 조작 요소가 화면 아래 ${first.top}px — 스크롤해야 보임`);
      if (first.h < 44 || first.w < 44) bad.push(`첫 조작 요소가 ${first.w}x${first.h}px — 44px 미만`);
    }

    // ── 3) 좁은 화면에서 가로 스크롤
    await page.setViewport({ width: 360, height: 740 });
    await new Promise(r => setTimeout(r, 600));
    const over = await page.evaluate(() =>
      document.documentElement.scrollWidth - document.documentElement.clientWidth);
    if (over > 2) bad.push(`폭 360px에서 가로로 ${over}px 넘침`);

    // ── 4) 키보드로 짚어 갈 수 있는가
    await page.setViewport({ width: 1024, height: 800 });
    const tabbable = await page.evaluate(() =>
      document.querySelectorAll('a[href],button:not([disabled]),input:not([disabled]),select,[tabindex]:not([tabindex="-1"])').length);
    if (tabbable < 2) bad.push(`키보드로 짚을 수 있는 요소가 ${tabbable}개`);

    // ── 5) 주 버튼을 눌러도 터지지 않는가
    const before = errors.length;
    await page.evaluate(() => {
      const b = [...document.querySelectorAll('button:not([disabled])')]
        .find(x => x.offsetParent !== null);
      if (b) b.click();
    });
    await new Promise(r => setTimeout(r, 1500));
    if (errors.length > before) bad.push(`버튼을 누르자 오류: ${errors[errors.length - 1]}`);

    // ── 6) 글자 양 (본문 전체)
    const chars = await page.evaluate(() =>
      (document.body.innerText || '').replace(/\s+/g, ' ').trim().length);
    if (chars > 900) bad.push(`페이지 전체 글자 ${chars}자 — 화면을 나눠도 많은 편`);

    // ── 7) 사진
    await page.screenshot({ path: resolve(SHOT, `${name}.png`), fullPage: true });
  } catch (e) {
    bad.push(`열다가 실패: ${String(e).slice(0, 160)}`);
  } finally {
    await page.close();
  }

  report[name] = bad;
  total += bad.length;
  console.log(`${name.padEnd(5)} ${bad.length ? bad.length + '건' : 'OK'}`);
  bad.forEach(m => console.log('   -', m));
}

await browser.close();
writeFileSync(resolve(ROOT, '_tools/_헤드리스결과.json'),
  JSON.stringify(report, null, 2) + '\n', 'utf-8');
console.log(`\n${pages.length}쪽 / 헤드리스 지적 ${total}건 → _tools/_헤드리스결과.json`);
process.exit(total ? 1 : 0);
