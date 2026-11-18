"""챕터 조각(chNN.html)을 template.html에 끼워 book/opencode-v2.html 한 파일로 만든다.
_chat.html(책 Q&A 챗봇 화면)은 </body> 앞에 넣는다. 챗봇은 python book/server.py 로 열었을 때만 동작한다."""
import pathlib, re, sys

src = pathlib.Path(__file__).parent
out = src.parent / "opencode-v2.html"
chapters = sorted(src.glob("ch[0-9][0-9].html"))
body = "\n".join(p.read_text(encoding="utf-8") for p in chapters)
body = body.replace("<!--KEYBINDS-->", (src / "_keybinds.html").read_text(encoding="utf-8"))
html = (src / "template.html").read_text(encoding="utf-8").replace("<!--CHAPTERS-->", body)
html = html.replace("</body>", (src / "_chat.html").read_text(encoding="utf-8") + "\n</body>")
out.write_text(html, encoding="utf-8")

ids = re.findall(r'id="([^"]+)"', body)
dups = {i for i in ids if ids.count(i) > 1}
print(f"{len(chapters)} chapters, {len(re.findall('class=\"mermaid\"', html))} diagrams, {len(html):,} bytes -> {out}")
if dups:
    print("DUPLICATE IDS:", dups)
    sys.exit(1)
