# 강의교안 모음 쪽: python _tools/make_lecture_index.py -> lecture/index.html (책의 QR이 가리키는 쪽)
# 머리와 꼬리는 tools/index.html을 그대로 쓰고 본문만 바꾼다(같은 깊이라 상대 경로가 맞다).
import re, json, html, os
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
T = open('tools/index.html', encoding='utf-8').read()
L = open('lessons/index.html', encoding='utf-8').read()
pub = json.load(open('lecture/_published.json', encoding='utf-8'))
lab = dict(re.findall(r'href="\.\./lecture/(B\d\d)/"[^>]*aria-label="([^"]*?) 교안"', L))
def card(B):
    t = json.load(open(f'lecture/_src/{B}.json', encoding='utf-8'))['title_plain']
    return (f'<div class="box" style="margin:0"><p class="small muted" style="margin:0">{B} · {html.escape(lab.get(B, ""))}</p>'
            f'<h3 style="margin:4px 0 8px"><a href="{B}/">{html.escape(t)}</a></h3>'
            f'<div><a class="chip" href="{B}/">수업 화면</a> <a class="chip" href="{B}/{B}_강의교안.pdf">PDF</a></div></div>')
def sec(title, lo, hi):
    return f'<h2>{title}</h2><div class="grid">' + ''.join(card(b) for b in sorted(pub) if lo <= int(b[1:]) <= hi) + '</div>'
main = ('<main id="main">\n<span class="kick">수업 자료</span><h1>강의교안</h1>'
        '<p class="lead">교실 화면에 띄우는 수업 슬라이드예요. 활동지 장에서 「예시 보기」를 누르면 예시 답을 볼 수 있고, PDF에는 활동지 쪽 뒤에 예시 답 쪽이 있어요.</p>'
        + sec('5학년 SW 교과 융합', 1, 14) + sec('6학년 AI 실생활 문제해결', 15, 28) + '\n</main>')
out = re.sub(r'<main.*?</main>', lambda m: main, T, count=1, flags=re.S)
out = re.sub(r'<title>.*?</title>', '<title>강의교안 — 에듀다움</title>', out, count=1, flags=re.S)
out = re.sub(r'(<meta name="description" content=")[^"]*', r'\g<1>에듀다움 블록별 강의교안(수업 화면과 PDF) 모음', out, count=1)
open('lecture/index.html', 'w', encoding='utf-8').write(out)
print(len(pub), 'cards', len(lab), 'labels')
