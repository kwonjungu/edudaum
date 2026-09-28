# -*- coding: utf-8 -*-
"""서식 자료실 파일을 정리한다 — 크기·쪽수 기록, 묶음(zip) 만들기, 구글 드라이브 폴더와 맞추기.

  python _tools/forms_pack.py            forms.json의 파일 크기·쪽수를 채우고 묶음(zip)을 다시 만든다
  python _tools/forms_pack.py --sync     위 일 + 구글 드라이브 「서식 자료실(공개용)」로 같은 파일을 복사한다

원본은 저장소 assets/forms/ 하나다. 드라이브에서 직접 고치지 않는다(site_check S16이 두 곳을 대조한다).
드라이브 폴더 안 자리: 묶음 → 00_한 벌 묶음(zip), 작성 예시 → 08_작성 예시, 나머지 → 서식의 단계 폴더.
드라이브 경로는 환경변수 EDUDAUM_DRIVE_FORMS 로 바꿀 수 있다.

묶음 정의(forms.json sets[])
  {"id": "set-edu5", "name": "…", "zip": "에듀다움_5학년SW_종합세트.zip",
   "include": {"forms": ["F02", …], "roles": ["작성 예시"], "extra": ["assets/pdf/B01.pdf", "_forms/public/B01….hwpx"]},
   "folder": "에듀다움_5학년SW_종합세트"}   ← zip 안 최상위 폴더 이름
  include.forms × include.roles 로 서식 파일을 고르고, extra는 저장소 기준 경로를 그대로 넣는다.
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FD = ROOT / 'assets/forms'
DATA = ROOT / '_data/forms.json'
DRIVE = Path(os.environ.get('EDUDAUM_DRIVE_FORMS', r'G:\내 드라이브\경기 에듀다움 - 학교자율시간 AI 교육과정 개발·검증\서식 자료실(공개용)'))
STAGE_DIR = {'01': '01_사전 준비', '02': '02_설계', '03': '03_자체 점검', '04': '04_컨설팅·승인 신청',
             '05': '05_학운위 심의·결재', '06': '06_나이스 입력·기록', '07': '07_성찰·보완'}
SET_DIR, EX_DIR = '00_한 벌 묶음(zip)', '08_작성 예시'
for s in (sys.stdout, sys.stderr):
    try:
        s.reconfigure(encoding='utf-8', errors='replace')
    except Exception:  # noqa: BLE001
        pass


ORG = '에듀다움 연구회'


def clean_meta(p: Path) -> bool:
    """한글이 저장하며 넣은 문서 정보(마지막 저장자 = 윈도 계정명)를 지우고 작성자를 연구회로 맞춘다.
    zip 항목 순서·압축 방식은 그대로 둔다(mimetype 첫 항목·무압축)."""
    import re
    zi = zipfile.ZipFile(p)
    hpf = zi.read('Contents/content.hpf').decode('utf-8')
    new = re.sub(r'(name="creator" content="text">)[^<]*(<)', r'\g<1>%s\2' % ORG, hpf)
    new = re.sub(r'(name="lastsaveby" content="text">)[^<]*(<)', r'\1\2', new)
    if new == hpf:
        return False
    items = [(it, zi.read(it.filename)) for it in zi.infolist()]
    zi.close()
    with zipfile.ZipFile(p, 'w') as zo:
        for it, data in items:
            if it.filename == 'Contents/content.hpf':
                data = new.encode('utf-8')
            zo.writestr(it, data, compress_type=it.compress_type)
    return True


def pages_of(p: Path) -> int:
    if p.suffix == '.pdf':
        try:
            import pypdfium2 as pdfium
            return len(pdfium.PdfDocument(str(p)))
        except Exception:  # noqa: BLE001
            return 0
    return 0


def set_members(fm, s):
    """묶음에 넣을 (원본 경로, 묶음 안 경로) 목록.
    종합세트(include.order)는 채운 양식을 도입 순서대로 01_, 02_ … 번호를 붙여 넣는다."""
    by = {f['id']: f for f in fm['forms']}
    inc = s.get('include', {})
    ok = lambda x: x.get('role') in inc.get('roles', ['빈 양식']) and (not inc.get('grade') or x.get('grade') in (inc['grade'], 'all'))
    out, items = [], []
    if inc.get('order'):
        for i, fid in enumerate(inc['order'], 1):
            fs = [x for x in by[fid].get('files', []) if ok(x)] if fid in by else []
            if fs:
                items.append({'no': i, 'id': fid, 'name': by[fid]['name'], 'files': [{'fmt': x['fmt'], 'file': x['file']} for x in fs]})
            out += [(FD / x['file'], '%02d_%s' % (i, x['file'])) for x in fs]
    else:
        for fid in inc.get('forms', []):
            out += [(FD / x['file'], x['file']) for x in by[fid].get('files', []) if ok(x)]
    for rel in inc.get('extra', []):
        name = rel.split('/')[-1]
        if rel.startswith('assets/pdf/'):
            arc = '과정안_PDF/' + name
        elif rel.startswith('assets/forms/'):
            arc = '함께쓰는_빈양식/' + name          # 종합세트 안내가 가리키는 빈 양식(설문·워크시트 등)
        elif name.endswith('.hwpx') and name.startswith('B') and name[1:3].isdigit():
            arc = '과정안_한글/' + name
        else:
            arc = name
        out.append((ROOT / rel, arc))
    s['items'] = items
    return out


def build_sets(fm):
    for s in fm.get('sets', []):
        files = set_members(fm, s)
        top = s.get('folder') or Path(s['zip']).stem
        z = FD / s['zip']
        with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as zo:
            for p, arc in files:
                if not p.exists():
                    raise SystemExit('묶음 %s: 파일 없음 %s' % (s['id'], p))
                # 날짜를 고정해 같은 내용이면 같은 바이트가 되게 한다(깃 변경·드라이브 대조가 흔들리지 않게)
                zi = zipfile.ZipInfo('%s/%s' % (top, arc), date_time=(2026, 1, 1, 0, 0, 0))
                zi.compress_type = zipfile.ZIP_DEFLATED
                zo.writestr(zi, p.read_bytes())
        s['bytes'] = z.stat().st_size
        s['count'] = len(files)
        print('  묶음 %-40s %3d개 %6.1fMB' % (s['zip'], len(files), s['bytes'] / 1048576))


BLANK_DIR = '3_빈 양식 (다른 과정을 직접 만들 때)'


def drive_plan(fm):
    """드라이브 폴더에 둘 파일 {상대 경로: 원본 경로}.
    채운 양식(종합세트)이 먼저 보이게 1_·2_ 폴더에 풀어 두고, 빈 양식은 3_ 폴더 아래 단계별로 둔다."""
    plan = {}
    for s in fm.get('sets', []):
        if s.get('edudaum'):
            d = s['drive_dir']
            plan['%s/%s' % (d, s['zip'])] = FD / s['zip']
            for p, arc in set_members(fm, s):
                plan['%s/%s' % (d, arc)] = p
        else:
            plan['%s/%s/%s' % (BLANK_DIR, SET_DIR, s['zip'])] = FD / s['zip']
    for f in fm['forms']:
        for x in f.get('files', []):
            if x.get('role') == '빈 양식':
                plan['%s/%s/%s' % (BLANK_DIR, STAGE_DIR[f['stage']], x['file'])] = FD / x['file']
    return plan


def sync():
    if not DRIVE.exists():
        raise SystemExit('드라이브 폴더 없음: %s' % DRIVE)
    fm = json.loads(DATA.read_text(encoding='utf-8'))
    plan = drive_plan(fm)
    # 계획에 없는 파일(옛 자리·지운 서식)은 뺀다. desktop.ini 는 드라이브가 만든 것이라 둔다.
    for p in sorted(DRIVE.rglob('*'), key=lambda q: -len(q.parts)):
        rel = p.relative_to(DRIVE).as_posix()
        if p.is_file() and p.name != 'desktop.ini' and rel not in plan:
            p.unlink()
            print('  드라이브에서 뺌:', rel)
        elif p.is_dir() and not any(k == rel or k.startswith(rel + '/') for k in plan):
            shutil.rmtree(p, ignore_errors=True)
    n = 0
    for rel, src in plan.items():
        dst = DRIVE / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if not dst.exists() or dst.stat().st_size != src.stat().st_size or dst.read_bytes() != src.read_bytes():
            shutil.copyfile(src, dst)
            n += 1
    print('드라이브 맞춤: %d개 복사, 전체 %d개' % (n, len(plan)))


def main(argv):
    fm = json.loads(DATA.read_text(encoding='utf-8'))
    for f in fm['forms']:
        for x in f.get('files', []):
            p = FD / x['file']
            if not p.exists():
                raise SystemExit('파일 없음: %s' % p)
            if p.suffix == '.hwpx':
                clean_meta(p)
            x['bytes'] = p.stat().st_size
            x['pages'] = pages_of(p) or x.get('pages', 0)
    build_sets(fm)
    DATA.write_text(json.dumps(fm, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print('forms.json: 서식 %d종 · 묶음 %d개' % (len(fm['forms']), len(fm.get('sets', []))))
    if '--sync' in argv:
        sync()


if __name__ == '__main__':
    main(sys.argv[1:])
