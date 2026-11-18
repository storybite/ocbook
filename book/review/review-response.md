# codex 검토 반영 결과

검토 원문: `codex-review.md` (14건). 각 지적을 v2.3.0 소스로 직접 확인한 뒤 판단했습니다.

| # | 지적 | 판단 | 근거 확인 | 반영 위치 |
|---|---|---|---|---|
| 1 | 리뷰어 예제의 셸 권한이 허용 목록이 아님 | 수용 | `schema/src/agent.ts` Info.default의 `*:* allow` + 설정 규칙 push | 12.3 예제·경고 상자, 17.5 |
| 2 | 서비스 설정 파일과 등록 파일 혼동 | 수용 | `service-config.ts` `file`(state) vs `configFile`(config) | 4.3, 16.1, 16.17 |
| 3 | 플러그인 대기 원칙의 예외 누락 | 수용 | `server/src/location.ts` `awaitPlugins` 5초 | 14.5 |
| 4 | 이벤트 카탈로그 개수·영속성 분류 오류 | 수용 | `session-event.ts` ephemeral 6개, `step.first_token` 누락(정규식이 `_`를 놓침) | 6.2 표 |
| 5 | Started 이벤트가 전체 텍스트를 담는다는 설명 오류 | 수용 | `Text.Started`에 text 필드 없음, Ended가 재생 경계 | 6.2 |
| 6 | 압축 요약 헤딩 검증을 과장 | 수용 | `compaction.ts` `filled` = `some(...)` | 9.6 |
| 7 | 에이전트 temperature가 "효과 없다"는 단정이 틀림 | **거부** | 공식 `migrate-v1.mdx:181` "Agent request.body is kept but not sent to the model"; 코어에서 agent.request를 요청에 싣는 경로 없음. 오히려 원고의 "request.body로 옮기라"가 오류였으므로 그쪽을 수정 | 12.1 표, 12.3, 15.3 상자(추론임을 명시), 16.6 |
| 8 | write·patch를 독립 action으로 나열 | 수용 | `file-write.ts`, `patch.ts` 모두 `action: "edit"` | 16.4 목록·경고 상자 |
| 9 | 프롬프트 후 SSE 구독 시작은 이벤트를 놓침 | 수용 | `shared-events.ts` 지연 연결, server.connected는 필터 무관 전달 | 17.3 예제 재작성 |
| 10 | prompt에 `/review` 문자열은 명령 실행이 아님 | 수용 | 생성 클라이언트 `session.command({sessionID, name, text})` | 17.5 그림·본문 |
| 11 | env.ts 단정, 환경 변수 누락 | 수용 | `cli/src/index.ts` no_proxy·SSH_ASKPASS, `tui/src/app.tsx` OPENCODE_STORY, `worktree.ts` WORKTREE_* | 4.1, 16.18 |
| 12 | SessionInbox 범위를 세션별로 표기 | 수용 | `inbox.ts` makeGlobalNode | 7.1 표 |
| 13 | 채널별 파일명·Windows local 포트 | 수용 | `filename`, `defaultPort`, `channelPort` | 4.3, 16.17 |
| 14 | inputWindow 생략 | 수용 | `compaction.ts` inputWindow | 9.6 |
