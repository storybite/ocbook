"""책 한 권의 설정(book.toml)을 읽어 엔진이 쓰는 Book 으로 만든다.

책 폴더 = book.toml 이 있는 폴더. 원고는 <책>/src/chNN.html, 빌드 결과는 <책>/<output>,
실행 데이터(대화·사용량·수정 기록·색인·업로드)는 <책>/.bookbot/ 에 둔다. 형식은 FORMAT.md 를 따른다.
"""
import re
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

ID_RE = re.compile(r"[a-z0-9][a-z0-9_-]{0,31}")
PREFIX_RE = re.compile(r"[a-z][a-z0-9_]{0,23}")


class BookError(Exception):
    """book.toml 이 없거나 잘못됨. 메시지는 사용자에게 그대로 보여 준다."""


@dataclass(frozen=True)
class Repo:
    id: str            # 도구의 version 값 (예: "v2")
    label: str         # 사람이 읽는 이름 (예: "OpenCode 2.3.0 (V2)")
    root: Path         # 저장소 폴더 (읽기 전용으로만 쓴다)
    desc: str          # 도구 스키마의 version 설명 조각 (예: "v2 = OpenCode 2.x(2.3.0)")


@dataclass(frozen=True)
class Sources:
    """책이 분석한 소스 저장소(선택). 있으면 <prefix>_search·<prefix>_read 도구를 준다."""
    name: str                  # 소스 이름 (예: "OpenCode")
    prefix: str                # 도구 이름 앞부분 (예: "opencode" → opencode_search)
    repos: tuple[Repo, ...]
    scope: str                 # 검색 도구 설명의 괄호 안 (예: "책이 분석한 v2=2.3.0, v1=1.19.5")
    pattern_example: str       # 검색 패턴 예
    path_scope_example: str    # 검색 범위 예
    path_example: str          # 읽기 경로 예
    rules: str                 # 시스템 프롬프트의 소스 규칙(없으면 엔진 기본 문안)
    edit_rules: str            # 책 수정 규칙 중 근거·코드 인용 문단(없으면 엔진 기본 문안)


@dataclass(frozen=True)
class Book:
    root: Path
    id: str
    title: str
    subtitle: str
    output: str
    port: int
    intro: str                 # 시스템 프롬프트 첫머리: 책 소개와 웹 출처 안내
    topics: str                # 웹 검색을 허용하는 책의 주제 목록
    style: str                 # 책 수정 때 따를 문체
    cite_example: str          # 근거 절 인용 예: [7.2 SessionInbox](#ch07-2)
    includes: dict = field(default_factory=dict)   # 빌드 때 장 본문의 자리표시 → 파일(책 폴더 기준)
    sources: Sources | None = None

    @property
    def src(self):
        return self.root / "src"

    @property
    def data(self):
        return self.root / ".bookbot"

    @property
    def html(self):
        return self.root / self.output

    @property
    def corpus(self):
        return self.data / "corpus"


def _need(d, key, where):
    v = d.get(key)
    if v is None or (isinstance(v, str) and not v.strip()):
        raise BookError(f"book.toml 의 {where}{key} 가 비어 있습니다.")
    return v


def load_book(path) -> Book:
    """책 폴더(또는 그 안의 book.toml)를 받아 Book 을 돌려준다. 잘못되면 BookError."""
    p = Path(path).resolve()
    f = p if p.name == "book.toml" else p / "book.toml"
    if not f.is_file():
        raise BookError(f"book.toml 이 없습니다: {f}\n새 책은 python -m bookbot new <폴더> 로 만듭니다.")
    try:
        d = tomllib.loads(f.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as e:
        raise BookError(f"book.toml 을 읽지 못했습니다: {e}") from e
    root = f.parent
    bid = _need(d, "id", "")
    if not ID_RE.fullmatch(bid):
        raise BookError(f"book.toml 의 id 는 영소문자·숫자·-·_ 로 32자 이내여야 합니다: {bid!r}")
    output = _need(d, "output", "")
    if "/" in output or "\\" in output or not output.endswith(".html"):
        raise BookError(f"book.toml 의 output 은 책 폴더 안의 .html 파일 이름이어야 합니다: {output!r}")
    pr = d.get("prompt") or {}
    title = _need(d, "title", "")
    includes = (d.get("build") or {}).get("includes") or {}
    for mark, rel in includes.items():
        if not (root / rel).is_file():
            raise BookError(f"book.toml [build.includes] 의 파일이 없습니다: {mark} → {rel}")

    sources = None
    if s := d.get("sources"):
        prefix = _need(s, "tool_prefix", "[sources] ")
        if not PREFIX_RE.fullmatch(prefix):
            raise BookError(f"[sources] tool_prefix 는 영소문자로 시작하는 24자 이내 이름이어야 합니다: {prefix!r}")
        repos = []
        for r in s.get("repo") or []:
            rid = _need(r, "id", "[[sources.repo]] ")
            root_dir = Path(_need(r, "root", "[[sources.repo]] ")).expanduser()
            if not root_dir.is_dir():
                raise BookError(f"소스 저장소 폴더가 없습니다: {rid} → {root_dir}")
            label = r.get("label") or rid
            repos.append(Repo(rid, label, root_dir, r.get("desc") or f"{rid} = {label}"))
        if not repos:
            raise BookError("[sources] 에는 [[sources.repo]] 가 하나 이상 있어야 합니다.")
        if len({r.id for r in repos}) != len(repos):
            raise BookError("[[sources.repo]] 의 id 가 겹칩니다.")
        name = s.get("name") or prefix
        sources = Sources(
            name=name, prefix=prefix, repos=tuple(repos),
            scope=s.get("scope") or ", ".join(r.label for r in repos),
            pattern_example=s.get("pattern_example") or "함수이름, class \\w+Service",
            path_scope_example=s.get("path_scope_example") or "src, src/**/*.ts",
            path_example=s.get("path_example") or "src/index.ts, src",
            rules=s.get("rules") or "", edit_rules=s.get("edit_rules") or "")

    return Book(
        root=root, id=bid, title=title, subtitle=d.get("subtitle") or "", output=output,
        port=int(d.get("port") or 8771),
        intro=_need(pr, "intro", "[prompt] ").strip("\n"),
        topics=_need(pr, "topics", "[prompt] "),
        style=pr.get("style") or "합쇼체, 원리 중심 설명",
        cite_example=pr.get("cite_example") or "[1.2 절 제목](#ch01-2)",
        includes=dict(includes), sources=sources)
