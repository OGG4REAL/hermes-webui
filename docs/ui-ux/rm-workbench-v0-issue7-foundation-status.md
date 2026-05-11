# Structured UI Subsystem Issue 7 Foundation Status (formerly "RM Workbench V0 Issue 7 Foundation Status")

路径：`docs/ui-ux/rm-workbench-v0-issue7-foundation-status.md`
状态：`active / acceptance closeout input (realigned 2026-05-09)`
更新时间：`2026-05-09`
入口：`docs/ui-ux/rm-workbench-v0-index.md`
受约束于：`docs/ui-ux/rm-workbench-v0-adr.md`（特别是 ADR-009 ~ ADR-013）

---

## -1. 2026-05-09 方向校准（必读）

本文档下面 § 0 ~ § 5 的原文写于 Issue 7.7（MYM-38）启动前，此后 Codex 在 5 轮迭代中
均无法通过真实 WebUI smoke。最终从服务器日志找到的根因不是任何一行代码，而是
**早期 ADR 没有把 "AI 生成 UI 是 Hermes 工作台的原子能力" 和 "RM Workbench 是它的
第一个 consumer" 清晰分层**。

### Codex 5 轮迭代记录（MYM-38）

| 轮次 | Codex 修复 | 暴露的下一层问题 |
|---|---|---|
| 1 | 加 contract schema 内层 properties（修 schema 剥参数） | validator 只接受 `rm.pre_meeting_brief` |
| 2 | validator 拆双路接受 `rm_workbench` kind | adapter 在 generic 路径上 KeyError |
| 3 | adapter 用 `.get(..., [])` 兼容 generic | `_validate_ui_blocks` 块级 schema 严格 |
| 4 | embedded mode 加 error banner 显示 RUN_ERROR | BarChart 缺 series 仍直接 RUN_ERROR，前端零渲染 |
| 5 | (未跑完即被叫停) | — |

每轮只能修症状，下一轮在新位置暴露同类问题。证据集中点：
[`~/.hermes/logs/errors.log`](~/.hermes/logs/errors.log) 的 `2026-05-09 15:55:08` 记录显示
`BarChart 'chart_1' props.series must be a non-empty array`——这是 validator 严格度问题，
不是模型构造能力问题。

### 真实根因

- **Layer 0 validator 把"渲染要求"和"业务合规要求"等价**：缺 `series` 抛 ValueError，
  整轮对话视觉一片空白。这违背了"AI 生成 UI 应该宽容兜底"的产品直觉。
- **Layer 0 contract 把 `kind` 当业务路由器**（`ALLOWED_KINDS = {"rm_workbench", "rm.pre_meeting_brief"}`），
  必填 `run_id`/`thread_id`/`skill`——所有这些把通用底座绑死在 RM 命名空间。
- **Layer 0 命名层全部 RM 化**：tool 名、SSE event、CUSTOM 名、前端 host、DOM、CSS。
- **coding-boundary 文档把 RM 化硬约束作为"不许 relitigate 的 upstream decision"**，
  Codex 每轮被边界绑死，只能修代码不能动 framing。

### 校准动作（2026-05-09）

- 新增 ADR-009 ~ ADR-013（原子能力定位 / best-effort 渲染 / 信封最小化 / `emit_ui` 重命名 /
  Skill-driven Layer 1 迁移）
- 修订 ADR-007 验收口径：Issue 7.7 退出标准从"完整 RM brief 渲染"降级为
  "Layer 0 渲染至少 1 个 generic primitive"
- 修订 coding-boundary § 4.2 / § 0.1（删 RM 化硬约束、加 ADR 优先锚点）
- roadmap 重排 Issue 序列：Issue 8 后插入 Issue 9（Skill-driven Layer 1 migration）
  和 Issue 10（命名整改）
- 决定**停止把 7.7 交给 Codex 做**，由人类直接在 VSCode 里完成重构，避免 agent 在
  窄边界内反复修症状

### 给读者的指引

- 下面 § 0 ~ § 5 是 2026-05-09 之前的快照，**作为历史保留**，能帮助理解当时的思考。
- 但具体的 acceptance criteria、validator 严格度、tool 命名、Layer 1 处理方式，
  **以 ADR / coding-boundary / roadmap 当前版本为准**。
- 如果你是后续 agent 准备做 7.7 收口或 Issue 8 / 9 / 10：直接跳到 ADR-009 ~ ADR-013 和
  roadmap § 6，不要从下面 § 0 倒推 acceptance。

---

## 0. 一句话结论

> （以下为 2026-05-09 之前的原文，保留作历史。结论本身仍部分成立，
> 但具体下一步由上面 § -1 的校准动作覆盖。）

Issue 7 到目前为止，已经把 **协议、bridge、runtime alignment、generic renderer catalog、真实 stream 可见性问题** 基本摸清；Issue 7.6 现在可以按已验收能力收口。

但有一个非常重要的产品化结论现在已经明确：

```text
RM Workbench React renderer / mock path 已经成立
!=
当前主 WebUI chat 前端已经适合作为第一条真实 RM workflow 的正式宿主
```

在进入 Issue 8 之前，当前下一步已经收敛成：

```text
Issue 7.7: React frontend foundation for the real WebUI path
```

否则后续真实 RM Skill workflow 会把：

- tool call 稳定性
- SSE bridge
- generic UI rendering
- 主前端状态管理
- pending interaction / resume UX

混在一起验，工程上会越修越歪。

---

## 1. 截止当前已经确认的“成立部分”

### 1.1 后端 / 协议骨架已成立

已成立的链路：

```text
Hermes Agent runtime
  -> hermes-webui backend
  -> /api/chat/stream 现有 top-level SSE
  -> event: rm_workbench
  -> kind = agui_events
  -> CUSTOM name = a2ui.surface.messages
  -> pending interaction resolve
```

这部分由 `MYM-24` 到 `MYM-34` 打通，当前结论稳定：

- 不改 `/api/chat/stream` top-level protocol
- 不引入 CopilotKit runtime takeover
- `rm_workbench_emit_contract` 继续是唯一结构化 UI emit tool
- Memory 继续 proposal-first，不自动写入

### 1.2 Hermes runtime alignment 已成立

`MYM-34` 之后已经确认：

- WebUI / runtime 真实加载路径应对齐到 `~/hermes-agent`
- `~/.hermes/hermes-agent/venv` 作为 runtime venv
- editable install 继续指向 `~/hermes-agent`

补充结论：

- 不应再把“工具是否可见”与“双目录漂移”混为一谈
- 后续所有 runtime/tool smoke 必须先确认当前 WebUI 进程实际加载的 `tools` / `toolsets` 路径

### 1.3 React generic renderer catalog 已成立

`MYM-35` 证明了下面这条链路在 React workbench host / mock path 中可通：

```text
rm_workbench SSE
  -> AG-UI CUSTOM
  -> A2UI surface messages
  -> React generic renderer
```

已真实渲染验证的 primitives：

- `MetricCard`
- `DataTable`
- `LineChart`
- `BarChart`
- `PieChart`
- `ChoiceList`

同时仍保持：

- `CustomerProfileCard`
- `ProductFitTable`
- `BriefExportPanel`

并验证了：

- `ProductFitTable` 选择后仍可 resolve pending interaction
- `MYM-35` 的截图与 SSE 证据仍有效，可继续作为 7.6 closeout 证据：
  - `.playwright-cli/mym35-generic-a2ui-catalog.png`
  - `.playwright-cli/mym35-productfit-resolved.png`
- 当前树在 2026-05-09 再次通过：
  - `tests/test_rm_workbench_adapter.py tests/test_rm_workbench_mock_stream.py`
  - `tests/test_rm_workbench_real_stream_bridge.py`
  - `frontend/npm run build`

---

## 2. 截止当前已经确认的“不成立部分”

### 2.1 “主 WebUI chat 已经能自然一句话生 UI” 这个结论不成立

当前不成立的不是 React renderer，而是下面这件事：

```text
用户在主 WebUI chat 中给自然语言
  -> Hermes 稳定产生正确 rm_workbench contract
  -> 主前端自然显示图表 / 表格 / 选择控件
```

它不成立的原因不是单点，而是两类问题叠加：

1. **模型 / provider 对深嵌套 object 参数不稳定**
2. **当前主 WebUI 前端不是 React workbench host，本质上仍是旧前端壳 + 渐进 bridge**

### 2.2 `MYM-36` 结论：没有本地 schema stripping bug

`MYM-36` 的最终结论必须作为后续 planning 的硬约束：

- `rm_workbench_emit_contract` 的 registry schema 在本地没有被剥成空参数
- `AIAgent.tools` 中 `contract` 参数存在
- provider request 前的 payload 中 `tools.parameters.properties.contract` 存在
- Hermes 自报的

```text
type rm_workbench_emit_contract = () => any
```

不是 ground truth

也就是说：

```text
当前问题不是“本地工具 schema 传丢了”
而是“模型/provider 对 opaque nested object 参数表现不稳定”
```

### 2.3 主前端宿主问题现在已经暴露出来

当前已经不能再把 `frontend/` 里的 React workbench host 当作“只是一个 smoke app”。

因为它事实上承担了：

- A2UI/generic renderer
- structured UI state upsert
- RM semantic surface rendering
- pending interaction UI

而你真正日常使用的主 WebUI 前端，仍然不是这个 React host。

所以当前架构状态更准确的描述是：

```text
React RM Workbench host 已经证明协议和 renderer 可行
主 WebUI 前端还没有完成对这套能力的正式接管
```

---

## 3. 为什么 Issue 8 前必须补 React 前端基建

### 3.1 如果不补，会把三个问题混在一起

如果现在直接进入第一条真实 RM workflow，Issue 8 会同时验：

- RM Skill 是否能在正确时机 emit contract
- 模型是否能稳定构造 structured tool args
- 主前端是否能承接 structured UI 的增量状态

这会让失败原因变得不可分：

```text
失败了
  到底是 skill 不对
  还是 tool 参数不稳
  还是前端宿主不对
  还是 interaction state 不对
```

### 3.2 React 化不是“好看一点”，而是宿主层必须换范式

RM Workbench 要承载的是：

- surface 生命周期
- 多块 UI 增量 upsert
- pending interaction / cancel / resume
- chart/table/choice 等 catalog primitives
- 后续真实 workflow 状态流转

这些东西长期不适合继续堆在当前主前端的命令式脚本层里。

结论：

```text
RM Workbench 这条线，React 化不是可选优化，而是基建的一部分
```

### 3.3 但这不等于立刻全站重写

当前更合理的工程边界是：

1. 先把 RM Workbench / structured UI 区域 React 化
2. 让主 chat 页面把这块 mount 成正式宿主
3. 再决定整个 WebUI 是否完全迁到 React

因此这里需要的不是“完整 React 重构 Issue”，而是一个 **Issue 7.x frontend foundation slice**。

---

## 4. 建议给编排器的下一步顺序

### 4.1 Issue 7.6 已可以关闭

当前 closeout 结论：

```text
Generic A2UI Renderer Catalog 已在 React workbench host / mock path 成立，并且不应再扩成新的 runtime 或 frontend host 实现 issue。
```

本次收口保留的验收口径：

- 同一条 `rm_workbench_emit_contract` 链路能承载 generic UI blocks
- React renderer catalog 的边界清晰
- 主 WebUI chat 还不是正式 structured-UI 宿主，这件事留给 Issue 7.7

### 4.2 然后插入新的 Issue 7.x：React Frontend Foundation

建议名称：

```text
RM Workbench V0 React Frontend Foundation
```

目标不是重做全部 WebUI，而是完成下面三件事：

1. 明确 **React workbench host** 才是 RM structured UI 的正式宿主
2. 明确主 WebUI chat 如何把 `rm_workbench` SSE / A2UI state 挂进 React 区域
3. 把真实 workflow 前必需的 state/render/interaction 基座稳定下来

建议验收：

- 主 WebUI 中能挂载 React RM Workbench 区域
- 真实 `rm_workbench` SSE event 能驱动该区域更新
- generic primitives 与 `ProductFitTable` 在主路径中都可见
- `pending/resolve` 在主路径中仍可闭环

### 4.3 再进入 Issue 8

这时再做：

```text
First Real Pre-Meeting Brief Workflow
```

才会比较干净地只验证：

- RM Skill/workflow 逻辑
- tool emit 时机
- 用户交互闭环

而不是顺手再 debug 主前端宿主。

Issue 8 的用户侧进入条件应该写得更直白：

```text
只有当用户在真实 WebUI chat 里和 Hermes 对话时，Hermes 能直接在对话体验里渲染图表 / 表格 / 选择 UI，Issue 8 才能开始。
```

---

## 5. 当前对编排器最重要的约束

### 5.1 不要再把 `() => any` 当本地 schema 断点

`MYM-36` 已经说明：

- wire payload 中 schema 在
- 本地没有 schema stripping bug

后续如果继续追“为什么模型嘴里说它是无参工具”，那是另一类问题：

- prompt / tool description
- parameter shape
- provider/model 行为

不是本地 tool registration 问题。

### 5.2 不要把 Issue 8 设计成“前端、runtime、workflow 一锅炖”

Issue 8 前最好先把 React frontend foundation 单独切出来。

否则你会得到一个非常难 review 的 issue：

- 改了 skill
- 改了 tool contract
- 改了 bridge
- 改了前端宿主
- 最后还要解释为什么图没出来

### 5.3 不要把 generic renderer 与主前端宿主混成同一个概念

当前已经确认：

- generic renderer 可通
- 主前端宿主未完成

这两件事必须在规划里明确分开。

---

## 6. 当前阶段性结论

```text
Issue 7 到现在，协议/bridge/runtime/generic renderer 基本成立。
但在进入第一条真实 RM workflow 前，还必须补一层 React frontend foundation。
```

给编排器的推荐顺序：

```text
Issue 7.6
  -> accepted / closed: Generic A2UI Renderer Catalog

Issue 7.7（建议新增）
  -> React Frontend Foundation for real WebUI path

Issue 8
  -> First Real Pre-Meeting Brief Workflow
```
