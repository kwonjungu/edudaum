# -*- coding: utf-8 -*-
"""체험 게임 쪽 윗줄을 누리집에 잇는다 — 여러 번 돌려도 같다.

  python _tools/link_games.py

- 돌아가기 링크(`../`, `../index.html`)를 체험 게임 목록 `../play/`로 바꾸고 글을 `체험 목록`으로 한다.
- 첫 돌아가기 링크 옆에 그 차시 과정안 쪽 `../lessons/BXX/` 링크(`과정안`)를 붙인다.
게임 규격(`_공통기준.md`)에 맞게 글자는 세 자만 더한다. make_site.py가 끝에 부른다.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from blocks import LESSON  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
BACK = re.compile(r'<a((?:\s+class="[^"]*")?)\s+href="\.\./(?:index\.html)?"([^>]*)>([\s\S]*?)</a>')


def main():
    n = 0
    for c in sorted(LESSON):
        f = ROOT / c / 'index.html'
        if not f.exists():
            continue
        h = f.read_text(encoding='utf-8')
        if 'href="../lessons/%s/"' % c in h:
            continue
        first = [True]

        def rep(m):
            cls, rest, inner = m.group(1), m.group(2), m.group(3).replace('전체 목록', '체험 목록')
            a = '<a%s href="../play/"%s>%s</a>' % (cls, rest, inner)
            if first[0]:
                first[0] = False
                return ('<span style="display:inline-flex;gap:8px;flex-wrap:wrap;align-items:center">%s'
                        '<a%s href="../lessons/%s/">과정안</a></span>' % (a, cls, c))
            return a
        h2 = BACK.sub(rep, h)
        if h2 != h:
            f.write_text(h2, encoding='utf-8')
            n += 1
    print('게임 쪽 %d개를 누리집에 이음' % n)


if __name__ == '__main__':
    main()
