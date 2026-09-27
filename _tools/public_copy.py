# -*- coding: utf-8 -*-
"""과정안 hwpx의 공개용 사본을 만든다 — 개발자 칸을 연구회 이름으로 바꾸고 문서 정보의 작성자를 비운다.

  python _tools/public_copy.py "<원본 hwpx 폴더>" "<공개용 사본 폴더>"

그 다음 공개용 사본으로 PDF를 뽑는다.
  powershell -File _tools/hwpx2pdf.ps1 -Src "<공개용 사본 폴더>" -Out assets/pdf
  python _tools/public_copy.py --strip-pdf assets/pdf     # PDF 문서 정보(작성자 등) 비우기

원본은 건드리지 않는다. 이름 목록을 저장소에 두지 않으려고, 이름을 찾아 지우지 않고
개요 표의 '개발자' 칸(표 1의 4행 3열) 자체를 바꾼다.
"""
import re
import sys
import zipfile
from pathlib import Path

ORG = '경기 AI 융합교육 에듀다움 교사연구회'


def fix_section(x: str) -> str:
    tbls = [m for m in re.finditer(r'<hp:tbl\b[\s\S]*?</hp:tbl>', x)]
    t = tbls[1]
    tb = t.group(0)

    def cell(m):
        c = m.group(0)
        if not re.search(r'<hp:cellAddr colAddr="3" rowAddr="4"', c):
            return c
        first = [True]

        def tx(_):
            if first[0]:
                first[0] = False
                return '<hp:t>%s</hp:t>' % ORG
            return '<hp:t/>'
        return re.sub(r'<hp:t>[\s\S]*?</hp:t>|<hp:t/>', tx, c)
    tb2 = re.sub(r'<hp:tc\b[\s\S]*?</hp:tc>', cell, tb)
    # 개발자 칸 라벨 확인
    assert '개발자' in tb, '표 1에 개발자 칸이 없음'
    return x[:t.start()] + tb2 + x[t.end():]


def copy(src: Path, dst: Path) -> None:
    zin = zipfile.ZipFile(src)
    with zipfile.ZipFile(dst, 'w') as zout:
        for it in zin.infolist():
            data = zin.read(it.filename)
            if it.filename == 'Contents/section0.xml':
                data = fix_section(data.decode('utf-8')).encode('utf-8')
            elif it.filename == 'Contents/content.hpf':
                s = data.decode('utf-8')
                s = re.sub(r'(<opf:meta name="(?:creator|lastsaveby)" content="text">)[^<]*(</opf:meta>)', r'\1\2', s)
                data = s.encode('utf-8')
            elif it.filename.startswith('Preview/'):
                continue   # 미리보기 글·그림에는 원래 개발자 칸이 들어 있다
            zout.writestr(it, data, compress_type=zipfile.ZIP_STORED if it.filename == 'mimetype' else zipfile.ZIP_DEFLATED)


def strip_pdf(folder: Path) -> None:
    import fitz
    for f in sorted(folder.glob('*.pdf')):
        d = fitz.open(f)
        d.set_metadata({})
        d.del_xml_metadata()
        tmp = f.with_suffix('.tmp.pdf')
        d.save(tmp, garbage=4, deflate=True)
        d.close()
        tmp.replace(f)
    print('PDF 문서 정보 비움:', folder)


def main(argv):
    if argv[0] == '--strip-pdf':
        return strip_pdf(Path(argv[1]))
    src, out = Path(argv[0]), Path(argv[1])
    out.mkdir(parents=True, exist_ok=True)
    for f in sorted(src.glob('B*.hwpx')):
        copy(f, out / f.name)
        print('공개용', f.name)


if __name__ == '__main__':
    main(sys.argv[1:])
