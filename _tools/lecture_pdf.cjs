// 강의교안 PDF: node _tools/lecture_pdf.cjs lecture/B01/index.html lecture/B01/B01_강의교안.pdf
const puppeteer = require('C:/Users/권준구/projects/edudaum/node_modules/puppeteer-core');
const path = require('path'); const { pathToFileURL } = require('url');
(async () => {
  const [src, dst] = process.argv.slice(2);
  const b = await puppeteer.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', args: ['--allow-file-access-from-files'] });
  const p = await b.newPage(); await p.setViewport({ width: 1280, height: 720 });
  await p.goto(pathToFileURL(path.resolve(src)).href, { waitUntil: 'networkidle0' });
  await p.evaluate(() => document.fonts.ready);
  await p.emulateMediaType('print');
  // PDF 용량 줄이기: 그림을 보이는 크기의 2배로 줄여 JPEG(투명 그림은 PNG)으로 바꿔 넣는다
  await p.evaluate(async () => {
    const imgs = [...document.querySelectorAll('img')];
    imgs.forEach(im => { im.loading = 'eager'; });
    await Promise.all(imgs.map(im => im.decode().catch(() => {})));
    for (const im of imgs) {
      if (!im.complete || !im.naturalWidth) continue;
      const r = im.getBoundingClientRect(); const w = Math.max(r.width, 120) * 2, k = Math.min(1, w / im.naturalWidth);
      const c = document.createElement('canvas'); c.width = Math.round(im.naturalWidth * k); c.height = Math.round(im.naturalHeight * k);
      const g = c.getContext('2d'); const alpha = /\/chars\//.test(im.src);
      if (!alpha) { g.fillStyle = '#fff'; g.fillRect(0, 0, c.width, c.height); }
      g.drawImage(im, 0, 0, c.width, c.height);
      im.src = alpha ? c.toDataURL('image/png') : c.toDataURL('image/jpeg', 0.82);
      await im.decode().catch(() => {});
    }
  });
  await p.pdf({ path: dst, width: '1280px', height: '720px', printBackground: true, preferCSSPageSize: true });
  await b.close();
})();
