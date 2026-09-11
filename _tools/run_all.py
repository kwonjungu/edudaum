# -*- coding: utf-8 -*-
"""문법·감사·헤드리스를 한 번에 돌리고 한 장으로 보고한다.

  python _tools/run_all.py            전부
  python _tools/run_all.py B07 B10    지정한 차시만
  python _tools/run_all.py --no-head  브라우저 검사는 건너뛴다

셋 다 0건이어야 낼 수 있다. 하나라도 남으면 종료 코드가 1이다.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPORT = ROOT / '_tools' / '_감사보고.md'

# 윈도우 기본 콘솔(cp949)에서 한글·줄표를 찍다가 죽지 않게 한다.
for stream in (sys.stdout, sys.stderr):
    try:
        stream.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass


def run(cmd: list) -> tuple:
    env = dict(os.environ, PYTHONIOENCODING='utf-8', PYTHONUTF8='1')
    r = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True,
                       encoding='utf-8', errors='replace', shell=True, env=env)
    return r.returncode, (r.stdout or '') + (r.stderr or '')


def main(argv: list) -> int:
    only = [a for a in argv if a.startswith('B')]
    skip_head = '--no-head' in argv

    steps = [('문법 (node --check)', [sys.executable, '_tools/jscheck.py', *only]),
             ('감사 (공통기준)', [sys.executable, '_tools/audit.py', *only])]
    if not skip_head:
        steps.append(('헤드리스 (Edge)', ['node', '_tools/headless.mjs', *only]))

    lines = ['# 감사 보고', '']
    failed = 0
    for title, cmd in steps:
        code, out = run(cmd)
        mark = 'OK' if code == 0 else '지적 있음'
        if code != 0:
            failed += 1
        print('\n===== %s — %s =====' % (title, mark))
        print(out.strip()[-3000:])
        lines += ['## %s — %s' % (title, mark), '', '```', out.strip()[-4000:], '```', '']

    lines += ['## 판정', '',
              '세 검사 모두 0건이어야 낼 수 있다.' if failed == 0 else
              '**%d개 검사에 지적이 남았다. 고친 뒤 다시 돌린다.**' % failed, '']
    REPORT.write_text('\n'.join(lines), encoding='utf-8')
    print('\n==================================================')
    print('통과' if failed == 0 else '미통과 — 검사 %d개에 지적 남음' % failed)
    print('보고서:', REPORT.relative_to(ROOT))
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
