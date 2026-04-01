# Claude Code v2.1.88 — 源码分析

> **免责声明**: 本仓库中所有源码版权归 **Anthropic 和 Claude** 所有。本仓库仅用于技术研究和科研爱好者交流学习参考，**严禁任何个人、机构及组织将其用于商业用途、盈利性活动、非法用途及其他未经授权的场景。** 若内容涉及侵犯您的合法权益、知识产权或存在其他侵权问题，请及时联系我们，我们将第一时间核实并予以删除处理。

> 从 npm 包 `@anthropic-ai/claude-code` **2.1.88** 版本中提取。
> 发布的包只有一个打包后的 `cli.js`（~12MB）。本仓库的 `src/` 目录包含从 npm 包中解包的 **TypeScript 源码**。

**语言**: [English](README.md) | **中文** | [한국어](README_KR.md) | [日本語](README_JA.md) | [Spanish](README_ES.md)

---

## 目录

- [深度分析文档 (`docs/`)](#深度分析文档-docs) — 遥测、模型代号、卧底模式、远程控制、未来路线图
- [缺失模块说明](#缺失模块说明108-个模块) — 108 个被 feature gate 移除的模块
- [架构概览](#架构概览) — 入口 → 查询引擎 → 工具/服务/状态
- [构建说明](#构建说明) — 为什么不能直接编译

---

## 深度分析文档 (`docs/`)

基于 v2.1.88 反编译源码的分析报告，中英双语。

```
docs/
├── en/                                        # English
│   ├── [01-telemetry-and-privacy.md]          # Telemetry & Privacy — what's collected, why you can't opt out
│   ├── [02-hidden-features-and-codenames.md]  # Codenames (Capybara/Tengu/Numbat), feature flags, internal vs external
│   ├── [03-undercover-mode.md]                # Undercover Mode — hiding AI authorship in open-source repos
│   ├── [04-remote-control-and-killswitches.md]# Remote Control — managed settings, killswitches, model overrides
│   └── [05-future-roadmap.md]                 # Future Roadmap — Numbat, KAIROS, voice mode, unreleased tools
│
└── zh/                                        # 中文
    ├── [01-遥测与隐私分析.md]                    # 遥测与隐私 — 收集了什么，为什么无法退出
    ├── [02-隐藏功能与模型代号.md]                # 隐藏功能 — 模型代号，feature flag，内外用户差异
    ├── [03-卧底模式分析.md]                     # 卧底模式 — 在开源项目中隐藏 AI 身份
    ├── [04-远程控制与紧急开关.md]                # 远程控制 — 托管设置，紧急开关，模型覆盖
    └── [05-未来路线图.md]                       # 未来路线图 — Numbat，KAIROS，语音模式，未上线工具
```

> 点击文件名即可跳转到对应报告。

| # | 主题 | 核心发现 | 链接 |
|---|------|---------|------|
| 01 | **遥测与隐私** | 双层分析管道（1P→Anthropic, Datadog）。环境指纹、进程指标、每个事件携带会话/用户 ID。**没有面向用户的退出开关**。`OTEL_LOG_TOOL_DETAILS=1` 可记录完整工具输入。 | [EN](docs/en/01-telemetry-and-privacy.md) · [中文](docs/zh/01-遥测与隐私分析.md) |
| 02 | **隐藏功能与代号** | 动物代号体系（Capybara v8, Tengu, Fennec→Opus 4.6, **Numbat** 下一代）。Feature flag 用随机词对掩盖用途。内部用户获得更好的 prompt 和验证代理。隐藏命令：`/btw`、`/stickers`。 | [EN](docs/en/02-hidden-features-and-codenames.md) · [中文](docs/zh/02-隐藏功能与模型代号.md) |
| 03 | **卧底模式** | Anthropic 员工在公开仓库自动进入卧底模式。模型指令："**不要暴露你的掩护身份**" — 剥离所有 AI 归属，commit 看起来像人类写的。**没有强制关闭选项。** | [EN](docs/en/03-undercover-mode.md) · [中文](docs/zh/03-卧底模式分析.md) |
| 04 | **远程控制与 Killswitch** | 每小时轮询 `/api/claude_code/settings`。危险变更弹出阻塞对话框 — **拒绝 = 程序退出**。6+ 紧急开关（绕过权限、快速模式、语音模式、分析 sink）。GrowthBook 可无同意改变任何用户行为。 | [EN](docs/en/04-remote-control-and-killswitches.md) · [中文](docs/zh/04-远程控制与紧急开关.md) |
| 05 | **未来路线图** | **Numbat** 代号确认。Opus 4.7 / Sonnet 4.8 开发中。**KAIROS** = 完全自主代理模式，心跳 `<tick>`、推送通知、PR 订阅。语音模式（push-to-talk）已就绪。发现 17 个未上线工具。 | [EN](docs/en/05-future-roadmap.md) · [中文](docs/zh/05-未来路线图.md) |

---

## 缺失模块说明（108 个模块）

> **源码不完整。** 108 个被 `feature()` 门控的模块**未包含**在 npm 包中。
> 它们仅存在于 Anthropic 的内部 monorepo 中，在编译时被死代码消除。
> **无法**从 `cli.js`、`sdk-tools.d.ts` 或任何已发布的制品中恢复。

### Anthropic 内部代码（~70 个模块，从未发布）

这些模块在 npm 包中没有任何源文件。它们是 Anthropic 内部基础设施。

<details>
<summary>点击展开完整列表</summary>

| Module | Purpose | Feature Gate |
|--------|---------|-------------|
| `daemon/main.js` | 后台守护进程管理器 | `DAEMON` |
| `daemon/workerRegistry.js` | 守护进程 worker 注册 | `DAEMON` |
| `proactive/index.js` | 主动通知系统 | `PROACTIVE` |
| `contextCollapse/index.js` | 上下文折叠服务（实验性） | `CONTEXT_COLLAPSE` |
| `contextCollapse/operations.js` | 折叠操作 | `CONTEXT_COLLAPSE` |
| `contextCollapse/persist.js` | 折叠持久化 | `CONTEXT_COLLAPSE` |
| `skillSearch/featureCheck.js` | 远程技能特性检查 | `EXPERIMENTAL_SKILL_SEARCH` |
| `skillSearch/remoteSkillLoader.js` | 远程技能加载器 | `EXPERIMENTAL_SKILL_SEARCH` |
| `skillSearch/remoteSkillState.js` | 远程技能状态 | `EXPERIMENTAL_SKILL_SEARCH` |
| `skillSearch/telemetry.js` | 技能搜索遥测 | `EXPERIMENTAL_SKILL_SEARCH` |
| `skillSearch/localSearch.js` | 本地技能搜索 | `EXPERIMENTAL_SKILL_SEARCH` |
| `skillSearch/prefetch.js` | 技能预取 | `EXPERIMENTAL_SKILL_SEARCH` |
| `coordinator/workerAgent.js` | 多代理协调器 worker | `COORDINATOR_MODE` |
| `bridge/peerSessions.js` | 桥接对等会话管理 | `BRIDGE_MODE` |
| `assistant/index.js` | KAIROS 助手模式 | `KAIROS` |
| `assistant/AssistantSessionChooser.js` | 助手会话选择器 | `KAIROS` |
| `compact/reactiveCompact.js` | 响应式上下文压缩 | `CACHED_MICROCOMPACT` |
| `compact/snipCompact.js` | 基于裁剪的压缩 | `HISTORY_SNIP` |
| `compact/snipProjection.js` | 裁剪投影 | `HISTORY_SNIP` |
| `compact/cachedMCConfig.js` | 缓存微压缩配置 | `CACHED_MICROCOMPACT` |
| `sessionTranscript/sessionTranscript.js` | 会话转录服务 | `TRANSCRIPT_CLASSIFIER` |
| `commands/agents-platform/index.js` | 内部代理平台 | `ant` (内部) |
| `commands/assistant/index.js` | 助手命令 | `KAIROS` |
| `commands/buddy/index.js` | Buddy 系统通知 | `BUDDY` |
| `commands/fork/index.js` | Fork 子代理命令 | `FORK_SUBAGENT` |
| `commands/peers/index.js` | 多对等命令 | `BRIDGE_MODE` |
| `commands/proactive.js` | 主动命令 | `PROACTIVE` |
| `commands/remoteControlServer/index.js` | 远程控制服务器 | `DAEMON` + `BRIDGE_MODE` |
| `commands/subscribe-pr.js` | GitHub PR 订阅 | `KAIROS_GITHUB_WEBHOOKS` |
| `commands/torch.js` | 内部调试工具 | `TORCH` |
| `commands/workflows/index.js` | 工作流命令 | `WORKFLOW_SCRIPTS` |
| `jobs/classifier.js` | 内部任务分类器 | `TEMPLATES` |
| `memdir/memoryShapeTelemetry.js` | 记忆形态遥测 | `MEMORY_SHAPE_TELEMETRY` |
| `services/sessionTranscript/sessionTranscript.js` | 会话转录 | `TRANSCRIPT_CLASSIFIER` |
| `tasks/LocalWorkflowTask/LocalWorkflowTask.js` | 本地工作流任务 | `WORKFLOW_SCRIPTS` |
| `protectedNamespace.js` | 内部命名空间守卫 | `ant` (内部) |
| `protectedNamespace.js` (envUtils) | 受保护命名空间运行时 | `ant` (内部) |
| `coreTypes.generated.js` | 生成的核心类型 | `ant` (内部) |
| `devtools.js` | 内部开发工具 | `ant` (内部) |
| `attributionHooks.js` | 内部归属钩子 | `COMMIT_ATTRIBUTION` |
| `systemThemeWatcher.js` | 系统主题监视器 | `AUTO_THEME` |
| `udsClient.js` / `udsMessaging.js` | UDS 消息客户端 | `UDS_INBOX` |

</details>

### Feature-Gated 工具（~20 个模块）

这些工具有类型签名，但实现被编译时移除。

<details>
<summary>点击展开完整列表</summary>

| Tool | Purpose | Feature Gate |
|------|---------|-------------|
| `REPLTool` | 交互式 REPL（VM 沙箱） | `ant` (内部) |
| `SnipTool` | 上下文裁剪 | `HISTORY_SNIP` |
| `SleepTool` | 代理循环中的休眠/延迟 | `PROACTIVE` / `KAIROS` |
| `MonitorTool` | MCP 监控 | `MONITOR_TOOL` |
| `OverflowTestTool` | 溢出测试 | `OVERFLOW_TEST_TOOL` |
| `WorkflowTool` | 工作流执行 | `WORKFLOW_SCRIPTS` |
| `WebBrowserTool` | 浏览器自动化 | `WEB_BROWSER_TOOL` |
| `TerminalCaptureTool` | 终端捕获 | `TERMINAL_PANEL` |
| `TungstenTool` | 内部性能监控 | `ant` (内部) |
| `VerifyPlanExecutionTool` | 计划验证 | `CLAUDE_CODE_VERIFY_PLAN` |
| `SendUserFileTool` | 向用户发送文件 | `KAIROS` |
| `SubscribePRTool` | GitHub PR 订阅 | `KAIROS_GITHUB_WEBHOOKS` |
| `SuggestBackgroundPRTool` | 建议后台 PR | `KAIROS` |
| `PushNotificationTool` | 推送通知 | `KAIROS` |
| `CtxInspectTool` | 上下文检查 | `CONTEXT_COLLAPSE` |
| `ListPeersTool` | 列出活跃对等方 | `UDS_INBOX` |
| `DiscoverSkillsTool` | 技能发现 | `EXPERIMENTAL_SKILL_SEARCH` |

</details>

### 文本/Prompt 资源（~6 个文件）

| File | Purpose |
|------|---------|
| `yolo-classifier-prompts/auto_mode_system_prompt.txt` | 自动模式分类器系统提示 |
| `yolo-classifier-prompts/permissions_anthropic.txt` | Anthropic 内部权限提示 |
| `yolo-classifier-prompts/permissions_external.txt` | 外部用户权限提示 |
| `verify/SKILL.md` | 验证技能文档 |
| `verify/examples/cli.md` | CLI 验证示例 |
| `verify/examples/server.md` | 服务端验证示例 |

### 为什么缺失

```
  Anthropic 内部 Monorepo              发布的 npm 包
  ──────────────────────               ─────────────────────
  feature('DAEMON') → true    ──构建──→   feature('DAEMON') → false
  ↓                                         ↓
  daemon/main.js  ← 包含        ──打包──→  daemon/main.js  ← 删除 (DCE)
  tools/REPLTool  ← 包含        ──打包──→  tools/REPLTool  ← 删除 (DCE)
  proactive/      ← 包含        ──打包──→  （被引用但 src/ 中不存在）
```

  Bun 的 `feature()` 是**编译时内建函数**：

- 在 Anthropic 内部构建中返回 `true` → 代码保留在 bundle 中
- 在发布构建中返回 `false` → 代码被死代码消除
- 108 个模块在已发布的制品中根本不存在

---

## 版权与免责声明

```
Copyright (c) Anthropic. All rights reserved.

本仓库中所有源码均为 Anthropic 和 Claude 的知识产权。
本仓库仅用于技术研究和教育目的。严禁商业使用。

如果您是版权所有者并认为本仓库侵犯了您的权利，
请联系仓库所有者立即删除。
```

---

## 统计数据

| 项目 | 数量 |
|------|------|
| 源文件 (.ts/.tsx) | ~1,884 |
| 代码行数 | ~512,664 |
| 最大单文件 | `query.ts` (~785KB) |
| 内置工具 | ~40+ |
| 斜杠命令 | ~80+ |
| 依赖 (node_modules) | ~192 个包 |
| 运行时 | Bun（编译为 Node.js >= 18 bundle）|

---

## 代理模式

```
                    核心循环
                    ========

    用户 --> messages[] --> Claude API --> 响应
                                          |
                                stop_reason == "tool_use"?
                               /                          \
                             是                           否
                              |                             |
                        执行工具                        返回文本
                        追加 tool_result
                        循环回退 -----------------> messages[]


    这就是最小的代理循环。Claude Code 在此循环上
    包裹了生产级线束：权限、流式传输、并发、
    压缩、子代理、持久化和 MCP。
```

---

## 目录参考

```
src/
├── main.tsx                 # REPL 引导程序，4,683 行
├── QueryEngine.ts           # SDK/headless 查询生命周期引擎
├── query.ts                 # 主代理循环 (785KB，最大文件)
├── Tool.ts                  # 工具接口 + buildTool 工厂
├── Task.ts                  # 任务类型、ID、状态基类
├── tools.ts                 # 工具注册、预设、过滤
├── commands.ts              # 斜杠命令定义
├── context.ts               # 用户输入上下文
├── cost-tracker.ts          # API 成本累积
├── setup.ts                 # 首次运行设置流程
│
├── bridge/                  # Claude Desktop / 远程桥接
│   ├── bridgeMain.ts        #   会话生命周期管理器
│   ├── bridgeApi.ts         #   HTTP 客户端
│   ├── bridgeConfig.ts      #   连接配置
│   ├── bridgeMessaging.ts   #   消息中继
│   ├── sessionRunner.ts     #   进程生成
│   ├── jwtUtils.ts          #   JWT 刷新
│   ├── workSecret.ts        #   认证令牌
│   └── capacityWake.ts      #   基于容量的唤醒
│
├── cli/                     # CLI 基础设施
│   ├── handlers/            #   命令处理器
│   └── transports/          #   I/O 传输 (stdio, structured)
│
├── commands/                # ~80 个斜杠命令
├── components/              # React/Ink 终端 UI
├── entrypoints/             # 应用入口点
├── hooks/                   # React hooks
├── services/                # 业务逻辑层
├── state/                   # 应用状态
├── tasks/                   # 任务实现
├── tools/                   # 40+ 工具实现
├── types/                   # 类型定义
├── utils/                   # 工具函数（最大目录）
└── vendor/                  # 原生模块源码存根
```

---

## 架构概览

```
┌─────────────────────────────────────────────────────────────────────┐
│                         入口层                                      │
│  cli.tsx ──> main.tsx ──> REPL.tsx (交互式)                        │
│                     └──> QueryEngine.ts (headless/SDK)              │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       查询引擎                                      │
│  submitMessage(prompt) ──> AsyncGenerator<SDKMessage>               │
│    ├── fetchSystemPromptParts()    ──> 组装系统提示词               │
│    ├── processUserInput()          ──> 处理 /命令                   │
│    ├── query()                     ──> 主代理循环                   │
│    │     ├── StreamingToolExecutor ──> 并行工具执行                  │
│    │     ├── autoCompact()         ──> 上下文压缩                   │
│    │     └── runTools()            ──> 工具编排                     │
│    └── yield SDKMessage            ──> 流式传输给消费者             │
└──────────────────────────────┬──────────────────────────────────────┘
```

---

## 构建说明

本源码**不能直接从本仓库编译**：

- 缺少 `tsconfig.json`、构建脚本和 Bun bundler 配置
- `feature()` 调用是 Bun 编译时内建函数 — 在打包时解析
- `MACRO.VERSION` 在构建时注入
- `process.env.USER_TYPE === 'ant'` 部分是 Anthropic 内部的
- 编译后的 `cli.js` 是一个自包含的 12MB bundle，只需 Node.js >= 18

**构建说明详见 [QUICKSTART.md](QUICKSTART.md)。**

---

## 许可证

本仓库中所有源码版权归 **Anthropic 和 Claude** 所有。本仓库仅用于技术研究和教育目的。完整许可条款请参阅原始 npm 包。
