# Structured UI Subsystem Roadmap (formerly "RM Workbench V0 Roadmap")

路径：`docs/ui-ux/rm-workbench-v0-roadmap.md`
状态：`active / sequencing (realigned 2026-05-09)`
更新时间：`2026-05-09`
入口：`docs/ui-ux/rm-workbench-v0-index.md`
架构事实：`docs/ui-ux/rm-workbench-v0-architecture.md`
技术决策：`docs/ui-ux/rm-workbench-v0-adr.md`（特别是 ADR-009 ~ ADR-013，定义了 Layer 0 / Layer 1 分层）

---

## 0. Roadmap 目标

这份 roadmap 只回答三件事：

1. V0 现在已经做到哪一步。
2. 接下来应该先补哪条技术链。
3. 哪些事情现在不要提前做。

它不维护架构事实和技术决策。架构事实进入 `rm-workbench-v0-architecture.md`，技术取舍进入 `rm-workbench-v0-adr.md`。

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
- `MYM-35` RM Workbench V0 Generic A2UI Renderer Catalog
- `MYM-36` RM Workbench V0 rm_workbench_emit_contract Schema Exposure Debug

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
- `MYM-35` 截图与 SSE 证据已覆盖 `MetricCard`、`DataTable`、`LineChart`、`BarChart`、`PieChart`、`ChoiceList`
- 当前树已再次通过 adapter/mock-stream tests、real stream bridge tests、frontend build，可作为 7.6 closeout 验收依据

但当前还没有成立的结论：

- 主 WebUI chat 前端已经是第一条真实 RM workflow 的合适正式宿主
- "让它一句话自然生成图表" 已经稳定可用

`MYM-36` 的最终结论需要作为后续 sequencing 的约束：

- 当前不是本地 schema stripping bug
- `() => any` 不能当作 ground truth
- 真实风险已经开始从 tool registration 漂移到
  - provider/model 对 nested object args 的稳定性
  - 主前端宿主如何正式承接 React structured-UI host
- `MYM-36` 保留的本地修复只有 WebUI `tool.completed` args recovery；不把 schema redesign 带入后续阶段

### MYM-38 暴露的层级错误（2026-05-09）

MYM-38（Issue 7.7）在 Codex 5 轮迭代中无法通过真实 WebUI smoke。每轮修一处症状，
下一轮在新位置暴露同类问题。最终从 `~/.hermes/logs/errors.log` 找到的根因不是
任何单一 bug，而是早期 ADR 没有把 **"AI 生成 UI 是 Hermes 工作台的原子能力"** 和
**"RM Workbench 是它的第一个 consumer"** 清晰分层。

具体表现：

- Layer 0 validator 把"渲染要求"和"业务合规要求"等价（`_validate_ui_blocks` 对每种
  chart/table/choice props 做硬校验），导致模型差一点 → RUN_ERROR → 一个块都不画。
- Layer 0 contract 信封把 `kind` 当业务路由器（`ALLOWED_KINDS = {"rm_workbench",
  "rm.pre_meeting_brief"}`），把 `run_id`/`thread_id`/`skill` 设为必填。
- Layer 0 命名层把原子能力 RM 化（tool 名 / SSE event / DOM / CSS）。
- Codex 被 coding-boundary 文档锁在窄边界内，每轮只能修症状不能动 framing。

这些观察导致了 ADR-009 ~ ADR-013 的新增和 ADR-003/006/007 的修订。本 roadmap
后续阶段顺序也据此重排（见 § 3）。

---

## 2. 下一步主线

### Phase 1.5: React Frontend Foundation + Layer 0 校准

建议作为 **Issue 7.7**（当前进行中，对应 MYM-38）。

目标（2026-05-09 重新对齐）：

```text
1. 把已验证的 React structured-UI host 从独立 smoke / mock path
   推进成主 WebUI chat 路径中的正式宿主。
2. 同步把 Layer 0 校准做掉：放宽 validator、最小化 contract 信封、
   `emit_ui` 重命名（ADR-009 ~ ADR-012）。
```

为什么现在必须插入它：

- `MYM-35` 证明了 React generic renderer 可通，但证明的是 React workbench host / mock path，不是当前主 WebUI chat 宿主。
- `MYM-36` 进一步证明，真实问题已经不只是 tool registration，还包括主前端宿主如何稳定承接 structured UI。
- `MYM-38` 暴露了 Layer 0 / Layer 1 分层错误——必须在进入 Issue 8 前修正，否则 RM workflow 会撞同样问题。
- 如果跳过这一步直接进入真实 RM workflow，会把 skill logic、tool args、SSE bridge、frontend host state、Layer 0 严格度全部混在一个 issue 里。

退出标准（ADR-007 修订验收口径）：

**Layer 0 验收（必须，用于关闭 Issue 7.7）：**

- 主 WebUI path 中有明确的 React structured-UI mount point ✅（MYM-38 已完成）
- 从主 chat 触发任意可达通用 contract（mock-stream / inject endpoint / 任意通过宽松校验的真实 tool 调用），能在主路径渲染至少 1 个 generic primitive
- Layer 0 validator 已放宽到最小校验，缺字段由 primitive 兜底
- Layer 0 contract 信封最小化（kind/run_id/thread_id/skill 全可选）
- `emit_ui` tool 命名落地（旧名 `rm_workbench_emit_contract` 物理重命名，无别名）
- `pending/resolve` 在主路径中仍可闭环

**Layer 1 验收（不阻塞 Issue 7.7，归 Issue 8）：**

- RM Skill 在真实模型对话中稳定构造 RM 语义 contract
- 触发完整 brief 渲染（CustomerProfileCard 等）

### Phase 2: First Real RM Workflow

建议作为 **Issue 8**，前提是 Phase 1.5 Layer 0 部分完成。

目标：

```text
Implement one real RM workflow path driven by RM Skill.md + emit_ui.
```

**重要约束（ADR-013）**：本 issue **不应该**为 RM 添加新的 React surface 组件
或新的后端 RM 分支。RM Skill 通过 prompt 教模型用现有 Layer 0 primitive 表达
业务（"客户档案 = 3 个 MetricCard"，"产品选择 = DataTable + ChoiceList + interaction"），
而不是依赖 `frontend/src/rm/surfaces/` 下的预制组件。

> 现有的 `CustomerProfileCard` / `ProductFitTable` / `BriefExportPanel` 是过渡态
> 资产，由 Issue 9（Skill-driven Layer 1 migration）一次性替换并删除。Issue 8
> 写 RM Skill 时**不要**进一步加深对这些 React 组件的依赖。

为什么现在轮到它：

- Issue 7.5 / `MYM-34` 已证明 runtime 与 WebUI 真实链路可用。
- Issue 7.6 先证明通用 UI renderer catalog 可用。
- Issue 7.7 把 React structured-UI host 正式接到真实主路径里 + Layer 0 校准。
- 这一阶段要验证 RM Skill.md prompt 教学能否成功诱导模型用 Layer 0 primitive 表达 RM 业务。

退出标准：

- RM Skill.md 能指导 Agent 在正确节点 `emit_ui`。
- 前端能看到真实 run 触发的客户档案展示（用 MetricCard 组合表达）。
- 前端能看到真实 run 触发的产品选择 UI（用 DataTable + ChoiceList 表达）。
- 用户选择后能把结构化输入送回 run，Agent 继续下一步。

建议只做一个场景：

- `pre_meeting_brief`

### Phase 2.5: Skill-driven Layer 1 Migration

建议作为 **Issue 9**。可与 Issue 8 并行准备（Skill 资产前期工作不冲突），但合并落地
应在 Issue 8 收口附近。

目标：

```text
让 Layer 1 完全脱离代码形态，迁移到 Skill 资产形态。
```

具体动作：

- 让 `ChoiceList` 等 primitive 加 `on_confirm` interaction wiring，使 Layer 0 自带
  结构化输入回传能力（pending_interaction.resolve）。
- 写出 RM Skill 资产，验证 RM workflow 能完全用 Layer 0 primitive 表达。
- 删除 `frontend/src/rm/surfaces/` 下的 RM React 组件。
- 删除 `api/rm_workbench/adapter.py` 中的 RM 分支（`map_surface_to_a2ui_messages`）。
- 删除 contract 的 `surfaces` 字段（ui.blocks 是唯一通用路径）。

退出标准：

- RM workflow 在删除 React surfaces 后仍能完整工作。
- 新业务 consumer（CFA / 投资 / 日常 UI）的添加只需要写 Skill，不需要改代码。

### Phase 3: 命名整改

建议作为 **Issue 10**。

目标：

```text
落实 ADR-012 deprecation 队列，去掉所有 rm_workbench 系工程命名。
```

清单：

- 后端目录 `api/rm_workbench/` → `api/generative_ui/`（暂定）
- SSE event 名 `rm_workbench` → `ui`（或 `generative_ui`）
- AG-UI CUSTOM 名 `rm.skill.output` 等改成 generic
- 前端 `RmWorkbenchHost.tsx` / `rmWorkbenchIsland.tsx` / `#rmWorkbenchIslandRoot` /
  `window.__rmWorkbenchEvent` / `.rm-workbench-island` 同步改名
- 文档文件名 `rm-workbench-v0-*.md` 改名

这件事必须等 Issue 9 完成（删了 RM 代码分支后整改面才小）。

### Phase 4: Memory Review Path

建议作为 **Issue 11**（原 Issue 9，因新增 Layer 1 migration 与命名整改后顺延）。

目标：

```text
Turn proposal-first memory into a reviewable human workflow, still without automatic writes.
```

这阶段才处理：

- Memory proposal 的 review UX（用 Layer 0 primitive 表达，不写 `MemoryDiffCard.tsx`）
- proposal approve / reject 状态
- 后续写入目标系统边界

### Phase 5: Productization

这阶段才考虑：

- 多 workflow 扩展（每个新 workflow 都是新的 Skill，不动代码）
- 更完整的 primitive catalog（按需扩充 Layer 0 词汇表，每次独立 issue）
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

状态：已接受并关闭；实现来自 `MYM-35`，closeout 由 `MYM-37` 复核。

### Issue 7.7

`RM Workbench V0 React Frontend Foundation + Layer 0 校准`

状态：进行中（MYM-38）；2026-05-09 验收口径修订（见 § 2 Phase 1.5）。
不再使用旧版"必须看到完整 RM brief 渲染"作为退出标准，改为 Layer 0 渲染至少
1 个 generic primitive 即满足。

### Issue 8

`First Real Pre-Meeting Brief Workflow`

状态：Issue 7.7 Layer 0 部分收口后启动；通过 RM Skill prompt 教模型用 Layer 0
primitive 表达 RM 业务，不添加新 React surface（ADR-013）。

### Issue 9

`Skill-driven Layer 1 Migration`

状态：可与 Issue 8 并行准备，合并落地在 Issue 8 收口附近。删除 `frontend/src/rm/surfaces/`、
adapter RM 分支、contract.surfaces 字段。让 Layer 1 完全脱离代码形态。

### Issue 10

`命名整改：rm_workbench 系工程命名去 RM 化`

状态：Issue 9 完成后启动。落实 ADR-012 deprecation 队列。

### Issue 11

`Memory Proposal Review Flow`

状态：原 Issue 9，因前面新增 Issue 9/10 顺延。Memory review UX 用 Layer 0 primitive
表达，不写专用 React 组件。

### Issue 12+

- 多 workflow（每个是新 Skill，不动代码）
- Layer 0 catalog 扩充（按需独立 issue）
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
- **为新业务 consumer（CFA / 投资 / 日常 UI）新建 `frontend/src/<domain>/surfaces/` 目录或后端分支**（违反 ADR-013）
- **在 Layer 0 validator 加 per-type 字段强校验或 kind 白名单**（违反 ADR-010 / ADR-011）
- **在 Issue 8 RM Skill 实现中进一步加深对 `frontend/src/rm/surfaces/` 现有组件的依赖**——这些组件即将在 Issue 9 删除

原因：

- 当前主风险已经从协议形状转为 **Layer 0 / Layer 1 分层是否清晰**（MYM-38 暴露的）和
  **真实 RM workflow 能否通过 Skill prompt 诱导模型用 Layer 0 primitive 表达业务**。
- 在进入真实 RM workflow 前，还需要先完成 Layer 0 校准（validator 放宽、信封最小化、emit_ui 重命名）。
- 真实客户数据、自动 memory 写入、CopilotKit runtime takeover、RM 化新组件都会把 Issue 8 的验收边界放大或把 Layer 0 RM 化错误进一步固化。

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
Issue 7.5  已完成
Issue 7.6  已完成: generic A2UI renderer catalog
Issue 7.7  进行中: React frontend foundation + Layer 0 校准
            退出标准已修订（ADR-007）: Layer 0 渲染至少 1 个 generic primitive 即满足
Issue 8    Issue 7.7 收口后: first real pre_meeting_brief workflow
            约束: 通过 RM Skill prompt 教模型用 Layer 0 primitive 表达，不加新 React surface
Issue 9    Skill-driven Layer 1 migration: 删除 RM React surfaces，让 Layer 1 完全脱离代码
Issue 10   命名整改: 落实 ADR-012 deprecation 队列
Issue 11   Memory proposal review flow（用 Layer 0 表达）
Issue 12+  productization
```
