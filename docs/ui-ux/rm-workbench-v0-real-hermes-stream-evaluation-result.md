# RM Workbench V0: Real Hermes Stream Evaluation Result

路径：`docs/ui-ux/rm-workbench-v0-real-hermes-stream-evaluation-result.md`
状态：`working / accepted evaluation result`
更新时间：`2026-05-06`
权威文档：`rm-workbench-v0-index.md`、`rm-workbench-v0-architecture.md`、`rm-workbench-v0-adr.md`

注意：本文保留 MYM-28 的评估过程和论证。已被接受的决策应以 ADR 为准，当前架构事实应以 Architecture 为准。

---

## 1. 推荐架构

### 1.1 推荐方案：方案 A — 保留现有 `/api/chat/stream` SSE，用 `rm_workbench` event 承载 AG-UI payload

```text
React workbench
  -> POST /api/chat/start (沿用现有 session / stream 初始化)
  -> GET /api/chat/stream (沿用现有 SSE 通道)
  -> api.streaming._run_agent_streaming
  -> Hermes Agent runtime (run_conversation)
  -> RM Skill.md 指导 Agent 完成 RM 工作流判断
  -> Agent 调用 rm_workbench_emit_contract 工具提交 structured RM contract
  -> api.streaming 中 tool_complete_callback 只识别该专用工具的 contract
  -> api.rm_workbench.adapter.map_rm_skill_contract_to_agui_events()
  -> put('rm_workbench', { kind: 'agui_events', events: [...] })
  -> 前端现有 SSE consumer 在收到 rm_workbench event 时分发给 aguiReducer
  -> A2UI renderer 渲染 surfaces
  -> 用户操作 -> POST /api/rm-workbench/pending/resolve
  -> api.pending_interactions.resolve_pending() 唤醒 blocking wait
  -> Hermes run 继续执行
```

### 1.2 拒绝方案

**方案 B — 把 `/api/chat/stream` 整体改为 AG-UI top-level events**

拒绝理由：
- 现有 Hermes WebUI chat 全部功能（text streaming、tool progress、approval、clarify、metering、cancel、compress）都依赖当前 SSE event names（`token`、`tool`、`tool_complete`、`approval`、`clarify`、`done`、`cancel` 等）。
- 把 top-level SSE protocol 改成 AG-UI 要求同时重写前端 chat 消费逻辑，风险极高且超出 V0 范围。
- AG-UI 的 `TEXT_MESSAGE_*`、`TOOL_CALL_*` 等标准事件与 Hermes 现有 token/tool 事件语义重合但 schema 不同，强行映射必然引入 N 对 N 转换层且无增量收益。

**方案 C — 新开 `/api/rm-workbench/stream` 独立路由做真实 RM runs**

拒绝理由：
- `/api/chat/start` + `/api/chat/stream` 已经管理 session、stream_id、cancel_event、STREAMS dict、agent lock、checkpoint 等全套状态。
- 另开路由意味着要复制或共享这套状态管理，极容易出现 session 不同步、cancel 失效、stream_id 冲突。
- `api.streaming._run_agent_streaming` 已经注册了 `pending_interaction_notify_cb`，把 `rm_workbench` SSE event 注入到现有 stream queue 里，架构缝隙已经存在。
- Mock stream 路由 `/api/rm-workbench/mock-stream` 可以继续保留供开发验证，不需要升级为生产路由。

---

## 2. Skill / Tool / Adapter 边界

### 2.1 必须区分文档型 Skill 和结构化 Emit Tool

Hermes 当前的 Skill 机制是文档型 skill：

```text
SKILL.md
  -> skill_view 或 /skill-name 读取
  -> 作为 user message 注入上下文
  -> LLM 按技能文档执行工作流
```

它不是一个天然会执行并返回 JSON 的函数。因此 V0 不应再使用“RM Skill tool 返回 structured JSON contract”这个表述。

V0 的正确边界是：

```text
RM Skill.md
  = 业务逻辑 / 工作流 / know-how / 输出意图
  = 决定该不该展示 UI、展示什么业务 surface、需要什么用户输入、是否提出 memory proposal

rm_workbench_emit_contract tool
  = 结构化出口
  = 接收 Skill 推理出的 RM contract
  = 给 hermes-webui adapter 一个稳定、可识别、可验证的抓取点

api.rm_workbench.adapter
  = 协议翻译层
  = RM contract -> AG-UI events + A2UI surface messages

frontend hook
  = /api/chat/stream 中的 rm_workbench SSE event
  = 不读取 SKILL.md，不解析 assistant text，不直接理解任意 tool result
```

### 2.2 与 ai_sandbox 的差异

`ai_sandbox` 的模式可以概括为：

```text
Skill.md 指导 Agent
  -> Agent 调用多个具体 UI tools: render_table / render_chart / show_notification
  -> 每个 UI tool 直接绑定一个具体 UI 类型
```

RM Workbench V0 应该升级为：

```text
Skill.md 指导 Agent
  -> Agent 调用一个协议化 rm_workbench_emit_contract tool
  -> contract 声明 surfaces / data / pending_interactions / memory_proposals
  -> adapter 根据协议映射到 A2UI catalog
  -> frontend 统一消费 rm_workbench SSE event
```

这样避免 `render_table`、`render_chart`、`render_card` 这类具体 UI 工具膨胀，也避免把前端形态绑死在 Agent tool 层。

### 2.3 前端真正 hook 什么

前端只 hook：

```text
event: rm_workbench
data.kind = "agui_events"
```

前端不 hook：

```text
SKILL.md
assistant text
任意 tool result
rm_workbench_emit_contract tool args
```

`rm_workbench_emit_contract` 是 backend-side detection seam；`rm_workbench` SSE event 才是 frontend hook point。

---

## 3. `/api/chat/stream` SSE event 承载方式

### 3.1 保留现有 SSE event names

现有 SSE event names 不变：`token`、`tool`、`tool_complete`、`approval`、`clarify`、`done`、`cancel`、`metering`、`apperror`、`compressed`、`stream_end`。

### 3.2 `rm_workbench` event 承载 AG-UI payload

当 `_run_agent_streaming` 识别到 `rm_workbench_emit_contract` 工具提交的 structured RM contract 时，通过 `put('rm_workbench', ...)` 发出以下 SSE event：

```text
event: rm_workbench
data: {
  "kind": "agui_events",
  "events": [
    { "type": "RUN_STARTED", "thread_id": "...", "run_id": "..." },
    { "type": "CUSTOM", "name": "rm.skill.output", "value": {...} },
    { "type": "CUSTOM", "name": "a2ui.surface.messages", "value": {...} },
    { "type": "CUSTOM", "name": "rm.pending_interaction.created", "value": {...} },
    { "type": "STATE_DELTA", "delta": [...] },
    { "type": "STEP_FINISHED", "step_name": "skill:pre_meeting_brief" }
  ]
}
```

已有的 `rm_workbench` event（`kind: 'pending_interaction'`）保持不变，与 `kind: 'agui_events'` 并存。

### 3.3 为什么用 `kind` 字段区分

`rm_workbench` SSE event 已经有 `kind: 'pending_interaction'` 的先例（`api/streaming.py:1262-1268`）。新增 `kind: 'agui_events'` 保持一致性，前端可按 `kind` dispatch。

---

## 4. RM Workbench Contract Shape

### 4.1 最小 contract

```json
{
  "kind": "rm.pre_meeting_brief",
  "version": "0.1.0",
  "run_id": "run_001",
  "thread_id": "thread_001",
  "skill": "pre_meeting_brief",
  "customer": {
    "id": "cust_001",
    "name": "张总",
    "risk_level": "R3",
    "aum": "5000万"
  },
  "product_candidates": [
    {
      "id": "prod_001",
      "name": "稳健增长 A",
      "asset_class": "fixed_income",
      "risk_level": "R2",
      "fit_score": 0.85
    }
  ],
  "surfaces": [
    {
      "id": "surface_customer_001",
      "surface": "CustomerProfileCard",
      "props": {}
    },
    {
      "id": "surface_product_fit_001",
      "surface": "ProductFitTable",
      "props": {}
    }
  ],
  "pending_interactions": [
    {
      "id": "pi_001",
      "surface_id": "surface_product_fit_001",
      "action": "select_products",
      "blocking": true,
      "schema": {
        "type": "object",
        "properties": {
          "selected_product_ids": {
            "type": "array",
            "items": { "type": "string" }
          }
        },
        "required": ["selected_product_ids"]
      }
    }
  ],
  "memory_proposals": [
    {
      "id": "mem_prop_001",
      "target": "customer",
      "operation": "upsert",
      "summary": "客户确认更偏好低回撤产品。",
      "evidence": ["用户在产品筛选中排除了所有 R4 以上产品"],
      "requires_approval": true
    }
  ]
}
```

### 4.2 `rm_workbench_emit_contract` 工具形态

V0 Real Stream Bridge 应新增或暴露一个专用工具：

```text
tool name: rm_workbench_emit_contract
purpose: Emit a structured RM Workbench contract for adapter mapping and frontend rendering.
```

建议参数：

```json
{
  "contract": {
    "kind": "rm.pre_meeting_brief",
    "version": "0.1.0",
    "run_id": "run_001",
    "thread_id": "thread_001",
    "skill": "pre_meeting_brief",
    "surfaces": [],
    "pending_interactions": [],
    "memory_proposals": []
  }
}
```

建议工具返回：

```json
{
  "ok": true,
  "contract_id": "rmc_001",
  "emitted_events": 9,
  "pending_interactions": ["pi_001"],
  "memory_proposals": ["mem_prop_001"]
}
```

注意：

- Tool 参数里的 `contract` 是 adapter 的原材料。
- Tool 返回值是给 Hermes Agent 继续推理的摘要。
- 前端不读取 tool 参数或返回值；前端只读取 `/api/chat/stream` 的 `rm_workbench` SSE event。

### 4.3 `memory_proposals` 边界

- `memory_proposals` 是 contract 的可选字段，默认 `[]`。
- V0 adapter 遇到 `memory_proposals` 时生成 `CUSTOM name = rm.memory_proposal.created` 事件。
- 前端渲染 `MemoryDiffCard` surface 展示 proposal 内容。
- **V0 不做任何 Memory 写入** — 不写 Hermes Memory、不写 Codex Memory、不写银行事实源。
- Memory proposal 的 `requires_approval: true` 表示必须等待人工审批后才能在后续版本写入。
- V0 不实现审批 → 写入的链路，只展示。

### 4.4 Contract 检测方式

V0 不扫描所有 tool result，也不按 `kind: "rm.*"` 泛化猜测。只识别专用工具：

```text
tool_name == "rm_workbench_emit_contract"
```

识别步骤：

```text
1. tool_complete_callback 收到 rm_workbench_emit_contract 的 tool completion
2. 从 tool args 或 tool result 中提取 contract
3. contract["kind"] 以 "rm." 开头
4. contract["version"] 存在
5. api.rm_workbench.contracts.validate_contract(contract) 通过
6. api.rm_workbench.adapter.map_rm_skill_contract_to_agui_events(contract)
7. put('rm_workbench', { kind: 'agui_events', events: [...] })
```

V0 不解析 assistant text，不猜测 UI，不从任意 tool result 中探测 RM contract。

如果 Hermes Agent 暂时没有真实 RM Skill，仍可以先实现 `rm_workbench_emit_contract` 作为 hermes-webui-side contract injection seam。后续真实 RM Skill.md 只需要指导 Agent 调用这个工具即可。

---

## 5. Pending Interaction Resume Semantics

### 5.1 `interaction_id` 是否必填

**必填。** 当同一 session 存在多个 pending interaction 时（例如 V1 支持多 surface 各有一个 pending），只按 oldest 解析会导致误 resolve。`resolve_pending` 必须按 `interaction_id` 匹配。

当前 `api.pending_interactions.resolve_pending(session_key, payload, resolve_all=False)` 的实现是 resolve oldest entry。V0 实现需要：

- `resolve_pending` 新增 `interaction_id` 参数。
- 匹配 `interaction_id` 后 resolve 对应 entry。
- 如果 `interaction_id` 不存在于 pending queue，返回 404 错误。

### 5.2 Blocking Wait 机制

当前 `_PendingInteractionEntry` 使用 `threading.Event` 做 blocking wait。这与 `clarify_callback_impl` 的模式一致（`api/streaming.py:1275-1310`）。

推荐方式：

```text
1. rm_workbench_emit_contract 工具发现 contract 中存在 blocking pending_interaction。
2. 工具调用 submit_pending(session_key, data)。
2. submit_pending 创建 _PendingInteractionEntry，设置 threading.Event。
3. pending_interaction_notify_cb 将 rm_workbench SSE event 推到前端。
4. tool 调用 entry.event.wait(timeout=timeout) 阻塞等待。
5. 前端 POST /api/rm-workbench/pending/resolve 提交 payload。
6. resolve_pending 把 payload 写入 entry.result，set() event。
7. tool 从 wait 返回，读取 entry.result，继续 Hermes run。
```

实现时可以先支持一个 non-blocking emit mode，用于只渲染 surfaces；涉及用户输入时再启用 blocking wait。这个拆分可以降低 V0 implementation 风险。

### 5.3 Timeout

- 默认 timeout：**300 秒**（5 分钟），与 clarify 的 120 秒不同，因为 RM Skill 的用户决策（选产品、review memory）通常需要更多时间。
- Timeout 后 tool 返回 timeout error message，Hermes Agent 用 best judgement 继续（与 clarify timeout 行为一致）。
- Timeout 可通过 pending interaction 的 `timeout` 字段覆盖。

### 5.4 Cancel Stream 处理

当用户取消 stream（`cancel_stream(stream_id)`）时：

- `cancel_event.is_set()` 会导致 blocking wait 在下一次 poll 时退出（参照 clarify cancel 逻辑 `api/streaming.py:1297-1302`）。
- 必须调用 `clear_pending(session_id)` unblock 所有等待的 entry。
- 推荐在 `cancel_stream` 的 finally 块中加入 `clear_pending`，与现有 `clear_clarify_pending` 并列。

### 5.5 同 Session 多 Pending 处理原则

V0 原则：**同一时刻最多一个 blocking pending interaction**。

- 如果 RM Skill contract 包含多个 `pending_interactions`，adapter 按顺序生成事件，但 Hermes run 只在第一个 blocking interaction 处阻塞。
- 解析第一个后，如果有下一个 blocking interaction，Skill tool 再次 submit_pending。
- 这避免了前端同时展示多个 blocking modal 的 UX 复杂度。

### 5.6 Resolve Payload 返回给 Tool

`resolve_pending` 将 payload 写入 `entry.result`。Tool 从 `entry.event.wait()` 返回后读取 `entry.result`：

```python
result = entry.result  # {"selected_product_ids": ["prod_001", "prod_002"]}
```

Tool 将 result 作为 tool output 的一部分返回给 Hermes Agent，Agent 在下一轮推理中使用这些结构化输入。

---

## 6. Memory Proposal 边界

### 6.1 展示，不自动写入

- RM Workbench contract 的 `memory_proposals` 字段由 adapter 映射为：

```json
{
  "type": "CUSTOM",
  "name": "rm.memory_proposal.created",
  "value": {
    "run_id": "run_001",
    "thread_id": "thread_001",
    "proposals": [
      {
        "id": "mem_prop_001",
        "target": "customer",
        "operation": "upsert",
        "summary": "...",
        "evidence": ["..."],
        "requires_approval": true
      }
    ]
  }
}
```

- 前端 `aguiReducer` 在收到此事件时更新 state 中的 `memoryProposals`。
- `MemoryDiffCard` surface 渲染这些 proposals，展示 summary 和 evidence。
- **V0 不提供 "Approve" 按钮**。用户看到 proposal 但无法操作。后续版本添加审批 → 写入链路。
- 不写入 Hermes `~/.hermes/memories/`，不写入任何外部 Memory store。

---

## 7. CopilotKit 定位

### 7.1 结论：reference-only / defer

CopilotKit 在 V0 阶段保持 **reference-only** 定位。

### 7.2 理由

1. **运行时冲突**：CopilotKit 的 `CopilotRuntime` 要求自己管理 agent run lifecycle（start、stream、state）。Hermes Agent 已经通过 `run_conversation` 管理完整 lifecycle，引入 CopilotKit runtime 意味着要么二者共存（两套 run state），要么放弃 Hermes runtime（超出 V0 决策）。

2. **SSE 协议不兼容**：CopilotKit 使用自己的 SSE protocol（与 AG-UI 对齐但有私有扩展），现有 `/api/chat/stream` 使用 Hermes-specific SSE protocol。在同一 stream 里混合两种协议增加了前端消费复杂度。

3. **session/state 管理冲突**：CopilotKit 使用 `CopilotContext`、`useCopilotChat` 等 hooks 管理前端 state。现有 workbench 使用自建 `aguiReducer` + React state。引入 CopilotKit hooks 意味着两套 state 需要同步。

4. **可局部复用的部分**：CopilotKit 的 `@copilotkit/react-ui` 中的某些 UI 组件（如 message bubble、streaming text renderer）理论上可以独立使用，但 V0 smoke workbench 已经有足够简单的 UI，引入额外依赖没有增量价值。

5. **defer 到何时**：当 real Hermes stream bridge 稳定运行后，可以评估 CopilotKit 的 frontend utility 是否能替换自建 UI 组件。这应该是独立的 `CopilotKit Boundary Evaluation` issue。

---

## 8. 下一张 Implementation Issue 精确文件范围

### 8.1 标题

```text
RM Workbench V0 Real Stream Bridge
```

### 8.2 允许修改的文件

```text
api/streaming.py                  — 只识别 rm_workbench_emit_contract tool completion 并调用 adapter
api/pending_interactions.py        — resolve_pending 新增 interaction_id 参数；blocking wait helper
api/routes.py                      — /api/rm-workbench/pending/resolve 路由支持 interaction_id
api/rm_workbench/emit_tool.py      — 新增专用 emit tool 的 contract extraction / result formatting helper
api/rm_workbench/adapter.py        — 新增 memory_proposals 映射
api/rm_workbench/contracts.py      — memory_proposals 字段可选；校验 emit tool contract
frontend/src/api/hermesClient.ts   — 新增 real chat stream 中 rm_workbench event 解析
frontend/src/agui/aguiReducer.ts   — 消费 rm_workbench SSE payload 中的 AG-UI events
frontend/src/App.tsx               — 支持从 real chat stream 触发 workbench mode
tests/test_rm_workbench_real_stream_bridge.py — 新增
tests/test_pending_interactions.py             — 扩展
```

### 8.3 不允许修改的文件

```text
/Users/hywl/hermes-agent/**  — Hermes Agent runtime 不改
frontend/src/rm/surfaces/**          — V0 surfaces 已完成，不需要改
frontend/src/a2ui/**                 — A2UI renderer 已完成，不需要改
```

如果评估发现必须修改 Hermes Agent runtime（例如需要新增 callback 参数），必须拆成独立 issue 并说明为什么 hermes-webui adapter seam 不够。

---

## 9. 下一张 Implementation Issue 测试清单和验收命令

### 9.1 测试清单

```text
1. emit tool 检测：tool_complete_callback 只在 tool_name == rm_workbench_emit_contract 时调用 adapter
2. rm_workbench SSE event：adapter 生成的 AG-UI events 通过 put('rm_workbench', ...) 发出
3. 前端 reducer：aguiReducer 能消费 rm_workbench payload 中的 AG-UI events 并生成 surfaces
4. pending interaction resolve by interaction_id：resolve_pending 按 ID 匹配正确 entry
5. blocking wait + timeout：submit_pending 阻塞，resolve_pending 唤醒，timeout 后返回默认
6. stream cancel clears pending：cancel_stream 调用 clear_pending，阻塞 wait 退出
7. memory proposals：adapter 生成 rm.memory_proposal.created 事件，前端展示但不写入
8. 现有 clarify/approval/cancel 测试不受影响：所有已有测试继续通过
9. mock stream 路由不受影响：/api/rm-workbench/mock-stream 继续正常工作
```

### 9.2 验收命令

```bash
# 后端测试
cd /Users/hywl/hermes-webui
python -m pytest tests/test_rm_workbench_real_stream_bridge.py -v
python -m pytest tests/test_pending_interactions.py -v
python -m pytest tests/test_rm_workbench_adapter.py -v
python -m pytest tests/test_rm_workbench_routes.py -v
python -m pytest tests/test_rm_workbench_mock_stream.py -v

# 确保现有测试不 break
python -m pytest tests/ -v --tb=short

# 前端 type check (如果 tsconfig 可用)
cd frontend && npx tsc --noEmit 2>/dev/null; cd ..

# 文档验证
rg -n "rm_workbench|AG-UI|A2UI|CUSTOM|contract|pending|memory_proposals" api/streaming.py | head -20
```

---

## 10. 下一张 Implementation Issue 完整草案

```text
Title:
  RM Workbench V0 Real Stream Bridge

Repository:
  /Users/hywl/hermes-webui

Source of truth docs:
  - docs/ui-ux/rm-workbench-v0-index.md
  - docs/ui-ux/rm-workbench-v0-real-hermes-stream-boundary.md
  - docs/ui-ux/rm-workbench-v0-real-hermes-stream-evaluation-result.md
  - docs/ui-ux/rm-workbench-v0-agui-a2ui-alignment.md

Allowed files:
  - api/streaming.py
  - api/pending_interactions.py
  - api/routes.py
  - api/rm_workbench/adapter.py
  - api/rm_workbench/contracts.py
  - frontend/src/api/hermesClient.ts
  - frontend/src/agui/aguiReducer.ts
  - frontend/src/App.tsx
  - tests/test_rm_workbench_real_stream_bridge.py (new)
  - tests/test_pending_interactions.py

Disallowed files:
  - /Users/hywl/hermes-agent/** (read-only reference only)
  - frontend/src/rm/surfaces/** (already complete)
  - frontend/src/a2ui/** (already complete)

Goal:
  在现有 /api/chat/stream SSE 通道中，当 Hermes Agent 调用专用
  rm_workbench_emit_contract 工具提交符合 RM contract schema 的 JSON 时，
  自动调用 adapter 生成 AG-UI events，
  通过 rm_workbench SSE event 推送到前端，前端 aguiReducer 消费并渲染 surfaces。
  同时完善 pending interaction 的 interaction_id 匹配、blocking wait、timeout、
  cancel 清理逻辑。Memory proposals 只展示不写入。

Implementation steps:
  1. api/rm_workbench/emit_tool.py — 新增 rm_workbench_emit_contract helper：
     接收 contract，调用 validate_contract，返回标准 tool result 摘要。
  2. api/streaming.py — 在 tool_complete_callback 中只识别
     rm_workbench_emit_contract tool completion，从 tool args/result 提取 contract，
     通过后调用 adapter 并 put('rm_workbench', { kind: 'agui_events', events: [...] })。
  3. api/pending_interactions.py — resolve_pending 新增 interaction_id 参数；
     submit_pending 返回 entry 引用供 blocking wait；新增 wait_for_resolution
     helper（封装 event.wait + timeout + cancel check）。
  4. api/routes.py — /api/rm-workbench/pending/resolve 接受 interaction_id 参数，
     传给 resolve_pending。
  5. api/rm_workbench/adapter.py — 新增 memory_proposals -> CUSTOM rm.memory_proposal.created
     映射。
  6. api/rm_workbench/contracts.py — memory_proposals 字段可选（默认 []）。
  7. frontend/src/api/hermesClient.ts — 新增 parseRmWorkbenchEvent(data) helper，
     从 rm_workbench SSE payload 中提取 AG-UI events。
  8. frontend/src/agui/aguiReducer.ts — 新增 LOAD_REAL_STREAM action，消费从
     real chat stream 收到的 AG-UI events。
  9. frontend/src/App.tsx — 在 chat stream SSE consumer 中识别 rm_workbench event，
     dispatch 给 aguiReducer，切换到 workbench mode。
  10. tests — 编写完整测试覆盖上述所有步骤。

Acceptance commands:
  python -m pytest tests/ -v --tb=short
  test -f tests/test_rm_workbench_real_stream_bridge.py

Manual audit:
  - 确认 tool_complete_callback 只识别 rm_workbench_emit_contract，不扫描任意 tool result。
  - 确认 cancel_stream 后 pending interaction blocking wait 正确退出。
  - 确认 rm_workbench SSE event 格式与 mock stream 的 AG-UI event 格式一致，
    前端 reducer 可以无差异消费。

Do not do:
  - 不实现真实 RM Skill（Hermes Agent 侧）。
  - 不改 Hermes Agent runtime 代码。
  - 不接真实客户数据或真实产品池。
  - 不做 Memory 自动写入。
  - 不接 CopilotKit runtime。
  - 不改现有 Hermes chat 的 token/tool/approval/clarify SSE event 格式。
```

---

## 11. 风险、开放问题、明确不做事项

### 11.1 风险

1. **Hermes Agent 是否支持注入新 callback**：当前 `AIAgent.__init__` 接受 `tool_complete_callback` 等回调参数。如果 V0 Real Stream Bridge 需要在 tool complete 时拦截并阻塞 Agent 线程（等待 pending interaction resolve），现有 callback 是否支持返回值来阻塞执行？
   - **调研结论**：当前 `tool_complete_callback` 是 fire-and-forget（`api/streaming.py:1421-1434` 中只是 `put('tool_complete', ...)`，不等待返回值）。**阻塞不应该发生在 callback 中**，而应该发生在 **rm_workbench_emit_contract 工具内部**。tool_complete_callback 只是在 tool 完成后触发 adapter 映射。
   - **结论**：不需要修改 Hermes Agent runtime。contract 检测在 tool_complete_callback 中触发 adapter，但 blocking wait 在 tool 执行内部完成。这与 clarify_callback 的模式完全对齐。

2. **专用 emit tool 是否需要注册到 Hermes Agent 工具集**：V0 不能只在 hermes-webui 写 helper，还必须确认该工具能被 Agent 看见并调用。
   - **缓解**：下一张 issue 必须先定位 Hermes WebUI 当前 tool schema 来源。如果新增工具必须进入 Hermes Agent repo，则拆成独立 issue；如果 hermes-webui 能通过 toolset/adapter 暴露工具，则保持在 hermes-webui 范围内。

3. **Contract 检测的误判**：如果扫描任意 tool result，会有误判风险。
   - **缓解**：V0 不扫描任意 tool result，只识别 `tool_name == "rm_workbench_emit_contract"`。

4. **前端双模式复杂度**：同一个 SSE stream 里混合 Hermes chat events 和 rm_workbench events，前端需要同时维护 chat state 和 workbench state。
   - **缓解**：workbench state 由独立的 `aguiReducer` 管理，与 chat state 互不干扰。`rm_workbench` event 的 `kind` 字段清晰区分 `agui_events` 和 `pending_interaction`。

### 11.2 开放问题（需要用户拍板）

1. **RM Skill 与 emit tool 的拆分**：RM Skill.md 负责业务逻辑，`rm_workbench_emit_contract` 负责结构化出口。V0 Real Stream Bridge 先实现 emit tool 和 adapter bridge，不实现完整真实 RM Skill.md。用户是否同意这个拆分？

2. **Timeout 时长**：pending interaction 默认 300 秒。是否需要更长？

3. **Memory proposal 后续路径**：V0 只展示不写入。V1 是否需要审批 → 写入链路？如果需要，写入目标是 Hermes Memory 还是外部系统？

4. **emit tool 注册位置**：如果 hermes-webui 不能直接暴露该工具给 Hermes Agent，是否允许开独立 issue 修改 `/Users/hywl/hermes-agent`？

### 11.3 明确不做事项

- 不实现完整真实 RM Skill.md。
- 不修改 Hermes Agent runtime。
- 不接真实客户数据或真实产品池。
- 不做 Memory 自动写入。
- 不接 CopilotKit runtime。
- 不做 React/CopilotKit runtime 改造。
- 不重写完整 Hermes chat stream 协议。
- 不做完整 RM 工作台视觉设计。
- 不把 `/api/chat/stream` top-level event protocol 改成 AG-UI。
