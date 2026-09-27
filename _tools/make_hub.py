# -*- coding: utf-8 -*-
"""예전 허브 생성기 자리. 이제 index.html은 누리집 홈이고, 체험 게임 목록은 play/index.html이다.

  python _tools/make_hub.py      → make_site.py를 그대로 돌린다
"""
import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).resolve().parent / 'make_site.py'), run_name='__main__')
