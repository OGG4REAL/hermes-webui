# RM Agent-Native Workbench V0：技术选型骨架

> 路径：`docs/ui-ux/rm-workbench-v0-technical-skeleton.md`
> 状态：`active / V0 technical boundary`
> 目的：先固定 RM Workbench V0 的技术选型、协议边界和待审核决策点；具体 Skill、mock 数据和 UI 组件细节放到后续文档。
> V0 入口：`docs/ui-ux/rm-workbench-v0-index.md`

---

## 0. 结论先行

V0 不应先自研 Hermes 私有 UI 协议。技术路线应是：

```text
Hermes Agent Runtime
        ↓
hermes-webui backend as source of truth
        ↓
AG-UI-compatible adapter
        ↓
A2UI fixed catalog / surfaces
        ↓
React workbench host
```

CopilotKit 不是简单“用 / 不用”的问题，而是接入深度问题：

- 可以局部使用它的 React、AG-UI、A2UI integration 能力
- 暂不默认让 CopilotKit runtime 接管 Hermes runtime
- 等 adapter 原型跑通后，再评估是否加深到 CopilotRuntime 主导

一句话：

> Hermes 管 agent runtime，hermes-webui 管后端事实源，AG-UI 管双向事件轨道，A2UI 管后到前 UI surface，React 管 workbench host，CopilotKit 作为可加深接入的成熟前端/runtime 能力来源。

---

## 1. 已确定的架构事实

### 1.1 Hermes Agent 是 runtime

Hermes Agent 继续负责：

- conversation loop
- tools
- skills
- memory
- approval / clarify
- session-aware agent execution

V0 不为了 UI 先大改 Hermes agent loop。

### 1.2 `hermes-webui` 是后端事实源

`hermes-webui` 保留为正式 workbench 后端，因为它已经有：

- session
- SSE stream
- tool lifecycle
- approval
- clarify
- workspace / upload
- persistence

V0 的后端改造重点不是重写 runtime，而是在 `hermes-webui` 上加一层 adapter。

### 1.3 React 是新的 workbench host

vanilla JS 不适合继续承载复杂双向状态。

React workbench 负责：

- chat surface
- workspace panels
- A2UI surface renderer
- AG-UI / CopilotKit client integration
- local state store
- user interaction dispatcher

### 1.4 业务 V0 只是压力测试

V0 业务场景暂定：

**Pre-Meeting Brief with Product Fit**

它用来压测架构，不是现在就完整实现 RM 售前、售中、售后。

该场景需要同时覆盖：

- 客户画像展示
- 产品/组合推荐表
- 收益风险图表
- RM 勾选/确认/补充
- Agent 基于 UI 操作继续推理
- Memory proposal
- report / brief artifact

---

## 2. 核心待决策点

目前真正需要审核的是 CopilotKit 接入深度。

### 2.1 路线 A：Hermes runtime 主导 + AG-UI/A2UI adapter

```text
Hermes Agent Runtime
        ↓
hermes-webui backend
        ↓
AG-UI adapter + A2UI surfaces
        ↓
React workbench, partially using CopilotKit
```

特点：

- Hermes runtime 不动
- `hermes-webui` 继续是后端事实源
- approval / clarify / session / memory 先保留 Hermes 语义
- 后端输出 AG-UI-compatible events
- 后到前 UI render 用 A2UI fixed catalog
- 前端局部使用 CopilotKit 能力

收益：

- 保住 Hermes 现有资产
- adapter 比全 runtime 替换更可控
- 可以逐步验证 AG-UI / A2UI 的适配质量

代价：

- adapter 要自己维护
- CopilotKit 的高级 shared state / runtime 能力可能吃不满
- Hermes 特有语义到 AG-UI 的映射要认真设计

### 2.2 路线 B：CopilotKit runtime 主导 + Hermes adapter

```text
React workbench + CopilotKit runtime/client
        ↓
CopilotKit / AG-UI / A2UI protocol
        ↓
Hermes runtime adapter
        ↓
Hermes Agent Runtime
```

特点：

- 前端更完整进入 CopilotKit 范式
- AG-UI / A2UI / frontend actions / shared state 更系统
- Hermes runtime 被包装成 CopilotKit/AG-UI agent source

收益：

- 更充分利用成熟框架
- 前端 agent-native 能力可能更完整
- 后续与 AG-UI / A2UI 生态对齐更自然

代价：

- adapter 更厚
- Hermes approval / clarify / session / memory 需要重新承载到 CopilotKit runtime 语义里
- 如果 CopilotKit runtime 假设与 Hermes agent loop 冲突，调试面会更大

### 2.3 当前建议

当前建议先走路线 A。

原因：

- Hermes runtime 与 `hermes-webui` 后端已经能跑真实 agent 工作流
- 先做 AG-UI/A2UI adapter 可以验证成熟协议是否足够承载 Hermes
- 不过早把 runtime 主导权交给 CopilotKit
- 若 adapter 原型证明 CopilotKit runtime 能显著减少复杂度，再升级到路线 B

---

## 3. 后到前：A2UI surface

后到前指：

```text
Agent / Skill / backend 产出结构化结果
        ↓
adapter 包成 A2UI surface operations
        ↓
AG-UI stream 承载
        ↓
React workbench 渲染
```

A2UI 解决的是：

- backend 如何描述 UI
- frontend 如何知道渲染哪个 component
- UI surface 如何创建、更新、替换
- data model 如何传给前端 renderer

V0 采用 fixed catalog，不做任意动态 UI。

Catalog 分两层：

1. **通用 UI primitives**
   这些不是 RM 语义，属于通用渲染能力，例如文本、按钮、表格、表单、折线图、柱状图、饼图、卡片、布局容器。能用 A2UI Basic Catalog 或我们扩展的 common catalog 承载。
2. **RM semantic surfaces**
   这些才是 RM 业务语义组件，例如客户画像、产品适配、记忆变更确认、brief 导出。

所以常规图表、表格、按钮、输入框不计入 RM semantic catalog 数量。它们是基础组件能力，RM 组件可以组合这些 primitives。

第一批 RM semantic catalog 候选：

- `CustomerProfileCard`
- `ProfileGapTable`
- `ProductFitTable`
- `PerformanceChart`
- `RebalanceTimeline`
- `TalkTrackCard`
- `MemoryDiffCard`
- `BriefExportPanel`
- `SkillLauncher`

V0 后到前的重点不是组件多，而是先验证：

```text
Skill structured output
        ↓
A2UI surface
        ↓
React renderer
```

---

## 4. 前到后：AG-UI interaction + Hermes pending interaction

前到后指：

```text
RM 在 UI 上选择、填写、确认、审批
        ↓
frontend 发 AG-UI-compatible event / response
        ↓
adapter 校验并转换
        ↓
Hermes agent 继续推理或更新状态
```

这里分两类。

### 4.1 Non-blocking event

Agent 不暂停，只记录或同步状态。

例子：

- RM 展开某产品详情
- RM 切换收益图时间区间
- RM 调整表格排序
- RM 临时选中某几行

这些可以映射成 AG-UI state delta / custom event。

### 4.2 Blocking interaction

Agent 暂停，等待 RM 完成结构化输入。

例子：

- 从候选产品中选择 1-3 个
- 确认画像缺口
- 补充 KYC 关键字段
- 确认是否写入 memory

这类交互类似 Hermes `clarify` 的泛化版：

```text
agent/workflow requests input
        ↓
backend creates pending interaction
        ↓
frontend renders A2UI surface
        ↓
RM submits response
        ↓
adapter resolves pending interaction
        ↓
Hermes agent resumes
```

---

## 5. Approval / Clarify 的真实作用

Hermes 现有 `approval` / `clarify` 不是完整 UI 协议。

它们的价值是证明 Hermes 已经具备一部分 **human-in-the-loop runtime 基建**。

### 5.1 Approval

```text
agent wants risky action
        ↓
backend creates pending approval
        ↓
frontend shows approval card
        ↓
user approves / denies
        ↓
backend resolves
        ↓
agent continues / aborts
```

### 5.2 Clarify

```text
agent lacks required information
        ↓
backend creates pending clarify
        ↓
frontend shows question / choices / input
        ↓
user submits answer
        ↓
backend resolves
        ↓
agent continues with answer
```

### 5.3 RM UI interaction

RM 结构化 UI 交互是第三类，不应该硬塞进 approval 或 clarify：

```text
agent/workflow needs structured UI input
        ↓
backend creates pending interaction
        ↓
frontend renders ProductFitTable / KYC form / MemoryDiffCard
        ↓
RM selects / edits / confirms
        ↓
adapter resolves interaction
        ↓
agent continues
```

结论：

- approval = 高风险动作确认
- clarify = 信息不足时的问答
- pending interaction = 结构化 UI 输入

三者底层都需要 pending request + response + resume，但上层语义要分开。

---

## 6. Skill / Surface / Action / Tool 边界

V0 要避免把所有东西都做成 tool。

### 6.1 Skill

Skill 负责 RM 业务工作流。

例：

- `pre_meeting_brief`
- `profile_gap_analysis`
- `product_fit_analysis`
- `talk_track_generation`
- `memory_update_proposal`
- `brief_export`

Skill 输出不应只有自然语言，应输出：

- text summary
- A2UI surfaces
- pending interactions
- memory proposals
- report artifacts
- next actions

这里的关键点：

> Adapter 只做结构化 contract 到 AG-UI/A2UI 的协议映射，不负责从自然语言里猜 UI 和 action。

这与 `ai_sandbox` 里的“计算 / 展示分离”逻辑一致：

```text
Skill produces structured result
        ↓
presentation layer renders UI
```

区别是：

- `ai_sandbox` 里更像由 Agent 调用 `render_chart` / `render_table` 这类 UI tool
- RM Workbench V0 里由 RM Skill 直接返回结构化 output contract
- `hermes-webui` adapter 读取 contract，映射成 AG-UI events 和 A2UI surfaces

V0 不要求改 Hermes Agent runtime，但要求 RM Skill 从第一天就按 contract 输出结构化 JSON。

### 6.2 Surface

Surface 负责展示。

例：

- `CustomerProfileCard`
- `ProductFitTable`
- `PerformanceChart`

Surface 不是 tool，也不直接做业务推理。

### 6.3 Action

Action 负责 RM 在 surface 上做的动作。

例：

- `select_products`
- `confirm_profile_gaps`
- `edit_constraints`
- `approve_memory_update`
- `generate_brief`

Action 通过 AG-UI-compatible event / response 回到 adapter。

### 6.4 Tool

Tool 留给 agent 主动调用的能力。

例：

- 查询客户画像
- 读取产品池
- 计算产品适配评分
- 生成报告 artifact
- 写入确认后的 memory

不要把每个 UI button 都做成 backend tool。

---

## 7. Memory 与风控边界

金融场景不能让 agent 静默写长期记忆。

V0 采用 proposal-first：

```text
agent proposes memory change
        ↓
frontend renders MemoryDiffCard
        ↓
RM approves / rejects / edits
        ↓
backend persists approved change
```

Memory proposal 至少要包含：

- target type
- target id
- old value
- new value
- evidence
- confidence
- rationale
- source

产品推荐也要有责任边界：

```text
hard filter
        ↓
scoring
        ↓
LLM explanation
        ↓
RM confirmation
```

V0 不表达成“AI 替客户做投资决策”，而是表达成“AI 辅助 RM 准备沟通和解释”。

---

## 8. V0 不做什么

V0 明确不做：

- 不接真实银行系统
- 不接真实客户隐私数据
- 不一次做完整售前、售中、售后平台
- 不上动态任意 UI schema
- 不把 A2UI 当完整双向协议
- 不把所有按钮都做成 tool
- 不让 agent 静默写 memory
- 不默认让 CopilotKit runtime 接管 Hermes

---

## 9. 审核点

下面这些点已经按当前讨论记录为 V0 决策。

### 审核点 A：CopilotKit 接入路线

决策：先走路线 A。

```text
Hermes runtime 主导 + AG-UI/A2UI adapter + 局部 CopilotKit
```

备选：路线 B。

```text
CopilotKit runtime 主导 + Hermes adapter
```

状态：已确认。

### 审核点 B：A2UI catalog 范围

决策：V0 先只做 5 个核心 RM semantic surface：

- `CustomerProfileCard`
- `ProductFitTable`
- `PerformanceChart`
- `MemoryDiffCard`
- `BriefExportPanel`

延后：

- `ProfileGapTable`
- `RebalanceTimeline`
- `TalkTrackCard`
- `SkillLauncher`

补充：

- 通用图表、表格、表单、按钮、布局不算在这 5 个 RM semantic surface 内。
- 这些应作为 common/basic catalog primitives 处理。

状态：已确认。

### 审核点 C：Pending interaction 语义

决策：新增独立 pending interaction，不把结构化 UI 输入塞进 clarify。

```text
approval = 高风险确认
clarify = 问答补充信息
pending interaction = 结构化 UI 输入
```

状态：已确认。

### 审核点 D：下一份文档

决策：下一份写：

```text
rm-workbench-v0-protocol-examples.md
```

内容只放 examples：

- skill output example
- A2UI surface example
- AG-UI event mapping example
- non-blocking event example
- blocking pending interaction example
- memory proposal example

状态：由 Codex 决定，先写 protocol examples，再写 implementation plan。

### 审核点 E：RM Skill output contract

决策：RM Skill 必须输出结构化 contract，adapter 不做自然语言语义猜测。

```text
Hermes runtime 不动
RM Skill 输出结构化 JSON
adapter 只做 AG-UI/A2UI 映射
```

状态：已确认。

---

## 10. 当前可开工状态

这份文档本身还不是 implementation plan。

它可以支持下一步开始写：

- protocol examples
- adapter spike plan
- React host scaffold plan

但不建议直接进入编码实现。

进入实现前至少还需要：

1. 审核上面的 A-D 决策点
2. 写 `rm-workbench-v0-protocol-examples.md`
3. 再写 implementation plan
