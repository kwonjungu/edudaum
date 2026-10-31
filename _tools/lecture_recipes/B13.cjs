// B13 체험: 기록 두 장으로 막힌 곳 짚기 — 한 판으로 z_start·z_pick·z_result·z_fix(+22장 카드용 z_card_fix·z_card_count)를 이어 찍는다.
// 판은 무작위라, 처음 두 장이 모두 '수신기가 늦음'이고 짚은 뒤 가장 많은 곳이 다른 판이 나올 때까지 다시 불러온다.
// 컷 뒤처리(1.64 비율 흰 바탕 webp)는 마지막에 python으로 한다.
const { execFileSync } = require('child_process');
const path = require('path');
const GUESS = '수신기가 늦음';
module.exports = async (p, { shot, shotEl, sleep }) => {
  const OUT = path.resolve('lecture/_shots/B13');
  const css = '.fun-stamp,.fun-guide,.fun-say,.fun-bubble,[class^="fun-"]{display:none!important} .nav,header{display:none!important} body{background:#fff!important;margin:0} .wrap{max-width:440px!important;padding:6px 6px 6px!important} section{margin:0 0 4px!important}';
  const ready = async () => {
    await p.setViewport({ width: 440, height: 900, deviceScaleFactor: 3 });
    await p.reload({ waitUntil: 'load' }); await sleep(700);
    await p.addStyleTag({ content: css }); await sleep(400);
    return p.evaluate(G => {
      const tr = [...document.querySelectorAll('#rows tr')].slice(0, 2).map(r => r.cells[3].textContent);
      const has = [...document.querySelectorAll('#cands button')].some(b => b.textContent === G);
      return has && tr[0] === G && tr[1] === G;
    }, GUESS);
  };
  const clip = async (n, fn) => {
    await sleep(400);
    const r = await p.evaluate(typeof fn === 'string' ? `(${fn})()` : fn);
    await p.screenshot({ path: `${OUT}/${n}_raw.png`, clip: { x: r.x, y: r.y, width: r.w, height: r.h } }); console.log(n, JSON.stringify(r));
  };
  const rectOf = sel => `()=>{const e=document.querySelector('${sel}').getBoundingClientRect();return {x:e.left-8,y:e.top+scrollY-4,w:e.width+16,h:e.height+8}}`;
  const secTo = (si, endSel, pad = 6) => `()=>{const s=document.querySelectorAll('section')[${si}].getBoundingClientRect();const o=document.querySelector('${endSel}').getBoundingClientRect();return {x:s.left+8,y:s.top+scrollY,w:s.width-16,h:o.bottom-s.top+${pad}}}`;
  // 조건에 맞는 판이 나올 때까지 다시 불러와, 한 판 안에서 단계마다 찍는다.
  for (let tries = 0; tries < 80; tries++) {
    if (!(await ready())) continue;
    await clip('z_start', secTo(0, '#rows tr:nth-child(2)', -1));
    const idx = await p.evaluate(G => [...document.querySelectorAll('#cands button')].findIndex(b => b.textContent === G), GUESS);
    await (await p.$$('#cands button'))[idx].click(); await sleep(300);
    await clip('z_pick', secTo(1, '#say'));
    await p.click('#open'); await sleep(3300);
    const good = await p.evaluate(() => /^짚은 곳 \d번, 가장 많은 곳/.test(document.querySelector('#say').textContent));
    if (!good) continue;
    await clip('z_result', () => { const s = document.querySelectorAll('section')[1]; const a = s.getBoundingClientRect(); const o = document.querySelector('#say').getBoundingClientRect(); const b = document.querySelector('#bars').getBoundingClientRect(); return { x: a.left + 8, y: o.top + scrollY - 6, w: a.width - 16, h: b.bottom - o.top + 12 }; });
    await clip('z_fix', () => { const s = document.querySelector('#fixSec'); const h = document.querySelector('#h-fix').getBoundingClientRect(); const g = document.querySelector('#grid').getBoundingClientRect(); const a = s.getBoundingClientRect(); return { x: a.left + 8, y: h.top + scrollY - 4, w: a.width - 16, h: g.bottom - h.top + 12 }; });
    // 22장 카드용: 좁은 화면에서 글자를 키워 칩 줄과 막대만 크게
    await p.setViewport({ width: 360, height: 900, deviceScaleFactor: 3 });
    await p.addStyleTag({ content: '.grid{grid-template-columns:44px 1fr 1fr!important;font-size:15px!important} .chip{font-size:15px!important;white-space:nowrap;padding:1px 6px!important} .grid .cell{min-height:60px!important} .bar{font-size:17px!important;grid-template-columns:minmax(0,1fr) 80px 40px!important} .bar i{height:18px!important} .wrap{max-width:360px!important}' });
    await sleep(500);
    await clip('z_card_fix', rectOf('#grid'));
    await clip('z_card_count', rectOf('#bars'));
    const info = await p.evaluate(() => ({ rows: [...document.querySelectorAll('#rows tr')].map(r => [...r.cells].map(c => c.textContent).join('|')), bars: [...document.querySelectorAll('#bars .bar')].map(b => b.textContent), say: document.querySelector('#say').textContent, chips: [...document.querySelectorAll('#grid .chip')].map(c => c.textContent) }));
    console.log(JSON.stringify(info));
    // 뒤처리: 장 칸 비율(1.64)에 흰 바탕으로 맞춰 webp
    const py = `
from PIL import Image
import sys
d=sys.argv[1]
def pad(n,ratio,out,maxw=1500):
    im=Image.open(f'{d}/{n}_raw.png').convert('RGB'); w,h=im.size
    W,H=w,h
    if w/h>ratio: H=round(w/ratio)
    else: W=round(h*ratio)
    c=Image.new('RGB',(W,H),'white'); c.paste(im,((W-w)//2,(H-h)//2))
    if W>maxw: c=c.resize((maxw,round(H*maxw/W)),Image.LANCZOS)
    c.save(f'{d}/{out}.webp','WEBP',quality=82)
for n in ['z_start','z_pick','z_result']: pad(n,1.64,n)
pad('z_card_fix',1.64,'z_fix')
for n in ['z_card_fix','z_card_count']: pad(n,1.5,n)
`;
    execFileSync('python', ['-c', py, OUT]);
    return;
  }
  throw new Error('두 번째 탐색 실패');
};
