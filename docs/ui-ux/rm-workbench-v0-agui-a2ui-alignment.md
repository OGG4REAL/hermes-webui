# RM Workbench V0: AG-UI / A2UI Alignment Notes

路径：`docs/ui-ux/rm-workbench-v0-agui-a2ui-alignment.md`
状态：`active / protocol alignment / checked against current public docs on 2026-04-29`
目的：把 V0 mock adapter 与 AG-UI/A2UI 当前公开协议对齐，避免把自定义概念误写成官方标准事件。
V0 入口：`docs/ui-ux/rm-workbench-v0-index.md`

---

## 0. 结论

当前 V0 adapter 应该这样收敛：

```text
Hermes runtime event / RM Skill contract
  -> AG-UI standard event rail
  -> AG-UI CUSTOM event carries A2UI message stream
  -> React renderer renders A2UI surfaces
  -> UI action resolves Hermes pending interaction
```

关键点：

- AG-UI 是 event rail，不是 UI surface protocol。
- A2UI 是 UI surface/render protocol，不是完整 agent run lifecycle。
- RM semantic surface 不应该变成 AG-UI 标准事件。
- A2UI message 可以作为 AG-UI `CUSTOM` event 的 payload 传到前端。
- Pending interaction 是 Hermes/RM workbench 的业务交互状态，不能硬塞进 `clarify`。

---

## 1. 当前官方协议事实

### 1.1 AG-UI

AG-UI 当前核心是 streaming event-based architecture。

官方事件类型包含：

- lifecycle:
  - `RUN_STARTED`
  - `RUN_FINISHED`
  - `RUN_ERROR`
  - `STEP_STARTED`
  - `STEP_FINISHED`
- text message:
  - `TEXT_MESSAGE_START`
  - `TEXT_MESSAGE_CONTENT`
  - `TEXT_MESSAGE_END`
- tool call:
  - `TOOL_CALL_START`
  - `TOOL_CALL_ARGS`
  - `TOOL_CALL_END`
  - `TOOL_CALL_RESULT`
- state:
  - `STATE_SNAPSHOT`
  - `STATE_DELTA`
  - `MESSAGES_SNAPSHOT`
- activity:
  - `ACTIVITY_SNAPSHOT`
  - `ACTIVITY_DELTA`
- extension:
  - `RAW`
  - `CUSTOM`
- reasoning:
  - `REASONING_START`
  - `REASONING_MESSAGE_START`
  - `REASONING_MESSAGE_CONTENT`
  - `REASONING_MESSAGE_END`
  - `REASONING_MESSAGE_CHUNK`
  - `REASONING_END`

对 V0 最重要的是：

```text
CUSTOM = application-specific custom event
STATE_DELTA = JSON Patch state update
```

所以我们不能发一个自造的 AG-UI event type 叫 `surface.created`。正确做法是：

```json
{
  "type": "CUSTOM",
  "name": "a2ui.surface.messages",
  "value": {
    "surface_id": "surface_product_fit_001",
    "messages": []
  }
}
```

### 1.2 A2UI

A2UI 当前定位是 declarative UI protocol。

官方文档里 v0.8 是 current production release，v0.9 是 draft。v0.9 明确把 server-to-client message stream 拆成：

- `createSurface`
- `updateComponents`
- `updateDataModel`
- `deleteSurface`

并且强调：

- server-to-client 是一串 JSON object stream；
- client 逐条解析并增量更新 UI；
- component hierarchy 使用 flat component list + ID references；
- user actions 通常通过单独 endpoint 回传给 server/agent；
- A2UI transport-agnostic，不规定一定用 SSE、WebSocket 或 AG-UI。

对 V0 最重要的是：

```text
A2UI message stream 可以嵌在 AG-UI CUSTOM event 里，
但 A2UI 本身不负责 Hermes run lifecycle。
```

---

## 2. V0 Mapping Table

| Hermes / RM Workbench concept | AG-UI carrier | A2UI carrier | V0 decision |
| --- | --- | --- | --- |
| Agent run started | `RUN_STARTED` | none | 标准 AG-UI event |
| Agent run finished | `RUN_FINISHED` | none | 标准 AG-UI event |
| Agent run error | `RUN_ERROR` | none | 标准 AG-UI event |
| Skill started | `STEP_STARTED` | none | `step_name = skill:<name>` |
| Skill finished | `STEP_FINISHED` | none | `step_name = skill:<name>` |
| Text answer | `TEXT_MESSAGE_*` | none | 标准 AG-UI message stream |
| Tool call | `TOOL_CALL_*` | none | 标准 AG-UI tool lifecycle |
| RM Skill structured output | `CUSTOM` | none | `name = rm.skill.output` |
| CustomerProfileCard | `CUSTOM` | `createSurface` + `updateComponents` + `updateDataModel` | `name = a2ui.surface.messages` |
| ProductFitTable | `CUSTOM` | `createSurface` + `updateComponents` + `updateDataModel` | `name = a2ui.surface.messages` |
| PerformanceChart | `CUSTOM` | `createSurface` + `updateComponents` + `updateDataModel` | chart as common/custom catalog component |
| Pending interaction created | `CUSTOM` + optional `STATE_DELTA` | component `action.event` | `name = rm.pending_interaction.created` |
| Pending interaction resolved | frontend -> backend request | A2UI action event context | backend emits resume event later |
| Memory proposal | `CUSTOM` or `STATE_DELTA` | optional surface | do not auto-write memory |

---

## 3. Why CUSTOM Instead Of New Event Types

AG-UI already gives us a sanctioned extension point:

```json
{
  "type": "CUSTOM",
  "name": "rm.pending_interaction.created",
  "value": {}
}
```

This is preferable to inventing new top-level event types because:

- AG-UI clients can still parse the event stream.
- Unknown RM-specific payloads remain namespaced.
- We can later replace a custom payload with a standard event if AG-UI adds one.
- Frontend code can subscribe to `CUSTOM` names without forking the protocol.

So the V0 rule is:

> Only use official AG-UI `type` values. Put RM/A2UI semantics inside `CUSTOM.name` and `CUSTOM.value`.

---

## 4. A2UI Surface Shape For V0

The spike harness now uses A2UI v0.9-style messages:

```json
[
  {
    "version": "v0.9",
    "createSurface": {
      "surfaceId": "surface_product_fit_001",
      "catalogId": "rm-workbench-v0"
    }
  },
  {
    "version": "v0.9",
    "updateComponents": {
      "surfaceId": "surface_product_fit_001",
      "components": [
        {
          "id": "surface_product_fit_001_root",
          "component": "Table",
          "data": {
            "path": "/product_candidates"
          },
          "columns": ["name", "asset_class", "risk_level", "fit_score"]
        }
      ]
    }
  },
  {
    "version": "v0.9",
    "updateDataModel": {
      "surfaceId": "surface_product_fit_001",
      "path": "/",
      "data": {}
    }
  }
]
```

V0 still needs a final choice:

- Use v0.8 stable for implementation.
- Use v0.9 draft because its `createSurface` / `updateComponents` / `updateDataModel` envelopes fit our adapter model better.

Current recommendation:

> Spike with v0.9-style messages, but do not lock production until we inspect the current SDK package shape in the repo implementation step.

---

## 5. Pending Interaction Alignment

A2UI actions can dispatch events back to the agent/server. For V0, a button or table selection should produce:

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

This payload should be handled by hermes-webui backend/adapter, not by A2UI itself.

The backend then resumes Hermes/RM Skill with structured input.

---

## 6. Updated Spike Harness Result

The executable mock has been updated to follow this alignment:

```bash
python3 docs/ui-ux/rm-workbench-v0-spike/mock_adapter_check.py
```

Current output:

```text
OK: validated RM Skill contract
OK: mapped 3 surfaces
OK: produced 9 AG-UI-compatible events
OK: resolved pending interaction pi_001 with 2 selected products
```

What changed:

- Event types now use AG-UI-style uppercase standard names.
- RM-specific events use `CUSTOM`.
- A2UI surfaces are carried as `CUSTOM name = a2ui.surface.messages`.
- Pending interaction state is also reflected through `STATE_DELTA`.
- RM Skill output and pending resolve payload now have JSON Schema drafts under `docs/ui-ux/rm-workbench-v0-spike/schemas/`.

---

## 7. Implementation Implication

For the formal implementation plan, the first backend adapter should expose three internal functions:

```text
mapHermesRunToAgUiEvents(...)
mapRmSkillContractToA2UiMessages(...)
resolvePendingInteraction(...)
```

The first frontend renderer should subscribe to:

```text
AG-UI standard events
CUSTOM name = a2ui.surface.messages
CUSTOM name = rm.pending_interaction.created
STATE_DELTA pending_interactions
```

This keeps the architecture mature-protocol-first:

- AG-UI owns run/event/state transport.
- A2UI owns surface/component/data model.
- Hermes owns runtime.
- hermes-webui owns fact source and pending interaction state.
- RM Skill owns business semantics.

---

## 8. Sources Checked

- AG-UI Python SDK events: `https://docs.ag-ui.com/sdk/python/core/events`
- AG-UI JS SDK events: `https://docs.ag-ui.com/sdk/js/core/events`
- A2UI overview and version status: `https://a2ui.org/`
- A2UI v0.9 protocol specification: `https://a2ui.org/specification/v0.9-a2ui/`
