# OpenCode V2 해부 — 책 원고

『OpenCode V2 해부』(원리로 읽는 코딩 에이전트 하네스 · v2.3.0 기준)의 원고입니다. 책 HTML 빌드와 책 Q&A 챗봇은 저장소 루트의 **bookbot 엔진**(`../bookbot/`)이 맡고, 이 폴더에는 책에 속한 것만 둡니다.

## 실행
```bash
pip install -e .                         # 저장소 루트에서, 엔진 설치 (한 번만)
cd book
python -m bookbot build                  # src/chNN.html → opencode-v2.html → 챗봇 색인(.bookbot/corpus)
python -m bookbot serve                  # http://127.0.0.1:8771/
```
챗봇 기능(블록 클릭 질문, 모델 선택, 이미지, 책 수정·되돌리기, Esc 중지)과 보안 주의는 루트의 `README.md`를, 원고 형식은 루트의 `FORMAT.md`를 보세요.

## 이 폴더
| 경로 | 역할 |
|---|---|
| `book.toml` | 책 설정: 제목·포트(8771)·챗봇 프롬프트 조각(책 소개·웹 검색 주제·인용 형식)·OpenCode 소스 저장소 |
| `src/ch01.html` ~ `ch20.html` | 원고 (장마다 한 파일. `ch20.html`은 부록 A, 장 id는 `appA`) |
| `src/_keybinds.html` · `src/gen_keybinds.py` | 17장 키바인드 표와 그 생성 스크립트(OpenCode 소스에서 뽑음). `book.toml`의 `<!--KEYBINDS-->`로 끼움 |
| `opencode-v2.html` | 빌드한 책 |
| `.bookbot/` | 챗봇 실행 데이터(git 제외): 대화, 사용량, 수정 기록, 업로드 이미지, 색인 |
| `directions.md` · `review/` | 집필 지침과 Codex 검토 기록 |

## OpenCode 소스
챗봇과 집필은 아래 로컬 저장소를 근거로 씁니다(읽기 전용). 챗봇 도구는 `opencode_search`·`opencode_read`입니다.
- V2 = OpenCode 2.3.0: `D:\workspace\cc\opencode\v2\repo`
- V1 = OpenCode 1.19.5: `D:\workspace\cc\opencode\v1\repo`
