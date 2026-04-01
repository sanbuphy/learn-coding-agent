# Claude Code v2.1.88 — ソースコード分析

> **免責事項**: 本リポジトリのすべてのソースコードは **AnthropicおよびClaude** の知的財産です。本リポジトリは技術研究、学習、教育目的の交流のためにのみ提供されます。**商用利用は厳禁です。** いかなる個人、機関、団体も、本コンテンツを商業目的、営利活動、違法行為、その他の無許可の用途に使用することはできません。本コンテンツがお客様の法的権利、知的財産権、その他の利益を侵害する場合は、ご連絡いただければ直ちに確認・削除いたします。

> npmパッケージ `@anthropic-ai/claude-code` **2.1.88** バージョンから抽出。
> 配布パッケージはバンドルされた単一の `cli.js`（約12MB）のみを含む。本リポジトリの `src/` ディレクトリにはnpmターボールから抽出した**バンドル前のTypeScriptソース**が格納されている。

**言語**: [English](README.md) | [中文](README_CN.md) | [한국어](README_KR.md) | **日本語** | [Spanish](README_ES.md)

---

## 目次

- [詳細分析レポート (`docs/`)](#詳細分析レポート-docs) — テレメトリ、コードネーム、アンダーカバーモード、リモート制御、今後のロードマップ
- [欠損モジュール案内](#欠損モジュール案内108モジュール) — feature gateにより除去された108モジュール
- [アーキテクチャ概要](#アーキテクチャ概要) — エントリポイント → クエリエンジン → ツール/サービス/状態
- [ビルド案内](#ビルド案内) — 直接コンパイルできない理由

---

## 詳細分析レポート (`docs/`)

v2.1.88デコンパイルソースコードに基づく分析レポート。英語/中国語/韓国語/日本語の4言語で提供。

```
docs/
├── en/                                        # English
│   ├── [01-telemetry-and-privacy.md]          # Telemetry & Privacy — what's collected, why you can't opt out
│   ├── [02-hidden-features-and-codenames.md]  # Codenames (Capybara/Tengu/Numbat), feature flags, internal vs external
│   ├── [03-undercover-mode.md]                # Undercover Mode — hiding AI authorship in open-source repos
│   ├── [04-remote-control-and-killswitches.md]# Remote Control — managed settings, killswitches, model overrides
│   └── [05-future-roadmap.md]                 # Future Roadmap — Numbat, KAIROS, voice mode, unreleased tools
│
├── ja/                                        # 日本語
│   ├── [01-テレメトリとプライバシー.md]          # テレメトリとプライバシー — 収集項目、無効化不可の理由
│   ├── [02-隠し機能とコードネーム.md]           # 隠し機能 — モデルコードネーム、feature flag、内部/外部ユーザーの違い
│   ├── [03-アンダーカバーモード.md]             # アンダーカバーモード — オープンソースでのAI著作隠匿
│   ├── [04-リモート制御とキルスイッチ.md]       # リモート制御 — 管理設定、キルスイッチ、モデルオーバーライド
│   └── [05-今後のロードマップ.md]               # 今後のロードマップ — Numbat、KAIROS、音声モード、未公開ツール
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

> ファイル名をクリックすると該当レポートに移動します。

| # | テーマ | 主要発見 | リンク |
|---|--------|---------|------|
| 01 | **テレメトリとプライバシー** | 二層分析パイプライン（1P→Anthropic、Datadog）。環境フィンガープリント、プロセスメトリクス、全イベントにセッション/ユーザーID。**ユーザー向け無効化設定なし。** `OTEL_LOG_TOOL_DETAILS=1` で全ツール入力記録可能。 | [EN](docs/en/01-telemetry-and-privacy.md) · [日本語](docs/ja/01-テレメトリとプライバシー.md) |
| 02 | **隠し機能とコードネーム** | 動物コードネーム体系（Capybara v8、Tengu、Fennec→Opus 4.6、**Numbat** 次期）。Feature flagにランダム単語ペアで目的を難読化。内部ユーザーは優遇プロンプトと検証エージェントを利用可能。隠しコマンド: `/btw`、`/stickers`。 | [EN](docs/en/02-hidden-features-and-codenames.md) · [日本語](docs/ja/02-隠し機能とコードネーム.md) |
| 03 | **アンダーカバーモード** | Anthropic社員は公開リポジトリで自動的にアンダーカバーモードに突入。モデルへの指示: **「正体を明かすな」** — 全AI帰属表示を除去し、人間が書いたようにコミット。**強制無効化オプションなし。** | [EN](docs/en/03-undercover-mode.md) · [日本語](docs/ja/03-アンダーカバーモード.md) |
| 04 | **リモート制御とキルスイッチ** | 1時間ごとに `/api/claude_code/settings` をポーリング。危険な変更時にブロッキングダイアログ — **拒否＝アプリ終了**。6以上のキルスイッチ（パーミッションバイパス、Fastモード、音声モード、分析シンク）。GrowthBookで同意なくユーザー動作変更可能。 | [EN](docs/en/04-remote-control-and-killswitches.md) · [日本語](docs/ja/04-リモート制御とキルスイッチ.md) |
| 05 | **今後のロードマップ** | **Numbat** コードネーム確認。Opus 4.7 / Sonnet 4.8開発中。**KAIROS** ＝ 完全自律エージェントモード、`<tick>`ハートビート、プッシュ通知、PR購読。音声モード（push-to-talk）準備完了。未公開ツール17個発見。 | [EN](docs/en/05-future-roadmap.md) · [日本語](docs/ja/05-今後のロードマップ.md) |

---

## 欠損モジュール案内（108モジュール）

> **このソースは不完全である。** `feature()` ゲートで分岐した108モジュールがnpmパッケージに**含まれていない**。
> これらはAnthropicの内部モノレポにのみ存在し、コンパイル時にデッドコード除去される。
> `cli.js`、`sdk-tools.d.ts`、その他配布アーティファクトから**復元できない**。

### Anthropic内部コード（約70モジュール、未公開）

npmパッケージにソースファイルが一切ないモジュール。Anthropic内部インフラに該当する。

<details>
<summary>全リスト展開</summary>

| Module | 用途 | Feature Gate |
|--------|------|-------------|
| `daemon/main.js` | バックグラウンドデーモン管理 | `DAEMON` |
| `daemon/workerRegistry.js` | デーモンワーカーレジストリ | `DAEMON` |
| `proactive/index.js` | 先行通知システム | `PROACTIVE` |
| `contextCollapse/index.js` | コンテキスト縮小サービス（実験的） | `CONTEXT_COLLAPSE` |
| `contextCollapse/operations.js` | 縮小操作 | `CONTEXT_COLLAPSE` |
| `contextCollapse/persist.js` | 縮小永続化 | `CONTEXT_COLLAPSE` |
| `skillSearch/featureCheck.js` | リモートスキル機能検査 | `EXPERIMENTAL_SKILL_SEARCH` |
| `skillSearch/remoteSkillLoader.js` | リモートスキルローダー | `EXPERIMENTAL_SKILL_SEARCH` |
| `skillSearch/remoteSkillState.js` | リモートスキル状態 | `EXPERIMENTAL_SKILL_SEARCH` |
| `skillSearch/telemetry.js` | スキル検索テレメトリ | `EXPERIMENTAL_SKILL_SEARCH` |
| `skillSearch/localSearch.js` | ローカルスキル検索 | `EXPERIMENTAL_SKILL_SEARCH` |
| `skillSearch/prefetch.js` | スキルプリフェッチ | `EXPERIMENTAL_SKILL_SEARCH` |
| `coordinator/workerAgent.js` | マルチエージェントコーディネーターワーカー | `COORDINATOR_MODE` |
| `bridge/peerSessions.js` | ブリッジピアセッション管理 | `BRIDGE_MODE` |
| `assistant/index.js` | KAIROSアシスタントモード | `KAIROS` |
| `assistant/AssistantSessionChooser.js` | アシスタントセッション選択 | `KAIROS` |
| `compact/reactiveCompact.js` | リアクティブコンテキスト圧縮 | `CACHED_MICROCOMPACT` |
| `compact/snipCompact.js` | スニップベース圧縮 | `HISTORY_SNIP` |
| `compact/snipProjection.js` | スニッププロジェクション | `HISTORY_SNIP` |
| `compact/cachedMCConfig.js` | キャッシュマイクロ圧縮設定 | `CACHED_MICROCOMPACT` |
| `sessionTranscript/sessionTranscript.js` | セッショントランスクリプトサービス | `TRANSCRIPT_CLASSIFIER` |
| `commands/agents-platform/index.js` | 内部エージェントプラットフォーム | `ant`（内部） |
| `commands/assistant/index.js` | アシスタントコマンド | `KAIROS` |
| `commands/buddy/index.js` | Buddyシステム通知 | `BUDDY` |
| `commands/fork/index.js` | Forkサブエージェントコマンド | `FORK_SUBAGENT` |
| `commands/peers/index.js` | マルチピアコマンド | `BRIDGE_MODE` |
| `commands/proactive.js` | 先行コマンド | `PROACTIVE` |
| `commands/remoteControlServer/index.js` | リモート制御サーバー | `DAEMON` + `BRIDGE_MODE` |
| `commands/subscribe-pr.js` | GitHub PR購読 | `KAIROS_GITHUB_WEBHOOKS` |
| `commands/torch.js` | 内部デバッグツール | `TORCH` |
| `commands/workflows/index.js` | ワークフローコマンド | `WORKFLOW_SCRIPTS` |
| `jobs/classifier.js` | 内部タスク分類器 | `TEMPLATES` |
| `memdir/memoryShapeTelemetry.js` | メモリ形状テレメトリ | `MEMORY_SHAPE_TELEMETRY` |
| `services/sessionTranscript/sessionTranscript.js` | セッショントランスクリプト | `TRANSCRIPT_CLASSIFIER` |
| `tasks/LocalWorkflowTask/LocalWorkflowTask.js` | ローカルワークフロータスク | `WORKFLOW_SCRIPTS` |
| `protectedNamespace.js` | 内部ネームスペースガード | `ant`（内部） |
| `protectedNamespace.js` (envUtils) | 保護ネームスペースランタイム | `ant`（内部） |
| `coreTypes.generated.js` | 生成されたコアタイプ | `ant`（内部） |
| `devtools.js` | 内部開発ツール | `ant`（内部） |
| `attributionHooks.js` | 内部帰属フック | `COMMIT_ATTRIBUTION` |
| `systemThemeWatcher.js` | システムテーマウォッチャー | `AUTO_THEME` |
| `udsClient.js` / `udsMessaging.js` | UDSメッセージクライアント | `UDS_INBOX` |

</details>

### Feature-Gatedツール（約20モジュール）

型シグネチャは存在するが、実装がコンパイル時に除去されたツール。

<details>
<summary>全リスト展開</summary>

| Tool | 用途 | Feature Gate |
|------|------|-------------|
| `REPLTool` | インタラクティブREPL（VMサンドボックス） | `ant`（内部） |
| `SnipTool` | コンテキストスニッピング | `HISTORY_SNIP` |
| `SleepTool` | エージェントループ内スリープ/遅延 | `PROACTIVE` / `KAIROS` |
| `MonitorTool` | MCPモニタリング | `MONITOR_TOOL` |
| `OverflowTestTool` | オーバーフローテスト | `OVERFLOW_TEST_TOOL` |
| `WorkflowTool` | ワークフロー実行 | `WORKFLOW_SCRIPTS` |
| `WebBrowserTool` | ブラウザ自動化 | `WEB_BROWSER_TOOL` |
| `TerminalCaptureTool` | ターミナルキャプチャ | `TERMINAL_PANEL` |
| `TungstenTool` | 内部パフォーマンス監視 | `ant`（内部） |
| `VerifyPlanExecutionTool` | 計画実行検証 | `CLAUDE_CODE_VERIFY_PLAN` |
| `SendUserFileTool` | ユーザーへのファイル送信 | `KAIROS` |
| `SubscribePRTool` | GitHub PR購読 | `KAIROS_GITHUB_WEBHOOKS` |
| `SuggestBackgroundPRTool` | バックグラウンドPR提案 | `KAIROS` |
| `PushNotificationTool` | プッシュ通知 | `KAIROS` |
| `CtxInspectTool` | コンテキスト検査 | `CONTEXT_COLLAPSE` |
| `ListPeersTool` | アクティブピア一覧 | `UDS_INBOX` |
| `DiscoverSkillsTool` | スキル探索 | `EXPERIMENTAL_SKILL_SEARCH` |

</details>

### テキスト/プロンプトリソース（約6ファイル）

| File | 用途 |
|------|------|
| `yolo-classifier-prompts/auto_mode_system_prompt.txt` | autoモード分類器システムプロンプト |
| `yolo-classifier-prompts/permissions_anthropic.txt` | Anthropic内部権限プロンプト |
| `yolo-classifier-prompts/permissions_external.txt` | 外部ユーザー権限プロンプト |
| `verify/SKILL.md` | 検証スキルドキュメント |
| `verify/examples/cli.md` | CLI検証例 |
| `verify/examples/server.md` | サーバー検証例 |

### 欠損の理由

```
  Anthropic内部モノレポ                  配布npmパッケージ
  ──────────────────────               ─────────────────────
  feature('DAEMON') → true    ──ビルド──→   feature('DAEMON') → false
  ↓                                         ↓
  daemon/main.js  ← 含む        ──バンドル──→  daemon/main.js  ← 除去 (DCE)
  tools/REPLTool  ← 含む        ──バンドル──→  tools/REPLTool  ← 除去 (DCE)
  proactive/      ← 含む        ──バンドル──→  （参照のみ、src/に不在）
```

  Bunの `feature()` は**コンパイル時組込関数**:

- Anthropic内部ビルドで `true` 返却 → コードがバンドルに含まれる
- 配布ビルドで `false` 返却 → デッドコード除去
- 108モジュールが配布アーティファクトに存在しない

---

## 著作権および免責事項

```
Copyright (c) Anthropic. All rights reserved.

本リポジトリのすべてのソースコードはAnthropicおよびClaudeの知的財産です。
本リポジトリは技術研究および教育目的でのみ提供されます。商用利用は禁止です。

著作権者として本リポジトリがお客様の権利を侵害すると判断される場合は、
リポジトリ所有者にご連絡いただければ直ちに削除いたします。
```

---

## 統計

| 項目 | 数量 |
|------|------|
| ソースファイル (.ts/.tsx) | 約1,884 |
| コード行数 | 約512,664 |
| 最大単一ファイル | `query.ts`（約785KB） |
| 組込ツール | 約40以上 |
| スラッシュコマンド | 約80以上 |
| 依存関係 (node_modules) | 約192パッケージ |
| ランタイム | Bun（Node.js >= 18バンドルにコンパイル） |

---

## エージェントモード

```
                    コアループ
                    ========

    ユーザー --> messages[] --> Claude API --> レスポンス
                                          |
                                stop_reason == "tool_use"?
                               /                          \
                             はい                         いいえ
                              |                             |
                        ツール実行                      テキスト返却
                        tool_result追加
                        ループ再突入 -----------------> messages[]


    これが最小のエージェントループである。Claude Codeはこのループの上に
    プロダクショングレードのハーネスをラップする: 権限、ストリーミング、
    並行性、圧縮、サブエージェント、永続化、MCP。
```

---

## ディレクトリ参照

```
src/
├── main.tsx                 # REPLブートストラップ、4,683行
├── QueryEngine.ts           # SDK/headlessクエリライフサイクルエンジン
├── query.ts                 # メインエージェントループ（785KB、最大ファイル）
├── Tool.ts                  # ツールインターフェース + buildToolファクトリ
├── Task.ts                  # タスクタイプ、ID、状態ベースクラス
├── tools.ts                 # ツール登録、プリセット、フィルタリング
├── commands.ts              # スラッシュコマンド定義
├── context.ts               # ユーザー入力コンテキスト
├── cost-tracker.ts          # APIコスト累積
├── setup.ts                 # 初回実行セットアップフロー
│
├── bridge/                  # Claude Desktop / リモートブリッジ
│   ├── bridgeMain.ts        #   セッションライフサイクルマネージャ
│   ├── bridgeApi.ts         #   HTTPクライアント
│   ├── bridgeConfig.ts      #   接続設定
│   ├── bridgeMessaging.ts   #   メッセージリレー
│   ├── sessionRunner.ts     #   プロセススポーン
│   ├── jwtUtils.ts          #   JWTリフレッシュ
│   ├── workSecret.ts        #   認証トークン
│   └── capacityWake.ts      #   容量ベースウェイク
│
├── cli/                     # CLIインフラ
│   ├── handlers/            #   コマンドハンドラ
│   └── transports/          #   I/Oトランスポート（stdio, structured）
│
├── commands/                # 約80スラッシュコマンド
├── components/              # React/InkターミナルUI
├── entrypoints/             # アプリエントリポイント
├── hooks/                   # React hooks
├── services/                # ビジネスロジック層
├── state/                   # アプリ状態
├── tasks/                   # タスク実装
├── tools/                   # 40以上のツール実装
├── types/                   # 型定義
├── utils/                   # ユーティリティ（最大ディレクトリ）
└── vendor/                  # ネイティブモジュールソーススタブ
```

---

## アーキテクチャ概要

```
┌─────────────────────────────────────────────────────────────────────┐
│                         エントリ層                                   │
│  cli.tsx ──> main.tsx ──> REPL.tsx（インタラクティブ）               │
│                     └──> QueryEngine.ts（headless/SDK）              │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       クエリエンジン                                  │
│  submitMessage(prompt) ──> AsyncGenerator<SDKMessage>               │
│    ├── fetchSystemPromptParts()    ──> システムプロンプト組立        │
│    ├── processUserInput()          ──> /コマンド処理                 │
│    ├── query()                     ──> メインエージェントループ      │
│    │     ├── StreamingToolExecutor ──> 並列ツール実行               │
│    │     ├── autoCompact()         ──> コンテキスト圧縮             │
│    │     └── runTools()            ──> ツールオーケストレーション    │
│    └── yield SDKMessage            ──> コンシューマにストリーミング  │
└──────────────────────────────┬──────────────────────────────────────┘
```

---

## ビルド案内

このソースは**本リポジトリから直接コンパイルできない**:

- `tsconfig.json`、ビルドスクリプト、Bunバンドラー設定がない
- `feature()` 呼び出しはBunコンパイル時組込関数 — バンドリング時に解決される
- `MACRO.VERSION` はビルド時に注入される
- `process.env.USER_TYPE === 'ant'` 分岐はAnthropic内部用
- コンパイル済み `cli.js` は自己完結型12MBバンドル、Node.js >= 18のみ必要

**ビルドの詳細は [QUICKSTART.md](QUICKSTART.md) を参照。**

---

## ライセンス

本リポジトリのすべてのソースコードは **AnthropicおよびClaude** の著作物です。本リポジトリは技術研究および教育目的でのみ提供されます。完全なライセンス条項は元のnpmパッケージを参照してください。
