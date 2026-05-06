# RM Workbench V0: Real Hermes Stream Boundary Evaluation

路径：`docs/ui-ux/rm-workbench-v0-real-hermes-stream-boundary.md`
状态：`next planning / evaluation issue`
更新时间：`2026-05-06`

---

## 0. 这份文档解决什么

`MYM-24` 到 `MYM-27` 已经证明了 mock vertical slice：

```text
structured RM Skill-like contract
  -> api.rm_workbench.adapter
  -> AG-UI standard events + CUSTOM a2ui.surface.messages
  -> backend mock SSE stream
  -> React smoke workbench
  -> /api/rm-workbench/pending/resolve
```

下一步不要直接实现完整 RM 工作台，也不要直接接 CopilotKit runtime。现在要先回答一个更底层的问题：

```text
当事件来源从 backend mock stream 变成真实 Hermes Agent run 时，
AG-UI/A2UI events、pending interaction resolve、RM Skill.md、RM Workbench emit tool、
Memory proposal 分别应该接在哪一层？
```

这是一张 planning/evaluation issue，不是 feature implementation issue。

---

## 1. 当前已确认边界

已确认：

- Hermes Agent 继续做 runtime。
- hermes-webui 继续做 backend source of truth。
- React workbench host 继续消费 hermes-webui backend。
- AG-UI 负责运行事件和交互事件 rail。
- A2UI surface messages 继续放在 `CUSTOM name = a2ui.surface.messages` 里。
- pending interaction 继续独立于 approval/clarify。
- CopilotKit 不做 runtime takeover。

未确认：

- 真实 `/api/chat/stream` 是否直接输出 AG-UI-shaped event，还是继续输出现有 SSE event，再由 frontend bridge 映射。
- RM Skill.md 与专用 `rm_workbench_emit_contract` 工具如何分工。
- Hermes run 如何等待 structured UI input，并在 `/api/rm-workbench/pending/resolve` 后继续。
- Memory proposal 如何进入 UI，但不自动写入真实 Memory。
- CopilotKit frontend utilities 是否能只作为局部 UI helper 使用。

---

## 2. 下一张 Multica Issue 建议

标题：

```text
RM Workbench V0 Real Hermes Stream Boundary Evaluation
```

类型：

```text
planning / evaluation only
```

工作方式：

- 只读代码和文档。
- 不实现真实 RM Skill。
- 不改 Hermes Agent runtime。
- 不接 CopilotKit runtime。
- 不写 Memory。
- 允许创建一份 evaluation result 文档。

建议产物：

```text
docs/ui-ux/rm-workbench-v0-real-hermes-stream-evaluation-result.md
```

验收口径：

```text
This issue is complete only when the evaluation result doc makes a concrete architectural recommendation and gives the exact next implementation issue scope.
```

---

## 3. 必须回答的 5 个问题

### 3.1 真实 chat stream 如何承载 AG-UI/A2UI？

候选方案：

```text
A. Preserve existing /api/chat/stream SSE event names.
   Add rm_workbench events that carry AG-UI events as payload.

B. Change /api/chat/stream to emit AG-UI top-level events directly.

C. Add a separate /api/rm-workbench/stream route for real RM runs.
```

V0 倾向：

```text
A
```

原因：

- 现有 Hermes WebUI chat 已经依赖 `/api/chat/start` + `/api/chat/stream`。
- 直接把整个 chat stream 改成 AG-UI 风险高。
- 另开真实 RM stream 容易绕开现有 session/stream/cancel/title/tooling 状态。
- `rm_workbench` SSE event 已经在 `api.streaming` 里存在 pending interaction notify 的雏形。

下一张 issue 要验证：

- `frontend/src/api/hermesClient.ts` 是否应该新增 real chat stream client，还是只在后续 issue 里扩展。
- `frontend/src/agui/aguiReducer.ts` 是否能消费 `rm_workbench` SSE payload 中的 AG-UI events。
- `api/routes.py::_handle_sse_stream` 是否需要对 `rm_workbench` event 做任何特殊 envelope。

### 3.2 RM Skill.md 与 emit tool 如何分工？

当前 mock path：

```text
docs fixture -> api.rm_workbench.mock_data -> api.rm_workbench.adapter
```

真实 path 候选：

```text
A. RM Skill.md 指导 Agent；Agent 调用专用 rm_workbench_emit_contract 工具提交 structured contract。
B. 任意 Hermes Agent tool output 只要包含 rm_workbench_contract 字段就触发 adapter。
C. LLM text contains JSON and hermes-webui tries to parse it.
```

V0 倾向：

```text
A
```

原因：

- Hermes 当前 Skill 是文档型 skill：`SKILL.md` 通过 `skill_view` 或 slash command 注入上下文，不天然等于会返回 JSON 的函数。
- `rm_workbench_emit_contract` 给 adapter 一个稳定、可识别、可验证的抓取点。
- 扫描任意 tool output 容易误判，应该收窄到专用工具。
- 我们已经决定不从自然语言里猜 UI。
- adapter 只能 map structured contract，不能 parse assistant prose。

下一张 issue 要验证：

- Hermes WebUI 当前能否在不改 Hermes Agent runtime 的情况下暴露 `rm_workbench_emit_contract` 工具。
- `api.streaming._run_agent_streaming` 能否在该专用 tool completion 上识别 contract。
- 如果必须修改 `/Users/hywl/hermes-agent` 才能注册工具，是否拆成独立 issue。
- RM Skill.md 应如何指示 Agent 在需要 UI / pending interaction / memory proposal 时调用 emit tool。

### 3.3 pending interaction resolve 如何回到 Hermes run？

当前已有：

```text
api.pending_interactions.submit_pending(...)
api.pending_interactions.resolve_pending(...)
POST /api/rm-workbench/pending/resolve
api.streaming registers pending interaction notify callback
```

当前缺口：

```text
resolve_pending(...) 只把 result 放回 _PendingInteractionEntry。
但真实 Hermes run 需要一个 blocking wait point 或 callback，把 UI payload 返回给正在运行的 emit tool。
```

下一张 issue 要验证：

- 是否应该新增类似 clarify 的 blocking callback：

```text
pending_interaction_callback(request) -> dict
```

- Hermes Agent 是否支持注入新的 callback 参数。
- 如果不支持，是否通过 tool adapter 层阻塞等待 `entry.event`。
- cancel stream 时是否需要 `clear_pending(session_id)`，避免 agent 永久等待。
- resolve payload 是否必须带 `interaction_id`，避免同 session 多 pending 时误 resolve 最旧项。

### 3.4 Memory proposal 如何进入 UI？

V0 原则：

```text
Memory proposal-first, no automatic write.
```

下一张 issue 要验证：

- RM Workbench contract 是否应该包含：

```json
{
  "memory_proposals": [
    {
      "id": "mem_prop_001",
      "target": "customer",
      "operation": "upsert",
      "summary": "客户确认更偏好低回撤产品。",
      "evidence": ["..."],
      "requires_approval": true
    }
  ]
}
```

- adapter 是否应该新增：

```text
CUSTOM name = rm.memory_proposal.created
```

- V0 是否只渲染 `MemoryDiffCard`，不写入 Hermes memory、Codex memory 或银行事实源。

### 3.5 CopilotKit 在这一阶段做什么？

V0 原则：

```text
No CopilotKit runtime takeover.
```

下一张 issue 要验证：

- 是否有可复用的 frontend utility 或 UI pattern。
- 是否会引入第二套 run/session state。
- 是否需要单独起 `CopilotKit Boundary Evaluation` issue。

本 issue 的默认结论可以是：

```text
CopilotKit remains reference-only until real Hermes stream boundary is proven.
```

---

## 4. 必须阅读的代码位置

Backend:

- `api/routes.py`
  - `GET /api/chat/stream`
  - `POST /api/chat/start`
  - `GET /api/rm-workbench/mock-stream`
  - `POST /api/rm-workbench/pending/resolve`
- `api/streaming.py`
  - `_run_agent_streaming(...)`
  - approval notify registration
  - clarify callback
  - pending interaction notify registration
  - `cancel_stream(...)`
- `api/pending_interactions.py`
  - queue semantics
  - `submit_pending`
  - `resolve_pending`
  - `clear_pending`
- `api/rm_workbench/adapter.py`
  - structured contract -> AG-UI/A2UI mapping
- `api/rm_workbench/contracts.py`
  - V0 contract validation
- `tests/test_rm_workbench_adapter.py`
- `tests/test_pending_interactions.py`
- `tests/test_rm_workbench_routes.py`
- `tests/test_rm_workbench_mock_stream.py`

Frontend:

- `frontend/src/api/hermesClient.ts`
- `frontend/src/agui/aguiReducer.ts`
- `frontend/src/App.tsx`
- `frontend/src/a2ui/A2UISurfaceRenderer.tsx`
- `frontend/src/rm/surfaces/ProductFitTable.tsx`

Hermes Agent side, read-only:

- `/Users/hywl/hermes-agent/run_agent.py`
- `/Users/hywl/hermes-agent/skills/`
- Any existing Skill/tool result conventions discovered by `rg "clarify_callback|stream_delta_callback|tool_progress_callback|skill|structured|schema"`.

---

## 5. Evaluation Result 文档必须包含

`docs/ui-ux/rm-workbench-v0-real-hermes-stream-evaluation-result.md` 应包含：

### 5.1 Recommended Architecture

必须用一张文字 flow 写清：

```text
React workbench
  -> POST /api/chat/start
  -> GET /api/chat/stream
  -> api.streaming._run_agent_streaming
  -> Hermes Agent runtime
  -> RM Skill.md guides Agent
  -> rm_workbench_emit_contract submits structured contract
  -> api.rm_workbench.adapter
  -> rm_workbench SSE event carrying AG-UI events
  -> frontend aguiReducer + A2UI renderer
  -> POST /api/rm-workbench/pending/resolve
  -> blocking pending interaction wait resumes Hermes run
```

如果 worker 不同意这个 flow，必须明确说明替代 flow 的收益和代价。

### 5.2 Exact File Plan For Next Implementation Issue

必须列出下一张 implementation issue 允许改哪些文件。

建议默认文件边界：

```text
api/streaming.py
api/pending_interactions.py
api/routes.py
api/rm_workbench/emit_tool.py
api/rm_workbench/adapter.py
api/rm_workbench/contracts.py
frontend/src/api/hermesClient.ts
frontend/src/agui/aguiReducer.ts
frontend/src/App.tsx
tests/test_rm_workbench_real_stream_boundary.py
tests/test_pending_interactions.py
```

如果需要改 `/Users/hywl/hermes-agent`，必须拆成另一张 issue，并说明为什么 hermes-webui 侧 adapter seam 不够。

### 5.3 Contract Shape

必须给出最小 contract shape：

```json
{
  "kind": "rm.pre_meeting_brief",
  "version": "v0.1.0",
  "run_id": "run_001",
  "thread_id": "thread_001",
  "skill": "pre_meeting_brief",
  "surfaces": [],
  "pending_interactions": [],
  "memory_proposals": []
}
```

同时必须说明 `rm_workbench_emit_contract` 的最小接口：

```json
{
  "tool_name": "rm_workbench_emit_contract",
  "arguments": {
    "contract": {
      "kind": "rm.pre_meeting_brief",
      "version": "v0.1.0",
      "surfaces": [],
      "pending_interactions": [],
      "memory_proposals": []
    }
  }
}
```

### 5.4 Pending Interaction Resume Semantics

必须说明：

- `interaction_id` 是否必填。
- `resolve_pending` 是 resolve oldest 还是 resolve by id。
- blocking wait timeout 是多少。
- cancel stream 时如何 unblock。
- resolve payload 如何返回给 emit tool。

### 5.5 Tests Required For Next Implementation Issue

必须至少包含：

```text
1. real-stream bridge emits rm_workbench SSE event when rm_workbench_emit_contract submits structured contract
2. frontend reducer can consume rm_workbench payload containing AG-UI events
3. pending interaction resolve by interaction_id resumes waiting entry
4. stream cancel clears pending interaction and unblocks wait
5. no Memory write happens when memory proposals are emitted
6. existing clarify/approval/cancel tests still pass
```

### 5.6 Explicit Next Issue Draft

必须包含下一张 implementation issue 的可复制描述，至少包括：

```text
Title:
Repository:
Source of truth docs:
Allowed files:
Disallowed files:
Goal:
Implementation steps:
Acceptance commands:
Manual audit:
Do not do:
```

下一张 implementation issue 的默认标题建议：

```text
RM Workbench V0 Real Stream Bridge
```

这张 issue 的默认目标不是实现完整真实 RM Skill.md，而是先把真实 `/api/chat/stream` 能承载 `rm_workbench_emit_contract` -> adapter -> `rm_workbench` SSE payload 的 bridge 打通。

### 5.7 Open Questions That Require User Approval

如果 evaluation worker 发现以下任何问题，必须在 result doc 里标成 `requires user approval`：

- 需要修改 `/Users/hywl/hermes-agent` runtime。
- 需要引入 CopilotKit runtime。
- 需要连接真实客户数据或真实产品池。
- 需要把 Memory proposal 写入真实 Memory store。
- 需要把 `/api/chat/stream` top-level event protocol 改成 AG-UI。

---

## 6. 不要做的事

这张 planning/evaluation issue 不做：

- 不实现真实 RM Skill。
- 不改真实 Hermes Agent runtime 行为。
- 不接真实客户数据。
- 不接真实产品池。
- 不做 Memory 自动写入。
- 不接 CopilotKit runtime。
- 不做完整 RM 工作台视觉设计。
- 不把 `/api/chat/stream` 整体重写成 AG-UI 协议。

---

## 7. 推荐给 Multica 的 Issue 描述

```text
Repository: /Users/hywl/hermes-webui

Source of truth:
- docs/ui-ux/rm-workbench-v0-index.md
- docs/ui-ux/rm-workbench-v0-real-hermes-stream-boundary.md
- docs/ui-ux/rm-workbench-v0-implementation-plan.md

Context:
- MYM-24, MYM-25, MYM-26, and MYM-27 are complete and passed Codex review.
- The mock vertical slice now works: backend adapter -> mock SSE stream -> React smoke workbench -> pending resolve.
- This issue is planning/evaluation only. Do not implement real RM Skill or real Hermes stream integration yet.

Goal:
Produce docs/ui-ux/rm-workbench-v0-real-hermes-stream-evaluation-result.md, answering how the backend mock stream should evolve into a real Hermes /api/chat/stream integration.

Questions to answer:
1. Should real Hermes stream carry rm_workbench SSE events containing AG-UI events, or should /api/chat/stream become AG-UI top-level events?
2. How should RM Skill.md guide Agent to call rm_workbench_emit_contract, and where should that tool's contract be detected and mapped by api.rm_workbench.adapter?
3. How should /api/rm-workbench/pending/resolve return structured UI input to the running Hermes run?
4. How should Memory proposals be surfaced without automatic writes?
5. What remains reference-only for CopilotKit?

Required inspection:
- api/routes.py
- api/streaming.py
- api/pending_interactions.py
- api/rm_workbench/adapter.py
- api/rm_workbench/contracts.py
- frontend/src/api/hermesClient.ts
- frontend/src/agui/aguiReducer.ts
- frontend/src/App.tsx
- /Users/hywl/hermes-agent/run_agent.py read-only
- /Users/hywl/hermes-agent/skills read-only

Deliverable:
- Create docs/ui-ux/rm-workbench-v0-real-hermes-stream-evaluation-result.md.
- Include recommended architecture, rejected alternatives, exact implementation file plan, minimal contract shape, pending interaction resume semantics, tests required, risks, and concise acceptance checklist.

Do not do:
- Do not implement real RM Skill.
- Do not modify Hermes Agent runtime.
- Do not connect CopilotKit runtime.
- Do not write Memory.
- Do not use real customer/product data.
- Do not broaden into full RM workbench UI design.
```
