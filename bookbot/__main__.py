"""python -m bookbot <명령> [책 폴더]

  serve [폴더] [--port N]               책 HTML 과 챗봇 서버 (127.0.0.1 전용)
  build [폴더]                          원고(src/chNN.html) → 책 HTML(<output>) → 챗봇 색인(.bookbot/corpus)
  index [폴더]                          책 HTML → 챗봇 색인만
  new <폴더> --id ID --title 제목        새 책 뼈대(book.toml, src/ch01.html, .gitignore)

폴더를 빼면 현재 폴더. 책 폴더 = book.toml 이 있는 폴더.
"""
import argparse
import os
import sys
from pathlib import Path

from .book import ID_RE, BookError, load_book


def _build(book, also_index=True):
    from .build import BuildError, build
    from .build_index import IndexError_, index
    try:
        n, dia, size = build(book)
        print(f"장 {n}개, 그림 {dia}개, {size:,}자 → {book.html}")
        if also_index:
            ch, files, chars = index(book)
            print(f"색인: 장 {ch}개, 파일 {files}개 + index.md ({chars:,}자) → {book.corpus}")
    except (BuildError, IndexError_) as e:
        sys.exit(f"오류: {e}")


def _index(book):
    from .build_index import IndexError_, index
    try:
        ch, files, chars = index(book)
    except IndexError_ as e:
        sys.exit(f"오류: {e}")
    print(f"색인: 장 {ch}개, 파일 {files}개 + index.md ({chars:,}자) → {book.corpus}")


BOOK_TOML = '''# 『{title}』 — 책 챗봇 설정 (엔진: bookbot, 원고 형식: 엔진의 FORMAT.md)
# 실행: python -m bookbot build  →  python -m bookbot serve

id = "{id}"
title = "{title}"
subtitle = "{subtitle}"
output = "{id}.html"
port = {port}

[prompt]
# 시스템 프롬프트 첫머리: 책이 무엇을 다루는지, 웹에서 믿을 출처는 어디인지
intro = """당신은 『{title}』이라는 책에 대해 묻고 답하는 조수입니다.
이 책은 …을 다룹니다.
다루는 내용: …"""
# 웹 검색을 허용하는 책의 주제(이 밖의 질문은 검색하지 않는다)
topics = "…"
style = "합쇼체, 원리 중심 설명"            # 책을 고칠 때 따를 문체
cite_example = "[1.1 첫 절](#ch01-1)"       # 근거 절 인용 예

# (선택) 책이 분석한 소스 저장소. 있으면 <tool_prefix>_search·<tool_prefix>_read 도구를 준다(읽기 전용)
# [sources]
# name = "MyLib"
# tool_prefix = "mylib"
# [[sources.repo]]
# id = "main"
# label = "MyLib 1.0"
# root = 'D:\\path\\to\\repo'

# (선택) 빌드 때 장 본문의 자리표시를 파일 내용으로 바꾼다
# [build.includes]
# "<!--TABLE-->" = "src/_table.html"
'''

CH01 = '''<section class="chapter" id="ch01">
<h1><span class="num">1장</span> 시작하기</h1>
<p class="lead">이 장에서 다룰 내용을 한두 문장으로 소개합니다.</p>

<h2 id="ch01-1">1.1 첫 절</h2>
<p>본문 문단입니다. <b>강조</b>와 <code>인라인 코드</code>를 쓸 수 있습니다.</p>
<div class="box why"><b>왜 이렇게 만들었나</b> 설계 이유를 설명하는 상자입니다.</div>
<pre><code><span class="src">src/example.py — 예시 함수</span>def hello():
    return "hello"</code></pre>

<h2 id="ch01-2">1.2 둘째 절</h2>
<div class="mermaid">flowchart LR
  A["입력"] --> B["처리"] --> C["출력"]</div>
<p class="cap">그림 1-1 예시 흐름</p>
<ul>
<li>목록 항목</li>
</ul>
</section>
'''


def _new(a):
    root = Path(a.dir).resolve()
    if (root / "book.toml").exists():
        sys.exit(f"오류: 이미 book.toml 이 있습니다: {root / 'book.toml'}")
    if not ID_RE.fullmatch(a.id):
        sys.exit(f"오류: --id 는 영소문자·숫자·-·_ 로 32자 이내여야 합니다: {a.id!r}")
    if '"' in a.title or '"' in a.subtitle:
        sys.exit("오류: 제목·부제에는 큰따옴표를 쓸 수 없습니다.")
    (root / "src").mkdir(parents=True, exist_ok=True)
    (root / "book.toml").write_text(BOOK_TOML.format(id=a.id, title=a.title, subtitle=a.subtitle, port=a.port),
                                    encoding="utf-8")
    if not (root / "src" / "ch01.html").exists():
        (root / "src" / "ch01.html").write_text(CH01, encoding="utf-8")
    gi = root / ".gitignore"
    if not gi.exists():
        gi.write_text("# 챗봇 실행 데이터(대화·사용량·업로드·수정 기록·색인)\n.bookbot/\n.env\n__pycache__/\n", encoding="utf-8")
    print(f"새 책을 만들었습니다: {root}")
    print("다음: book.toml 의 [prompt] intro·topics 를 채우고, src/chNN.html 로 장을 쓴 뒤")
    print(f"      python -m bookbot build {root}  →  python -m bookbot serve {root}")


def main(argv=None):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(prog="python -m bookbot", description="책 HTML 과 책 Q&A 챗봇")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("serve", help="책과 챗봇 서버 실행")
    p.add_argument("book", nargs="?", default=".")
    p.add_argument("--port", type=int, help="book.toml 의 port 대신 쓸 포트")
    for name, help_ in (("build", "책 HTML 과 색인 빌드"), ("index", "색인만 빌드")):
        sub.add_parser(name, help=help_).add_argument("book", nargs="?", default=".")
    p = sub.add_parser("new", help="새 책 뼈대 만들기")
    p.add_argument("dir")
    p.add_argument("--id", required=True)
    p.add_argument("--title", required=True)
    p.add_argument("--subtitle", default="")
    p.add_argument("--port", type=int, default=8772)
    a = ap.parse_args(argv)

    if a.cmd == "new":
        return _new(a)
    try:
        book = load_book(a.book)
    except BookError as e:
        sys.exit(f"오류: {e}")
    if a.cmd == "build":
        _build(book)
    elif a.cmd == "index":
        _index(book)
    elif a.cmd == "serve":
        os.environ["BOOKBOT_BOOK"] = str(book.root)       # server 는 import 할 때 이 책을 읽는다
        if a.port:
            os.environ["CHAT_PORT"] = str(a.port)
        from . import server
        server.main()


if __name__ == "__main__":
    main()
