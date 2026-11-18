# 검토 요청: OpenCode V2 해부 (HTML 책)

## 검토 대상
- 원고(장별 조각): `D:\workspace\cc\book\oc2\book\src\ch01.html` ~ `ch18.html`
- 빌드 결과(한 파일): `D:\workspace\cc\book\oc2\book\opencode-v2.html` (src를 `build.py`로 합친 것. 수정은 src 기준으로 제안)
- 작성 지침: `D:\workspace\cc\book\oc2\book\directions.md`

## 근거 자료
- OpenCode v2.3.0 소스: `D:\workspace\cc\opencode\v2\repo` (특히 `packages/core/src`, `packages/schema/src`, `specs/v2`, `AGENTS.md`)
- OpenCode v1.19.5 소스: `D:\workspace\cc\opencode\v1\repo`

## 검토 관점 (우선순위 순)
1. **사실 오류**: 본문의 파일 경로, 함수/상수 이름, 기본값, 수치, 동작 설명이 v2.3.0 소스와 다른 곳. 반드시 소스 파일·줄을 근거로 제시.
2. **원리 설명의 타당성**: "왜 이렇게 설계했나" 상자(class="box why")의 설명이 소스·명세의 의도와 어긋나거나 근거 없이 추측한 곳.
3. **설정 누락**: 16장 설정 총람에서 빠진 설정 키·환경 변수·플래그·CLI 옵션.
4. **이해를 막는 설명**: 독자가 오해할 만한 표현, 순서가 뒤바뀐 설명, 다이어그램과 본문의 불일치.
5. 형식: 합쇼체 위반, 깨진 HTML.

## 출력 방식
- 파일은 수정하지 마십시오. 읽기만 하십시오.
- 결과를 `D:\workspace\cc\book\oc2\book\review\codex-review.md`에 한국어로 작성하십시오.
- 각 지적은 다음 형식으로:
  - `[심각도: 높음/중간/낮음] 장·절 — 지적 요약`
  - 본문의 문제 문장(짧게 인용)
  - 근거(소스 경로:줄, 인용)
  - 제안 수정
- 확신이 없는 지적은 "추정"이라고 표시하십시오. 칭찬이나 일반론은 쓰지 마십시오.
- 작성을 마치면 "REVIEW DONE"이라고만 답하십시오.
