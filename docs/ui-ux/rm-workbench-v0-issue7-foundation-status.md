# RM Workbench V0 Issue 7 Foundation Status

路径：`docs/ui-ux/rm-workbench-v0-issue7-foundation-status.md`
状态：`active / planning input`
更新时间：`2026-05-08`
入口：`docs/ui-ux/rm-workbench-v0-index.md`

---

## 0. 一句话结论

Issue 7 到目前为止，已经把 **协议、bridge、runtime alignment、generic renderer catalog、真实 stream 可见性问题** 基本摸清。

但有一个非常重要的产品化结论现在已经明确：

```text
RM Workbench React renderer / mock path 已经成立
!=
当前主 WebUI chat 前端已经适合作为第一条真实 RM workflow 的正式宿主
```

在进入 Issue 8 之前，除了 Issue 7.6 generic catalog，本项目还需要补一层：

```text
React frontend foundation for the real WebUI path
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

### 4.1 先做 Issue 7.6

继续保持已定方向：

```text
Generic A2UI Renderer Catalog
```

因为它确认的是：

- 同一条 `rm_workbench_emit_contract` 链路能承载 generic UI blocks
- React renderer catalog 的边界清晰

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
  -> Generic A2UI Renderer Catalog

Issue 7.7（建议新增）
  -> React Frontend Foundation for real WebUI path

Issue 8
  -> First Real Pre-Meeting Brief Workflow
```
