# Structured UI Subsystem Architecture (formerly "RM Workbench V0 Architecture")

路径：`docs/ui-ux/rm-workbench-v0-architecture.md`
状态：`active / canonical architecture (realigned 2026-05-09)`
更新时间：`2026-05-09`
入口：`docs/ui-ux/rm-workbench-v0-index.md`
受约束于：`docs/ui-ux/rm-workbench-v0-adr.md`（ADR 与本文档冲突时以 ADR 为准）

---

## 0. 这份文档负责什么

这份文档只维护 Hermes WebUI 结构化 UI 子系统（即原 "RM Workbench V0"）的当前架构事实。

它回答：

- 系统由哪些部分组成。
- 各部分职责边界是什么。
- 后到前 UI 和前到后交互怎么走。
- 哪些能力已经成立，哪些还没有成立。

它不负责：

- 记录每个 issue 的过程。
- 保存 spike 细节。
- 记录被否决方案的完整讨论。
- 写具体实现步骤。

被否决方案、取舍理由和历史判断放在 `rm-workbench-v0-adr.md`。

执行顺序放在 `rm-workbench-v0-roadmap.md`。

具体代码改动边界放在 `rm-workbench-v0-coding-boundary.md`。

---

## 1. 当前一句话架构

```text
Hermes Agent runtime
  -> hermes-webui backend as source of truth
  -> /api/chat/stream existing SSE rail
  -> event: rm_workbench  (命名包袱，机制是 Layer 0 通用通道)
  -> AG-UI CUSTOM carries A2UI messages
  -> React structured-UI host
  -> pending interaction resolve returns structured user input
```

子系统目标：让模型在对话中通过 structured tool args 选 catalog primitive 并填 props，
**而不是**让模型生成任意前端代码。

```text
Agent chooses catalog primitive + fills props
  -> frontend renders known component (best-effort)
```

### 1.1 Layer 分层（2026-05-09 校准）

```text
Layer 0  Generative UI atomic capability （工作台底座）
  - primitive catalog: MetricCard / DataTable / LineChart / BarChart / PieChart / ChoiceList
  - contract envelope: emit_ui tool
  - interaction protocol: pending_interaction.resolve
  - 不依赖任何业务 consumer 的形状要求

Layer 1  Business consumer
  - RM Workbench 是第一个 consumer，不是所有者
  - 业务的"约定 / 预设 / 字段命名"应以 Skill 形式存在（ADR-013）
  - 不应该硬编码新的 React surface 或新的后端分支
  - 当前过渡态：仍保留 frontend/src/rm/surfaces/ 与对应后端 RM 分支，
    标记为 transitional，由 Skill-driven Layer 1 migration issue 收口
```

详见 ADR-009 ~ ADR-013。

---

## 2. System Components

### 2.1 Hermes Agent

职责：

- conversation loop
- tool calling
- Skill instruction loading
- runtime memory / approval / clarify 等既有能力

不改 Hermes 主 runtime loop。

Hermes Agent 只暴露一个 Layer 0 结构化 UI emit tool（ADR-012）：

```text
emit_ui
```

> 历史名 `rm_workbench_emit_contract` 已物理重命名为 `emit_ui`，不保留兼容别名。

不新增 `render_table` / `render_chart` / `render_form` / `render_card` 等 per-component 工具（ADR-009）。

### 2.2 hermes-webui backend

职责：

- 继续作为 session / SSE / tool lifecycle / pending interaction 的事实源。
- 保留 `/api/chat/stream` top-level SSE protocol。
- 在真实 stream 中识别 `emit_ui` tool completion，把 contract 转成 `event: rm_workbench`。
- 维护 pending interaction resolve API（Layer 0 通用机制）。

关键边界：

```text
backend adapter maps contract (Layer 0 only)
frontend primitive renders known catalog (best-effort)
```

backend 不从 assistant text 猜 UI。

Layer 0 validator（`api/rm_workbench/contracts.py`）只校验最小可识别性：
block 必须有 id / type / props，type 在 catalog allowlist 内。
per-type 字段缺失（chart series / table columns / choice options）由 primitive
在前端兜底，不在后端抛 ValueError（ADR-010）。

业务级 schema 严格性（如 RM 要求 customer / product_candidates 必须存在）由
RM Skill 自己负责，不下沉到 Layer 0 validator。

### 2.3 React structured-UI host

职责：

- 消费 `event: rm_workbench`。
- 解析 AG-UI events 和 A2UI messages。
- 维护 structured UI surface state。
- 渲染 generic primitives 和 RM semantic surfaces。
- 发起 pending interaction resolve。

当前已经成立的是独立 React workbench / mock path。

还没有完全成立的是：

```text
主 WebUI chat path 中的正式 React structured-UI host
```

所以 Issue 8 前必须先完成 React frontend foundation。

---

## 3. Protocol Boundary

### 3.1 AG-UI

AG-UI 在 V0 中是 event rail。

规则：

- 只使用官方 AG-UI top-level event type。
- RM / A2UI 语义放进 `CUSTOM.name` 和 `CUSTOM.value`。
- 不自造 `surface.created` 这类 top-level event。

核心 carrier：

```json
{
  "type": "CUSTOM",
  "name": "a2ui.surface.messages",
  "value": {
    "surface_id": "surface_001",
    "messages": []
  }
}
```

### 3.2 A2UI

A2UI 在 V0 中是 declarative UI surface protocol。

当前采用 v0.9-style message envelope：

- `createSurface`
- `updateComponents`
- `updateDataModel`
- `deleteSurface`

A2UI 不负责 Hermes run lifecycle，也不负责 pending interaction 存储。

### 3.3 Pending interaction

Pending interaction 是 Hermes WebUI 的独立抽象，不能塞进 clarify。

典型前端回传：

```json
{
  "type": "pending_interaction.resolve",
  "run_id": "run_001",
  "thread_id": "thread_rm_001",
  "interaction_id": "pi_001",
  "surface_id": "surface_product_fit_001",
  "payload": {
    "selected_product_ids": ["prod_001", "prod_002"]
  }
}
```

---

## 4. UI Catalog

### 4.1 Layer 0 — Generic UI primitives（工作台 UI 词汇表）

Generic primitives 是所有 consumer 复用的 Layer 0 底座，是工作台的 UI 词汇表。
扩充 catalog = 工作台原子能力扩张，每次都是独立的有价值 issue。

V0 allowlist：

- `MetricCard`
- `DataTable`
- `LineChart`
- `BarChart`
- `PieChart`
- `ChoiceList`

这些不是 RM 语义组件。它们必须能从 mock fixture、inject endpoint、真实模型 emit
三种来源共同驱动；必填 props 缺失时显示空状态/警告，不抛运行时异常（ADR-010）。

### 4.2 Layer 1 — Business surfaces（过渡态保留，目标态废弃）

业务 surface 在目标态下不应该以 React 组件形式存在，而应该以 Skill prompt 资产
形式存在——Skill 教模型如何用 Layer 0 primitive 组合出业务语义（ADR-013）。

**当前过渡态**保留以下 React 组件，将由 Skill-driven Layer 1 migration issue 一次性
迁移并删除：

- `frontend/src/rm/surfaces/CustomerProfileCard`（≈ 多个 MetricCard）
- `frontend/src/rm/surfaces/ProductFitTable`（≈ DataTable + ChoiceList + interaction）
- `frontend/src/rm/surfaces/BriefExportPanel`（≈ Card + 标题文本）
- `frontend/src/rm/surfaces/MemoryDiffCard`（待评估是否能由 DataTable 表达）

**禁止**为新业务 consumer（CFA / 投资 / 日常 UI 生成）新建 `frontend/src/<domain>/surfaces/`
目录或对应后端分支。新业务通过 Skill 教模型用 Layer 0 primitive 表达。

---

## 5. Current State

已成立：

- Hermes Agent 能暴露 emit tool（命名重整后为 `emit_ui`）。
- WebUI backend 能在真实 stream bridge 中识别该 tool。
- runtime path 已通过 editable install 对齐到 `/Users/hywl/hermes-agent`。
- generic renderer catalog 已在 React workbench / mock path 中证明可渲染 table / chart / choice primitives。
- React structured-UI island 已 mount 进主 WebUI chat path（MYM-38 完成 host wiring）。

未成立 / 进行中（2026-05-09 校准后）：

- Layer 0 validator 仍是 RM-strict 状态（per-type 字段硬校验、kind 白名单、必填 metadata），
  本轮重构会放宽到最小校验。
- Layer 0 contract 信封仍包含 RM-only 必填字段（run_id / thread_id / skill），本轮改为可选+后端补默认。
- Layer 1 RM 业务字段（customer / product_candidates 等）目前在 `adapter.py` 通用路径上硬编码，
  本轮重构会把 RM 分支标记 transitional，由 Skill-driven Layer 1 migration issue 最终迁出。
- 主 WebUI chat path 渲染 generic primitive 的真实端到端 smoke 仍未完成（被 validator 严格度阻塞）。
- 第一条真实 RM workflow 尚未实现（Issue 8）。

---

## 6. Architecture Rules

- 不让 CopilotKit runtime takeover Hermes runtime。
- 不改 `/api/chat/stream` top-level SSE protocol。
- 不从 assistant text 猜 UI。
- 不执行任意 JSX / HTML / remote JS。
- 不为每种 UI primitive 新增独立 Hermes tool。
- Memory proposal-first，不自动写入。
- runtime / streaming / frontend host 相关 issue 必须有真实 WebUI smoke 证据。
- **Layer 0 路径不访问任何 Layer 1 业务字段**（`contract["customer"]` 等）。
  业务字段访问只能在 Layer 1 surface 渲染分支或 Skill 校验中出现（ADR-009 / ADR-013）。
- **Layer 0 validator 不抛 per-type 严格校验错误**。缺字段由 primitive 在前端兜底（ADR-010）。
- **Layer 0 contract 不做 kind 白名单路由**。kind/run_id/thread_id/skill 都可选（ADR-011）。
- **新业务 consumer 不写新代码**。先尝试用 Skill + Layer 0 primitive 表达，
  无法表达时独立提案扩充 Layer 0 catalog（ADR-013）。
