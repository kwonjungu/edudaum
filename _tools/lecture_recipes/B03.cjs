// B03 체험(로봇 명령 되감아 버그 찾기) 캡처 — 교사 준비용 쪽. 활동지 활동4의 틀린 명령 여섯 개를 그대로 넣는다.
// 앞으로 한 칸·오른쪽 돌기·앞으로 한 칸·앞으로 한 칸·앞으로 한 칸·집기
module.exports = async (p, { shot, shotEl, sleep }) => {
  await p.addStyleTag({ content: 'nav.nav,header{display:none!important}.wrap{max-width:1040px!important;display:grid;grid-template-columns:1fr 1fr;gap:12px;padding:12px!important}.wrap>section{margin:0!important}.board{max-width:320px!important}.cmd{font-size:20px!important}.tip,.legend{font-size:18px!important}h2{font-size:18px!important}.fun-stamp,.fun-guide,.fun-say{display:none!important}' });
  await p.setViewport({ width: 1100, height: 700, deviceScaleFactor: 2 });
  await sleep(500);
  await shotEl(p, '.wrap', 0, 'z_start');
  // 명령 여섯 줄: 앞, 오른쪽, 앞, 앞, 앞, 집기 (줄마다 단추를 눌러 돈다: 1번 클릭=앞으로, 2번=오른쪽, 4번=집기)
  const rows = [1, 2, 1, 1, 1, 4];
  const btns = await p.$$('.cmd');
  for (let i = 0; i < 6; i++) for (let k = 0; k < rows[i]; k++) { await btns[i].click(); await sleep(60); }
  const cells = await p.$$('.cellbg');
  await cells[1 * 4 + 2].evaluate(el => el.dispatchEvent(new MouseEvent('click', { bubbles: true })));   // 끝 칸 예상: 분실물이 있는 다3
  await sleep(300);
  await shotEl(p, '.wrap', 0, 'z_pick');
  for (let i = 0; i < 6; i++) { await p.$eval('#fwd', el => el.click()); await sleep(250); }
  await sleep(700);
  await shotEl(p, '.wrap', 0, 'z_result');
};
