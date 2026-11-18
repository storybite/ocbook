"""장 조각(src/chNN.html)을 템플릿에 끼워 책 HTML 한 파일(<책>/<output>)로 만든다.

- 템플릿: 책 폴더에 src/template.html 이 있으면 그것을, 없으면 엔진의 assets/template.html 을 쓴다.
  {{title}}·{{subtitle}}·{{book_id}} 를 book.toml 값으로, <!--CHAPTERS--> 를 장 본문으로 바꾼다.
- [build.includes] 의 자리표시(예: <!--KEYBINDS-->)는 장 본문 안에서 그 파일 내용으로 바꾼다.
- 챗봇 화면(assets/chat.html)은 </body> 앞에 넣는다. 챗봇은 python -m bookbot serve 로 열었을 때만 동작한다.
"""
import html as _html
import re
from pathlib import Path

ASSETS = Path(__file__).resolve().parent / "assets"


class BuildError(Exception):
    pass


def fill(text, book):
    return (text.replace("{{title}}", _html.escape(book.title, quote=False))
            .replace("{{subtitle}}", _html.escape(book.subtitle, quote=False))
            .replace("{{book_id}}", book.id))


def build(book):
    """책 HTML 을 쓰고 (장 수, 그림 수, 바이트 수)를 돌려준다. 중복 id 가 있으면 BuildError."""
    chapters = sorted(book.src.glob("ch[0-9][0-9].html"))
    if not chapters:
        raise BuildError(f"장 파일(src/chNN.html)이 없습니다: {book.src}")
    body = "\n".join(p.read_text(encoding="utf-8") for p in chapters)
    for mark, rel in book.includes.items():
        body = body.replace(mark, (book.root / rel).read_text(encoding="utf-8"))
    own = book.src / "template.html"
    template = (own if own.is_file() else ASSETS / "template.html").read_text(encoding="utf-8")
    html = fill(template, book).replace("<!--CHAPTERS-->", body)
    html = html.replace("</body>", fill((ASSETS / "chat.html").read_text(encoding="utf-8"), book) + "\n</body>")

    ids = re.findall(r'id="([^"]+)"', body)
    dups = sorted({i for i in ids if ids.count(i) > 1})
    if dups:
        raise BuildError("중복 id: " + ", ".join(dups))
    book.html.write_text(html, encoding="utf-8")
    return len(chapters), len(re.findall('class="mermaid"', html)), len(html)
