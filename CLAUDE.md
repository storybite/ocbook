# OpenCode V2 책 프로젝트

## OpenCode 소스코드

OpenCode 버전별 소스코드는 아래 로컬 저장소를 참조한다. 책을 쓰거나 고칠 때, OpenCode 동작을 설명할 때 근거는 기억이나 웹 문서가 아니라 이 소스에서 찾는다.

| 버전 | 경로 | git 브랜치 |
|---|---|---|
| V1 | `D:\workspace\cc\opencode\v1\repo` | `v1` |
| V2 | `D:\workspace\cc\opencode\v2\repo` | `v2` |

- 저장소 루트는 각 버전 폴더 바로 아래가 아니라 `repo\` 이다.

## 책 챗봇 엔진

책 HTML 빌드와 책 Q&A 챗봇은 이 저장소의 **bookbot 엔진**(`bookbot\` 패키지, 루트의 `pyproject.toml`로 `pip install -e .` 설치)이 맡는다. 책 쪽 `book\`에는 `book.toml`(책 설정·프롬프트 조각·소스 저장소)과 원고 `src\chNN.html`만 둔다. 엔진 사용법은 루트 `README.md`, 원고 형식은 `FORMAT.md`.

- 빌드: `book\`에서 `python -m bookbot build` (원고 → `opencode-v2.html` → 색인 `.bookbot\corpus`)
- 실행: `book\`에서 `python -m bookbot serve` → http://127.0.0.1:8771/
- 챗봇 기능이나 화면을 고칠 때는 `bookbot\`(엔진)을 고치고, 책 고유 문구는 `book\book.toml`에 둔다.
- 저장소 루트에서 `python -m bookbot`을 실행해도 된다(`bookbot\`이 곧 패키지). 엔진 폴더를 `bookbot\bookbot\`처럼 한 겹 더 감싸면 실행 위치에 따라 다른 `bookbot`을 import하므로 그렇게 두지 않는다.
- 챗봇 실행 데이터(대화·사용량·수정 기록·업로드)는 `book\.bookbot\`에 있고 git에서 제외된다.
