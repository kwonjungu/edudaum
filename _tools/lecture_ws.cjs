// 강의교안용 활동지 캡처: node _tools/lecture_ws.cjs B01
// 새 판 활동지 html을 인쇄 크기(180×260mm)로 열어 쪽마다 전체(ws_pN.png)와 활동 칸(ws_actK.png, 그 칸의 h2 글 포함)을 2배로 찍는다
const puppeteer = require('C:/Users/권준구/projects/edudaum/node_modules/puppeteer-core');
const path = require('path'); const fs = require('fs'); const { pathToFileURL } = require('url');
const B = process.argv[2];
const SRC = `C:/Users/권준구/Desktop/에듀다움_책만들기/work/ws/html/${B}.html`, OUT = path.resolve(`lecture/_shots/${B}`); fs.mkdirSync(OUT, { recursive: true });
(async () => {
  const b = await puppeteer.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', args: ['--allow-file-access-from-files'] });
  const p = await b.newPage(); await p.emulateMediaType('print'); await p.setViewport({ width: 680, height: 983, deviceScaleFactor: 2.5 });
  await p.goto(pathToFileURL(SRC).href, { waitUntil: 'networkidle0' }); await p.evaluate(() => document.fonts.ready);
  const secs = await p.$$('section.act, section.review'); const list = [];
  let k = 0;
  for (const s of secs) {
    k++; const name = `ws_act${k}.png`; await s.screenshot({ path: `${OUT}/${name}` });
    const t = await s.evaluate(e => (e.querySelector('h2') || e).innerText.split('\n')[0].trim());
    // 칸 단위 확대 컷: 활동 안의 표·상자·그림 묶음을 따로 찍는다(교실 화면에서 읽히게)
    const parts = await s.$$(':scope > table, :scope > .box, :scope > .two, :scope > div.lines, :scope > ul, :scope > table + p.say');
    const pl = []; let j = 0;
    for (const el of parts) { j++; const pn = `ws_act${k}_${j}.png`; await el.screenshot({ path: `${OUT}/${pn}` }); const w = await el.evaluate(x => Math.round(x.getBoundingClientRect().width / (96 / 25.4))); pl.push({ file: pn, mm: w }); }
    list.push({ file: name, title: t, parts: pl });
  }
  fs.writeFileSync(`${OUT}/ws_list.json`, JSON.stringify(list, null, 1));
  console.log(list.map(x => x.file + ' ' + x.title).join('\n'));
  await b.close();
})();
