# RM Workbench V0 Architecture

路径：`docs/ui-ux/rm-workbench-v0-architecture.md`
状态：`active / canonical architecture`
更新时间：`2026-05-09`
入口：`docs/ui-ux/rm-workbench-v0-index.md`

---

## 0. 这份文档负责什么

这份文档只维护 RM Workbench V0 的当前架构事实。

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
  -> event: rm_workbench
  -> AG-UI CUSTOM carries A2UI messages
  -> React structured-UI host
  -> pending interaction resolve returns structured user input
```

V0 的目标不是让模型生成任意前端代码，而是让模型通过结构化参数选择 catalog item。

```text
Agent chooses catalog item + fills props
  -> frontend renders known component
```

---

## 2. System Components

### 2.1 Hermes Agent

职责：

- conversation loop
- tool calling
- Skill instruction loading
- runtime memory / approval / clarify 等既有能力

V0 不改 Hermes 主 runtime loop。

Hermes Agent 只需要暴露一个结构化 UI emit tool：

```text
rm_workbench_emit_contract
```

中期可以泛化为：

```text
emit_ui_contract
```

但 V0 不新增 `render_table`、`render_chart`、`render_form` 这类分散工具。

### 2.2 hermes-webui backend

职责：

- 继续作为 session / SSE / tool lifecycle / pending interaction 的事实源。
- 保留 `/api/chat/stream` top-level SSE protocol。
- 在真实 stream 中识别 `rm_workbench_emit_contract` tool completion。
- 把 tool contract 转成 `event: rm_workbench`。
- 维护 pending interaction resolve API。

关键边界：

```text
backend adapter maps contract
frontend renderer renders known catalog
```

backend 不从 assistant text 猜 UI。

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

### 4.1 Generic UI primitives

Generic primitives 是所有 Agent UI 场景复用的底座。

V0 allowlist：

- `MetricCard`
- `DataTable`
- `LineChart`
- `BarChart`
- `PieChart`
- `ChoiceList`

这些不是 RM 语义组件。

### 4.2 RM semantic surfaces

RM semantic surfaces 是业务组件。

当前 V0 重点：

- `CustomerProfileCard`
- `ProductFitTable`
- `BriefExportPanel`
- `MemoryDiffCard`

RM semantic surface 可以组合 generic primitives，也可以附带 RM-specific interaction semantics。

---

## 5. Current State

已成立：

- Hermes Agent 能暴露 `rm_workbench_emit_contract`。
- WebUI backend 能在真实 stream bridge 中识别该 tool。
- runtime path 已通过 editable install 对齐到 `/Users/hywl/hermes-agent`。
- generic renderer catalog 已在 React workbench / mock path 中证明可渲染 table / chart / choice primitives。

未成立：

- 主 WebUI chat path 还没有正式 React structured-UI host。
- 日常对话中一句话自然生成 UI 还不稳定。
- provider/model 对 deep nested object tool args 的稳定性仍需隔离验证。
- 第一条真实 RM workflow 尚未实现。

---

## 6. Architecture Rules

- 不让 CopilotKit runtime takeover Hermes runtime。
- 不改 `/api/chat/stream` top-level SSE protocol。
- 不从 assistant text 猜 UI。
- 不执行任意 JSX / HTML / remote JS。
- 不为每种 UI primitive 新增独立 Hermes tool。
- Memory proposal-first，不自动写入。
- runtime / streaming / frontend host 相关 issue 必须有真实 WebUI smoke 证据。
