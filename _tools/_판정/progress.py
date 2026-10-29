# 재미 개편 진행 표: python _tools/_판정/progress.py  → _tools/_판정/_진행.md
# 블록마다 BXX_rN.json을 회차 순으로 읽어, 마지막 두 회차가 모두 PASS면 통과(연속 2회).
import json, glob, os, re
D = os.path.dirname(os.path.abspath(__file__))
rows = ['| 블록 | 작업 | 판정 기록 | 연속 PASS | 상태 |', '|---|---|---|---|---|']
done = 0
for b in ['HUB'] + [f'B{i:02d}' for i in range(1, 29)]:
    rs = sorted(glob.glob(f'{D}/{b}_r*.json'), key=lambda f: int(re.search(r'_r(\d+)\.json', f).group(1)))
    vs = []
    for f in rs:
        try: j = json.load(open(f, encoding='utf8')); vs.append((j.get('round'), j.get('verdict'), len(j.get('critical', []))))
        except Exception: vs.append(('?', 'ERR', 0))
    streak = 0
    for _, v, _ in reversed(vs):
        if v == 'PASS': streak += 1
        else: break
    ok = streak >= 1; done += ok   # 2026-10-29 밤 사용자 지시: 판정 한 번 통과면 끝
    work = '끝' if os.path.exists(f'{D}/{b}_작업.md') else ''
    rec = ' '.join(f'r{r}:{v}{"(" + str(c) + ")" if c else ""}' for r, v, c in vs)
    rows.append(f'| {b} | {work} | {rec} | {streak} | {"통과" if ok else ""} |')
open(f'{D}/_진행.md', 'w', encoding='utf8').write('# 재미 개편 진행\n\n통과 조건: 마지막 판정 PASS 한 번(사용자 지시로 2회→1회).\n\n' + '\n'.join(rows) + f'\n\n통과 {done}/29\n')
print(f'통과 {done}/29'); print('\n'.join(rows))
