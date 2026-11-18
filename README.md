# bookbot — 책 HTML + 책 Q&A 챗봇 엔진 · 『OpenCode V2 해부』

이 저장소에는 **엔진**(`bookbot/`)과 **책**(`book/`)이 함께 있습니다. 둘은 분리되어 있어서, 책을 바꿀 때 엔진은 그대로 둡니다.
책 한 권 = **`book.toml` + 원고(`src/chNN.html`)**. 엔진이 원고를 한 파일짜리 책 HTML로 조립하고, 본문을 클릭해 묻는 챗봇을 붙입니다. 원고 형식은 [FORMAT.md](FORMAT.md)를 따릅니다.

```
oc2/                      ← 이 저장소
  pyproject.toml          엔진 패키지 설정 (pip install -e .)
  README.md · FORMAT.md   엔진 사용법 · 원고 형식
  bookbot/                엔진: server.py · prompts.py · book.py · build.py · build_index.py · __main__.py
                                assets/ template.html · chat.html · favicon.svg
  book/                   책 『OpenCode V2 해부』 (book/README.md)
    book.toml             제목·포트·프롬프트 조각·(선택) 소스 저장소
    src/ch01.html …       원고 (장마다 한 파일)
    opencode-v2.html      빌드한 책
    .bookbot/             실행 데이터 (git 제외): conversations/ uploads/ usage.jsonl edits.jsonl corpus/ prompts/
```
새 책은 `book/` 옆에 폴더 하나(예: `book2/`)로 두거나, 다른 곳에 두고 같은 엔진으로 띄울 수 있습니다.

## 실행
명령은 **저장소 루트에서** 책 폴더를 인자로 줍니다. 그러면 따로 설치하지 않아도 이 저장소의 엔진(`bookbot/`)을 씁니다.
```bash
pip install fastapi uvicorn claude-agent-sdk python-dotenv pydantic anyio   # 의존 패키지 (한 번만)
python -m bookbot build book      # 원고 → opencode-v2.html → 챗봇 색인(book/.bookbot/corpus)
python -m bookbot serve book      # http://127.0.0.1:8771/
```
- 모델은 Claude Agent SDK로 부르며, SDK가 띄우는 `claude` CLI의 로그인(**Claude Code 구독**)을 씁니다. 미리 `claude`에서 `/login` 해 두세요.
- Codex 모델도 쓰려면 Codex CLI를 설치하고 로그인해 두세요(ChatGPT 로그인). 없으면 Claude 모델만 나옵니다.
- `ANTHROPIC_API_KEY`·`ANTHROPIC_AUTH_TOKEN`이 환경에 있으면 API 과금으로 넘어가므로, 서버가 시작할 때 무시합니다.
- `pip install -e .`로 엔진을 설치하면 어느 폴더에서나 `python -m bookbot`을 쓸 수 있습니다. 다만 설치는 PC에 하나뿐이라, 이 저장소를 복사해 책을 여러 권 두면 설치한 쪽 엔진이 불립니다. 루트에서 실행하면 늘 그 저장소의 엔진을 씁니다.

## 새 책 만들기
이 저장소를 복사해 `book/`만 새 책으로 채웁니다.
1. `book/directions.md`의 **1부(책의 방향성)**를 새 책 것으로 바꿉니다.
2. 그 파일을 프롬프트로 주어 책을 만들게 합니다.

복사한 뒤 무엇을 지우고 무엇을 남기는지, `book.toml` 작성법, 디자인 관례는 `directions.md`의 2부(제작 규칙)에 있습니다.

책을 저장소 밖 다른 곳에 따로 둘 때는 뼈대를 만드는 명령을 씁니다.
```bash
python -m bookbot new D:\books\mybook --id mybook --title "내 책" --subtitle "부제" --port 8772
python -m bookbot build D:\books\mybook
python -m bookbot serve D:\books\mybook
```
- 원고를 손으로 고쳤으면 `build`를 다시 돌리세요. 색인이 책보다 오래되면 서버가 시작할 때 경고합니다.
- 채팅으로 고친 것은 서버가 알아서 다시 빌드합니다.
- 책마다 `port`를 다르게 주면 여러 책을 동시에 띄울 수 있습니다(서버 하나 = 책 한 권).
- 책 HTML을 파일로 직접 열면 책은 읽히지만 챗봇은 동작하지 않습니다.

## book.toml
| 키 | 뜻 |
|---|---|
| `id` | 책 id (영소문자·숫자·`-`·`_`). 브라우저 저장 키와 API의 `book` 값 |
| `title` · `subtitle` | 탭 제목과 목차 위 제목·부제 |
| `output` | 빌드한 책 HTML 파일 이름 (책 폴더 안) |
| `port` | 서버 포트 (`--port`나 `CHAT_PORT`가 있으면 그것) |
| `[prompt] intro` | 시스템 프롬프트 첫머리: 책 소개, 다루는 내용, 웹에서 믿을 출처 |
| `[prompt] topics` | 웹 검색을 허용하는 책의 주제. 이 밖의 질문은 검색하지 않음 |
| `[prompt] style` | 책을 고칠 때 따를 문체 (기본 "합쇼체, 원리 중심 설명") |
| `[prompt] cite_example` | 근거 절 인용 예 (기본 `[1.2 절 제목](#ch01-2)`) |
| `[sources]` (선택) | 책이 분석한 소스 저장소. 있으면 읽기 전용 소스 도구를 줌 (아래) |
| `[build.includes]` (선택) | 빌드 때 장 본문의 자리표시(예: `<!--TABLE-->`)를 파일 내용으로 바꿈 |

`src/template.html`을 책 폴더에 두면 엔진 템플릿 대신 그것을 씁니다. `favicon.svg`도 마찬가지입니다.

### 소스 저장소 (`[sources]`, 선택)
```toml
[sources]
name = "OpenCode"            # 프롬프트에 쓰는 이름
tool_prefix = "opencode"     # → opencode_search · opencode_read
# scope · pattern_example · path_scope_example · path_example : 도구 설명의 예 (선택)
# rules : 시스템 프롬프트의 소스 규칙 전문, edit_rules : 책 수정 때 근거·코드 인용 문단 (비우면 엔진 기본 문안)
[[sources.repo]]
id = "v2"                    # 도구의 version 값
label = "OpenCode 2.3.0 (V2)"
root = 'D:\workspace\cc\opencode\v2\repo'
```
- 도구: `<prefix>_search(version, pattern, path?)`는 `git grep -E`로 추적 파일을 검색합니다(파일당 5줄, 전체 60줄). `<prefix>_read(version, path, start?, end?)`는 줄 번호와 함께 읽습니다(한 번에 400줄, 폴더면 목록).
- 저장소 밖 경로, `.git`, `.env`·키 파일은 거부합니다. 소스를 고치는 도구는 없습니다.
- `[sources]`가 없는 책은 소스 도구와 소스 규칙이 빠지고, 프롬프트의 "책과 소스" 문장이 "책"만 가리키게 바뀝니다.

## 챗봇 기능
- **블록 클릭:** 본문의 문단·표·그림·코드 블록을 클릭하면 💬 팝업이 열리고, 클릭한 위치와 앞뒤 문단을 맥락으로 묻습니다.
  - 절 제목(`<h2>`)을 클릭하면 그 **절 전체**를 맥락으로 묻습니다. 절 본문은 서버가 색인의 절 파일에서 직접 읽어 넣습니다(최대 24,000자).
  - 대화를 나눈 블록과 절 제목 옆에 💬가 붙습니다.
- **책 읽기:** 색인(`index.md`)을 시스템 프롬프트에 미리 넣고, 모델은 `read("<절id>.md")`로 필요한 절만 읽습니다. 도구 호출 한도는 읽기·소스·수정을 합쳐 16회입니다(`CHAT_MAX_TOOL_CALLS`).
- **모델 선택:** 챗 창 제목줄에서 Claude 또는 Codex 모델과 생각 깊이를 고릅니다(브라우저에 기억).
  - 대화 맥락(요약·최근 턴)은 매 요청에 붙여 보내므로, 도중에 Claude ↔ Codex를 바꿔도 대화가 이어집니다.
  - Codex는 사용자 설정을 무시하고(`--ignore-user-config`), 셸은 읽기 전용 샌드박스로 띄웁니다. 책 도구는 서버의 `/mcp/<token>`으로 붙고, 이 주소는 요청 하나 동안만 유효합니다.
  - 비용은 SDK가 알려 주는 **API 환산 금액**이며 실제 청구는 없습니다(구독 사용량에서 차감). Codex는 토큰 수만 표시합니다.
- **웹 검색:** 각 하네스의 내장 웹 도구(Claude: WebSearch·WebFetch, Codex: web_search)를 `topics` 안의 질문에만 씁니다.
- **이미지 붙이기:** Ctrl+V, 끌어 놓기, 📎 버튼으로 질문 하나에 4장까지(PNG·JPEG·WebP·GIF).
  - 큰 이미지는 브라우저가 줄여 보내고, 서버가 형식과 크기(5MB)를 다시 확인합니다.
  - 이미지는 그 질문에만 보내고, `.bookbot/uploads/<대화 id>/`에 저장합니다. 대화를 지우면 함께 지웁니다.
- **책 수정:** 제목줄의 **[✏️ 책 수정]**을 켰을 때만 모델이 원고를 고칩니다. **Ctrl+Enter**로 보내면 켜고 바로 수정 요청으로 보냅니다.
  - 모델은 `read_source("<절id>")`로 원고 HTML을 읽고 `replace_text(id, old, new)`로 고칩니다. 서버는 고친 뒤 책과 색인을 다시 빌드합니다.
  - 기존 `id`를 없애는 수정, 스크립트·이벤트 속성·외부 리소스 태그를 넣는 수정, 빌드가 깨지는 수정은 거절하거나 되돌립니다.
  - 고치면 수정 카드(diff, [고친 곳 보기], [되돌리기])가 나오고, 책 화면은 그 장만 바로 바뀝니다. 한 번 고치면 수정 모드는 저절로 꺼집니다.
  - 기록은 `.bookbot/edits.jsonl`에 남습니다(`old`·`new` 원문). 되돌리기는 이 기록으로 합니다. 그 뒤 같은 곳을 또 고쳤으면 거절합니다.
- **답변 중지(Esc)와 새 대화(Ctrl+N):**
  - Esc를 누르면 화면은 그 자리에서 끝나고 바로 입력할 수 있습니다.
  - 서버는 Claude에는 interrupt를 보내고(사용량 기록), Codex는 프로세스를 끝냅니다.
  - 멈춘 답은 `⏹ 중지함`으로 저장되고, 다음 질문에 "사용자가 답변 도중 중지함"이 함께 갑니다.
  - 멈춘 직후 보낸 질문은 서버가 앞 턴을 저장한 뒤에 보냅니다(`앞 답변 정리 중`).
  - Ctrl+N은 [새 대화]와 같습니다. 단 일반 브라우저 탭에서는 브라우저가 이 키를 먼저 가져가므로, `chrome --app=http://127.0.0.1:<port>/`처럼 앱 창으로 열 때만 동작합니다.

## 환경 변수
| 이름 | 기본 | 뜻 |
|---|---|---|
| `CHAT_MODEL` | `claude-opus-5-5` | 기본 모델 |
| `CHAT_REASONING_EFFORT` | `xhigh` | 기본 생각 깊이 |
| `CHAT_PORT` | book.toml `port` | 포트 |
| `CHAT_MAX_TOOL_CALLS` | 16 | 질문 하나의 도구 호출 한도 |
| `CODEX_BIN` | PATH의 `codex` | Codex 실행 파일 |

`.env`는 책 폴더와 엔진 폴더의 것을 차례로 읽습니다.

## 보안 주의
- 기록 API(`/api/usage`, `/api/conversations`), 책 수정(채팅·`/api/edits`), 업로드에는 **인증이 없습니다**. 서버는 127.0.0.1에만 열립니다. 외부에 공개하면 누구나 원고를 고칠 수 있습니다.
- 소스 도구는 읽기 전용이며, 설정한 저장소 밖과 비밀 파일은 읽지 않습니다.

## 엔진 구조
| 파일 | 역할 |
|---|---|
| `bookbot/__main__.py` | `python -m bookbot serve·build·index·new` |
| `bookbot/book.py` | `book.toml` 읽기·검증 → `Book` |
| `bookbot/prompts.py` | 시스템 프롬프트 공통 틀(답변 규칙·책 수정 규칙·Codex 안내)에 책 조각을 끼움 |
| `bookbot/server.py` | 책 HTML과 챗봇 API(SSE 스트리밍, 대화 압축, 도구 한도·예산, 책 수정·되돌리기, 중지, 이미지) |
| `bookbot/build.py` | 원고 → 책 HTML (템플릿·includes·챗 화면 삽입, 중복 id 검사) |
| `bookbot/build_index.py` | 책 HTML → 절 단위 마크다운과 색인(`index.md`) |
| `bookbot/assets/` | 기본 템플릿, 챗 화면(`chat.html`), favicon |

Claude에는 시스템 프롬프트를 `--system-prompt` 대신 파일(`.bookbot/prompts/<해시>.md`)로 넘깁니다. Windows 명령줄 32,767자 한도 때문입니다.
