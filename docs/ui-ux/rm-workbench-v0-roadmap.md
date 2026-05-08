# RM Workbench V0 Roadmap

路径：`docs/ui-ux/rm-workbench-v0-roadmap.md`
状态：`active / sequencing`
更新时间：`2026-05-08`
入口：`docs/ui-ux/rm-workbench-v0-index.md`

---

## 0. Roadmap 目标

这份 roadmap 只回答三件事：

1. V0 现在已经做到哪一步。
2. 接下来应该先补哪条技术链。
3. 哪些事情现在不要提前做。

---

## 1. 当前已完成的阶段

### Phase 0: 技术骨架 + mock 到 real bridge

已完成：

- `MYM-24` Backend Adapter
- `MYM-25` Pending Interaction Backend
- `MYM-26` Frontend Smoke Workbench
- `MYM-27` Backend Mock Stream Integration
- `MYM-28` Real Hermes Stream Boundary Evaluation
- `MYM-29` Real Stream Bridge
- `MYM-30` Review RM Workbench V0 Real Stream Bridge
- `MYM-31` Hermes Agent rm_workbench_emit_contract Tool Registration
- `MYM-32` Review Hermes Agent rm_workbench_emit_contract Tool Registration
- `MYM-34` RM Workbench V0 Runtime Alignment + Real Stream Readiness

这一阶段结束后，已经确认：

- Hermes Agent 继续做 runtime。
- `hermes-webui` 继续做 backend source of truth。
- `/api/chat/stream` 保留现有 top-level SSE protocol。
- `rm_workbench` SSE event 是前端 workbench 的 hook point。
- `CUSTOM name = a2ui.surface.messages` 继续承载 A2UI message。
- 前端只消费 `event: rm_workbench` 且 `data.kind === "agui_events"`。
- Memory 继续是 proposal-first，不自动写入。

当前已经打通的最小链路：

- Hermes Agent 能真实暴露 `rm_workbench_emit_contract`
- Hermes WebUI real chat runs 会在支持时自动补上 `rm_workbench` toolset
- `MYM-29` 的 bridge 已经可以消费该 tool 的 completion
- runtime venv 已通过 editable install 对齐到 `/Users/hywl/hermes-agent`
- WebUI 启动诊断和真实 chat smoke 已证明模型能看见 `rm_workbench_emit_contract`
- React generic renderer 已证明可消费 `rm_workbench` / A2UI catalog 并渲染 table / chart / choice primitives

但当前还没有成立的结论：

- 主 WebUI chat 前端已经是第一条真实 RM workflow 的合适正式宿主
- “让它一句话自然生成图表” 已经稳定可用

`MYM-36` 的最终结论需要作为后续 sequencing 的约束：

- 当前不是本地 schema stripping bug
- `() => any` 不能当作 ground truth
- 真实风险已经开始从 tool registration 漂移到
  - provider/model 对 nested object args 的稳定性
  - 主前端宿主如何正式承接 React RM workbench

---

## 2. 下一步主线

### Phase 1: Generic A2UI Renderer Catalog

建议作为 **Issue 7.6**。

目标：

```text
Prove that Hermes can emit generic structured UI blocks through the existing UI contract path, and React can render table/chart/choice primitives before the first RM-specific workflow.
```

为什么现在先做它：

- V0 的目标不是只证明 RM 定制组件能渲染，而是证明 Agent 能通过结构化参数生成常规 UI。
- 当前 React smoke host 只支持 `CustomerProfileCard`、`ProductFitTable`、`BriefExportPanel`，还不能渲染 chart。
- 如果直接进入 Issue 8，会把“通用 UI 基建是否可用”和“RM workflow 是否跑通”混在一起验收。

退出标准：

- 同一条 `rm_workbench_emit_contract` 链路能承载 generic UI blocks。
- 前端能渲染 `MetricCard`、`DataTable`、`LineChart` 或 `BarChart`、`PieChart`、`ChoiceList`。
- 不引入 `render_table` / `render_chart` 等多个 Hermes tools。
- 不执行任意 JSX / HTML / remote JS。
- 现有 RM surfaces 仍可渲染，`ProductFitTable` pending interaction 仍可 resolve。

### Phase 2: First Real RM Workflow

在当前结论下，**不建议直接进入**。Issue 8 前需要再插一个前端基建阶段。

### Phase 1.5: React Frontend Foundation for real WebUI path

建议作为 **Issue 7.7**。

目标：

```text
Turn the existing React RM workbench host from a validated renderer path into the formal structured-UI host for the real WebUI chat path.
```

为什么现在必须插入它：

- `MYM-35` 证明了 React generic renderer 可通，但证明的是 React workbench host / mock path，不是当前主 WebUI chat 宿主。
- `MYM-36` 进一步证明，真实问题已经不只是 tool registration，还包括主前端宿主如何稳定承接 structured UI。
- 如果跳过这一步直接进入真实 RM workflow，会把 skill logic、tool args、SSE bridge、frontend host state 全部混在一个 issue 里。

退出标准：

- 主 WebUI path 中有明确的 React RM workbench mount point。
- 真实 `event: rm_workbench` 能驱动该 React 区域更新。
- generic primitives 与 RM semantic surfaces 都能在主路径中显示。
- `pending/resolve` 在主路径中仍可闭环。

### Phase 2: First Real RM Workflow

建议作为 **Issue 8**，但前提是 Phase 1.5 完成。

目标：

```text
Implement one real RM workflow path driven by RM Skill.md + rm_workbench_emit_contract.
```

为什么现在轮到它：

- Issue 7.5 / `MYM-34` 已证明 runtime 与 WebUI 真实链路可用。
- Issue 7.6 先证明通用 UI renderer catalog 可用。
- Issue 7.7 再把 React RM workbench host 正式接到真实主路径里。
- 之后最值得验证的是第一条真实 workflow，而不是继续停留在基础设施层。
- 这一阶段要验证 RM Skill.md、tool 调用时机、以及用户交互闭环是否真的成立。

退出标准：

- RM Skill.md 能指导 Agent 在正确节点 emit contract。
- 前端能看到真实 run 触发的 `CustomerProfileCard`。
- 前端能看到真实 run 触发的 `ProductFitTable`。
- 用户选择后能把结构化输入送回 run，Agent 继续下一步。

建议只做一个场景：

- `pre_meeting_brief`

### Phase 3: Memory Review Path

建议作为 **Issue 9**。

目标：

```text
Turn proposal-first memory into a reviewable human workflow, still without automatic writes.
```

这阶段才处理：

- `MemoryDiffCard` 的 review UX
- proposal approve / reject 状态
- 后续写入目标系统边界

### Phase 4: Productization

这阶段才考虑：

- 多 workflow 扩展
- 更完整的 chart / table / report catalog
- 真实客户数据接入
- artifact / export 深化
- CopilotKit frontend utility 是否有局部复用价值

---

## 3. 建议的 Issue 序列

### Issue 7

`Hermes Agent rm_workbench_emit_contract Tool Registration`

### Issue 7.5

`RM Workbench V0 Runtime Alignment + Real Stream Readiness`

状态：已完成，`MYM-34`。

### Issue 7.6

`RM Workbench V0 Generic A2UI Renderer Catalog`

状态：下一步主线。

### Issue 7.7

`RM Workbench V0 React Frontend Foundation`

状态：建议新增，位于 Issue 7.6 与 Issue 8 之间。

### Issue 8

`RM Workbench V0 First Real Pre-Meeting Brief Workflow`

状态：Issue 7.6 + Issue 7.7 之后。

### Issue 9

`RM Workbench V0 Memory Proposal Review Flow`

### Issue 10+

- 多 workflow
- 真实数据
- artifact/export 深化
- 前端产品化

---

## 4. 当前不要提前做的事

- CopilotKit runtime takeover
- 完整 RM 工作台视觉重做
- 多 workflow 并行扩展
- 真实客户数据 / 真实产品池接入
- 自动 Memory 写入
- 为了 UI 去改 Hermes 整体 runtime loop

原因：

- 当前主风险已经从协议形状转为 **真实 RM workflow 是否能稳定诱导 tool call 并完成交互闭环**。
- 在进入真实 RM workflow 前，还需要先补齐两件事：
  - **通用 UI catalog 是否能渲染图表/表格/选择控件**
  - **主 WebUI path 是否已经有正式的 React structured-UI 宿主**
- 真实客户数据、自动 memory 写入、CopilotKit runtime takeover 都会把 Issue 8 的验收边界放大。

---

## 5. Runtime / Streaming Issue 完成门槛

凡是改动以下任一层的 issue：

- Hermes Agent runtime / tools / toolsets
- Hermes WebUI streaming bridge
- `/api/chat/stream` 或 SSE event
- 前端真实 stream 消费路径

完成标准必须包含一次真实 WebUI smoke：

```text
从 WebUI 真实 chat 触发
  -> 观察到预期 tool call 或 SSE event
  -> 观察到预期 UI 渲染或明确的错误 surface
```

验收记录必须进入 issue comment，至少包含其一：

- 截图
- SSE log
- browser console log
- server log 中的 `event: rm_workbench` / tool call 证据

mock-stream、unit test、文档 review 只能证明协议形状，不能单独证明 runtime integration 已完成。

每个涉及 Hermes Agent 的 issue 还必须先过开发环境对齐 checklist：

```text
1. which hermes 指向预期 venv
2. runtime venv import 的 tools/toolsets 来自预期 agent 目录
3. 新增 tool 可在 runtime venv 中 import
4. WebUI 启动时 HERMES_WEBUI_AGENT_DIR / discover_agent_dir 指向同一目录
5. WebUI 真实 chat 中模型能看见新增 tool
```

---

## 6. 当前主线结论

```text
Issue 7.5 已完成。
先完成 Issue 7.6：generic A2UI renderer catalog。
再补 Issue 7.7：React frontend foundation for real WebUI path。
最后再进入 Issue 8：first real pre-meeting brief workflow。
```
