# Claude Code v2.1.88 — 소스 코드 분석

> **면책 조항**: 이 저장소의 모든 소스 코드는 **Anthropic과 Claude**의 지적 재산입니다. 이 저장소는 기술 연구, 학습, 교육 목적의 교류를 위해서만 제공됩니다. **상업적 사용은 엄격히 금지됩니다.** 어떠한 개인, 기관, 단체도 이 콘텐츠를 상업적 목적, 영리 활동, 불법 활동 또는 기타 무단 사용에 활용할 수 없습니다. 본 콘텐츠가 귀하의 법적 권리, 지적 재산권 또는 기타 이익을 침해하는 경우, 연락 주시면 즉시 확인 후 삭제 조치하겠습니다.

> npm 패키지 `@anthropic-ai/claude-code` **2.1.88** 버전에서 추출.
> 배포 패키지는 단일 번들 `cli.js`(~12MB)만 포함한다. 이 저장소의 `src/` 디렉터리에는 npm 타르볼에서 추출한 **번들 전 TypeScript 소스**가 들어 있다.

**언어**: [English](README.md) | [中文](README_CN.md) | **한국어** | [日本語](README_JA.md) | [Spanish](README_ES.md)

---

## 목차

- [심층 분석 보고서 (`docs/`)](#심층-분석-보고서-docs) — 텔레메트리, 코드네임, 언더커버 모드, 원격 제어, 향후 로드맵
- [누락 모듈 안내](#누락-모듈-안내108개-모듈) — feature gate로 제거된 108개 모듈
- [아키텍처 개요](#아키텍처-개요) — 진입점 → 쿼리 엔진 → 도구/서비스/상태
- [빌드 안내](#빌드-안내) — 직접 컴파일이 불가능한 이유

---

## 심층 분석 보고서 (`docs/`)

v2.1.88 디컴파일 소스 코드 기반 분석 보고서. 영어/중국어/한국어 3개 국어 제공.

```
docs/
├── en/                                        # English
│   ├── [01-telemetry-and-privacy.md]          # Telemetry & Privacy — what's collected, why you can't opt out
│   ├── [02-hidden-features-and-codenames.md]  # Codenames (Capybara/Tengu/Numbat), feature flags, internal vs external
│   ├── [03-undercover-mode.md]                # Undercover Mode — hiding AI authorship in open-source repos
│   ├── [04-remote-control-and-killswitches.md]# Remote Control — managed settings, killswitches, model overrides
│   └── [05-future-roadmap.md]                 # Future Roadmap — Numbat, KAIROS, voice mode, unreleased tools
│
├── ko/                                        # 한국어
│   ├── [01-텔레메트리와-프라이버시.md]          # 텔레메트리 및 프라이버시 — 수집 항목, 비활성화 불가 이유
│   ├── [02-숨겨진-기능과-코드네임.md]          # 숨겨진 기능 — 모델 코드네임, feature flag, 내부/외부 사용자 차이
│   ├── [03-언더커버-모드.md]                   # 언더커버 모드 — 오픈소스에서 AI 저작 은폐
│   ├── [04-원격-제어와-킬스위치.md]            # 원격 제어 — 관리 설정, 킬스위치, 모델 오버라이드
│   └── [05-향후-로드맵.md]                     # 향후 로드맵 — Numbat, KAIROS, 음성 모드, 미공개 도구
│
└── zh/                                        # 中文
    ├── [01-遥测与隐私分析.md]                    # 遥测与隐私 — 收集了什么，为什么无法退出
    ├── [02-隐藏功能与模型代号.md]                # 隐藏功能 — 模型代号，feature flag，内外用户差异
    ├── [03-卧底模式分析.md]                     # 卧底模式 — 在开源项目中隐藏 AI 身份
    ├── [04-远程控制与紧急开关.md]                # 远程控制 — 托管设置，紧急开关，模型覆盖
    └── [05-未来路线图.md]                       # 未来路线图 — Numbat，KAIROS，语音模式，未上线工具
```

> 파일명을 클릭하면 해당 보고서로 이동합니다.

| # | 주제 | 핵심 발견 | 링크 |
|---|------|----------|------|
| 01 | **텔레메트리 및 프라이버시** | 이중 분석 파이프라인 (1P→Anthropic, Datadog). 환경 핑거프린트, 프로세스 메트릭, 모든 이벤트에 세션/사용자 ID 포함. **사용자 대상 비활성화 설정 없음.** `OTEL_LOG_TOOL_DETAILS=1`로 전체 도구 입력 기록 가능. | [EN](docs/en/01-telemetry-and-privacy.md) · [한국어](docs/ko/01-텔레메트리와-프라이버시.md) · [中文](docs/zh/01-遥测与隐私分析.md) |
| 02 | **숨겨진 기능과 코드네임** | 동물 코드네임 체계 (Capybara v8, Tengu, Fennec→Opus 4.6, **Numbat** 차기). Feature flag에 무작위 단어 조합으로 목적 난독화. 내부 사용자는 더 나은 프롬프트와 검증 에이전트 제공. 숨겨진 명령어: `/btw`, `/stickers`. | [EN](docs/en/02-hidden-features-and-codenames.md) · [한국어](docs/ko/02-숨겨진-기능과-코드네임.md) · [中文](docs/zh/02-隐藏功能与模型代号.md) |
| 03 | **언더커버 모드** | Anthropic 직원은 공개 저장소에서 자동으로 언더커버 모드 진입. 모델 지시: **"정체를 들키지 마라"** — 모든 AI 저작 표시를 제거하고, 사람이 작성한 것처럼 커밋. **강제 비활성화 옵션 없음.** | [EN](docs/en/03-undercover-mode.md) · [한국어](docs/ko/03-언더커버-모드.md) · [中文](docs/zh/03-卧底模式分析.md) |
| 04 | **원격 제어 및 킬스위치** | 1시간마다 `/api/claude_code/settings` 폴링. 위험 변경 시 차단 다이얼로그 — **거부 = 앱 종료**. 6개 이상 킬스위치 (권한 우회, fast 모드, 음성 모드, 분석 싱크). GrowthBook으로 동의 없이 사용자 동작 변경 가능. | [EN](docs/en/04-remote-control-and-killswitches.md) · [한국어](docs/ko/04-원격-제어와-킬스위치.md) · [中文](docs/zh/04-远程控制与紧急开关.md) |
| 05 | **향후 로드맵** | **Numbat** 코드네임 확인. Opus 4.7 / Sonnet 4.8 개발 중. **KAIROS** = 완전 자율 에이전트 모드, `<tick>` 하트비트, 푸시 알림, PR 구독. 음성 모드(push-to-talk) 준비 완료. 미공개 도구 17개 발견. | [EN](docs/en/05-future-roadmap.md) · [한국어](docs/ko/05-향후-로드맵.md) · [中文](docs/zh/05-未来路线图.md) |

---

## 누락 모듈 안내（108개 모듈）

> **이 소스는 불완전하다.** `feature()` 게이트로 분기된 108개 모듈이 npm 패키지에 **포함되어 있지 않다**.
> 이 모듈들은 Anthropic 내부 모노레포에만 존재하며, 컴파일 시 데드 코드 제거된다.
> `cli.js`, `sdk-tools.d.ts` 또는 기타 배포 아티팩트에서 **복구할 수 없다**.

### Anthropic 내부 코드 (~70개 모듈, 미공개)

npm 패키지에 소스 파일이 전혀 없는 모듈이다. Anthropic 내부 인프라에 해당한다.

<details>
<summary>전체 목록 펼치기</summary>

| Module | 용도 | Feature Gate |
|--------|------|-------------|
| `daemon/main.js` | 백그라운드 데몬 관리자 | `DAEMON` |
| `daemon/workerRegistry.js` | 데몬 워커 레지스트리 | `DAEMON` |
| `proactive/index.js` | 선제적 알림 시스템 | `PROACTIVE` |
| `contextCollapse/index.js` | 컨텍스트 축소 서비스 (실험적) | `CONTEXT_COLLAPSE` |
| `contextCollapse/operations.js` | 축소 연산 | `CONTEXT_COLLAPSE` |
| `contextCollapse/persist.js` | 축소 영속화 | `CONTEXT_COLLAPSE` |
| `skillSearch/featureCheck.js` | 원격 스킬 기능 검사 | `EXPERIMENTAL_SKILL_SEARCH` |
| `skillSearch/remoteSkillLoader.js` | 원격 스킬 로더 | `EXPERIMENTAL_SKILL_SEARCH` |
| `skillSearch/remoteSkillState.js` | 원격 스킬 상태 | `EXPERIMENTAL_SKILL_SEARCH` |
| `skillSearch/telemetry.js` | 스킬 검색 텔레메트리 | `EXPERIMENTAL_SKILL_SEARCH` |
| `skillSearch/localSearch.js` | 로컬 스킬 검색 | `EXPERIMENTAL_SKILL_SEARCH` |
| `skillSearch/prefetch.js` | 스킬 프리페치 | `EXPERIMENTAL_SKILL_SEARCH` |
| `coordinator/workerAgent.js` | 멀티 에이전트 코디네이터 워커 | `COORDINATOR_MODE` |
| `bridge/peerSessions.js` | 브릿지 피어 세션 관리 | `BRIDGE_MODE` |
| `assistant/index.js` | KAIROS 어시스턴트 모드 | `KAIROS` |
| `assistant/AssistantSessionChooser.js` | 어시스턴트 세션 선택기 | `KAIROS` |
| `compact/reactiveCompact.js` | 반응형 컨텍스트 압축 | `CACHED_MICROCOMPACT` |
| `compact/snipCompact.js` | 스닙 기반 압축 | `HISTORY_SNIP` |
| `compact/snipProjection.js` | 스닙 프로젝션 | `HISTORY_SNIP` |
| `compact/cachedMCConfig.js` | 캐시 마이크로압축 설정 | `CACHED_MICROCOMPACT` |
| `sessionTranscript/sessionTranscript.js` | 세션 트랜스크립트 서비스 | `TRANSCRIPT_CLASSIFIER` |
| `commands/agents-platform/index.js` | 내부 에이전트 플랫폼 | `ant` (내부) |
| `commands/assistant/index.js` | 어시스턴트 명령 | `KAIROS` |
| `commands/buddy/index.js` | Buddy 시스템 알림 | `BUDDY` |
| `commands/fork/index.js` | Fork 서브에이전트 명령 | `FORK_SUBAGENT` |
| `commands/peers/index.js` | 멀티 피어 명령 | `BRIDGE_MODE` |
| `commands/proactive.js` | 선제적 명령 | `PROACTIVE` |
| `commands/remoteControlServer/index.js` | 원격 제어 서버 | `DAEMON` + `BRIDGE_MODE` |
| `commands/subscribe-pr.js` | GitHub PR 구독 | `KAIROS_GITHUB_WEBHOOKS` |
| `commands/torch.js` | 내부 디버그 도구 | `TORCH` |
| `commands/workflows/index.js` | 워크플로우 명령 | `WORKFLOW_SCRIPTS` |
| `jobs/classifier.js` | 내부 작업 분류기 | `TEMPLATES` |
| `memdir/memoryShapeTelemetry.js` | 기억 형태 텔레메트리 | `MEMORY_SHAPE_TELEMETRY` |
| `services/sessionTranscript/sessionTranscript.js` | 세션 트랜스크립트 | `TRANSCRIPT_CLASSIFIER` |
| `tasks/LocalWorkflowTask/LocalWorkflowTask.js` | 로컬 워크플로우 태스크 | `WORKFLOW_SCRIPTS` |
| `protectedNamespace.js` | 내부 네임스페이스 가드 | `ant` (내부) |
| `protectedNamespace.js` (envUtils) | 보호 네임스페이스 런타임 | `ant` (내부) |
| `coreTypes.generated.js` | 생성된 코어 타입 | `ant` (내부) |
| `devtools.js` | 내부 개발 도구 | `ant` (내부) |
| `attributionHooks.js` | 내부 저작 표시 훅 | `COMMIT_ATTRIBUTION` |
| `systemThemeWatcher.js` | 시스템 테마 감시기 | `AUTO_THEME` |
| `udsClient.js` / `udsMessaging.js` | UDS 메시지 클라이언트 | `UDS_INBOX` |

</details>

### Feature-Gated 도구 (~20개 모듈)

타입 시그니처는 있으나 구현이 컴파일 시 제거된 도구.

<details>
<summary>전체 목록 펼치기</summary>

| Tool | 용도 | Feature Gate |
|------|------|-------------|
| `REPLTool` | 인터랙티브 REPL (VM 샌드박스) | `ant` (내부) |
| `SnipTool` | 컨텍스트 잘라내기 | `HISTORY_SNIP` |
| `SleepTool` | 에이전트 루프 내 슬립/지연 | `PROACTIVE` / `KAIROS` |
| `MonitorTool` | MCP 모니터링 | `MONITOR_TOOL` |
| `OverflowTestTool` | 오버플로우 테스트 | `OVERFLOW_TEST_TOOL` |
| `WorkflowTool` | 워크플로우 실행 | `WORKFLOW_SCRIPTS` |
| `WebBrowserTool` | 브라우저 자동화 | `WEB_BROWSER_TOOL` |
| `TerminalCaptureTool` | 터미널 캡처 | `TERMINAL_PANEL` |
| `TungstenTool` | 내부 성능 모니터링 | `ant` (내부) |
| `VerifyPlanExecutionTool` | 계획 실행 검증 | `CLAUDE_CODE_VERIFY_PLAN` |
| `SendUserFileTool` | 사용자에게 파일 전송 | `KAIROS` |
| `SubscribePRTool` | GitHub PR 구독 | `KAIROS_GITHUB_WEBHOOKS` |
| `SuggestBackgroundPRTool` | 백그라운드 PR 제안 | `KAIROS` |
| `PushNotificationTool` | 푸시 알림 | `KAIROS` |
| `CtxInspectTool` | 컨텍스트 검사 | `CONTEXT_COLLAPSE` |
| `ListPeersTool` | 활성 피어 목록 | `UDS_INBOX` |
| `DiscoverSkillsTool` | 스킬 탐색 | `EXPERIMENTAL_SKILL_SEARCH` |

</details>

### 텍스트/프롬프트 리소스 (~6개 파일)

| File | 용도 |
|------|------|
| `yolo-classifier-prompts/auto_mode_system_prompt.txt` | auto 모드 분류기 시스템 프롬프트 |
| `yolo-classifier-prompts/permissions_anthropic.txt` | Anthropic 내부 권한 프롬프트 |
| `yolo-classifier-prompts/permissions_external.txt` | 외부 사용자 권한 프롬프트 |
| `verify/SKILL.md` | 검증 스킬 문서 |
| `verify/examples/cli.md` | CLI 검증 예시 |
| `verify/examples/server.md` | 서버 검증 예시 |

### 누락 이유

```
  Anthropic 내부 모노레포               배포 npm 패키지
  ──────────────────────               ─────────────────────
  feature('DAEMON') → true    ──빌드──→   feature('DAEMON') → false
  ↓                                         ↓
  daemon/main.js  ← 포함        ──번들──→  daemon/main.js  ← 제거 (DCE)
  tools/REPLTool  ← 포함        ──번들──→  tools/REPLTool  ← 제거 (DCE)
  proactive/      ← 포함        ──번들──→  (참조만 있고 src/에 없음)
```

  Bun의 `feature()`는 **컴파일 시점 내장 함수**:

- Anthropic 내부 빌드에서 `true` 반환 → 코드가 번들에 포함
- 배포 빌드에서 `false` 반환 → 데드 코드 제거
- 108개 모듈이 배포 아티팩트에 존재하지 않음

---

## 저작권 및 면책 조항

```
Copyright (c) Anthropic. All rights reserved.

이 저장소의 모든 소스 코드는 Anthropic과 Claude의 지적 재산입니다.
본 저장소는 기술 연구 및 교육 목적으로만 제공됩니다. 상업적 사용은 금지됩니다.

저작권자로서 본 저장소가 귀하의 권리를 침해한다고 판단되는 경우,
저장소 소유자에게 연락 주시면 즉시 삭제하겠습니다.
```

---

## 통계

| 항목 | 수량 |
|------|------|
| 소스 파일 (.ts/.tsx) | ~1,884 |
| 코드 라인 수 | ~512,664 |
| 최대 단일 파일 | `query.ts` (~785KB) |
| 내장 도구 | ~40개 이상 |
| 슬래시 명령 | ~80개 이상 |
| 의존성 (node_modules) | ~192개 패키지 |
| 런타임 | Bun (Node.js >= 18 번들로 컴파일) |

---

## 에이전트 모드

```
                    코어 루프
                    ========

    사용자 --> messages[] --> Claude API --> 응답
                                          |
                                stop_reason == "tool_use"?
                               /                          \
                             예                           아니오
                              |                             |
                        도구 실행                        텍스트 반환
                        tool_result 추가
                        루프 재진입 -----------------> messages[]


    이것이 최소 에이전트 루프이다. Claude Code는 이 루프 위에
    프로덕션급 하니스를 래핑한다: 권한, 스트리밍, 동시성,
    압축, 서브에이전트, 영속화 및 MCP.
```

---

## 디렉터리 참조

```
src/
├── main.tsx                 # REPL 부트스트랩, 4,683줄
├── QueryEngine.ts           # SDK/headless 쿼리 라이프사이클 엔진
├── query.ts                 # 메인 에이전트 루프 (785KB, 최대 파일)
├── Tool.ts                  # 도구 인터페이스 + buildTool 팩토리
├── Task.ts                  # 태스크 타입, ID, 상태 베이스 클래스
├── tools.ts                 # 도구 등록, 프리셋, 필터링
├── commands.ts              # 슬래시 명령 정의
├── context.ts               # 사용자 입력 컨텍스트
├── cost-tracker.ts          # API 비용 누적
├── setup.ts                 # 최초 실행 설정 플로우
│
├── bridge/                  # Claude Desktop / 원격 브릿지
│   ├── bridgeMain.ts        #   세션 라이프사이클 매니저
│   ├── bridgeApi.ts         #   HTTP 클라이언트
│   ├── bridgeConfig.ts      #   연결 설정
│   ├── bridgeMessaging.ts   #   메시지 릴레이
│   ├── sessionRunner.ts     #   프로세스 스폰
│   ├── jwtUtils.ts          #   JWT 갱신
│   ├── workSecret.ts        #   인증 토큰
│   └── capacityWake.ts      #   용량 기반 웨이크
│
├── cli/                     # CLI 인프라
│   ├── handlers/            #   명령 핸들러
│   └── transports/          #   I/O 전송 (stdio, structured)
│
├── commands/                # ~80개 슬래시 명령
├── components/              # React/Ink 터미널 UI
├── entrypoints/             # 앱 진입점
├── hooks/                   # React hooks
├── services/                # 비즈니스 로직 레이어
├── state/                   # 앱 상태
├── tasks/                   # 태스크 구현
├── tools/                   # 40개 이상 도구 구현
├── types/                   # 타입 정의
├── utils/                   # 유틸리티 (최대 디렉터리)
└── vendor/                  # 네이티브 모듈 소스 스텁
```

---

## 아키텍처 개요

```
┌─────────────────────────────────────────────────────────────────────┐
│                         진입 레이어                                  │
│  cli.tsx ──> main.tsx ──> REPL.tsx (인터랙티브)                     │
│                     └──> QueryEngine.ts (headless/SDK)              │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       쿼리 엔진                                      │
│  submitMessage(prompt) ──> AsyncGenerator<SDKMessage>               │
│    ├── fetchSystemPromptParts()    ──> 시스템 프롬프트 조립          │
│    ├── processUserInput()          ──> /명령 처리                    │
│    ├── query()                     ──> 메인 에이전트 루프            │
│    │     ├── StreamingToolExecutor ──> 병렬 도구 실행               │
│    │     ├── autoCompact()         ──> 컨텍스트 압축                │
│    │     └── runTools()            ──> 도구 오케스트레이션           │
│    └── yield SDKMessage            ──> 소비자에게 스트리밍           │
└──────────────────────────────┬──────────────────────────────────────┘
```

---

## 빌드 안내

이 소스는 **이 저장소에서 직접 컴파일할 수 없다**:

- `tsconfig.json`, 빌드 스크립트, Bun 번들러 설정이 없음
- `feature()` 호출은 Bun 컴파일 시점 내장 함수 — 번들링 시 해석됨
- `MACRO.VERSION`은 빌드 시 주입됨
- `process.env.USER_TYPE === 'ant'` 분기는 Anthropic 내부용
- 컴파일된 `cli.js`는 자체 완결형 12MB 번들, Node.js >= 18만 필요

**빌드 상세 안내는 [QUICKSTART.md](QUICKSTART.md) 참고.**

---

## 라이선스

이 저장소의 모든 소스 코드는 **Anthropic과 Claude**의 저작물입니다. 본 저장소는 기술 연구 및 교육 목적으로만 제공됩니다. 전체 라이선스 조건은 원본 npm 패키지를 참조하세요.
