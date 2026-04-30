# Hermes Agent-Native Workbench：双向 UI 能力与技术选型平铺文档

> 路径：`docs/ui-ux/agent-native-workbench-tech-options.md`
> 状态：`historical / broad options memo / superseded for V0 execution`
> 目的：把目标、约束、能力模型、协议层、技术选型、候选框架与路线分支**平铺摊开**，用于后续深度讨论
> 本文原则：**先信息平铺，不先站队，不抢结论**
> V0 入口：`docs/ui-ux/rm-workbench-v0-index.md`

> 注意：本文是早期信息平铺文档，不是当前 V0 implementation source。工程执行请从 `rm-workbench-v0-index.md` 开始。

---

## 0. 本文要解决什么

这份文档不直接回答“该选哪条路线”，而是先把问题拆清楚：

1. **我们到底要实现什么能力**
2. **这些能力对前端、后端、协议层分别提出了什么要求**
3. **现有代码基座分别提供了什么 / 缺什么**
4. **CopilotKit、A2UI、AG-UI、MCP Apps、纯自研协议各自能解决哪一层问题**
5. **有哪些可组合的技术路线**
6. **每条路线的收益、代价、锁定风险、迁移路径分别是什么**

重点不是“哪个框架火”，而是：

> **为了让 Hermes 演进成一个前后端双向影响 UI 的 agent-native workbench，哪些能力必须自己掌握，哪些能力适合借成熟框架，哪些能力借了反而会形成约束。**

---

## 1. 目标能力模型：先讲功能，不讲框架

当前讨论的真实目标，不是“聊天里能渲染几张图”，而是一个更强的能力模型。

### 1.1 后端 → 前端

Agent / backend 需要能够：

- 渲染文本回复
- 渲染结构化 UI：卡片、表格、图表、表单、面板、布局块
- 更新已有 UI，而不只是追加新消息
- 控制某个工作区、面板或页面局部内容
- 请求用户在某个 UI 组件里完成交互
- 根据用户操作结果继续推理

### 1.2 前端 → 后端

前端 / user-facing app 需要能够把状态和交互反向喂给 agent，例如：

- 用户点击了哪个卡片 / 行 / tab
- 当前过滤条件、排序、时间区间是什么
- 图表是否 zoom / brush / drill-down
- 当前正在看的客户是谁
- 哪个 panel 打开 / 关闭
- 前端局部状态是否应成为 agent 的上下文

### 1.3 持续闭环

理想闭环是：

```text
Agent 生成 UI
→ 用户在 UI 上操作
→ 前端把事件 / 状态回传给 Agent
→ Agent 基于新上下文继续推理
→ Agent 再更新 UI
→ 用户继续操作
```

这比单向聊天复杂很多，因为它要求系统支持：

- 流式输出
- 结构化渲染
- 交互回传
- 状态同步
- 局部更新
- 阻塞式等待与非阻塞式观察两种交互模式并存

---

## 2. 要实现这件事，系统最少需要哪几层

把问题拆开，至少有 4 层。

### 2.1 Runtime 层

负责 agent 本身的运行：
- conversation loop
- tool calls
- approval / clarify
- memory
- session
- persistence
- streaming callback

Hermes 现有资产主要在这一层。

### 2.2 Backend API / Event Layer

负责把 runtime 的行为暴露给前端：
- HTTP API
- SSE / websocket / polling
- session endpoints
- upload / workspace / logs / history
- interaction response endpoints

`hermes-webui` 的 Python 后端主要在这一层。

### 2.3 UI Protocol Layer

这是当前最关键、也最容易被忽视的一层。

它回答的是：

- backend 向 frontend 发什么类型的 UI 事件
- frontend 向 backend 回什么类型的 UI 事件
- 一个 UI block 如何被标识、更新、销毁
- 一次交互是阻塞式还是非阻塞式
- 哪些状态属于 message，哪些属于 page，哪些属于 shared state

这层可以：
- 自研
- 部分借协议（如 AG-UI / A2UI）
- 完整借上层框架（如 CopilotKit 某些 runtime / conventions）

### 2.4 Frontend Host / Renderer Layer

这是用户实际看到的界面：
- React / vanilla JS / Web Components 等宿主
- message renderer
- workspace / panels
- charts / tables / forms
- client-side state store
- hooks / reducers / event dispatcher

---

## 3. 当前本地三套代码基座分别在哪些层强，哪些层弱

## 3.1 `~/hermes-webui`

### 强项

- 后端 API 与 Hermes runtime 语义深度贴合
- 已有聊天启动、流式输出、tool lifecycle
- 已有 approval / clarify / session / memory / cron / gateway 等真实能力
- SSE 架构已存在
- 是最接近 Hermes 正式产品语义的壳

### 弱项

- 前端是 static HTML + 原生 JS
- 消息流、approval、clarify、tool_complete、stream_end 等逻辑高度命令式耦合
- 不利于表达复杂长期共享状态
- 双向 UI 协议目前没有被显式建模，只是靠局部事件拼接

### 含义

`hermes-webui` 强在：
- runtime 对接
- backend 事件与 API

弱在：
- 前端宿主
- 客户端状态组织
- 可持续扩展的 UI protocol 抽象

---

## 3.2 `~/hermes-agent/web`

### 强项

- 已经是 React + TS + Vite + Tailwind 体系
- 工程化程度比 `hermes-webui/static` 高
- 适合承载较现代的前端状态模型

### 弱项

- 当前定位更像管理后台 / 控制台
- 不是为“理财经理工作台 + agent-native interaction”设计的
- 现有页面与业务交互模型不等于目标工作台

### 含义

`hermes-agent/web` 更像一个：
- React 工程模板 / 设计系统 / 管理台母体

但不天然等于：
- 你的目标前台产品

---

## 3.3 `~/ai_sandbox/frontend`

### 强项

- 已经验证了 React 工作台形态
- 有 chart / table / workspace / trajectory / eval 等组件雏形
- 已安装 CopilotKit 相关依赖
- 证明了“GenUI + workspace + panel”这类体验可以做出来

### 弱项

- 它服务的是 sandbox / experiment 语境
- 后端 API 契约与 Hermes 正式语义不完全一致
- 当前主聊天链路仍是手写 fetch + SSE
- 它是很好的参考实现，但不是天然正式前台

### 含义

`ai_sandbox/frontend` 更适合作为：
- 组件来源
- 交互原型来源
- 对比样本

而不是直接作为结论。

---

## 4. 讨论技术选型前，先把“协议问题”讲明白

如果目标只是“聊天里插一张图”，你可以不太关心协议层。

但如果目标是“前后端双向影响 UI”，协议层就是核心。至少要回答下面这些问题：

### 4.1 后端向前端要发哪些事件

可能需要：

- `message_token`
- `message_done`
- `tool_started`
- `tool_finished`
- `ui_render`
- `ui_patch`
- `ui_remove`
- `ui_focus`
- `ui_request_input`
- `approval_request`
- `clarify_request`
- `error`

### 4.2 前端向后端要回哪些事件

可能需要：

- `ui_event`
- `ui_action_submit`
- `ui_state_sync`
- `ui_selection_changed`
- `ui_filter_changed`
- `ui_block_closed`
- `ui_block_ack`
- `approval_response`
- `clarify_response`

### 4.3 哪些交互是阻塞式，哪些不是

#### 阻塞式
典型如：
- “请选择一个产品继续”
- “审批这条命令是否执行”
- “表单补充完再继续”

它会要求 agent 暂停，等前端回结果。

#### 非阻塞式
典型如：
- 用户切换了时间区间
- 用户展开了某个 panel
- 用户对图表做了 zoom

它更像前端状态变化，agent 未必立即等待，但未来可能读取。

### 4.4 状态属于谁

这是很关键的设计问题：

- message-local state：只属于某条消息
- panel-local state：属于某个工作区 panel
- page state：整个页面共享
- agent-readable state：可被 agent 读取
- agent-owned state：由 agent 主导更新

一旦不分清，会出现典型混乱：
- 什么都往 prompt 塞
- 什么都当 clarify
- 什么都走自定义 tool call

---

## 5. 现在把主要候选框架 / 协议逐个摊开

以下不先下结论，只讲：
- 它是什么
- 它解决哪层问题
- 它能带来什么
- 它会引入什么约束

---

## 5.1 CopilotKit

### 它是什么

CopilotKit 是一个 **React-first 的 agent-native frontend stack**。

从官方定位看，它主要提供的是：
- agent 与 React app 之间的连接约定
- chat UI / frontend tools / state rendering
- generative UI 相关能力
- runtime 与事件协议封装

### 它主要解决哪层

主要覆盖：
- UI protocol layer
- frontend host / renderer layer
- 一部分 runtime-to-frontend integration layer

它不是纯后端协议，也不是只是一堆 UI 组件。

### 它可能发挥作用的地方

1. **提供更成熟的 agent-native React 抽象**
   - hooks
   - provider
   - runtime conventions
   - frontend tools / state binding

2. **减少自研胶水代码**
   - 特别是 React app 与 agent 交互层

3. **给双向 UI 一套现成范式**
   - 不一定最贴 Hermes，但能让很多问题有现成思路

### 它的潜在代价

1. **React-first 假设很强**
   - 对现有 `hermes-webui` 不是无缝 drop-in

2. **会引入自己的交互范式与 runtime 约定**
   - 你不是只拿到能力，也拿到框架边界

3. **如果 Hermes 已有自己的流式协议，可能出现双重抽象**
   - 现有 SSE / session / clarify / approval
   - CopilotKit runtime / events / hooks

4. **长期会产生框架绑定问题**
   - 你是在用它加速，还是在把核心协议交给它定义，需要分清

### 对 Hermes 语境下的真实问题

CopilotKit 不是“能不能用”，而是：

- 用到哪一层合适
- 是用它定义主协议，还是只借它的某些前端能力
- Hermes 是否愿意把一部分 UI runtime 语义托管给它

---

## 5.2 A2UI

### 它是什么

A2UI（Agent-to-UI）更像是一个：

- **声明式 UI schema / 组件描述协议**
- 让 agent 输出结构化 UI，而不是直接输出 React 组件代码

### 它主要解决哪层

主要覆盖：
- UI protocol layer 里的 **render payload schema** 部分

它解决的是：
- agent 如何描述 UI

但不完整解决：
- 状态同步
- 交互回传
- 页面级 shared state
- 前后端 session 语义

### 它可能发挥作用的地方

1. **把 UI 渲染从自然语言里剥离出来**
   - 从“请前端自己猜”变成“明确结构化 schema”

2. **为多组件输出提供统一描述层**
   - 图表
   - 表格
   - 卡片
   - 表单
   - panel block

3. **便于做 renderer registry**
   - `schema type -> React component`

### 它的潜在代价

1. **它只解决了一半问题**
   - render 很重要，但双向 UI 不只 render

2. **如果 schema 设计过早过重，容易进入“低代码引擎化”**
   - 抽象很漂亮，迭代很慢

3. **交互语义仍要补**
   - 点击、筛选、确认、表单提交、状态更新等仍要自己定义

### 对 Hermes 语境下的真实问题

A2UI 更像：
- 一个可考虑采用的 **结构化 UI 表达层**

而不是：
- 整个 agent-native frontend solution

---

## 5.3 AG-UI

### 它是什么

AG-UI 更偏：
- **agent 与 user-facing app 之间的事件协议 / 标准化思路**

可以理解为，它关注的是：
- agent 如何与前端应用对话
- 事件如何流动
- 消息、状态、tool、UI 更新如何表达

### 它主要解决哪层

主要覆盖：
- UI protocol layer
- event transport conventions

### 它可能发挥作用的地方

1. **提供一套更标准化的双向事件思路**
2. **减少 Hermes 自研协议完全闭门造车的风险**
3. **让未来接别的前端 / agent-native 生态更顺畅**

### 它的潜在代价

1. **标准化意味着抽象学习成本**
2. **和 Hermes 现有事件流未必一一对应**
3. **如果只借名词不借约束，可能形成半吊子兼容层**

### 对 Hermes 语境下的真实问题

AG-UI 更适合作为：
- “Hermes 双向 UI 协议设计时的参考系”

它未必要求你完整实现它，但它可以帮助你避免自研协议太随意。

---

## 5.4 MCP Apps

### 它是什么

MCP Apps 更偏：
- 从工具 / MCP server 返回可嵌入 UI
- 常见形态是 iframe / sandboxed interactive app

### 它主要解决哪层

主要覆盖：
- 工具结果如何以交互 UI 形式嵌入前端

### 它可能发挥作用的地方

1. **快速把某些独立功能块变成交互 UI**
   - 图表 explorer
   - 表格 drilldown
   - 小型专题分析器

2. **对“聊天内嵌 applet”很友好**

3. **隔离性好**
   - iframe / sandbox 的思路有助于降低宿主污染

### 它的潜在代价

1. **更适合局部嵌入，不天然适合整页共享状态工作台**
2. **宿主前端与嵌入 app 的状态打通会更复杂**
3. **对于“理财经理工作台”这种持续状态协作场景，可能太碎片化**

### 对 Hermes 语境下的真实问题

MCP Apps 更像：
- 聊天内或工作台内的 **局部插件型交互块方案**

不是：
- 整个前后端双向 UI 主协议

---

## 5.5 纯自研协议 + React 宿主

### 它是什么

完全基于 Hermes 自己的：
- SSE / HTTP endpoints
- 自定义事件模型
- 自定义 render schema
- 自定义 interaction protocol
- React renderer / state layer

### 它主要解决哪层

理论上覆盖全部，但前提是你自己造全部。

### 它可能发挥作用的地方

1. **最大自由度**
2. **最贴 Hermes 现有 runtime 语义**
3. **不会被外部框架牵着走**

### 它的潜在代价

1. **设计责任全在自己**
2. **会重造别人已经踩过的坑**
3. **需要很强的协议意识和长期维护纪律**

### 对 Hermes 语境下的真实问题

纯自研不是不行，关键问题是：
- Hermes 是否准备好长期维护一套 agent-native frontend protocol
- 是否真有必要全自己定义
- 是否可以先自研主干、再借成熟 schema / conventions

---

## 6. 候选技术栈不是互斥的，而是可以分层组合

真正重要的是：

> **不要把技术选型理解成“单选题”，更像“分层组合题”。**

可以拆成下面几层分别选：

### 6.1 Frontend Host
可选：
- React
- vanilla JS
- Web Components / Lit

现实判断：
- 对“双向共享状态”的目标来说，React 显著更自然

### 6.2 Event Transport
可选：
- 继续 SSE
- websocket
- 混合模式

现实判断：
- 现有 Hermes 已有 SSE 资产
- 是否要升级 transport，不是最先要决定的事

### 6.3 UI Render Schema
可选：
- 纯 tool-specific typed payload
- A2UI
- 自研 block schema
- 混合（先 typed payload，后抽 schema）

### 6.4 Interaction Protocol
可选：
- clarify 扩展型
- 自定义 `ui_event / ui_state_sync`
- 借 AG-UI 思路
- 借 CopilotKit runtime conventions

### 6.5 Frontend Agent Integration Layer
可选：
- 完全自研 hooks/store
- 局部借 CopilotKit
- 完整采用 CopilotKit 主路径

---

## 7. 现在把几条“可讨论路线”平铺出来

这里不是推荐，只是摊开。

---

## 路线 A：Hermes-native 自研主协议，React 宿主，最少借外部

### 结构
- 后端：`hermes-webui` 保持主基座
- 前端：React 新宿主
- 协议：Hermes 自定义双向 UI 事件模型
- render：先 typed payload，后视情况抽 schema
- CopilotKit：暂不接主链路
- A2UI：可暂不使用或后置引入

### 优点
- 最贴现有 Hermes 语义
- 控制权最强
- 无外部 runtime 绑定

### 风险
- 协议设计责任最大
- 容易重造轮子
- 早期若抽象不稳，后续改动成本高

### 适合讨论的问题
- Hermes 是否要拥有自己的 agent-native frontend protocol

---

## 路线 B：Hermes-native 主协议 + A2UI 作为 render schema

### 结构
- 后端：`hermes-webui`
- 前端：React
- 协议：自研 interaction/state protocol
- render：A2UI 或 A2UI-like schema
- CopilotKit：不作为主 runtime

### 优点
- 结构化渲染更清晰
- 保留 Hermes 对 interaction/state 的控制权
- 既不全自研 render schema，也不全托管给外部框架

### 风险
- 仍需自己补 interaction/state 语义
- 容易出现“schema 用了，但生态没真正借上”的半整合状态

### 适合讨论的问题
- 是否把“render”与“state/interaction”两层拆开选型

---

## 路线 C：Hermes backend + React host + 局部借 CopilotKit

### 结构
- 后端：`hermes-webui`
- 前端：React
- 主协议：Hermes 自己掌握
- CopilotKit：只借特定 frontend capabilities
  - 例如部分 hooks / state conventions / frontend tools 思路
- render：可搭配 A2UI 或 typed payload

### 优点
- 既能保 Hermes 主导权
- 又能借成熟 agent-native frontend 经验
- 复杂度可能介于“纯自研”和“全接入”之间

### 风险
- 边界不好画时会很别扭
- 可能出现“双重心智模型”
  - Hermes 一套
  - CopilotKit 一套

### 适合讨论的问题
- 哪些 CopilotKit 能力是真增益，哪些只是换个包装

---

## 路线 D：React 主前端 + CopilotKit 深接入 + Hermes 适配

### 结构
- 前端与交互范式更接近 CopilotKit 主路径
- Hermes backend 需要向其 runtime / conventions 靠拢
- A2UI / frontend tools / shared state 等更系统地采用

### 优点
- 理论上能最快获得较完整 agent-native frontend 生态能力
- 少量问题可借社区既有模式

### 风险
- 对 Hermes 现有后端语义改造压力大
- 长期更依赖外部框架演进
- 如果 Hermes 特有交互模型不贴 CopilotKit，会持续出摩擦

### 适合讨论的问题
- Hermes 是否愿意把前端交互主范式显著外包给外部框架

---

## 路线 E：局部 MCP Apps / 插件化 UI 块 + Hermes 主工作台

### 结构
- 主工作台仍由 Hermes + React 宿主承载
- 某些复杂功能块采用 MCP Apps / sandboxed embedded apps
- 主聊天协议与页面 shared state 仍由 Hermes 主导

### 优点
- 对局部复杂交互块很灵活
- 可隔离高复杂度功能
- 对实验性模块友好

### 风险
- 主状态与嵌入状态之间的桥接更难
- 对“全局一致工作台”未必最优
- 容易形成碎片化体验

### 适合讨论的问题
- 哪些功能块适合当“独立微应用”而不是主工作台内建组件

---

## 8. 如果从“理财经理工作台”场景倒推，关键能力维度有哪些

为了后续讨论更具体，可以用以下维度去评每条路线。

### 8.1 消息内结构化输出
- 聊天里插卡片 / 表格 / 图表
- 哪条路线最自然

### 8.2 工作台侧边面板
- 右侧持仓、产品比较、客户画像、风险提醒
- 是否支持 message 外的持续 UI 区域

### 8.3 持续共享状态
- 当前客户是谁
- 当前产品篮子是什么
- 当前筛选器是什么
- 当前会话上下文与页面上下文如何互通

### 8.4 用户交互回传
- 点击、选择、筛选、表单提交、局部编辑
- 回传粒度与语义是否清晰

### 8.5 阻塞式交互
- 需要 agent 停下来等用户完成某个交互
- 例如方案确认、产品选择、审批

### 8.6 非阻塞式观察
- agent 能否感知前端状态变化，但不必立即停下来
- 例如 panel open/close、selected row、time range

### 8.7 长期演进空间
- 后续是否支持整页或多区域生成式 UI
- 是否支持更复杂布局与 shared state

---

## 9. “CopilotKit / A2UI / AG-UI”最值得关注的不是名字，而是它们分别提供了什么资产

为了避免讨论变成品牌偏好，建议这样看：

### CopilotKit 提供的资产
- React agent-native frontend conventions
- provider / hooks / runtime integration 思路
- frontend tools / state rendering / generative UI 经验

### A2UI 提供的资产
- 结构化 UI schema / render payload 思路
- agent 输出 UI 的声明式表达层

### AG-UI 提供的资产
- 双向 agent ↔ app 事件协议参考系
- 更标准化的交互事件思路

### MCP Apps 提供的资产
- 局部交互式 UI 块嵌入能力
- 更插件化、沙箱化的 UI 返回方式

### Hermes 自研能提供的资产
- 对现有 runtime 语义的精确贴合
- 最大控制权
- 与现有 approval / clarify / session / memory 机制的一致性

---

## 10. 这轮讨论里暂时不该过早决定的事

为了防止过早锁死，我建议以下几件事先不下结论：

1. **CopilotKit 是全接还是完全不用**
2. **A2UI 是官方 schema 还是自研同构 schema**
3. **AG-UI 要不要显式兼容**
4. **工作台是 message-centric 还是 page-centric**
5. **某些复杂块是否未来用 MCP Apps**

这些都应在更具体的能力清单和事件模型出来后再判断。

---

## 11. 这轮讨论里反而应该尽快钉死的事

### 11.1 双向 UI 最小事件模型
先不管是不是 CopilotKit / AG-UI 风格，至少要回答：

- 最小后端→前端事件集是什么
- 最小前端→后端事件集是什么
- 阻塞式与非阻塞式交互如何区分

### 11.2 页面状态边界
至少要分清：
- message state
- workspace state
- page state
- agent-readable shared state

### 11.3 第一批目标交互
先列清楚最重要的 5~10 个工作台交互：

例如：
- 生成产品比较表
- 点选某产品展开深挖
- 切换客户画像视角
- 选中某个持仓做风险诊断
- 在图表上圈选区间并让 agent 解释

只有这些交互具体了，技术选型讨论才不会漂。

---

## 12. 建议的下一份文档应该长什么样

如果这份“平铺文档”确认方向对，下一份不该直接是实现方案，而应该是：

# 《Hermes Agent-Native Workbench 双向 UI 最小协议草案》

它应该包含：

1. **目标交互清单**
2. **事件模型草案**
   - backend -> frontend
   - frontend -> backend
3. **状态域划分**
4. **阻塞式 / 非阻塞式交互定义**
5. **render payload 选型候选**
   - typed payload
   - A2UI
   - hybrid
6. **CopilotKit / AG-UI / 自研协议在这一草案中的映射关系**

这样下一轮讨论就会更具体，而不是继续空转在“感觉哪套更先进”。

---

## 13. 本文的临时性结论（不是选型结论）

这份文档只落三个临时结论，且都不是最终站队：

### 13.1 真正要设计的核心对象是“双向 UI 协议”，不是单个前端框架

### 13.2 CopilotKit、A2UI、AG-UI、MCP Apps 解决的问题层次并不相同，不能混着比较

### 13.3 技术选型更像“分层组合题”，不是单选题

---

## 14. 给后续讨论的提问框架

下一轮你如果要和我深聊，我建议我们按下面顺序推进：

1. **先列工作台最重要的 5~10 个交互场景**
2. **再定义最小双向事件模型**
3. **再看 A2UI 是否适合做 render schema**
4. **再看 CopilotKit 是局部借还是深接入**
5. **最后才落到基于哪个 repo、怎么实施**

这样顺序会更稳。

---

## 15. 一句话摘要

> 这轮不该先争“用不用 CopilotKit”或“站哪条技术路线”，而应先把 Hermes 想实现的 agent-native 双向 UI 能力模型拆清楚，再把 CopilotKit、A2UI、AG-UI、MCP Apps、自研协议分别映射到 render、interaction、state、event protocol 这些不同层上，最后再做分层组合式选型。
