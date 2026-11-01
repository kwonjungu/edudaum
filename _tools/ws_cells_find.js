// 활동지 빈 칸 찾기(브라우저 안에서 돈다). ws_cells.cjs와 lecture_ws.cjs --ex가 같이 쓴다.
// 돌려주는 것: [{el, kind, info}] — kind: text(칸·줄·빈칸) / pick(고르기)
window.__wsCells = function () {
  const mm = px => Math.round(px / (96 / 25.4));
  const T = e => (e ? e.innerText.replace(/\s+/g, ' ').trim() : '');
  const out = [];
  const secs = [...document.querySelectorAll('section.act, section.review')];
  secs.forEach((s, si) => {
    const h2 = s.querySelector('h2');
    const secTitle = h2 ? T(h2).replace(T(h2.querySelector('.when')), '').replace(/^\d+\s*/, '').trim() : '';
    const when = T(s.querySelector('.when'));
    let k = 0;
    const lastSay = el => { let x = el; while (x && x !== s) { let pv = x.previousElementSibling; while (pv) { if (pv.matches('p.say') && T(pv)) return T(pv); pv = pv.previousElementSibling; } x = x.parentElement; } return ''; };
    const push = (el, kind, ctx, extra) => {
      k++; const r = el.getBoundingClientRect();
      const w = mm(r.width), h = mm(r.height);
      const lines = Math.max(1, Math.floor(h / 7));
      const cap = Math.max(4, Math.floor(w / 4.2) * lines); // 11pt 안팎 한글 약 4.2mm
      out.push({ el, kind, info: Object.assign({ id: `${si + 1}-${k}`, sec: String(si), secNo: si + 1, secTitle, when, kind, wmm: w, hmm: h, cap, ctx: ctx.slice(0, 160) }, extra || {}) });
    };
    // 모든 후보를 문서 차례로 모은다
    const cand = [...s.querySelectorAll('td, .lines, .blank, .pick, .box')];
    for (const el of cand) {
      if (el.matches('.pick')) {
        if (el.closest('td.ex')) continue;
        const picks = [...el.querySelectorAll('i')].map(T);
        const td = el.closest('td'); let ctx = '';
        if (td) { const tr = td.parentElement; const tbl = td.closest('table'); const ci = [...tr.children].indexOf(td); const head = tbl.rows[0] && tbl.rows[0].children[ci]; ctx = `행:${T(tr.children[0]) || '-'} / 열:${T(head)}`; }
        else ctx = `문장: ${T(el.closest('p') || el.parentElement)}`;
        push(el, 'pick', ctx, { picks });
        continue;
      }
      if (el.matches('td')) {
        if (el.classList.contains('ex')) continue;
        if (el.querySelector('.pick')) { // 고르기 아래 쓰는 줄
          const ln = [...el.children].find(c => c.tagName === 'DIV');
          if (ln) { const tr = el.parentElement, tbl = el.closest('table'), ci = [...tr.children].indexOf(el); push(ln, 'text', `행:${T(tr.children[0]) || '-'} / 열:${T(tbl.rows[0].children[ci])} (고른 까닭)`); }
          continue;
        }
        if (T(el)) continue;
        const tr = el.parentElement, tbl = el.closest('table'); const ci = [...tr.children].indexOf(el);
        const prev = el.previousElementSibling;
        let col = '';
        if (prev && prev.tagName === 'TH') col = T(prev); // 가로 머리 칸(th td th td)
        else if (tbl.rows[0] && tbl.rows[0] !== tr) col = T(tbl.rows[0].children[ci]);
        else if (tbl.rows[0] === tr) col = T(tbl.rows[0].children[ci]);
        const rowh = T(tr.children[0]) && tr.children[0] !== el ? T(tr.children[0]) : '';
        const ri = [...tbl.rows].indexOf(tr);
        push(el, 'text', `${rowh ? '행:' + rowh + ' / ' : '줄' + ri + ' / '}열:${col} | 안내: ${lastSay(tbl)}`);
        continue;
      }
      if (el.matches('.lines')) { push(el, 'text', `줄 칸 | 안내: ${lastSay(el)}`); continue; }
      if (el.matches('.blank')) { push(el, 'text', `빈칸 | 문장: ${T(el.closest('p') || el.parentElement)}`); continue; }
      if (el.matches('.box')) { if (T(el)) continue; push(el, 'text', `상자 | 안내: ${lastSay(el)}`); continue; }
    }
  });
  return out;
};
