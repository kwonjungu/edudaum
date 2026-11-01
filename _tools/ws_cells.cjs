// 활동지 빈 칸 목록 뽑기: node _tools/ws_cells.cjs B01
// 원본 활동지 html(책 폴더, 읽기만)을 인쇄 크기로 열어 빈 칸을 같은 차례로 찾는다.
// 칸 id는 "섹션번호-칸번호". 주입 도구(lecture_ws.cjs --ex)도 이 차례(window.__wsCells)를 똑같이 쓴다.
// 결과: lecture/_src/ans/BXX_cells.json (+ 사람이 읽는 BXX_cells.md)
const puppeteer = require('C:/Users/권준구/projects/edudaum/node_modules/puppeteer-core');
const path = require('path'); const fs = require('fs'); const { pathToFileURL } = require('url');
const B = process.argv[2];
const SRC = `C:/Users/권준구/Desktop/에듀다움_책만들기/work/ws/html/${B}.html`;
const OUT = path.resolve('C:/Users/권준구/projects/edudaum/lecture/_src/ans'); fs.mkdirSync(OUT, { recursive: true });
const FIND = fs.readFileSync(path.join(__dirname, 'ws_cells_find.js'), 'utf8');
(async () => {
  const b = await puppeteer.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', args: ['--allow-file-access-from-files'] });
  const p = await b.newPage(); await p.emulateMediaType('print'); await p.setViewport({ width: 680, height: 983 });
  await p.goto(pathToFileURL(SRC).href, { waitUntil: 'networkidle0' });
  await p.addScriptTag({ content: FIND });
  const r = await p.evaluate(() => window.__wsCells().map(c => c.info));
  fs.writeFileSync(`${OUT}/${B}_cells.json`, JSON.stringify(r, null, 1));
  let md = `# ${B} 빈 칸 목록\n`; let sec = '';
  for (const c of r) {
    if (c.sec !== sec) { sec = c.sec; md += `\n## ${c.secNo}. ${c.secTitle} (${c.when})\n`; }
    md += `- **${c.id}** [${c.kind}${c.picks ? ': ' + c.picks.join('/') : ''}] ${c.wmm}×${c.hmm}mm 약 ${c.cap}자 | ${c.ctx}\n`;
  }
  fs.writeFileSync(`${OUT}/${B}_cells.md`, md);
  console.log(B, r.length, '칸');
  await b.close();
})();
