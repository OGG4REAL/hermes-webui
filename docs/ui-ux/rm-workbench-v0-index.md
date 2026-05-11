# Structured UI Subsystem: Documentation Index

> 历史名 "RM Workbench V0"。子系统已于 2026-05-09 重新定位为 Hermes WebUI 的
> 结构化 UI 原子能力（Generative UI），RM Workbench 是它的第一个 consumer，不是
> 它的所有者。详见 ADR-009 ~ ADR-013。文件名沿用历史名，进 deprecation 队列。

路径：`docs/ui-ux/rm-workbench-v0-index.md`
状态：`active / start here (realigned 2026-05-09)`
更新时间：`2026-05-09`
目的：作为本子系统的唯一入口，避免后续工程 agent 被早期讨论文档绕进去。

---

## 0. 文档体系结论

本子系统的文档以后按三层维护：

```text
Core docs
  -> Architecture
  -> ADR
  -> Roadmap
  -> Coding Boundary

Working docs
  -> issue-specific specs / foundation notes / review notes

Reference docs
  -> spike / protocol examples / historical options
```

后续新 issue 默认先读 core docs。涉及代码改动的 issue 必须读 Coding Boundary。只有 issue 明确需要时，才读对应 working/reference docs。

**Layer 0 / Layer 1 锚点（2026-05-09 校准）**：

```text
Layer 0 — Generative UI 原子能力（工作台底座）
  primitive catalog: MetricCard / DataTable / LineChart / BarChart / PieChart / ChoiceList
  contract envelope: emit_ui tool（最小信封，kind 不做路由门禁）
  interaction protocol: pending_interaction.resolve（结构化输入回传通道）

Layer 1 — Business consumer（应以 Skill 形式存在，不以代码形式存在）
  RM 是第一个 consumer；CFA / 投资 / 日常 AI 生成 UI 平级
  business 端的 schema 严格性、字段约定、组合范式归 Skill 负责，不下沉到 Layer 0
```

任何 issue 在动手前先回答："我现在改的是 Layer 0 还是 Layer 1？" 改 Layer 0 的影响面是
所有 consumer，要慎重；改 Layer 1 应优先考虑能不能用 Skill 表达，而不是写新代码。

当前一句话架构：

```text
Hermes Agent runtime
  -> hermes-webui backend
  -> event: rm_workbench  (命名包袱，机制是 Layer 0 通用通道)
  -> AG-UI CUSTOM carries A2UI messages
  -> React structured-UI host
  -> pending interaction resolve returns structured input
```

---

## 1. Core Docs

### 1.1 Architecture

`docs/ui-ux/rm-workbench-v0-architecture.md`

用途：

- 当前系统组成。
- runtime / backend / stream / React host / pending interaction 的职责边界。
- 已成立与未成立的架构事实。
- 后续 issue 不应该违反的 architecture rules。

### 1.2 ADR

`docs/ui-ux/rm-workbench-v0-adr.md`

用途：

- 已接受的技术决策。
- 被明确拒绝的方向。
- 每个决策的背景和影响。
- 新决策应该追加为 ADR，而不是散落在 issue comment 或临时文档里。

### 1.3 Roadmap

`docs/ui-ux/rm-workbench-v0-roadmap.md`

用途：

- 当前做到哪里。
- 下一步先做哪条技术链。
- Issue 7.6 / 7.7 / 8 的顺序。
- 当前不要提前做什么。

### 1.4 Coding Boundary

`docs/ui-ux/rm-workbench-v0-coding-boundary.md`

用途：

- 约束后续 RM Workbench coding issue 的代码改动边界。
- 说明 hermes-agent / hermes-webui backend / React structured-UI host 的目录归属。
- 说明 streaming、contract、frontend layering、测试和 manual smoke 要求。
- 作为 worker 开工前和 reviewer 验收时的代码边界依据。

---

## 2. Working Docs

这些文档围绕 core docs 展开。它们可以指导某个 issue，但不能覆盖 Architecture / ADR / Roadmap。

### 2.1 Generic UI Catalog

`docs/ui-ux/rm-workbench-v0-generic-ui-catalog-plan.md`

用途：

- Issue 7.6 输入。
- 说明 generic UI primitives 与 RM semantic surfaces 的分层。
- 说明为什么继续复用 `rm_workbench_emit_contract`，而不是新增 `render_table` / `render_chart` tools。

### 2.2 Issue 7 Foundation Status

`docs/ui-ux/rm-workbench-v0-issue7-foundation-status.md`

用途：

- Issue 7 阶段复盘。
- 说明 React renderer 在 `frontend/` / mock path 已成立，不等于主 WebUI chat 前端已完成正式接管。
- 说明为什么 Issue 7.7 必须先于 First Real RM Workflow。

### 2.3 Real Stream Evaluation

`docs/ui-ux/rm-workbench-v0-real-hermes-stream-evaluation-result.md`

用途：

- 真实 Hermes stream bridge 的评估结果。
- 解释 RM Skill.md 与 `rm_workbench_emit_contract` 的分工。
- 保留 pending interaction、memory proposal、CopilotKit 边界的过程依据。

### 2.4 Code Review / Runtime Notes

- `docs/ui-ux/rm-workbench-v0-code-review-2026-05-07.md`
- `docs/ui-ux/Hermes双目录问题.md`

用途：

- 保存重要 review 和 runtime 排障证据。
- 只有当 issue 涉及同类风险时才需要阅读。

---

## 3. Reference Docs

这些文档保留为参考，不再作为新 issue 的默认入口。

### 3.1 Protocol Alignment

`docs/ui-ux/rm-workbench-v0-agui-a2ui-alignment.md`

用途：

- AG-UI / A2UI 对齐细节。
- 作为 ADR-004 的来源材料。

### 3.2 Technical Skeleton

`docs/ui-ux/rm-workbench-v0-technical-skeleton.md`

用途：

- 早期技术选型骨架。
- 当前结论已经被 Architecture / ADR 吸收。

### 3.3 Implementation Plan

`docs/ui-ux/rm-workbench-v0-implementation-plan.md`

用途：

- 早期 V0 实现计划。
- 后续只作为历史任务拆分参考，不作为当前唯一执行计划。

### 3.4 Protocol Examples

`docs/ui-ux/rm-workbench-v0-protocol-examples.md`

用途：

- JSON 样例参考。
- 若与 Architecture / ADR 冲突，以 Core Docs 为准。

### 3.5 Spike Reference

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

### 3.6 Adapter Spike Plan

`docs/ui-ux/rm-workbench-v0-adapter-spike-plan.md`

用途：

- 保留技术验证过程和决策门。
- 解释为什么先做 mock harness，再进早期 implementation plan。

注意：

- 当前工程事实以 Core Docs 为准。

### 3.7 React Migration Plan

`docs/ui-ux/hermes-react-migration-plan.md`

用途：

- React workbench host 的背景参考。
- 解释为什么 React host 应该以 hermes-webui 后端为事实源。

注意：

- 这是 React host 背景材料，不是当前 sequencing source。当前顺序以 Roadmap 为准。

---

## 4. Historical / Superseded Docs

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
- 当前结论以 Core Docs 为准。

---

## 5. Documentation Maintenance Rules

### 5.1 什么时候改 Architecture

当系统当前事实发生变化时，改：

`docs/ui-ux/rm-workbench-v0-architecture.md`

例子：

- 主 WebUI path 已经有正式 React structured-UI host。
- `rm_workbench_emit_contract` 被泛化为 `emit_ui_contract`。
- pending interaction resume 机制发生变化。

### 5.2 什么时候改 ADR

当做出新的技术取舍，或推翻旧取舍时，改：

`docs/ui-ux/rm-workbench-v0-adr.md`

例子：

- 是否引入 CopilotKit runtime。
- 是否新增 generic emit tool。
- 是否改变 `/api/chat/stream` top-level protocol。

### 5.3 什么时候改 Roadmap

当 issue 顺序、阶段边界、完成标准变化时，改：

`docs/ui-ux/rm-workbench-v0-roadmap.md`

例子：

- Issue 7.7 插入 Issue 8 前。
- 某个阶段完成并进入下一阶段。
- 某个 issue 被拆分或取消。

### 5.4 什么时候新增 Working Doc

只有当一个 issue 需要独立上下文时，才新增 working doc。

新增后必须：

- 在本 index 的 Working Docs 里登记。
- 写清楚它依附哪个 core doc。
- 写清楚它是否会在 issue 完成后被吸收到 Architecture / ADR / Roadmap。

### 5.5 Git 管理

文档变更和代码变更尽量分开提交。

建议 commit 粒度：

```text
docs: update RM workbench architecture docs
docs: record RM workbench ADR
feat: implement RM workbench frontend host
test: add RM workbench stream smoke coverage
```

不要把代码实现、fixture 数据、文档重排混在同一个 commit，除非它们必须一起才能保持仓库可验证。

---

## 6. Multica Issue 拆分

### 6.0 当前状态

已完成并通过验收：

- `MYM-24`: RM Workbench V0 Backend Adapter
- `MYM-25`: RM Workbench V0 Pending Interaction Backend
- `MYM-26`: RM Workbench V0 Frontend Smoke Workbench
- `MYM-27` / `1b30919c-e851-4c18-a513-f42f4980fdf5`: RM Workbench V0 Backend Mock Stream Integration
- `MYM-28` / `a6638362-ccff-485d-809d-e8e245bdf1ee`: RM Workbench V0 Real Hermes Stream Boundary Evaluation
- `MYM-29` / `d88a0be8-d46f-4011-89ef-b5b395704756`: RM Workbench V0 Real Stream Bridge
- `MYM-31` / `d14c857d-c505-46f2-882d-d1638a788868`: Hermes Agent rm_workbench_emit_contract Tool Registration
- `MYM-34` / `a46a35ec-9135-48ff-acef-85099508a182`: RM Workbench V0 Runtime Alignment + Real Stream Readiness

验收依据：

- `MYM-30` / `a60250cc-3e47-44f6-9cff-3db2a7398213`: Review RM Workbench V0 Real Stream Bridge
- `MYM-32` / `f5c7e4e7-1bc7-40ba-8aef-8afc2fcb9e34`: Review Hermes Agent rm_workbench_emit_contract Tool Registration
- `MYM-34` final review comment: runtime alignment 与 real WebUI smoke 已通过，可进入下一阶段

当前下一步：

- **Issue 7.6: Generic A2UI Renderer Catalog（已接受，closeout 已归档）**
- **Issue 7.7: React Frontend Foundation for real WebUI path（下一步主线）**

补充说明：

- `MYM-28` 已产出评估文档，完成标准满足，可视为 pass。
- `MYM-29` 已完成，`MYM-30` 最终 review comment 结论为无阻断性 findings。
- `MYM-31` 已完成，`MYM-32` 最终 review comment 结论为无阻断性 findings，但该验收没有覆盖真实 WebUI runtime smoke。
- `MYM-34` 已补齐双目录 runtime alignment、真实 WebUI smoke、bridge 错误可见、`interaction_id` required、surface upsert 等 readiness 问题。
- `MYM-35` 已证明同一条 `rm_workbench_emit_contract` 链路能承载 generic UI blocks，且 React generic renderer 能真实渲染常规图表/表格/选择控件。
- `MYM-36` 已证明当前不是本地 schema stripping bug，而是模型/provider 对 opaque nested object 参数不稳定；该 issue 还顺手暴露了主 WebUI path 与 React RM host 之间仍有宿主层缺口。
- 因此进入 Issue 8 前，除了 Issue 7.6 的 generic catalog 收口，还应补一层 React frontend foundation，把 RM structured UI 的正式宿主问题单独解决。

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

状态：Issue 7.7 之后，尚未创建；只有当真实 WebUI chat 已能直接显示 Hermes 渲染的图表 / 表格 / 选择 UI 时才可开始。

目标：

```text
Implement one real RM workflow path driven by RM Skill.md + rm_workbench_emit_contract, using the already-finished bridge instead of adding more protocol infrastructure.
```

建议只做：

- `pre_meeting_brief`

建议先读：

- `docs/ui-ux/rm-workbench-v0-roadmap.md`
- `docs/ui-ux/rm-workbench-v0-generic-ui-catalog-plan.md`
- `docs/ui-ux/rm-workbench-v0-real-hermes-stream-evaluation-result.md`
- `docs/ui-ux/Hermes双目录问题.md`
- `docs/ui-ux/rm-workbench-v0-code-review-2026-05-07.md`

### Issue 7.6: Generic A2UI Renderer Catalog

状态：已完成实现并通过验收；closeout 结论是 generic renderer/catalog 能力成立于 React workbench host / mock path。

目标：

```text
Prove that Hermes can emit generic structured UI blocks through the existing UI contract path, and React can render table/chart/choice primitives before the first RM-specific workflow.
```

为什么现在做它：

- 当前前端已有 React/Vite smoke host，但只支持 `CustomerProfileCard`、`ProductFitTable`、`BriefExportPanel`。
- `PerformanceChart` 已在后端 surface allowlist 和文档中出现，但前端还没有 chart renderer，也没有 chart library。
- V0 需要先证明常规 AI-native UI 能生成，而不是只证明 RM 专属组件能渲染。

范围：

- 继续复用 `rm_workbench_emit_contract`。
- 拓展 contract，允许 `ui.blocks` 承载 generic UI blocks。
- 后端 adapter 将 generic blocks 映射成 `CUSTOM name = a2ui.surface.messages`。
- 前端新增 generic primitives：
  - `MetricCard`
  - `DataTable`
  - `LineChart`
  - `BarChart`
  - `PieChart`
  - `ChoiceList`
- 保持现有 RM semantic surfaces 可用。

验收：

```bash
cd /Users/hywl/hermes-webui
/Users/hywl/.hermes/hermes-agent/venv/bin/python -m pytest tests/test_rm_workbench_adapter.py tests/test_rm_workbench_mock_stream.py -q

cd /Users/hywl/hermes-webui/frontend
npm run build
```

人工验收：

```text
1. React workbench 能从 backend mock stream 或 fallback transcript 渲染 MetricCard。
2. React workbench 能渲染 DataTable。
3. React workbench 能渲染 LineChart 或 BarChart。
4. React workbench 能渲染 PieChart。
5. React workbench 能渲染 ChoiceList。
6. ProductFitTable 仍能选择并 resolve pending interaction。
7. issue comment 中保留截图或 SSE log。
```

不做：

- 不实现第一条真实 `pre_meeting_brief` workflow。
- 不要求真实 business prompt 稳定触发 tool call。
- 不新增 `render_table` / `render_chart` / `render_form` Hermes tools。
- 不执行任意 JSX / HTML / remote JS。
- 不接真实客户数据。
- 不引入 CopilotKit runtime。

### Issue 7.5: Runtime Alignment + Real Stream Readiness

状态：已完成，`MYM-34` / `a46a35ec-9135-48ff-acef-85099508a182`。

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

验收记录：

- runtime venv 已通过 editable install 对齐到 `/Users/hywl/hermes-agent`。
- WebUI 启动日志显示 `tools` / `toolsets` / `rm_workbench` 来自预期 agent 目录。
- `/tmp/hermes-smoke-final-evidence.log` 保存了启动日志、mock SSE、`interaction_id` enforcement、真实 chat session 与 runtime import 证据。
- final review comment 结论为 pass。
- 本阶段未要求真实业务 prompt 触发 tool call；该风险进入 Issue 8。

---

## 7. MYM-27 Acceptance Record

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

## 8. MYM-28 / MYM-29 Acceptance Notes

### 8.1 MYM-28

- `MYM-28` 已产出 `docs/ui-ux/rm-workbench-v0-real-hermes-stream-evaluation-result.md`
- 文档已明确推荐架构、拒绝方案、contract shape、pending interaction resume、memory proposal 边界、CopilotKit 定位、下一张 implementation issue 文件范围与测试清单。
- 后续本地文档还补充修正了一个关键口径：不是 RM Skill 返回 JSON，而是 `RM Skill.md + rm_workbench_emit_contract` 分工。

### 8.2 MYM-29 / MYM-30

- `MYM-29` 实现已完成。
- `MYM-30` 最终 review comment 结论为无阻断性 findings。
- 剩余风险不属于返工项，而是 follow-up issue：Hermes Agent 侧真实注册 `rm_workbench_emit_contract`。

---

## 9. 下一步建议

主线顺序（2026-05-09 重排）：

```text
Issue 7.5  -> done: runtime alignment + real WebUI smoke + readiness fixes
Issue 7.6  -> done: generic A2UI renderer catalog
Issue 7.7  -> in progress: React frontend foundation + Layer 0 校准
              （ADR-007 修订验收：从主 chat 触发任意可达 contract，
                能在主路径渲染至少 1 个 generic primitive 即满足）
Issue 8    -> first real RM workflow（在 7.7 收口、Layer 0 ready 后启动；
              RM 通过 Skill 教模型用 Layer 0 primitive 表达业务，
              不要再加新 React surface 组件，见 ADR-013）
Issue 9    -> Skill-driven Layer 1 migration（独立轨道，可与 Issue 8 并行准备）：
              - ChoiceList 等 primitive 加 on_confirm interaction wiring
              - 写出 RM Skill 资产，验证 RM workflow 能完全用 Layer 0 primitive 表达
              - 删除 frontend/src/rm/surfaces/ 与对应后端 RM 分支
              - 删除 contract.surfaces 字段和 map_surface_to_a2ui_messages 路径
Issue 10   -> 命名整改 issue：rm_workbench 系命名（目录 / SSE event / DOM / CSS）
              一次性去 RM 化，落实 ADR-012 deprecation 队列
Issue 11+  -> productization / 真实数据 / 多 consumer 扩展
```

完整阶段划分见：

- `docs/ui-ux/rm-workbench-v0-roadmap.md`

---

## 10. 当前不要提前做的事

- CopilotKit runtime takeover
- 完整 RM 工作台视觉重做
- 多 workflow 并行扩展
- 真实客户数据 / 真实产品池接入
- 自动 Memory 写入
- 为了 UI 去改 Hermes 整体 runtime loop
- 让模型生成任意 React code / JSX / HTML
- 为每种 UI primitive 新增一个 Hermes tool
- 为新业务 consumer（CFA / 投资 / 日常 UI）新建 `frontend/src/<domain>/surfaces/` 目录或后端分支
  （这是 ADR-013 明确禁止的 Layer 1 硬编码错误；新 consumer 应该是 Skill 资产，不是代码）
- 在 Layer 0 validator 里加 per-type 字段强校验（series.key 必须出现在 data row 等）
  （这是 ADR-010 明确禁止的；缺字段由 primitive 在前端兜底）
- 在 Layer 0 validator 里加 kind 白名单或路由门禁（违反 ADR-011）
- 把任何新 RM 化命名引入到模型可见的 surface（tool 名 / schema 描述 / prompt 引用）

---

## 11. Runtime / Streaming Issue 验收门槛

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

## 12. 推荐给下一张规划 / 实现 Issue 的开场指令

> 2026-05-09 重写。原版本绑死了 `rm_workbench_emit_contract` 命名和 RM 化预设，
> 是 MYM-38 反复推不动的诱因之一。新版本以 Layer 0 / Layer 1 分层为核心约束。

可以把下面这段丢给新窗口：

```text
请在 /Users/hywl/hermes-webui 中工作。先阅读 core docs：

- docs/ui-ux/rm-workbench-v0-index.md       （入口 + Layer 0/Layer 1 锚点）
- docs/ui-ux/rm-workbench-v0-adr.md         （决策主文件，特别是 ADR-009 ~ ADR-013）
- docs/ui-ux/rm-workbench-v0-architecture.md
- docs/ui-ux/rm-workbench-v0-roadmap.md
- docs/ui-ux/rm-workbench-v0-coding-boundary.md

只在 issue 明确需要时再读：
- rm-workbench-v0-issue7-foundation-status.md
- rm-workbench-v0-generic-ui-catalog-plan.md
- rm-workbench-v0-real-hermes-stream-evaluation-result.md

子系统定位（不要重新讨论）：
- "AI 在对话中生成结构化 UI" 是 Hermes WebUI 工作台的 Layer 0 原子能力。
- RM Workbench 是这个能力的第一个 Layer 1 consumer，不是它的所有者。
- Layer 0 包含：primitive catalog、emit_ui contract envelope、pending_interaction.resolve 通道。
- Layer 1（RM 等业务）应以 Skill 资产形式存在，Skill 教模型用 Layer 0 primitive
  组合出业务语义，不应该硬编码新的 React surface 或新的后端分支（见 ADR-013）。

硬约束（违反即不通过）:
- 模型可见的结构化 UI emit tool 命名为 emit_ui（ADR-012），不要使用旧名
  rm_workbench_emit_contract，也不要保留兼容别名。
- Layer 0 validator 只校验最小可识别性（id/type/props 存在、type 在 catalog 内）；
  per-type 字段缺失应在 primitive 内兜底，不抛 ValueError（ADR-010）。
- Layer 0 contract 的 kind / version / run_id / thread_id / skill 全部可选，
  缺省由后端补；kind 不再做路由门禁（ADR-011）。
- 不要为新业务 consumer 新建 frontend/src/<domain>/surfaces/ 或后端 RM 化分支。
- 不要引入 CopilotKit runtime takeover；不要改 /api/chat/stream top-level 协议；
  不要为每种 primitive 新增独立 tool；不要让 memory 自动写入。

issue 验收要求:
- L1 修复（仅文档 / 仅测试）：跑相关 pytest 和 frontend npm run build。
- L2/L3 修改了 runtime / tool / streaming / frontend host：必须包含一次真实
  WebUI manual smoke，证据贴在 issue comment（截图 / SSE log / browser console
  log / server log 任一）。

请围绕下一个 issue 给出 plan / implementation。如果你发现现有 ADR 与 issue 要做
的事冲突，先停下并提议修订 ADR，而不是绕开它。
```
