"""책 HTML을 절 단위 마크다운과 색인(index.md)으로 나눈다.

사용: python book/bookbot/build_index.py
출력: book/bookbot/corpus/  (index.md, <장id>.md, <절id>.md)

이 책은 장이 <section class="chapter" id="chNN">이고, 절은 따로 감싸지 않고 <h2 id="chNN-M">부터 다음 h2 앞까지다.
"""
import re
import sys
from collections import Counter
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path

HERE = Path(__file__).resolve().parent
BOOK_HTML = HERE.parent / "opencode-v2.html"
CORPUS = HERE / "corpus"
TITLE = "OpenCode V2 해부"

VOID = {"br", "hr", "img", "meta", "link", "input"}


class Node:
    def __init__(self, tag, attrs=None, parent=None):
        self.tag, self.attrs, self.parent, self.children = tag, dict(attrs or []), parent, []

    def cls(self):
        return (self.attrs.get("class") or "").split()

    def text(self):
        return "".join(c if isinstance(c, str) else c.text() for c in self.children)


class TreeBuilder(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = self.cur = Node("root")

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs, self.cur)
        self.cur.children.append(node)
        if tag not in VOID:
            self.cur = node

    def handle_endtag(self, tag):
        n = self.cur
        while n is not self.root and n.tag != tag:
            n = n.parent
        if n is not self.root:
            self.cur = n.parent

    def handle_data(self, data):
        self.cur.children.append(data)


def walk(node, pred):
    for c in node.children:
        if isinstance(c, Node):
            if pred(c):
                yield c
            yield from walk(c, pred)


def squash(s):
    return re.sub(r"\s+", " ", s).strip()


def inline(node):
    """문단 안의 인라인 요소를 마크다운으로."""
    out = []
    for c in node.children:
        if isinstance(c, str):
            out.append(c)
        elif c.tag == "code":
            out.append("`" + c.text() + "`")
        elif c.tag in ("b", "strong"):
            out.append("**" + inline(c) + "**")
        elif c.tag == "br":
            out.append("\n")
        else:
            out.append(inline(c))
    return "".join(out)


def table_md(node):
    rows = []
    for tr in walk(node, lambda n: n.tag == "tr"):
        cells = [squash(inline(td)).replace("|", "\\|") for td in tr.children
                 if isinstance(td, Node) and td.tag in ("th", "td")]
        rows.append("| " + " | ".join(cells) + " |")
    if rows:
        rows.insert(1, "|" + "---|" * rows[0].count(" | ") + "---|")
    return "\n".join(rows)


def list_md(node, ordered):
    items = [c for c in node.children if isinstance(c, Node) and c.tag == "li"]
    return "\n".join((f"{i}. " if ordered else "- ") + squash(inline(li)) for i, li in enumerate(items, 1))


def block_md(node):
    """장 직계 자식 블록 하나를 마크다운으로."""
    tag, cls = node.tag, node.cls()
    if tag == "div" and "mermaid" in cls:
        src = "".join(c if isinstance(c, str) else ("<br/>" if c.tag == "br" else c.text()) for c in node.children)
        return "[다이어그램]\n```mermaid\n" + src.strip() + "\n```"
    if tag == "pre":
        src = next(walk(node, lambda n: "src" in n.cls()), None)     # <pre><span class="src">파일</span>…
        head = f"(파일: {squash(src.text())})\n" if src else ""
        body = node.text()
        if src:
            body = body.replace(src.text(), "", 1)
        return head + "```\n" + body.strip("\n").rstrip() + "\n```"
    if tag == "table":
        return table_md(node)
    if tag in ("ul", "ol"):
        return list_md(node, tag == "ol")
    if tag == "div" and "box" in cls:
        kind = {"why": "왜", "warn": "주의", "note": "참고"}.get(next((c for c in cls if c != "box"), ""), "")
        label = next((c for c in node.children if isinstance(c, Node) and c.tag == "b"), None)
        rest = Node("div")
        rest.children = [c for c in node.children if c is not label]
        head = f"{kind}: {squash(label.text())}" if label is not None else kind
        return f"> **[{head}]** " + squash(inline(rest))
    if tag == "p" and "cap" in cls:
        return "(" + squash(node.text()) + ")"
    if tag in ("h3", "h4"):
        return "### " + squash(node.text())
    if tag == "blockquote":
        return "> " + squash(inline(node))
    return squash(inline(node))


def blocks_md(nodes):
    return "\n\n".join(md for md in (block_md(n) for n in nodes) if md)


def keywords(nodes, limit=8):
    cnt = Counter()
    for top in nodes:
        for n in [top, *walk(top, lambda n: n.tag in ("code", "b", "strong"))]:
            if n.tag not in ("code", "b", "strong") or (n.parent is not None and n.parent.tag == "pre"):
                continue  # 코드 블록 본문은 제외
            t = squash(n.text())
            if 2 <= len(t) <= (40 if n.tag == "code" else 20):  # 굵은 글씨는 짧은 용어만
                cnt[t] += 1
    return [k for k, _ in cnt.most_common(limit)]


def first_sentence(nodes, width=90):
    p = next((n for n in nodes if n.tag == "p" and "cap" not in n.cls()), None)
    s = squash(p.text()) if p else ""
    return s[:width] + ("…" if len(s) > width else "")


def split_chapter(art):
    """(장 제목, 머리말 블록들, [(절id, 절 제목, 블록들)])"""
    title, lead, secs = "", [], []
    for c in art.children:
        if not isinstance(c, Node):
            continue
        if c.tag == "h1":
            title = squash(c.text())
        elif c.tag == "h2" and c.attrs.get("id"):
            secs.append((c.attrs["id"], squash(c.text()), []))
        elif "pager" in c.cls():
            continue
        else:
            (secs[-1][2] if secs else lead).append(c)
    return title, lead, secs


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    if not BOOK_HTML.is_file():
        sys.exit(f"책 HTML이 없습니다. 먼저 python book/src/build.py 를 실행하세요: {BOOK_HTML}")
    tb = TreeBuilder()
    tb.feed(BOOK_HTML.read_text(encoding="utf-8"))
    chapters = list(walk(tb.root, lambda n: n.tag == "section" and "chapter" in n.cls()))
    if not chapters:
        sys.exit("책 HTML에서 section.chapter를 찾지 못했습니다.")

    CORPUS.mkdir(exist_ok=True)
    for old in CORPUS.glob("*.md"):
        old.unlink()

    mtime = datetime.fromtimestamp(BOOK_HTML.stat().st_mtime).isoformat(timespec="seconds")
    index = [
        f"# 『{TITLE}』 색인",
        f"<!-- source_mtime: {mtime} -->",
        "",
        '필요한 절의 파일을 read("<id>.md")로 읽으세요. 형식: `- <id> | <절 제목> | 핵심어 | 첫 문장`',
        "장 머리말(장 소개)은 read(\"<장id>.md\")로 읽을 수 있습니다.",
    ]
    n_files = 0
    for art in chapters:
        ch_id = art.attrs["id"]
        ch_title, lead, secs = split_chapter(art)
        (CORPUS / f"{ch_id}.md").write_text(f"# {ch_title}\n\n(장 머리말)\n\n{blocks_md(lead)}\n", encoding="utf-8")
        n_files += 1
        index += ["", f"## {ch_title}  (장 머리말: {ch_id}.md)"]
        for sid, title, nodes in secs:
            (CORPUS / f"{sid}.md").write_text(
                f"# {title}\n\n소속: {ch_title} / 링크: #{sid}\n\n{blocks_md(nodes)}\n", encoding="utf-8")
            n_files += 1
            index.append(f"- {sid} | {title} | {', '.join(keywords(nodes))} | {first_sentence(nodes)}")

    (CORPUS / "index.md").write_text("\n".join(index) + "\n", encoding="utf-8")
    text = (CORPUS / "index.md").read_text(encoding="utf-8")
    print(f"장 {len(chapters)}개, 파일 {n_files}개 + index.md ({len(text):,}자) → {CORPUS}")


if __name__ == "__main__":
    main()
