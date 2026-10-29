# 누리집 새판 작업 (2026-10-29)

## 바꾼 것
- `_tools/site.css`: Google Fonts 불러오기를 지우고 `assets/fonts`의 주아·고운돋움을 `@font-face`로 씀(`__UP__`을 make_site가 쪽 깊이에 맞게 바꿈). 바탕은 아이보리 점무늬, 머리와 바닥에도 새 색을 입힘. 긴 글(과정안 본문, 표, Q&A)은 시스템 고딕. 첫 띠, 새싹쌤 말풍선, 미션 지도, 네 입구, 차시 쪽 체험 단추, 체험 카드(캐릭터, 미션, 도장) 모양을 더함. `prefers-reduced-motion`이면 움직임을 끔.
- `_tools/make_site.py`: `assets/play/fun.js`의 CAST를 읽어 블록마다 캐릭터를 붙임. 첫 화면을 표지 그림 첫 띠(책 제목, 부제, 연구회 이름)와 새싹쌤 말풍선, 28블록 미션 지도(학년별, 단원별 징검다리. 돌을 누르면 체험 활동, 작은 글자를 누르면 과정안), 네 입구 차례로 새로 짬. `localStorage['edudaum.stamps']`에 있는 블록은 돌과 체험 카드에 도장이 찍힘(개수는 세지 않음). 차시 쪽 머리 띠에 노란 「체험 활동 열기」 단추를 넣음. 바닥에 캐릭터 줄그림을 넣음. 연구회 소개에 책 한 줄을 넣음. 바닥 지원 문구는 그대로.
- `_data/site.json`: `book`(제목, 부제, 소개 한 줄)을 더함.
- 게임 쪽(`BXX/`)과 `assets/play/`는 건드리지 않음(make_site 안의 link_games는 0개를 고침).

## 점검
- `python _tools/make_site.py` 정상.
- `python _tools/site_check.py`: 지적 3건이고 모두 S9(게임 쪽 테마)임. B01·B11은 통일 테마 표시가 없고, B12에는 굵은 먹 테두리가 있음. 다른 작업자가 지금 고치는 게임 파일이라 이번 범위 밖이어서 손대지 않음. 누리집 쪽 지적은 0건.
- puppeteer(Chrome)로 `/`, `/play/`, `/lessons/`, `/lessons/B01/`, `/plan/`, `/tools/`를 360·430·1280px로 찍음. 도장 3개(B01, B05, B16)를 넣은 상태로 `/`, `/play/`도 찍음. 결과: 콘솔 오류 0, 가로 스크롤 0, 글꼴은 Jua와 Gowun Dodum을 저장소 안 파일로 불러옴. 도장 3개가 표시됨.
- 사진: `_tools/_판정/shots/HUB_*.png`
