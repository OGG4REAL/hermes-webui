# RM Workbench V0: Documentation Index

路径：`docs/ui-ux/rm-workbench-v0-index.md`
状态：`active / start here`
更新时间：`2026-05-06`
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

## 1. 新窗口 / Multica Worker 只需要先读这些

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

### 1.4 下一步真实 Stream 边界评估

`docs/ui-ux/rm-workbench-v0-real-hermes-stream-boundary.md`

用途：

- 作为 `MYM-27` 之后的下一张 planning/evaluation issue 输入。
- 明确真实 Hermes `/api/chat/stream`、RM Skill.md 与 `rm_workbench_emit_contract` 分工、pending interaction resume、Memory proposal、CopilotKit 边界。
- 防止下一步直接漂到完整 RM Skill 或完整工作台 UI 大实现。

### 1.5 Roadmap

`docs/ui-ux/rm-workbench-v0-roadmap.md`

用途：

- 看当前阶段做到哪。
- 看 Issue 7 以后该怎么拆。
- 区分“技术闭环”与“业务扩展”。

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

已完成并通过验收：

- `MYM-24`: RM Workbench V0 Backend Adapter
- `MYM-25`: RM Workbench V0 Pending Interaction Backend
- `MYM-26`: RM Workbench V0 Frontend Smoke Workbench
- `MYM-27` / `1b30919c-e851-4c18-a513-f42f4980fdf5`: RM Workbench V0 Backend Mock Stream Integration
- `MYM-28` / `a6638362-ccff-485d-809d-e8e245bdf1ee`: RM Workbench V0 Real Hermes Stream Boundary Evaluation
- `MYM-29` / `d88a0be8-d46f-4011-89ef-b5b395704756`: RM Workbench V0 Real Stream Bridge
- `MYM-31` / `d14c857d-c505-46f2-882d-d1638a788868`: Hermes Agent rm_workbench_emit_contract Tool Registration

验收依据：

- `MYM-30` / `a60250cc-3e47-44f6-9cff-3db2a7398213`: Review RM Workbench V0 Real Stream Bridge
- `MYM-32` / `f5c7e4e7-1bc7-40ba-8aef-8afc2fcb9e34`: Review Hermes Agent rm_workbench_emit_contract Tool Registration

当前下一步：

- **Issue 7.5: Runtime Alignment + Real Stream Readiness**

补充说明：

- `MYM-28` 已产出评估文档，完成标准满足，可视为 pass。
- `MYM-29` 已完成，`MYM-30` 最终 review comment 结论为无阻断性 findings。
- `MYM-31` 已完成，`MYM-32` 最终 review comment 结论为无阻断性 findings，但该验收没有覆盖真实 WebUI runtime smoke。
- 双目录复盘显示 runtime 实际加载 `~/.hermes/hermes-agent`，而 MYM-31 改动落在 `~/hermes-agent`；因此下一步必须先做 runtime alignment 和真实 WebUI smoke。

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

### Issue 5: RM Workbench V0 Real Hermes Stream Boundary Evaluation

状态：`MYM-28` / `a6638362-ccff-485d-809d-e8e245bdf1ee` 已完成，可通过。

目标：

```text
Decide how the MYM-27 backend mock stream should evolve into a real Hermes /api/chat/stream integration before writing implementation code.
```

为什么现在做它：

- MYM-27 只证明了 backend mock stream，不证明真实 Hermes run 能产出、等待、恢复这些事件。
- pending interaction 当前已经能 resolve structured payload，但还没有定义真实 Hermes run 如何等待并拿回 payload。
- Memory proposal 必须先确认 proposal-first 边界，避免工程 worker 顺手做自动写入。
- CopilotKit 仍然不能作为 runtime takeover 进入主链路。

范围建议：

- 只读 `hermes-webui` 和 `/Users/hywl/hermes-agent` 相关代码。
- 产出 `docs/ui-ux/rm-workbench-v0-real-hermes-stream-evaluation-result.md`。
- 推荐或否决以下真实 stream 架构：
  - 保留现有 `/api/chat/stream` SSE event names，并新增/复用 `rm_workbench` event 承载 AG-UI payload。
  - 把 `/api/chat/stream` 整体改成 AG-UI top-level events。
  - 新增独立真实 `/api/rm-workbench/stream`。
- 明确 RM Skill.md 与专用 `rm_workbench_emit_contract` 工具的分工。
- 明确 pending interaction resume semantics。
- 明确 Memory proposal 只展示、不自动写入。
- 明确 CopilotKit 当前是 reference-only、defer，还是有可局部复用的 frontend utility。

验收：

```text
1. Evaluation result doc exists.
2. It chooses one stream architecture and rejects alternatives with concrete reasons.
3. It lists exact files for the next implementation issue.
4. It defines minimal RM Skill contract shape, including memory_proposals.
5. It defines pending interaction resolve by interaction_id / timeout / cancel semantics.
6. It lists tests for the next implementation issue.
7. It explicitly keeps real RM Skill, real data, Memory writes, and CopilotKit runtime out of this issue.
```

不做：

- 不实现真实 RM Skill。
- 不修改 Hermes Agent runtime。
- 不接真实客户数据或产品池。
- 不做 Memory 自动写入。
- 不接 CopilotKit runtime。
- 不重写完整 Hermes chat stream。

---

### Issue 6: RM Workbench V0 Real Stream Bridge

状态：`MYM-29` / `d88a0be8-d46f-4011-89ef-b5b395704756` 已完成，`MYM-30` review 已通过。

目标：

```text
Bridge the existing /api/chat/stream SSE channel with rm_workbench AG-UI payloads, without changing the top-level Hermes stream protocol.
```

关键结论：

- 只识别 `tool_name == "rm_workbench_emit_contract"`。
- `rm_workbench` SSE event 承载 `kind: "agui_events"`。
- 前端只消费 `event: rm_workbench`，不消费 tool result，不解析 assistant text。
- `memory_proposals` 只展示，不写入。

剩余 follow-up：

- Hermes Agent 侧尚未真实注册 `rm_workbench_emit_contract` 工具。

### Issue 7: Hermes Agent `rm_workbench_emit_contract` Tool Registration

状态：`MYM-31` / `d14c857d-c505-46f2-882d-d1638a788868` 已完成，`MYM-32` review 已通过。

目标：

```text
Expose rm_workbench_emit_contract to real Hermes Agent runs so the Issue 6 stream bridge can be exercised end-to-end.
```

结果：

- Hermes Agent 现在能真实注册并暴露 `rm_workbench_emit_contract`
- WebUI real chat runs 会在支持时自动补上 `rm_workbench` toolset
- `MYM-29` bridge 继续只识别该专用 tool name，不扫描任意 tool result

### Issue 8: First Real RM Workflow

状态：Issue 7.5 之后的下一步，尚未创建。

目标：

```text
Implement one real RM workflow path driven by RM Skill.md + rm_workbench_emit_contract, using the already-finished bridge instead of adding more protocol infrastructure.
```

建议只做：

- `pre_meeting_brief`

建议先读：

- `docs/ui-ux/rm-workbench-v0-roadmap.md`
- `docs/ui-ux/rm-workbench-v0-real-hermes-stream-evaluation-result.md`

### Issue 7.5: Runtime Alignment + Real Stream Readiness

状态：下一步主线，尚未创建。

目标：

```text
Align Hermes Agent runtime path with the development repo, then prove WebUI real chat can trigger the rm_workbench path before adding the first real RM workflow.
```

必须包含：

- 修正 `~/.hermes/hermes-agent` 与 `~/hermes-agent` 双目录导致的 runtime 路径不一致。
- 验证 runtime venv 能 import `tools.rm_workbench_tool`，且 `validate_toolset("rm_workbench") == True`。
- 重启 WebUI 后，通过真实 chat 触发或观察到 `rm_workbench_emit_contract` 可见。
- 至少保存一份截图、SSE log、browser console log 或 server log 作为 issue comment 验收证据。
- 修掉真实 stream 立刻会撞的 readiness 问题：bridge 错误可见、cancel 后不继续投递、surface upsert、基础 A2UI message 顺序处理、`interaction_id` required。

不做：

- 不实现完整 RM workflow。
- 不接真实客户数据。
- 不引入 CopilotKit runtime。

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

## 7. MYM-28 / MYM-29 Acceptance Notes

### 7.1 MYM-28

- `MYM-28` 已产出 `docs/ui-ux/rm-workbench-v0-real-hermes-stream-evaluation-result.md`
- 文档已明确推荐架构、拒绝方案、contract shape、pending interaction resume、memory proposal 边界、CopilotKit 定位、下一张 implementation issue 文件范围与测试清单。
- 后续本地文档还补充修正了一个关键口径：不是 RM Skill 返回 JSON，而是 `RM Skill.md + rm_workbench_emit_contract` 分工。

### 7.2 MYM-29 / MYM-30

- `MYM-29` 实现已完成。
- `MYM-30` 最终 review comment 结论为无阻断性 findings。
- 剩余风险不属于返工项，而是 follow-up issue：Hermes Agent 侧真实注册 `rm_workbench_emit_contract`。

---

## 8. 下一步建议

主线顺序：

```text
Issue 7.5 -> runtime alignment + real WebUI smoke + readiness fixes
Issue 8 -> first real RM workflow
Issue 9 -> memory proposal review path
Issue 10+ -> productization / real data / multi-workflow
```

完整阶段划分见：

- `docs/ui-ux/rm-workbench-v0-roadmap.md`

---

## 9. 当前不要提前做的事

- CopilotKit runtime takeover
- 完整 RM 工作台视觉重做
- 多 workflow 并行扩展
- 真实客户数据 / 真实产品池接入
- 自动 Memory 写入
- 为了 UI 去改 Hermes 整体 runtime loop

---

## 10. Runtime / Streaming Issue 验收门槛

凡是改动 Hermes Agent runtime / tools / toolsets、Hermes WebUI streaming bridge、`/api/chat/stream`、SSE event、或前端真实 stream 消费路径的 issue，不能只靠 unit test、mock-stream 或代码 review 关闭。

必须在 issue comment 中记录一次真实 WebUI smoke：

```text
从 WebUI 真实 chat 触发
  -> 观察到预期 tool call 或 SSE event
  -> 观察到预期 UI 渲染或明确错误 surface
```

验收证据至少包含一种：

- 截图
- SSE log
- browser console log
- server log 中的 tool call / `event: rm_workbench`

涉及 Hermes Agent 的 issue 还必须先确认 runtime 路径：

```text
which hermes
runtime venv import tools/toolsets 的实际路径
HERMES_WEBUI_AGENT_DIR / discover_agent_dir 命中的实际路径
WebUI 真实 chat 中模型可见的工具列表
```

---

## 11. 推荐给下一张规划 / 实现 Issue 的开场指令

可以把下面这段丢给新窗口：

```text
请在 /Users/hywl/hermes-webui 中工作。先阅读：

- docs/ui-ux/rm-workbench-v0-index.md
- docs/ui-ux/rm-workbench-v0-roadmap.md
- docs/ui-ux/rm-workbench-v0-real-hermes-stream-evaluation-result.md
- docs/ui-ux/Hermes双目录问题.md
- docs/ui-ux/rm-workbench-v0-code-review-2026-05-07.md

MYM-24 到 MYM-31 的代码形状基本完成，但复盘发现真实 runtime 仍加载 ~/.hermes/hermes-agent，而 MYM-31 改动在 ~/hermes-agent。现在不要直接做第一条 RM workflow，先做 runtime alignment + real WebUI smoke + high-risk readiness fixes。

请围绕下一个 issue：

RM Workbench V0 Runtime Alignment + Real Stream Readiness

请先解决 Hermes Agent 双目录问题，确保 WebUI/gateway runtime 实际加载 ~/hermes-agent，并通过 WebUI 真实 chat 观察到 rm_workbench_emit_contract 可见或 rm_workbench SSE 事件出现。验收必须包含截图、SSE log、browser console log 或 server log。然后修掉真实 stream readiness 的高风险问题：bridge 错误可见、cancel 后不继续投递、surface upsert、基础 A2UI message 顺序处理、interaction_id required。请不要实现完整 RM workflow，不要接真实客户数据，不要引入 CopilotKit runtime，不要改 /api/chat/stream top-level protocol。
```
