# -*- coding: utf-8 -*-
"""과정안 hwpx의 공개용 사본을 만든다 — 개발자 칸을 연구회 이름으로 바꾸고 문서 정보의 작성자를 비운다.

  python _tools/public_copy.py "<원본 hwpx 폴더>" "<공개용 사본 폴더>"

그 다음 공개용 사본으로 PDF를 뽑는다.
  powershell -File _tools/hwpx2pdf.ps1 -Src "<공개용 사본 폴더>" -Out assets/pdf
  python _tools/public_copy.py --strip-pdf assets/pdf     # PDF 문서 정보(작성자 등) 비우기

원본은 건드리지 않는다. 이름 목록을 저장소에 두지 않으려고, 이름을 찾아 지우지 않고
개요 표에서 라벨이 '개발자'인 행의 값 칸 자체를 바꾼다.
"""
import re
import sys
import zipfile
from pathlib import Path

ORG = '경기 AI 융합교육 에듀다움 교사연구회'


HP = '{http://www.hancom.co.kr/hwpml/2011/paragraph}'


def fix_section(x: bytes) -> bytes:
    """개요 표에서 라벨이 '개발자'인 행의 값 칸을 연구회 이름으로 바꾼다.
    행 위치로 찾지 않는다(지식·이해 행이 들어가면서 행 번호가 바뀌었다)."""
    from lxml import etree
    root = etree.fromstring(x.replace(b'\r', b'&#13;'))
    def text(el):
        return ''.join(t.text or '' for t in el.iter(HP + 't')).strip()
    hit = [t for t in root.iter(HP + 'tbl') if (next(t.iter(HP + 't'), None) is not None and (next(t.iter(HP + 't')).text or '').strip() == '개요')]
    assert len(hit) == 1, '개요 표를 하나로 찾지 못함(%d개)' % len(hit)
    for tr in hit[0].findall(HP + 'tr'):
        tcs = tr.findall(HP + 'tc')
        labs = [i for i, tc in enumerate(tcs) if text(tc) == '개발자']
        if not labs:
            continue
        val = tcs[labs[0] + 1]
        ts = list(val.iter(HP + 't'))
        for i, t in enumerate(ts):
            t.text = ORG if i == 0 else ''
            for ch in list(t):
                t.remove(ch)
        for p in val.iter(HP + 'p'):
            for ls in p.findall(HP + 'linesegarray'):
                p.remove(ls)
        return etree.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)
    return x   # 개발자 행이 없는 판 — 바꿀 것 없음


def copy(src: Path, dst: Path) -> None:
    zin = zipfile.ZipFile(src)
    with zipfile.ZipFile(dst, 'w') as zout:
        for it in zin.infolist():
            data = zin.read(it.filename)
            if it.filename == 'Contents/section0.xml':
                data = fix_section(data)
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
