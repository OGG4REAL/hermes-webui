# RM Workbench V0 ADR

路径：`docs/ui-ux/rm-workbench-v0-adr.md`
状态：`active / architectural decision record`
更新时间：`2026-05-09`
入口：`docs/ui-ux/rm-workbench-v0-index.md`

---

## 0. 这份文档负责什么

这份文档维护 Hermes WebUI 结构化 UI 子系统（即原 "RM Workbench V0"）的技术决策。

每条 ADR 只记录：

- decision
- status
- context
- consequences

当前架构事实放在 `rm-workbench-v0-architecture.md`。

执行顺序放在 `rm-workbench-v0-roadmap.md`。

过程材料、spike、review、issue status 不进入这份文档，除非它们改变了一个技术决策。

ADR 是 coding spec 的唯一 core 文件。当一条决策被证伪时：

- 不删除原 ADR 文本（保留追溯链）
- 在原 ADR 状态行打 `superseded by ADR-NNN`
- 新决策另开新编号 ADR

---

## 0.1 方向校准日志

### 2026-05-09：分层错误的发现

Issue 7.7（MYM-38）在 Codex 5 轮迭代中始终无法通过真实 WebUI smoke。每轮修一处症状，下轮在新位置暴露同类问题（schema strip → validator 只接受 RM kind → adapter KeyError → block 级字段缺失 → ……）。

根因不是任何一行代码，而是早期 ADR 没有把 **"AI 生成 UI 是 Hermes 工作台的原子能力"** 和 **"RM Workbench 是它的第一个 consumer"** 清晰分层。具体表现：

- 命名层把原子能力 RM 化（tool / SSE event / CUSTOM name / 前端 host / DOM id / CSS class 全部带 `rm_workbench` 前缀）
- 校验层把"渲染要求"和"业务合规要求"等价（`_validate_ui_blocks` 对每种 chart/table/choice 的 props 做了不能优雅降级的硬校验）
- 编排层把"模型必须严格构造完整契约"当成默认要求，而不是把渲染 best-effort 当成默认要求
- coding boundary 把 RM 化的命名与硬约束作为"不许 relitigate 的 upstream decision"，于是 Codex 每轮都被边界绑死

因此本日新增 ADR-009 ~ ADR-012，并将 ADR-003 标记 superseded、强化 ADR-006、重写 ADR-007 验收口径。

后续如果再次出现"反复修不动"的迭代，应**先回到本日志**对照分层判断有无新的 framing 错误，再决定是否继续修代码。

---

## ADR-001: Hermes runtime remains the agent runtime

状态：`accepted`

决策：

```text
V0 继续使用 Hermes Agent 作为 runtime，不让 CopilotKit runtime 接管 Hermes runtime。
```

背景：

- Hermes 已经承载 conversation loop、tools、skills、memory、approval、clarify。
- CopilotKit / AG-UI / A2UI 的价值主要在 frontend/event/UI protocol 层。
- 直接 runtime takeover 会把 Hermes 现有语义重新映射到 CopilotKit runtime，风险过大。

影响：

- CopilotKit 当前是 reference-only / future evaluation。
- V0 通过 adapter 对齐 AG-UI/A2UI，而不是替换 runtime。

---

## ADR-002: Keep `/api/chat/stream` top-level SSE protocol

状态：`accepted`

决策：

```text
不把 /api/chat/stream 整体改成 AG-UI top-level event stream。
保留现有 Hermes WebUI SSE event names，并新增/复用 event: rm_workbench 承载 AG-UI payload。
```

背景：

- WebUI 已经有稳定 chat stream、tool lifecycle、approval、clarify、cancel、metering 等事件。
- 全量替换 stream protocol 会扩大回归面。
- AG-UI 可以作为 payload rail 嵌入，而不是接管整条 SSE。

影响：

- frontend 只订阅 `event: rm_workbench` 获取 structured UI payload。
- 现有文本、tool card、approval、clarify 逻辑继续保持。

---

## ADR-003: ~~Use one emit contract tool, not many render tools~~ (废弃)

状态：`superseded (2026-05-09)`

> **本 ADR 已废弃，原文已删除以避免 agent 误读。**
>
> 本 ADR 原本试图同时表达两件事：
> 1. "Layer 0 用单 tool 而非多 render tool" —— 这个结论仍然正确，由 **ADR-009** 接管。
> 2. "tool 名 = `rm_workbench_emit_contract`" —— 这个命名错误地把原子能力 RM 化，由 **ADR-012** 替代。
>
> 如需查阅原文，见 git 历史：`git show HEAD~1 -- docs/ui-ux/rm-workbench-v0-adr.md`。

---

## ADR-004: AG-UI is event rail, A2UI is surface protocol

状态：`accepted`

决策：

```text
AG-UI 负责 event rail。
A2UI 负责 declarative UI messages。
RM semantic surface 不成为 AG-UI top-level event。
```

背景：

- AG-UI 提供 `CUSTOM` 作为扩展点。
- A2UI 的 `createSurface` / `updateComponents` / `updateDataModel` 更适合描述 UI。
- 自造 top-level event 会让后续协议升级困难。

影响：

- A2UI messages 通过 `CUSTOM name = a2ui.surface.messages` 承载。
- Pending interaction 通过独立 backend endpoint resolve。

---

## ADR-005: Pending interaction remains separate from clarify

状态：`accepted`

决策：

```text
结构化 UI 输入使用 pending interaction，不复用 clarify。
```

背景：

- clarify 是自然语言澄清。
- RM UI interaction 需要结构化 payload、surface_id、interaction_id、schema validation。
- 把结构化输入塞进 clarify 会混淆语义和测试边界。

影响：

- `interaction_id` required。
- resolve API 必须结构化。
- 后续 workflow resume 依赖 pending interaction，而不是 clarify text。

---

## ADR-006: Generic UI catalog is foundation, RM surfaces are domain layer

状态：`accepted (reaffirmed 2026-05-09)`

决策：

```text
通用 UI primitives 是底座，RM semantic surfaces 是业务层。
通用底座（Layer 0）独立成立，不被任何单一业务（Layer 1）的形状要求约束。
业务层的 schema 严格性归业务层负责，不向下污染底座。
```

背景：

- V0 不只是 RM 专属 UI 展示能力。
- 表格、图表、指标卡、选择列表是通用 Agent UI 能力。
- RM surfaces 可以组合 generic primitives，并定义业务交互。
- **2026-05-09 校准：** 本 ADR 在 Issue 7.6 的实施过程中没有被贯彻。
  Generic primitives 虽然在前端 catalog 中独立存在，但后端 `validate_contract`、
  `kind` 白名单、tool 命名都把通用底座绑死在 RM 命名空间内。这是 Issue 7.7
  反复推不动的真因，而不是模型的构造能力问题。

影响：

- Issue 7.6 先证明 generic renderer catalog。
- Issue 8 只验证第一条真实 RM workflow。
- 任何"通用底座只在 RM 路径下才能用"的实现都视为违反本 ADR，必须修正。

---

## ADR-007: React structured-UI host must enter the real WebUI path before Issue 8

状态：`accepted (acceptance criteria revised 2026-05-09)`

决策：

```text
在第一条真实 RM workflow 前，必须先把 React 结构化 UI host 接进主 WebUI chat path。
```

背景：

- React renderer / mock path 已经证明可行。
- 但用户日常使用的是主 WebUI chat，而不是独立 smoke app。
- 如果直接进入真实 workflow，skill logic、tool args、SSE bridge、frontend host state 会混在一起验。

影响：

- Issue 7.7 先做 React frontend foundation。
- Issue 8 只在主路径能真实渲染 structured UI 后开始。

**2026-05-09 验收口径修订：**

原 Issue 7.7 acceptance 把"模型能稳定生成完整合规 contract"和"前端 host 接好"绑在同一个验收上，
事实上这两件事属于不同层（前者是 Layer 1 RM Skill 的能力，后者是 Layer 0 host 接入），
绑在一起导致 Codex 5 轮迭代仍未通过。修订后的验收口径：

- **Layer 0 验收**（必须，用于关闭 Issue 7.7）：
  从主 WebUI chat 触发任意可达通用 contract（mock-stream / inject endpoint / 任意通过宽松校验的真实 tool 调用），
  能在主 chat 路径里渲染至少 1 个 generic primitive。
- **Layer 1 验收**（不阻塞 Issue 7.7，归 Issue 8）：
  RM Skill 在真实模型对话中稳定构造 RM 语义 contract 并触发完整 brief 渲染。

---

## ADR-008: Runtime and streaming changes require real WebUI smoke

状态：`accepted`

决策：

```text
凡是改 runtime / tool / streaming / frontend host 的 issue，验收必须包含一次真实 WebUI smoke。
```

背景：

- unit test 和 mock stream 只能证明协议形状。
- 之前已经出现过 runtime path 与开发目录不一致的问题。
- 主 WebUI path 与 React smoke path 也可能不一致。

影响：

- issue comment 必须包含截图、SSE log、browser console log 或 server log。
- 验收要证明从主 WebUI chat 触发到预期 SSE / UI 可见。

---

## ADR-009: Generative UI is an atomic capability of the workbench, not an RM feature

状态：`accepted (2026-05-09)`

决策：

```text
"AI 在对话中生成结构化 UI" 是 Hermes WebUI 工作台的一项原子能力（Layer 0）。
RM Workbench 是这项能力的第一个 consumer（Layer 1），不是它的所有者。
任何 Layer 0 实现细节（tool / SSE event / 前端 host / 校验 / 命名）都不得以
任何 Layer 1 业务的形状要求作为存在前提。
```

背景：

- 用户的工作台日常使用同样需要 AI 生成 UI（图表、表格、可填写表单、可选择列表），
  不局限于 RM 场景。
- 如果把 Generative UI 绑死在 RM 语义里，每个新 consumer（投资笔记、CFA 复习、
  日常数据查询……）都要绕一层伪装才能用。
- ADR-006 早就识别了"通用底座 + 业务层"的分层意图，但实施层把通用底座 RM 化了。
  本 ADR 把意图正式升格为根决策，作为后续所有 Layer 0 决策的母条款。

影响：

- 任何后续提案如果隐含"Generative UI 必须通过 RM 上下文"，视为违反本 ADR。
- Layer 1（RM 或其他 consumer）通过自己的 Skill / prompt / 校验逻辑塑造模型行为，
  不通过修改 Layer 0 的强约束达到目的。
- 文档命名带 "rm-workbench" 是历史包袱，会在 ADR-011 的过渡期内分批替换；
  在那之前，所有引用应理解为"工作台结构化 UI 子系统"。

---

## ADR-010: Renderer is best-effort; schema enforcement belongs in the Skill, not the Layer 0 validator

状态：`accepted (2026-05-09)`

决策：

```text
Layer 0 的 contract validator 只校验最小可识别性：
- block 必须有 id（非空字符串）
- block 必须有 type，且 type 在已注册 catalog 内
- block 必须有 props（object，可空）

per-type 字段（series / xKey / labelKey / columns / options 等）缺失或不完整时，
不抛 ValueError，由 primitive 在前端做空状态/警告渲染。

业务级的 schema 严格性（例如 RM 要求 customer/product_candidates 必须存在）
属于该业务 Skill 的职责，写在 Skill 自己的校验器里，不进入 Layer 0 validator。
```

背景：

- 现行 `_validate_ui_blocks` 把"模型必须严格构造完整 props"作为渲染前提。
  任何字段差一点就 RUN_ERROR，前端一个块都不画。
- 这与 LLM 在长结构化输出上的实际能力分布不匹配，也与"AI 生成 UI 应该宽容"
  的产品直觉不匹配。
- best-effort 渲染是 Generative UI 子系统的默认 mood：宁可显示一个空图加警告，
  也不要因为缺一个 series.key 让整轮对话视觉上一片空白。

影响：

- `api/rm_workbench/contracts.py:_validate_ui_blocks` 必须重写为最小校验。
- 前端 primitive（`MetricCard` / `DataTable` / `*Chart` / `ChoiceList`）必须能在
  必填字段缺失时渲染明确的"数据不完整"占位，而不是抛运行时异常。
- RM Skill 在 V1 实现时自带一份 RM-specific 严格校验，发现不合规直接由 Skill
  指导模型重新生成，而不是把错误传到 Layer 0。

---

## ADR-011: Contract envelope is minimal at Layer 0; consumer-specific fields are optional

状态：`accepted (2026-05-09)`

决策：

```text
Layer 0 contract 只要求：
- ui.blocks（非空数组），或 surfaces（非空数组），至少其中之一。

下列字段全部为可选；缺省时由后端补默认值或 uuid，不再作为校验阻塞点：
- kind        缺省 = "ui"
- version     缺省 = 当前 Layer 0 schema 版本
- run_id      缺省 = 后端生成 uuid
- thread_id   缺省 = 当前 WebUI session id
- skill       缺省 = 空字符串

kind 不再作为 validator 路由门禁。"rm.pre_meeting_brief" 等业务 kind 由
对应 Skill 在 Layer 1 自检；Layer 0 不维护 kind 白名单。
```

背景：

- 现行 `validate_contract` 用 `ALLOWED_KINDS = {"rm_workbench", "rm.pre_meeting_brief"}`
  做硬路由，任何非 RM 用途必须伪装 kind 才能通过。
- run_id / thread_id / skill 三个必填字段都是 RM workflow 概念，对日常 AI 生成 UI
  没有意义，但被强制要求，进一步把 Layer 0 RM 化。

影响：

- `validate_contract` 改写后，Layer 0 接受任意 kind。
- `map_rm_skill_contract_to_agui_events` 中所有 `contract["customer"]` /
  `contract["product_candidates"]` 等 RM-specific 字段访问，必须迁出 Layer 0
  通用路径，只在 RM 语义 surface 渲染分支中使用。
- 现有 RM smoke 测试需要补一份 Layer 0-only 测试用例，验证最小信封即可渲染。

---

## ADR-012: `emit_ui` is the canonical tool name; `rm_workbench_emit_contract` is removed

状态：`accepted (2026-05-09)`

决策：

```text
Layer 0 唯一对模型暴露的结构化 UI 工具命名为 emit_ui。
rm_workbench_emit_contract 直接物理重命名为 emit_ui，不保留兼容别名。

理由：该 tool 目前没有任何外部 consumer —— 只在 webui bridge 内部消费、
没有任何 Skill 在产线 prompt 中引用、没有第三方依赖。保留别名只会:
- 在模型 prompt 里同时呈现两个名字，强化 RM 化暗示，
- 给未来 agent 误读"两个名字都是当前规范"的空间。

去 RM 化的其余命名整改作为独立 issue 处理，本轮重构暂不强制改:
- SSE event name "rm_workbench"
- AG-UI CUSTOM names 以 "rm." 开头的非 RM 专用事件
- 前端 RmWorkbenchHost / rmWorkbenchIsland.tsx / #rmWorkbenchIslandRoot /
  window.__rmWorkbenchEvent / .rm-workbench-island
- 后端目录 api/rm_workbench/
- 文档命名 rm-workbench-v0-*

理由：这些名字虽然有 RM 化暗示，但它们不直接进入模型 prompt，对 Layer 0
行为修复（ADR-010 / ADR-011）不构成阻塞。一次性改它们会让本轮 PR 同时
跨 backend / frontend / static / 测试 / 文档，回归面过大；分开做更可控。
```

背景：

- `rm_workbench_emit_contract` 是模型唯一直接看到的 RM 化命名，在 tool description
  里直接给 LLM "我现在在做 RM 流程"的暗示。这是 Layer 0 RM 化最致命的一处。
- 其他命名（SSE event / DOM id / 后端目录）是工程内部名字，模型看不到，对原子
  能力的 framing 没有直接污染，可以延后处理。

影响：

- hermes-agent 端 `tools/rm_workbench_tool.py` 中 `EMIT_TOOL_NAME` 改为 `emit_ui`，
  registry 注册名同步改。
- webui 端 `_handle_rm_emit_tool` 触发条件从 `name == 'rm_workbench_emit_contract'`
  改为 `name == 'emit_ui'`。
- 所有相关测试（hermes-webui / hermes-agent 两侧）需同步替换 tool 名字符串。
- RM Skill 的引导词和系统 prompt 中所有对 tool 名的提及一律改成 `emit_ui`。
- 工程内部 `rm_workbench` 命名（目录 / event / DOM / CSS）保留不动，进 deprecation
  队列，由后续独立 issue 一次清理。

---

## ADR-013: Layer 1 consumers should manifest as Skills, not as code components

状态：`accepted (2026-05-09)`

决策：

```text
业务 consumer（RM / CFA / 投资 / 日常 AI 生成 UI ……）的预制 surface
不应该以专用 React 组件 + 专用后端分支的形式硬编码在仓库里。

业务 consumer 的"约定和预设"应该以 Skill 资产的形式存在：
- Skill 在 prompt 中教模型如何用 Layer 0 primitive 组合出业务语义
- 例：RM Skill 教模型 "要展示客户档案时，emit 3 个 MetricCard"，
      而不是仓库里有一个 CustomerProfileCard.tsx
- 例：RM Skill 教模型 "要让用户选产品时，emit 一个 DataTable +
      一个 ChoiceList（带 interaction_id）"，而不是仓库里有一个 ProductFitTable.tsx

Layer 0 catalog 是工作台的 UI 词汇表（primitives + interaction protocol）。
扩充 catalog = 工作台原子能力扩张，每次都是独立的有价值 issue。

业务 consumer 的扩充 = 写新的 Skill，不应触发任何 frontend / backend 代码改动
（除非业务确实需要新的 primitive 进入 catalog）。
```

背景：

- 当前 `frontend/src/rm/surfaces/` 下的 `CustomerProfileCard` / `ProductFitTable` /
  `BriefExportPanel` 看似是 "Layer 1 业务组件"，但拆解后会发现它们都是 Layer 0
  primitive 的预制组合（CustomerProfileCard ≈ 多个 MetricCard；ProductFitTable ≈
  DataTable + ChoiceList + interaction）。
- 把这些组合写成 React 组件意味着：每加一个新业务都要写新组件、改后端 adapter、
  扩 contract schema、写新测试，扩张代价 O(N) 业务数。
- 把这些组合写成 Skill 资产意味着：扩张代价是 O(1) Skill 文档，模型自己用现有
  primitive 表达，不动代码。
- 用户日常 AI 生成 UI 场景（"帮我把这周日程画成柱状图并让我点重点时段"）
  天然没有专用 React 组件，必须靠 Skill + Layer 0 primitive 完成。RM 工作流
  和这种日常场景不应该有结构性差异。

影响：

- **目标态**：`frontend/src/rm/surfaces/` 整体删除；contract 的 `surfaces` 字段
  和后端 `map_surface_to_a2ui_messages` 路径整体移除；RM 完全用 `ui.blocks` 表达。
- **过渡态（本轮重构）**：保留现有 RM React 组件以避免破坏 7.7 收口和已有测试。
  在 `adapter.py` 中明确把 RM 分支标记为 `transitional`，不拆 `rm_surfaces.py`，
  不试图为日常场景创造新 React 组件。
- **单独迁移 issue**（暂记 "Skill-driven Layer 1 migration"）：
  - 在 `ChoiceList` 等 primitive 上加 `on_confirm` interaction wiring，让 Layer 0
    自带结构化输入回传能力（pending_interaction.resolve）。
  - 写出 RM Skill 资产，验证 RM workflow 能完全用 Layer 0 primitive 表达。
  - 删 `frontend/src/rm/surfaces/` 与对应后端分支。
  - 这件事不阻塞 Issue 7.7 收口，也不阻塞 Issue 8 启动。
- 任何新业务 consumer（CFA、投资、日常 UI 生成）的第一反应都应该是
  "写 Skill"，而不是 "写新 React 组件 / 加新 contract 字段"。如果发现确实
  无法用现有 catalog 表达，再独立提案扩充 Layer 0 catalog。

