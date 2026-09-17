import puppeteer from 'puppeteer-core';
import { existsSync } from 'fs';
const EDGE=['C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe','C:/Program Files/Microsoft/Edge/Application/msedge.exe'].find(existsSync);
const b=await puppeteer.launch({executablePath:EDGE,headless:'new',args:['--allow-file-access-from-files','--use-fake-ui-for-media-stream']});
const R='file:///C:/Users/%EA%B6%8C%EC%A4%80%EA%B5%AC/projects/edudaum/';
const BAD=['맞았어요','틀렸','잘했','아쉬','정답','성공했','실패했','점수','등수','순위','다양한','살펴봅','알아봅','이를 통해','뿐만 아니라','나아가'];
const ids=[...Array(28)].map((_,i)=>'B'+String(i+1).padStart(2,'0'));
let bad=0;
for(const id of ids){
  const p=await b.newPage(); await p.setViewport({width:390,height:800});
  const errs=[]; p.on('pageerror',e=>errs.push(String(e).slice(0,50)));
  await p.goto(R+id+'/index.html',{waitUntil:'networkidle0'});
  await new Promise(r=>setTimeout(r,2600));
  const h=await p.evaluate(()=>document.documentElement.scrollHeight);
  const ov=await p.evaluate(()=>document.documentElement.scrollWidth>document.documentElement.clientWidth+2);
  const below=await p.$$eval('button,input',es=>es.filter(e=>!e.hidden&&!e.closest('[hidden]')&&e.getBoundingClientRect().bottom>800).length);
  const txt=await p.$eval('body',e=>e.innerText);
  const hits=BAD.filter(w=>txt.includes(w));
  const hasNext=/다음 판/.test(txt), hasBack=/다시 하기|다시 시작|처음으로|다시 보기/.test(txt);
  const flag=(errs.length||below||ov||hits.length)?'  ← ':'';
  if(flag) bad++;
  console.log(`${id} h${String(h).padStart(4)} 넘침${ov?'Y':'.'} 접힘아래${below} 금지어${hits.length?hits.join(','):'.'} 오류${errs.length} 다음판${hasNext?'O':'.'} 되돌림${hasBack?'O':'.'}${flag}`);
  await p.close();
}
console.log(bad?`\n!! ${bad}쪽에 지적`:'\n스물여덟 쪽 모두 깨끗');
await b.close();
