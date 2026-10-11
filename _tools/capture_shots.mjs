// 체험 활동 쪽(BXX/index.html)을 실제로 열어 첫 화면을 찍고 목록 카드 썸네일로 굽는다.
//
//   node _tools/capture_shots.mjs                 28쪽 전부
//   node _tools/capture_shots.mjs --only B01,B04  지정한 쪽만
//
// 1280×800 창에서 연 화면을 640×400 jpg(quality 78)로 assets/shots/BXX.jpg 에 쓴다.
// 체험 쪽 원본은 건드리지 않는다. 로컬 정적 서버(127.0.0.1)로 열고, 카메라·마이크 권한은
// 거부한 상태로 찍는다(연습 모드 같은 대체 화면이 찍혀도 된다).
// 브라우저는 headless.mjs와 같이 설치된 Edge/Chrome을 쓴다(EDUDAUM_BROWSER_PATH로 바꿀 수 있다).

import { readdirSync, existsSync, mkdirSync, createReadStream, statSync } from 'node:fs';
import { resolve, dirname, extname, join, normalize } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createServer } from 'node:http';
import puppeteer from 'puppeteer-core';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const OUT = resolve(ROOT, 'assets/shots');

// 첫 화면이 안내만 있고 판이 안 보이는 쪽은 여기에 '한 번 누를 단추'를 적는다.
const CLICK = {};

function findBrowser() {
  if (process.env.EDUDAUM_BROWSER_PATH) return process.env.EDUDAUM_BROWSER_PATH;
  const fixed = [
    'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
    'C:/Program Files/Microsoft/Edge/Application/msedge.exe',
    'C:/Program Files/Google/Chrome/Application/chrome.exe',
    '/usr/bin/google-chrome', '/usr/bin/chromium', '/usr/bin/chromium-browser',
  ].find(p => existsSync(p));
  if (fixed) return fixed;
  const cache = resolve(process.env.HOME || process.env.USERPROFILE || '.', '.cache/puppeteer/chrome');
  if (existsSync(cache)) {
    for (const v of readdirSync(cache)) {
      for (const rel of ['chrome-linux64/chrome', 'chrome-win64/chrome.exe']) {
        const p = resolve(cache, v, rel);
        if (existsSync(p)) return p;
      }
    }
  }
  return null;
}

const BROWSER = findBrowser();
if (!BROWSER) {
  console.error('브라우저를 찾지 못했습니다. EDUDAUM_BROWSER_PATH로 알려 주세요.');
  process.exit(2);
}

const arg = process.argv.indexOf('--only');
const want = arg > -1 ? (process.argv[arg + 1] || '').split(',').map(s => s.trim()).filter(Boolean) : [];
const pages = readdirSync(ROOT, { withFileTypes: true })
  .filter(d => d.isDirectory() && /^B\d\d$/.test(d.name))
  .map(d => d.name)
  .filter(n => !want.length || want.includes(n))
  .filter(n => existsSync(resolve(ROOT, n, 'index.html')));
if (!pages.length) { console.log('찍을 쪽이 없습니다.'); process.exit(0); }
mkdirSync(OUT, { recursive: true });

// ── 로컬 정적 서버
const TYPES = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.mjs': 'text/javascript',
  '.css': 'text/css', '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
  '.gif': 'image/gif', '.webp': 'image/webp', '.json': 'application/json', '.mp3': 'audio/mpeg', '.wav': 'audio/wav' };
const server = createServer((req, res) => {
  let p = decodeURIComponent(new URL(req.url, 'http://x').pathname);
  let f = normalize(join(ROOT, p));
  if (!f.startsWith(ROOT)) { res.writeHead(403).end(); return; }
  try { if (statSync(f).isDirectory()) f = join(f, 'index.html'); } catch { /* 아래에서 404 */ }
  if (!existsSync(f)) { res.writeHead(404).end(); return; }
  res.writeHead(200, { 'Content-Type': TYPES[extname(f).toLowerCase()] || 'application/octet-stream' });
  createReadStream(f).pipe(res);
});
await new Promise(r => server.listen(0, '127.0.0.1', r));
const BASE = `http://127.0.0.1:${server.address().port}`;

const browser = await puppeteer.launch({
  executablePath: BROWSER,
  headless: 'new',
  args: ['--no-sandbox', '--disable-dev-shm-usage', '--hide-scrollbars', '--mute-audio'],
});
// 권한은 아무것도 주지 않는다 → 카메라·마이크는 거부 상태
await browser.defaultBrowserContext().overridePermissions(BASE, []);

let fail = 0;
for (const name of pages) {
  const page = await browser.newPage();
  try {
    await page.setViewport({ width: 1280, height: 800, deviceScaleFactor: 1 });
    await page.goto(`${BASE}/${name}/`, { waitUntil: 'networkidle2', timeout: 30000 });
    await page.evaluate(() => document.fonts && document.fonts.ready);
    if (CLICK[name]) {
      await page.click(CLICK[name]).catch(() => {});
    }
    await new Promise(r => setTimeout(r, 1200));
    await page.evaluate(() => window.scrollTo(0, 0));
    // 체험 쪽은 가운데 좁은 단이라 1280 전체를 줄이면 흰 바탕만 남는다.
    // 내용이 차지한 폭(양옆 24px 여유)만큼 16:10으로 잘라 640×400에 맞춘다(최소 640, 최대 1280).
    const box = await page.evaluate(() => {
      let l = 1280, r = 0;
      for (const el of document.body.querySelectorAll('*')) {
        const b = el.getBoundingClientRect();
        if (b.width < 1 || b.height < 1 || b.width > 1200 || b.top > 800 || b.bottom < 0) continue;
        if (getComputedStyle(el).position === 'fixed') continue;
        l = Math.min(l, b.left); r = Math.max(r, b.right);
      }
      return r > l ? { l, r } : { l: 0, r: 1280 };
    });
    const w = Math.min(1280, Math.max(640, Math.round(box.r - box.l + 48)));
    const x = Math.min(1280 - w, Math.max(0, Math.round((box.l + box.r) / 2 - w / 2)));
    await page.screenshot({
      path: resolve(OUT, `${name}.jpg`), type: 'jpeg', quality: 78,
      clip: { x, y: 0, width: w, height: Math.round(w * 10 / 16), scale: 640 / w },
    });
    console.log(`${name} → assets/shots/${name}.jpg`);
  } catch (e) {
    fail++;
    console.log(`${name} 실패: ${String(e).slice(0, 160)}`);
  } finally {
    await page.close();
  }
}
await browser.close();
server.close();
console.log(`\n${pages.length - fail}/${pages.length}장 구움`);
process.exit(fail ? 1 : 0);
