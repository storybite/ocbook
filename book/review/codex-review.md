# OpenCode V2 원고 검토

기준: 로컬 V2 저장소 `D:/workspace/cc/opencode/v2/repo`, 커밋 `a6b15d33da`(`release: v2.3.0`). 아래 `V2/`는 이 경로를 뜻합니다. 원고 위치는 `book/src/` 기준입니다. 원고와 빌드 파일은 수정하지 않았습니다.

## 1. [심각도: 높음] 12.3·17.5 — 리뷰어 예제의 셸 권한이 허용 목록으로 제한되지 않습니다

- 본문의 문제 문장: `ch12.html`의 리뷰어는 `edit`을 deny하고 `shell: git diff *`만 allow합니다. `ch17.html`은 이를 “shell은 git diff *, git log *만 allow”라고 설명합니다.
- 근거: `V2/packages/schema/src/agent.ts:38`의 `Info.default`는 `permissions`에 `{ action: "*", resource: "*", effect: "allow" }`를 넣습니다(47행). `V2/packages/core/src/agent.ts:83`은 새 에이전트를 `Info.default(id)`로 만들고, `V2/packages/core/src/config/plugin/agent.ts:102`는 설정 규칙을 `agent.permissions.push(...)`로 덧붙입니다. 따라서 예제에는 다른 셸 명령을 막는 규칙이 없습니다. 파일 편집 도구를 막아도 셸을 통한 쓰기는 여전히 허용됩니다.
- 제안 수정: 리뷰어의 셸 규칙 앞에 `{ "action": "shell", "resource": "*", "effect": "deny" }`를 넣고 그 뒤에 허용할 명령을 나열하십시오. 17.5절의 플러그인 예시에도 같은 순서를 명시하십시오.

## 2. [심각도: 높음] 16.1·16.17 — 서비스 설정 파일과 서비스 등록 파일을 혼동합니다

- 본문의 문제 문장: “service.json — ~/.local/state/opencode/service.json — 백그라운드 서비스 설정·등록(opencode service get/set)”
- 근거: `V2/packages/cli/src/services/service-config.ts:122`는 등록 파일을 `path.join(global.state, name)`으로 정하지만, 130행은 설정 파일을 `configFile: path.join(global.config, name)`으로 따로 정합니다. 155~157행의 설정 읽기는 `fs.readFileString(configFile)`을 사용합니다. 등록 파일은 클라이언트 탐색용 URL·PID·버전·비밀번호이고, `disabled`, `hostname`, `env` 등을 저장하는 설정 파일과 역할이 다릅니다.
- 제안 수정: 표를 두 행으로 분리하십시오. 서비스 설정은 기본 `~/.config/opencode/service.json`, 등록 정보는 기본 `~/.local/state/opencode/service.json`으로 설명하고, 16.17절은 전자의 스키마라는 점을 명시하십시오. 등록 파일을 직접 편집해서 서비스 설정을 바꾸도록 오해하게 해서는 안 됩니다.

## 3. [심각도: 중간] 14.5 — 서버의 플러그인 로딩 대기에 실제 예외가 있습니다

- 본문의 문제 문장: “서버는 플러그인 로딩을 기다리지 않습니다(AGENTS.md). ‘지금 로드된 것으로 답한다.’”
- 근거: `V2/packages/server/src/location.ts:36`의 주석은 정책 적용 전 프로바이더가 노출되는 문제 때문에 일부 엔드포인트만 기다린다고 설명합니다. 39~48행은 `Plugin.awaitActivation`에 `duration: "5 seconds"`를 적용하고 시간 초과 시 `ServiceUnavailableError`를 반환합니다. 실제 호출 예는 `V2/packages/server/src/handlers/model.ts:13`, `provider.ts:14`, `generate.ts:27`, `voice.ts:22`, `websearch.ts:22`입니다. 루트 `AGENTS.md:206`도 이 임시 예외를 명시합니다.
- 제안 수정: 일반 원칙 뒤에 모델 목록·기본 모델·프로바이더 목록·생성·음성·웹 검색의 임시 예외와 5초 시간 초과를 적으십시오. “503으로 바꾸지 않는다”는 일반 원칙만으로 현행 동작을 설명하지 마십시오.

## 4. [심각도: 중간] 6.2 — 이벤트 카탈로그의 개수와 영속성 분류가 틀립니다

- 본문의 문제 문장: “세션 영속 이벤트 카탈로그”, “세션 이벤트 53종”, 표에 포함된 `text.delta`, `reasoning.delta`, `tool.input.delta`, `tool.progress`, `compaction.delta`, `usage.updated`.
- 근거: `V2/packages/schema/src/session-event.ts:172`, 420, 459, 503, 536, 610은 각각 해당 이벤트를 `Event.ephemeral`로 정의합니다. 350행에는 표에서 빠진 영속 이벤트 `session.step.first_token`이 있습니다. 이 파일의 이벤트 선언은 영속 48개, 휘발 6개로 총 54개이며, 721~727행은 `durability`로 두 카탈로그를 분리합니다.
- 제안 수정: 표 제목을 “세션 이벤트 카탈로그”로 바꾸고 영속·휘발 열을 추가하십시오. `session.step.first_token`을 넣고 총 54개(영속 48개·휘발 6개)로 고치십시오. 영속 로그에서 재생할 수 있는 이벤트를 별도로 구분하십시오.

## 5. [심각도: 중간] 6.2 — Started 이벤트에도 전체 텍스트가 있다는 설명은 틀립니다

- 본문의 문제 문장: “대신 *.Started/*.Ended 이벤트가 전체 텍스트를 담습니다.”
- 근거: `V2/packages/schema/src/session-event.ts:408`의 `Text.Started`에는 세션·assistant 메시지 ID와 `ordinal`만 있고 `text`가 없습니다. 431~440행의 `Text.Ended`에 `text: Schema.String`이 있습니다. 추론도 446행의 `Reasoning.Started`와 470행의 `Reasoning.Ended`가 같은 구분을 따릅니다. 419행 주석은 “Text.Ended is the replayable full-value boundary”라고 명시합니다.
- 제안 수정: “Started는 파트의 시작과 식별 정보를 기록하고, Ended가 전체 텍스트를 기록합니다. Delta는 실시간 전용입니다”로 바꾸십시오.

## 6. [심각도: 중간] 9.6 — 압축 요약의 헤딩 검증을 실제보다 엄격하게 설명합니다

- 본문의 문제 문장: “템플릿 헤딩을 빠뜨리면 한 번 재촉(NUDGE), 두 번째도 빠뜨리면 실패.”
- 근거: `V2/packages/core/src/session/compaction.ts:486`은 템플릿 헤딩 목록을 만들고, 487행은 `text.split("\n").some((line) => headings.includes(line.trim()))`으로 검사합니다. 즉 헤딩 중 하나만 있어도 통과합니다. 505행과 513행의 `if (filled(...)) return ...`도 이 조건을 그대로 사용합니다. 173행의 템플릿 자체도 해당하지 않는 절은 생략할 수 있다고 적습니다.
- 제안 수정: “템플릿 헤딩이 하나도 없으면 한 번 재촉하고, 재응답에도 하나도 없으면 실패합니다”로 고치십시오. 모든 필수 헤딩의 존재나 요약의 완전성을 검증한다는 인상을 없애십시오.

## 7. [심각도: 중간] 12.3·15.3 — 에이전트 샘플링 설정의 호환 동작과 설계 이유를 잘못 단정합니다

- 본문의 문제 문장: “V2에서는 에이전트의 temperature/top_p가 효과 없습니다.” 15.3절의 왜 상자는 “같은 에이전트가 모델을 바꿔도 잘못된 파라미터가 따라가지 않습니다”라고 설명합니다.
- 근거: `V2/packages/core/src/v1/config/migrate.ts:36`의 `migrateAgent`는 39~40행에서 `temperature`, `top_p`를 본문에 넣고, 45행에서 `request: { body }`로 이전합니다. 마크다운 에이전트도 `V2/packages/core/src/config/plugin/agent.ts:165`에서 레거시 형식을 판별하고 177행 이후 `ConfigMigrateV1.migrateAgent`를 호출합니다. 한편 같은 파일 92~94행은 V2 에이전트의 `request.body`를 그대로 병합하므로 에이전트 수준 샘플링 파라미터 자체가 금지된 구조도 아닙니다.
- 제안 수정: “V2 네이티브 스키마에서는 최상위 temperature/top_p 대신 request.body를 씁니다. V1 형식으로 해석되는 설정은 자동 이전됩니다”로 구분하십시오. 왜 상자의 ‘모델을 바꾸어도 파라미터가 따라가지 않는다’는 보장은 삭제하고, 모델별 변형을 활용하라는 설명으로 바꾸십시오. 샘플링 키 이동의 설계 동기를 별도 명세 없이 단정하는 부분은 **추정**으로 표시하십시오.

## 8. [심각도: 중간] 16.4 — write·patch를 독립 실행 권한 action처럼 나열합니다

- 본문의 문제 문장: “action 이름: read, edit(write·patch 포함), write, patch, …”
- 근거: `V2/packages/core/src/tool/plugin/write.ts:47`은 `fileWrite.write(...)`를 호출하고, `V2/packages/core/src/file-write.ts:74`의 승인은 `action: "edit"`입니다. `V2/packages/core/src/tool/plugin/patch.ts:192`도 `action: "edit"`을 검사합니다. V1 호환 키는 `V2/packages/core/src/v1/config/migrate.ts:29`의 `normalizeAction`이 `write`, `patch`, `apply_patch`를 `edit`으로 바꿉니다.
- 제안 수정: 현행 실행 권한 action 목록에서 `write`, `patch`를 빼고 “도구 이름은 write/patch여도 파일 변경 권한은 edit으로 검사한다”고 적으십시오. V1 별칭 정규화는 16.14절로 연결하십시오. 네이티브 permissions에서 write deny만 넣으면 파일 쓰기가 차단된다는 오해를 막아야 합니다.

## 9. [심각도: 중간] 17.3 — 프롬프트 접수 뒤에 시작하는 SSE 구독은 해당 실행을 놓칠 수 있습니다

- 본문의 문제 문장: 예제가 `await client.session.prompt(...)` 다음에 `for await (const event of client.event.subscribe(...))`를 실행합니다.
- 근거: `V2/packages/client/src/shared-events.ts:70`의 `subscribe`는 지연 iterable을 만들며, 150행 이후 `next()`에서 처음 `start()`를 호출합니다. 131~140행의 `start()`가 실제 연결을 시작합니다. `V2/packages/schema/src/session-event.ts:371`의 `session.step.ended`를 실시간으로 받기 전에 실행이 끝나면 이 구독에는 나타나지 않습니다. 본문 자체도 이벤트 구독이 실시간 전용임을 설명합니다.
- 제안 수정: 누락 없이 결과를 관찰하는 실습이라면 세션의 영속 로그 `client.experimental.session.log({ sessionID, after, follow: true })`를 사용하십시오. SSE 예제를 유지하면 이벤트 소비를 먼저 시작하고 `server.connected`를 확인한 뒤 prompt를 보내며 세션 ID도 필터링하십시오. 단순히 iterable을 변수에 대입하는 것만으로는 연결이 열리지 않는다는 점도 설명하십시오.

## 10. [심각도: 중간] 17.5 — prompt에 /review 문자열을 넣어도 슬래시 명령 API를 실행하지 않습니다

- 본문의 문제 문장: 그림 17-2의 `sessions.prompt('/review pr')`.
- 근거: `V2/packages/core/src/session/prompt.ts:34`의 `prepare`는 45~50행에서 `request.input.text`를 프롬프트 텍스트로 복사합니다. 명령 실행은 별도의 `V2/packages/core/src/session/command.ts:11`의 `SessionCommand.execute`이며, 24~26행에서 `commands.execute({ name: input.command, ... })`를 호출합니다. 생성 클라이언트 `V2/packages/client/src/promise/generated/client.ts:765`도 `/api/session/:sessionID/command`로 보내는 별도 `command` 메서드와 `name`, `text` 필드를 제공합니다.
- 제안 수정: 그림의 단계를 `sessions.command({ sessionID, name: "review", text: "pr" })`로 바꾸십시오. 일반 자연어 리뷰 요청을 보내려면 prompt를 쓰되 `/review` 템플릿 실행과 구분하십시오.

## 11. [심각도: 중간] 4.1·16.18 — 환경 변수 총람이 실제 CLI 읽기 지점과 누락 항목을 반영하지 않습니다

- 본문의 문제 문장: “CLI가 읽는 모든 환경 변수는 cli/src/env.ts 한 곳에 모여 있습니다.” 16.18절의 TUI·디버깅 및 자식 프로세스 변수 목록.
- 근거: `V2/packages/cli/src/env.ts:9`는 비밀번호 설정을 정의하지만, 실제로 `V2/packages/cli/src/index.ts:25`는 `process.env.NO_PROXY`와 `process.env.no_proxy`를 직접 읽고, 36행은 `OPENCODE_SSH_ASKPASS_PORT`를 직접 읽습니다. 또한 총람에 없는 `OPENCODE_STORY`는 `V2/packages/tui/src/app.tsx:369`에서 초기 라우트를 선택하고, 376~378행에서 `1`이면 인덱스, 다른 값이면 특정 스토리를 엽니다. `V2/packages/core/src/worktree.ts:244`와 245행은 시작 명령에 `OPENCODE_WORKTREE_BASE`, `OPENCODE_WORKTREE_PATH`를 제공합니다.
- 제안 수정: env.ts에 모두 모였다는 단정을 지우고 서버 부팅·TUI·보조 프로세스의 읽기 지점도 안내하십시오. 16.18절에 `OPENCODE_STORY`, 소문자 `no_proxy`, 워크트리 시작 명령용 두 변수를 추가하십시오. `OPENCODE_SSH_ASKPASS_PORT`는 사용자 설정과 구분해 내부 전달 변수로 적으십시오.

## 12. [심각도: 낮음] 7.1 — SessionInbox의 서비스 범위를 세션별로 표기합니다

- 본문의 문제 문장: 책임 표의 “SessionInbox — 세션별”.
- 근거: `V2/packages/core/src/session/inbox.ts:297`은 `makeGlobalNode({ service: Service, layer, deps: [Database.node, Bus.node] })`로 서비스를 선언합니다. 같은 파일 69~73행의 `inboxLocks`와 `serialized(sessionID, ...)`가 세션 ID별로 잠금을 나누는 것이지 서비스 인스턴스가 세션마다 생기는 것은 아닙니다.
- 제안 수정: 범위를 “프로세스 전역(세션 ID별 영속 입력·잠금)”으로 고치십시오. 데이터의 분할 단위와 Effect 서비스의 수명 범위를 분리해 설명하십시오.

## 13. [심각도: 낮음] 4.3·16.17 — 서비스 채널별 파일명과 Windows local 포트 설명이 불완전합니다

- 본문의 문제 문장: “채널이 다르면 service-<channel>.json”, “기본 49374 … Windows 28894, local 채널 49375”.
- 근거: `V2/packages/cli/src/services/service-config.ts:41`의 `filename`은 `latest`, `dev`, `beta`, `next`에 모두 `service.json`을 반환합니다. 55~57행의 Windows 변환은 local의 `0xC0DF`에도 적용되므로 Windows local은 `0x70DF`, 즉 28895입니다. 61~63행은 공유 채널의 `0xC0DE`와 local의 `0xC0DF`를 구분합니다.
- 제안 수정: latest/dev/beta/next는 등록·설정 파일명과 기본 포트를 공유하고, local 및 기타 채널만 별도 파일명을 쓴다고 명시하십시오. 포트는 비Windows 49374/local 49375, Windows 28894/local 28895로 표를 나누십시오.

## 14. [심각도: 낮음] 9.6 — inputWindow를 생략해 압축 임계치를 컨텍스트 창만으로 이해하게 합니다

- 본문의 문제 문장: “200k 창이면 … 천장은 170k입니다”, 발췌 코드에서 정의 없이 등장하는 `inputWindow(limit)`.
- 근거: `V2/packages/core/src/session/compaction.ts:1185`는 `limit.input && limit.context ? Math.min(limit.input, limit.context) : limit.input || limit.context`를 반환합니다. 1165행의 압축 계산은 이 입력 창을 기준으로 합니다. 예컨대 context 200k, input 100k라면 기본 여유는 max(15k, 16k)=16k여서 천장은 84k입니다.
- 제안 수정: 170k 예제에 “별도의 더 작은 input 제한이 없는 경우”라는 조건을 붙이고 `inputWindow` 정의를 함께 보여 주십시오. 16.10절의 buffer 설명도 context와 input 중 유효한 입력 창을 기준으로 한다고 보완하십시오.
