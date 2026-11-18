"""keybind.ts의 Definitions에서 키바인드 표(HTML 조각 _keybinds.html)를 만든다."""
import re, html, pathlib, sys

src = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")
body = src[src.index("export const Definitions"):src.index("} satisfies Record")]
pat = re.compile(r'^\s*"?([\w.\-]+)"?:\s*keybind\(\s*(.+?),\s*"((?:[^"\\]|\\.)*)"\s*\),?\s*$', re.M)
rows = pat.findall(body)
total = len(re.findall(r"keybind\(", body))
groups = {}
for name, default, desc in rows:
    default = default.strip()
    if default == "LeaderDefault":
        default = '"ctrl+x"'
    groups.setdefault(name.split(".")[0], []).append((name, default.strip('"'), desc))
out = []
for g, items in groups.items():
    out.append(f'<h3>{html.escape(g)} ({len(items)}개)</h3><table><tr><th>이름</th><th>기본값</th><th>설명</th></tr>')
    for n, d, desc in items:
        out.append(f"<tr><td><code>{html.escape(n)}</code></td><td><code>{html.escape(d)}</code></td><td>{html.escape(desc)}</td></tr>")
    out.append("</table>")
(pathlib.Path(__file__).parent / "_keybinds.html").write_text("\n".join(out), encoding="utf-8")
print(f"parsed {len(rows)} / {total} keybind() calls, {len(groups)} groups")
missing = set(re.findall(r'^\s*"?([\w.\-]+)"?:\s*keybind\(', body, re.M)) - {r[0] for r in rows}
if missing:
    print("UNPARSED:", sorted(missing))
