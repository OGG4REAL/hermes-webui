# RM Workbench V0 ADR

路径：`docs/ui-ux/rm-workbench-v0-adr.md`
状态：`active / architectural decision record`
更新时间：`2026-05-09`
入口：`docs/ui-ux/rm-workbench-v0-index.md`

---

## 0. 这份文档负责什么

这份文档维护 RM Workbench V0 的技术决策。

每条 ADR 只记录：

- decision
- status
- context
- consequences

当前架构事实放在 `rm-workbench-v0-architecture.md`。

执行顺序放在 `rm-workbench-v0-roadmap.md`。

过程材料、spike、review、issue status 不进入这份文档，除非它们改变了一个技术决策。

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

## ADR-003: Use one emit contract tool, not many render tools

状态：`accepted`

决策：

```text
V0 使用 rm_workbench_emit_contract 作为唯一结构化 UI emit tool。
不新增 render_table / render_chart / render_form / render_card 等工具。
```

背景：

- UI 表达应是 declarative contract，而不是 toolset 中一堆具体 UI function。
- 多工具会让模型选择空间和 tool registry 膨胀。
- 既有 bridge 已经围绕 `rm_workbench_emit_contract` 验证。

影响：

- generic UI primitives 和 RM semantic surfaces 都进入同一个 contract。
- 中期可新增 `emit_ui_contract`，让 `rm_workbench_emit_contract` 成为 RM wrapper 或兼容 alias。

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

状态：`accepted`

决策：

```text
通用 UI primitives 是底座，RM semantic surfaces 是业务层。
```

背景：

- V0 不只是 RM 专属 UI 展示能力。
- 表格、图表、指标卡、选择列表是通用 Agent UI 能力。
- RM surfaces 可以组合 generic primitives，并定义业务交互。

影响：

- Issue 7.6 先证明 generic renderer catalog。
- Issue 8 只验证第一条真实 RM workflow。

---

## ADR-007: React structured-UI host must enter the real WebUI path before Issue 8

状态：`accepted`

决策：

```text
在第一条真实 RM workflow 前，必须先把 React RM workbench host 接进主 WebUI chat path。
```

背景：

- React renderer / mock path 已经证明可行。
- 但用户日常使用的是主 WebUI chat，而不是独立 smoke app。
- 如果直接进入真实 workflow，skill logic、tool args、SSE bridge、frontend host state 会混在一起验。

影响：

- Issue 7.7 先做 React frontend foundation。
- Issue 8 只在主路径能真实渲染 structured UI 后开始。

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

