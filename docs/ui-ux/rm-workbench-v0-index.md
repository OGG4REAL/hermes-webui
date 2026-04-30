# RM Workbench V0: Documentation Index

路径：`docs/ui-ux/rm-workbench-v0-index.md`
状态：`active / start here`
更新时间：`2026-04-29`
目的：作为 RM Workbench V0 的唯一入口，避免后续工程 agent 被早期讨论文档绕进去。

---

## 0. 一句话结论

V0 先做成熟协议优先的最小技术闭环：

```text
Hermes Agent runtime
  -> hermes-webui backend as source of truth
  -> AG-UI standard event rail
  -> AG-UI CUSTOM carries A2UI surface messages
  -> React workbench host
  -> pending interaction resolve returns structured UI input
```

当前不做 CopilotKit runtime takeover。

当前也不从自然语言里猜 UI。RM Skill 必须输出结构化 contract，adapter 只负责映射。

---

## 1. 新窗口 / Multica Worker 只需要先读这三份

### 1.1 技术选型边界

`docs/ui-ux/rm-workbench-v0-technical-skeleton.md`

用途：

- 确认 Hermes Agent、hermes-webui、React、AG-UI、A2UI、CopilotKit 各自在哪一层。
- 确认 V0 为什么先走 Hermes runtime 主导 + AG-UI/A2UI adapter。

### 1.2 协议对齐结论

`docs/ui-ux/rm-workbench-v0-agui-a2ui-alignment.md`

用途：

- 确认 AG-UI 标准事件边界。
- 确认 A2UI surface message 边界。
- 确认为什么不用自造 `surface.created` 这类 AG-UI event type。
- 确认 V0 该用 `CUSTOM name = a2ui.surface.messages` 承载 A2UI message stream。

### 1.3 正式实现计划

`docs/ui-ux/rm-workbench-v0-implementation-plan.md`

用途：

- 工程执行入口。
- 包含文件边界、任务拆分、测试、验收标准。
- 后续 Multica issue 应从这份文档拆。

---

## 2. 可执行 Spike Reference

`docs/ui-ux/rm-workbench-v0-spike/`

用途：

- 提供 mock fixture、schema draft、mock adapter check。
- 验证 structured Skill output -> AG-UI-compatible events -> A2UI messages -> pending resolve 这条链路。

当前验证命令：

```bash
python3 docs/ui-ux/rm-workbench-v0-spike/mock_adapter_check.py
```

当前预期输出：

```text
OK: validated RM Skill contract
OK: mapped 3 surfaces
OK: produced 9 AG-UI-compatible events
OK: resolved pending interaction pi_001 with 2 selected products
```

---

## 3. Reference-Only 文档

这些文档可以读，但不作为工程执行的第一事实源。

### 3.1 Protocol Examples

`docs/ui-ux/rm-workbench-v0-protocol-examples.md`

用途：

- 看具体 JSON 样例。
- 帮助理解 Skill output、surface、pending interaction、memory proposal 如何串起来。

注意：

- 若样例和 `rm-workbench-v0-agui-a2ui-alignment.md` 冲突，以 alignment 文档为准。
- 若样例和 `rm-workbench-v0-implementation-plan.md` 冲突，以 implementation plan 为准。

### 3.2 Adapter Spike Plan

`docs/ui-ux/rm-workbench-v0-adapter-spike-plan.md`

用途：

- 保留技术验证过程和决策门。
- 解释为什么先做 mock harness，再进 implementation plan。

注意：

- 工程执行以 `rm-workbench-v0-implementation-plan.md` 为准。

### 3.3 React Migration Plan

`docs/ui-ux/hermes-react-migration-plan.md`

用途：

- React workbench host 的背景参考。
- 解释为什么 React host 应该以 hermes-webui 后端为事实源。

注意：

- V0 的第一批 backend adapter + pending interaction 已完成。下一批只做 frontend smoke workbench，不做完整 React chat replacement。

---

## 4. Historical / Superseded 文档

这些是早期讨论记录，保留用于追溯，不建议 Multica worker 默认阅读。

### 4.1 Broad Options Memo

`docs/ui-ux/agent-native-workbench-tech-options.md`

用途：

- 早期把问题摊开的 options memo。

注意：

- 它不是当前结论。
- 不作为 implementation source。

### 4.2 Early CopilotKit Decision Memo

`docs/ui-ux/copilotkit-workbench-plan.md`

用途：

- 早期 A/B/X/Y 方案讨论。

注意：

- 其中对 A2UI/AG-UI/CopilotKit 的角色划分已经被后续文档修正。
- 当前结论以 `rm-workbench-v0-technical-skeleton.md` 和 `rm-workbench-v0-agui-a2ui-alignment.md` 为准。

---

## 5. Multica Issue 拆分

### 5.0 当前状态

第一批 backend foundation issue 已完成并通过 Codex review：

- `MYM-24`: RM Workbench V0 Backend Adapter
- `MYM-25`: RM Workbench V0 Pending Interaction Backend
- `MYM-26`: RM Workbench V0 Frontend Smoke Workbench
- `MYM-27` / `1b30919c-e851-4c18-a513-f42f4980fdf5`: RM Workbench V0 Backend Mock Stream Integration

`MYM-27` 已完成并通过 Codex acceptance review。Codex 在验收中补了小修：mock stream loopback-only、中文 payload 回归测试、adapter surface data 补全、fixture 中文化，并完成浏览器 smoke。

### Issue 1: RM Workbench V0 Backend Adapter

状态：已完成。

目标：

```text
Move the spike adapter logic into production backend modules with tests.
```

范围：

- `api/rm_workbench/__init__.py`
- `api/rm_workbench/contracts.py`
- `api/rm_workbench/adapter.py`
- `api/rm_workbench/mock_data.py`
- `tests/test_rm_workbench_adapter.py`

验收：

```bash
python3 docs/ui-ux/rm-workbench-v0-spike/mock_adapter_check.py
pytest tests/test_rm_workbench_adapter.py -q
```

### Issue 2: RM Workbench V0 Pending Interaction Backend

状态：已完成。

目标：

```text
Add a structured pending interaction abstraction separate from clarify.
```

范围：

- `api/pending_interactions.py`
- `api/routes.py`
- `api/streaming.py`
- `tests/test_pending_interactions.py`
- `tests/test_rm_workbench_routes.py`

验收：

```bash
pytest tests/test_pending_interactions.py tests/test_rm_workbench_routes.py -q
pytest tests/test_clarify_unblock.py tests/test_approval_unblock.py tests/test_cancel_interrupt.py -q
```

### Issue 3: RM Workbench V0 Frontend Smoke Workbench

状态：已完成，并通过 Codex review。

目标：

```text
Create a minimal React workbench playground that renders the mock AG-UI/A2UI vertical slice and resolves product selection through the existing pending interaction backend.
```

范围建议：

- 新建 `frontend/` React/Vite host，或如果编排器认为现有 repo 约定更适合，先在 issue 里说明替代路径。
- 渲染 mock event transcript，不接真实 Hermes chat。
- 支持三个 surface：
  - `CustomerProfileCard`
  - `ProductFitTable`
  - `BriefExportPanel`
- `ProductFitTable` 允许选择 1-3 个产品。
- Confirm 后 POST 到 `/api/rm-workbench/pending/resolve`。

验收：

```bash
cd frontend
npm run build
```

人工验收：

```text
1. 本地能打开 React workbench 页面。
2. 页面能从 mock AG-UI/A2UI transcript 渲染客户卡片、产品表、brief 导出 panel。
3. ProductFitTable 可以选择 1-3 个产品。
4. Confirm 后能调用 /api/rm-workbench/pending/resolve。
5. 页面有清楚的 pending/resolved 状态反馈。
```

不做：

- 不接 CopilotKit runtime。
- 不接真实 RM Skill。
- 不接真实客户数据或真实产品池。
- 不做完整 Hermes chat replacement。
- 不做 Memory 自动写入。

### Issue 4: RM Workbench V0 Backend Mock Stream Integration

状态：`MYM-27` / `1b30919c-e851-4c18-a513-f42f4980fdf5` 已完成，并通过 Codex acceptance review。

目标：

```text
Expose a backend mock AG-UI/A2UI stream generated from api.rm_workbench.adapter, and update the smoke frontend to consume that stream instead of a static transcript.
```

为什么现在做它：

- MYM-24 已证明 backend adapter 可以生成 AG-UI/A2UI events。
- MYM-25 已证明 pending interaction backend 可以接 structured resolve。
- MYM-26 已证明 React smoke UI 可以渲染 surface 并提交选择。
- 下一步应该把“静态前端 fixture”替换成“后端 mock stream”，验证前后端协议链路真的打通。

范围建议：

- 后端新增 dev/test-only mock stream endpoint，例如：
  - `GET /api/rm-workbench/mock-stream`
  - 或者如果现有 SSE 约定更适合，使用类似 `/api/rm-workbench/mock/stream` 的路径。
- 后端 stream 数据必须由这些生产模块生成：
  - `api.rm_workbench.mock_data.load_pre_meeting_brief_fixture`
  - `api.rm_workbench.adapter.map_rm_skill_contract_to_agui_events`
- 前端改为从 mock stream 读取 AG-UI/A2UI events。
- 前端可以保留 static transcript 作为 dev fallback，但默认 smoke path 应走 backend mock stream。
- Pending interaction seed 应继续走 backend，不能假装 resolve 成功。

验收：

```bash
python3 docs/ui-ux/rm-workbench-v0-spike/mock_adapter_check.py
/Users/hywl/.hermes/hermes-agent/venv/bin/python -m pytest tests/test_rm_workbench_adapter.py tests/test_pending_interactions.py tests/test_rm_workbench_routes.py tests/test_rm_workbench_mock_stream.py -q
cd frontend
npm run build
```

人工验收：

```text
1. 启动 hermes-webui backend。
2. 启动 frontend dev server。
3. 前端从 backend mock stream 渲染 CustomerProfileCard、ProductFitTable、BriefExportPanel。
4. ProductFitTable 可以选择 1-3 个产品。
5. Confirm 后调用 /api/rm-workbench/pending/resolve，并显示成功状态。
```

不做：

- 不接真实 Hermes chat `/api/chat/stream`。
- 不接 CopilotKit runtime。
- 不接真实 RM Skill。
- 不接真实客户数据或真实产品池。
- 不做 Memory 自动写入。
- 不做完整 RM 工作台视觉设计。

---

## 6. MYM-27 Acceptance Record

Codex acceptance comment 结论：

- Approved after local review plus small follow-up fixes.
- `GET /api/rm-workbench/mock-stream` 已改成 loopback-only，符合 dev/test-only 边界。
- Backend stream payload 已覆盖中文 demo 数据和三类 semantic surfaces。
- Frontend 默认使用 backend mock stream，fallback 会显示中文警告和数据来源。
- Browser smoke 已确认 footer 显示 `数据来源：后端模拟流`，并完成选择 `稳健收益组合 A` -> `确认选择` -> `选择已确认`。

验收命令：

```bash
python3 docs/ui-ux/rm-workbench-v0-spike/mock_adapter_check.py
/Users/hywl/.hermes/hermes-agent/venv/bin/python -m pytest tests/test_rm_workbench_adapter.py tests/test_pending_interactions.py tests/test_rm_workbench_routes.py tests/test_rm_workbench_mock_stream.py -q
cd frontend
npm run build
```

验收结果：

```text
mock_adapter_check.py -> passed with expected four OK lines
pytest adapter/pending/routes/mock_stream -> 27 passed in 1.81s
npm run build -> passed, vite built in 303ms
browser smoke -> passed
```

本地人工验收命令：

```bash
HERMES_WEBUI_PORT=<port> /Users/hywl/.hermes/hermes-agent/venv/bin/python server.py
RM_WORKBENCH_BACKEND=http://127.0.0.1:<port> npm run dev -- --host 127.0.0.1
```

残余风险：

- Mock stream 仍是同步发送全部 SSE events；V0 smoke integration 可接受，未来真实 Hermes integration 需要渐进式异步 stream。

---

## 7. 下一步建议：真实 Hermes Chat / RM Skill 接入前的边界评估

MYM-27 之后，技术链路已经从 backend adapter 到 frontend renderer 打通。下一步不要立刻扩成完整 RM 工作台，建议先做一张 planning/evaluation issue：

```text
RM Workbench V0 Real Hermes Stream Boundary Evaluation
```

目标：

- 明确真实 Hermes `/api/chat/stream` 如何承载 AG-UI standard events 与 `CUSTOM a2ui.surface.messages`。
- 明确 RM Skill structured output 在 Hermes Agent runtime 内的生成位置。
- 明确 pending interaction resolve 如何回到 Hermes run，而不是只停在 hermes-webui backend。
- 明确是否需要 CopilotKit frontend utilities；不做 runtime takeover。
- 明确 Memory proposal 的只读/待确认边界，暂不做自动写入。

---

## 8. 不要在 Backend Mock Stream Issue 做的事

Backend mock stream issue 不做：

- CopilotKit runtime 接入。
- 真实 RM Skill。
- 真实客户数据。
- 真实产品池。
- Memory 自动写入。
- Hermes Agent runtime 深层改造。
- 完整 Hermes chat replacement。
- 完整 RM 工作台视觉设计。

原因：

- 当前要先验证 frontend smoke UI 能消费 backend adapter 生成的 event stream。
- 真正的 Hermes chat 接入和 CopilotKit 评估应在 backend mock stream 被验证后再进入下一批 issue。

---

## 9. 推荐给下一张规划 Issue 的开场指令

可以把下面这段丢给新窗口：

```text
请在 /Users/hywl/hermes-webui 中工作。先阅读 docs/ui-ux/rm-workbench-v0-index.md。

MYM-24、MYM-25、MYM-26、MYM-27 已完成并通过 Codex review。现在请创建一张 planning/evaluation issue：

RM Workbench V0 Real Hermes Stream Boundary Evaluation

请不要直接实现真实 RM Skill 或 CopilotKit runtime。目标是把 MYM-27 的 backend mock stream 推向真实 Hermes chat/stream 前，先明确事件承载、Skill structured output 生成位置、pending interaction resolve 回流路径、Memory proposal 边界和 CopilotKit 可用边界。请产出具体实现计划、文件边界、风险和验收标准。
```
