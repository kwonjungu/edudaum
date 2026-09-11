# -*- coding: utf-8 -*-
"""페이지 안의 <script> 블록을 뽑아 node --check로 문법을 본다.

  python _tools/jscheck.py           모든 차시
  python _tools/jscheck.py B07 B10   지정한 차시만

ebs 저장소의 jscheckNN.py와 같은 방식이다. 임시 파일은 _tools/_chk/ 에 둔다.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TMP = ROOT / '_tools' / '_chk'
SCRIPT = re.compile(r'<script([^>]*)>(.*?)</script>', re.S)


def pages(argv: list) -> list:
    want = [a for a in argv if not a.startswith('-')]
    out = []
    if not want or 'index' in want:
        if (ROOT / 'index.html').exists():
            out.append(ROOT / 'index.html')
    for d in sorted(ROOT.glob('B*')):
        if d.is_dir() and (d / 'index.html').exists():
            if not want or d.name in want:
                out.append(d / 'index.html')
    return out


def check(path: Path) -> list:
    name = path.parent.name if path.parent != ROOT else 'index'
    html = path.read_text(encoding='utf-8')
    bad = []
    n = 0
    for i, (attrs, body) in enumerate(SCRIPT.findall(html)):
        if not body.strip():
            continue
        if 'src=' in attrs:
            continue
        n += 1
        TMP.mkdir(parents=True, exist_ok=True)
        f = TMP / ('_chk_%s_%d.mjs' % (name, i))
        f.write_text(body, encoding='utf-8')
        r = subprocess.run(['node', '--check', str(f)],
                           capture_output=True, text=True, shell=True)
        if r.returncode != 0:
            bad.append('%s script[%d] 문법 오류\n%s' % (name, i, r.stderr[:500]))
    # 허브는 목록만 있는 쪽이라 script가 없어도 된다. 차시 쪽은 조작이 있어야 한다.
    if n == 0 and name != 'index':
        bad.append('%s 실행되는 script 블록이 없음 (조작할 것이 없다는 뜻)' % name)
    return bad


def main(argv: list) -> int:
    targets = pages(argv)
    if not targets:
        print('검사할 페이지가 없습니다.')
        return 0
    total = 0
    for p in targets:
        msgs = check(p)
        total += len(msgs)
        name = p.parent.name if p.parent != ROOT else 'index'
        print('%-6s %s' % (name, 'OK' if not msgs else '%d건' % len(msgs)))
        for m in msgs:
            print('   -', m)
    print('\n%d쪽 / 문법 지적 %d건' % (len(targets), total))
    return 1 if total else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
