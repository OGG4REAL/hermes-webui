# Hermes 前端 React 化迁移方案

> 路径：`docs/ui-ux/hermes-react-migration-plan.md`
> 状态：`reference / React host background`
> 目标读者：Hermes / Claude Code / 后续实现者
> V0 入口：`docs/ui-ux/rm-workbench-v0-index.md`

> 注意：本文只作为 React workbench host 的背景参考。RM Workbench V0 第一批工程改动以 backend adapter + pending interaction 为先，执行入口见 `rm-workbench-v0-implementation-plan.md`。

---

## 0. 结论先行

**正式结论：Hermes 的前端应以 `hermes-webui` 为后端与协议基座，做渐进式 React 化改造；`ai_sandbox/frontend` 只作为交互与组件参考，不作为正式基座直接迁入。**

一句话版：

```text
保留 hermes-webui Python 后端与现有 API / SSE / session / approval / clarify 契约
        ↓
新建 React 前端宿主，逐步替换 static/*.js 的渲染与状态管理
        ↓
从 ai_sandbox/frontend 有选择地迁移图表 / 表格 / workspace / trajectory / eval 这些 UI 模块
        ↓
CopilotKit 先不接管主聊天链路，只保留为后续可选增强项
```

---

## 1. 这次的明确站位

### 1.1 为什么不是直接用 `ai_sandbox/frontend`

`ai_sandbox/frontend` 有价值，但它不是 Hermes 正式前端基座，原因很直接：

1. **它与 Hermes 后端协议没有天然对齐**
   - 它依赖自己的一套 FastAPI 路由：`/sessions/...`
   - 主聊天链路当前仍是手写 `fetch + EventSource`
   - 它不是“装上就能跑 Hermes”的前端壳

2. **它更像工作台原型，而不是正式产品外壳**
   - 长处在于：三栏布局、workspace、trajectory、eval、chart/table renderer
   - 弱项在于：产品完整度、Hermes 特有行为适配、会话与工具语义的一致性

3. **直接搬过去会把问题从“React 化”变成“系统重接线”**
   - 你得到的是一套 UI 雏形
   - 但要重新适配 Hermes 的 approval / clarify / memory / cron / session stream 等能力

结论：**`ai_sandbox/frontend` 适合拆件借鉴，不适合整壳迁入。**

### 1.2 为什么应以 `hermes-webui` 为基准

因为 `hermes-webui` 不是单纯一个前端皮肤，它已经和 Hermes 运行时能力深度绑定。

已确认的后端与协议能力包括：

- 聊天启动与流式返回：`/api/chat/start` + `/api/chat/stream`
- session 持久化与恢复
- tool call / tool_complete 流事件
- approval pending / respond
- clarify pending / respond
- memory 读写 API
- cron 相关 API
- gateway session stream
- stream end / reconnect / 状态恢复链路

这意味着：

> **Hermes 真正难得的资产，不是现在这套 vanilla JS，而是 `hermes-webui` 已经整理好的 Python 后端契约。**

所以 React 化的正确对象不是“重新发明后端”，而是：

- **保留 `hermes-webui` 后端为事实源**
- **替换前端状态管理与渲染层**

---

## 2. 当前三套代码的角色划分

### 2.1 `~/hermes-webui`

角色：**正式后端与现行产品壳**

优点：
- Hermes 语义最完整
- API 和事件流最贴近真实运行时
- approval / clarify / memory / cron / gateway 等机制都在
- 适合继续作为唯一后端事实源

问题：
- 前端是 static HTML + 原生 JS
- `messages.js` 已经成为高耦合命令式事件中心
- 随着 GenUI / 工作台能力上升，维护成本会继续恶化

### 2.2 `~/hermes-agent/web`

角色：**管理后台 / 运营台 / 配置台**

已看到的页面包括：
- Status
- Sessions
- Analytics
- Logs
- Cron
- Skills
- Config
- Env

判断：
- 它是 React 没错
- 但它更像 Hermes 的后台控制面板
- 不是要承载“理财经理工作台 / 对话式工作区”的产品前台

因此：
- 可以借其工程栈（React + TS + Vite + Tailwind）
- **不应把它当现成业务前台直接扩进去**

### 2.3 `~/ai_sandbox/frontend`

角色：**交互与组件样板库**

已确认可借鉴部分：
- `ChartAction`
- `TableAction`
- `WorkspacePanel`
- `TrajectoryPanel`
- `EvaluationPanel`
- 三栏 ChatLayout 组织方式

判断：
- 它证明了 React 工作台形态是可行的
- 也证明了“CopilotKit 不是必须整套接管”
- 但它不应反客为主，替代 Hermes 正式基座

---

## 3. 目标架构

### 3.1 核心原则

1. **后端不换脑**：继续以 `hermes-webui` Python API 为唯一后端事实源
2. **前端换范式**：从命令式 DOM 操作切换到 React 状态驱动渲染
3. **先兼容，后增强**：先完整复刻现有能力，再加 GenUI / 工作台增强
4. **拒绝双重翻译层**：不为了“看起来先进”引入多余 runtime adapter
5. **组件复用优先**：优先复用 `ai_sandbox` 中成熟 UI 组件，而不是重写

### 3.2 建议拓扑

```text
Hermes Agent runtime
        ↑
hermes-webui Python backend
  - /api/chat/start
  - /api/chat/stream
  - /api/approval/*
  - /api/clarify/*
  - /api/sessions/*
  - /api/memory/*
  - /api/crons/*
        ↑
React frontend (new)
  - session store
  - stream reducer
  - message renderer
  - tool renderer
  - workspace panel
  - GenUI renderers
```

### 3.3 不建议的拓扑

#### 方案 A：继续在 `static/*.js` 上打补丁
问题：
- 越做越乱
- 状态机继续散落在 DOM 与 EventSource callback 中
- 后面接 GenUI 会越来越难验证

#### 方案 B：整壳切到 `ai_sandbox/frontend`
问题：
- 后端协议不对齐
- Hermes 特有能力适配成本高
- 容易为了前端速度牺牲整体一致性

#### 方案 C：一上来完整接入 CopilotKit 主聊天 runtime
问题：
- 当前 Hermes 已有自己的后端协议与 SSE 语义
- 再套一层 runtime/adapter，大概率只是在翻译而不是增能
- 早期会增加调试面和不确定性

---

## 4. React 化不是“大重写”，而是渐进迁移

### 4.1 迁移目标

不是“做一个全新产品然后替换老站”，而是：

- 保住现有 Hermes 后端能力
- 提炼出稳定的前端协议层
- 用 React 重构消息流、工具流、交互流的状态管理
- 给后续工作台 / GenUI 留出扩展空间

### 4.2 迁移原则

1. **先保行为一致，再谈界面升级**
2. **先抽流式状态层，再抽 UI 组件层**
3. **先迁高价值主链路，再迁边角功能**
4. **新前端消费旧 API，而不是反过来改后端迎合前端**

---

## 5. 分阶段方案

## Phase 1：React 宿主落地，完整复刻现有聊天主链路

### 5.1 目标

建立一个新的 React 前端壳，直接消费 `hermes-webui` 现有 API 与 SSE 流，先把这些能力完整接住：

- session 列表 / 切换
- 发送消息
- 流式 assistant token
- tool call / tool_complete
- approval
- clarify
- stream_end / reconnect
- 基础文件上传与 workspace 入口（如果当前 webui 已有）

### 5.2 这阶段不做什么

- 不改 Hermes 后端协议语义
- 不引入 CopilotKit 主聊天 runtime
- 不上来做全页面生成式工作台
- 不先碰复杂 A2UI 协议设计

### 5.3 交付标准

当 React 前端达到下面标准，Phase 1 算完成：

1. 用户可在 React 前端完成一轮完整对话
2. 流式输出、tool 卡片、approval、clarify 行为与现有 WebUI 等价
3. session 恢复、切换、刷新后状态不乱
4. 旧前端可并存，新前端不破坏现有后端

---

## Phase 2：把当前命令式事件流收敛成 React 状态层

### 6.1 目标

把当前 `messages.js` 中散落的事件处理逻辑提炼为稳定的客户端状态模型。

建议抽出：

- `useHermesSessionList()`
- `useHermesChatStart()`
- `useHermesStream(streamId)`
- `useApprovalState()`
- `useClarifyState()`
- `useWorkspaceState()`

### 6.2 推荐做法

用 reducer 管理流事件，而不是在组件里堆 EventSource callback：

```ts
 type StreamEvent =
   | { type: 'token'; text: string }
   | { type: 'tool'; payload: ToolCall }
   | { type: 'tool_complete'; payload: ToolComplete }
   | { type: 'approval'; payload: ApprovalRequest }
   | { type: 'clarify'; payload: ClarifyRequest }
   | { type: 'stream_end'; payload: { session_id: string } }
   | { type: 'error'; payload: { message: string } };
```

收益：
- 更好测
- 更好重连
- 更好做局部 UI 替换
- 更适合后面接结构化渲染

### 6.3 交付标准

- EventSource 生命周期集中管理
- 消息、工具、approval、clarify 有明确状态边界
- UI 组件不直接耦合底层 SSE 细节

---

## Phase 3：引入工作台与结构化 UI

### 7.1 目标

在不破坏主聊天链路的前提下，引入右侧工作台与结构化渲染区。

第一批建议接入：
- 图表渲染
- 表格渲染
- 文件 / workspace 预览
- trajectory 面板
- eval 面板

### 7.2 组件复用来源

优先从 `ai_sandbox/frontend` 拿这些成熟件：

- `ChartAction`
- `TableAction`
- `WorkspacePanel`
- `TrajectoryPanel`
- `EvaluationPanel`
- `ChatLayout` 的三栏布局经验

但注意：
- **只迁 UI 组件与布局模式**
- **不迁它那套 API 契约与应用骨架**

### 7.3 结构化渲染的最小路线

先不要抽象到过度通用。

第一版只需要：

- `render_chart` → `ChartAction`
- `render_table` → `TableAction`
- `show_notification` → Notification card/toast
- 文件 / run / eval → 专用 panel 组件

也就是说先走：

```text
tool_name -> typed React renderer
```

而不是一上来就：

```text
万能 schema -> 通用解释器 -> 低代码工作台引擎
```

前者简单、可测、够用。

---

## Phase 4：再评估 CopilotKit 的接入边界

### 8.1 当前判断

当前阶段**不建议**让 CopilotKit 接管主聊天链路。

理由：
- Hermes 已有自己的 SSE 协议与交互机制
- 早接入只会增加适配层
- 真正要解决的问题不是“缺一个 AI 前端框架”，而是“需要一个可维护的 React 客户端状态层”

### 8.2 可以重新评估的场景

CopilotKit 只有在下面场景里才值得重新评估：

1. 你明确需要它的 frontend tools / shared state 能力
2. 你明确要让 UI 与 agent 形成更标准化的 agent-native 前端协议
3. 你确认自己不想长期维护 Hermes 自有的客户端状态抽象

### 8.3 即便未来接，也应是局部接入

正确顺序应是：

1. 先把 Hermes 自己的 React 前端做稳
2. 再选局部场景试接 CopilotKit
3. 验证增益是否大于适配复杂度

而不是反过来。

---

## 9. 推荐目录与文件组织

以下是建议的新前端组织，不代表本轮立即实现：

```text
hermes-webui/
  frontend/
    src/
      app/
      pages/
        ChatPage.tsx
      components/
        chat/
          MessageList.tsx
          MessageBubble.tsx
          ToolCallCard.tsx
          ApprovalCard.tsx
          ClarifyCard.tsx
          Composer.tsx
        workspace/
          WorkspacePanel.tsx
          FilePreview.tsx
          TrajectoryPanel.tsx
          EvalPanel.tsx
        renderers/
          ChartAction.tsx
          TableAction.tsx
      hooks/
        useHermesSessions.ts
        useHermesStream.ts
        useApprovalState.ts
        useClarifyState.ts
      lib/
        api.ts
        streamReducer.ts
        eventTypes.ts
      types/
```

### 为什么建议单独 `frontend/`

因为这样最干净：
- 不污染现有 `static/` 旧前端
- 迁移期可双跑
- 更容易明确新旧边界

如果后续需要，也可以通过构建产物再接回 Python 静态资源分发。

---

## 10. 迁移优先级

### 第一优先级：先把主链路跑通

- 新 React 壳
- session 列表
- chat start
- chat stream
- token render
- tool events
- approval
- clarify
- stream_end

### 第二优先级：接工作台能力

- workspace panel
- chart/table render
- file preview
- run / trajectory / eval

### 第三优先级：再谈更开放的 GenUI

- 更通用 schema
- 更复杂交互块
- shared state
- 局部 CopilotKit 能力评估

---

## 11. 风险与控制点

### 风险 1：一开始就大重写

后果：
- 现有 Hermes 行为跑不全
- React UI 看起来更现代，但核心能力反而倒退

控制：
- 必须以“复刻现有行为”为第一验收门槛

### 风险 2：为了 React 把后端协议也一起改崩

后果：
- 调试面激增
- 问题到底在 agent / backend / stream / frontend 无法切分

控制：
- Phase 1 明确要求：React 客户端先消费旧协议，不先改协议

### 风险 3：被 CopilotKit 吸走注意力

后果：
- 花很多时间在 adapter 与概念层
- 主问题还没解决

控制：
- 把 CopilotKit 明确降级为后续可选增强，而不是当前主线

### 风险 4：组件复用变成组件迁坟

后果：
- 从 `ai_sandbox` 搬来一堆与 Hermes 语义不合的壳代码

控制：
- 只迁 renderer / panel / layout 思想，不迁整套 app skeleton

---

## 12. 成功标准

这条路线成功，不是因为“看起来更像现代前端”，而是因为以下四件事同时成立：

1. **Hermes 特有能力没有回退**
   - approval
   - clarify
   - session
   - memory / cron / gateway 相关入口能力

2. **前端状态模型显著变干净**
   - 不再靠散落的命令式 callback 拼接全局状态

3. **工作台能力可持续扩展**
   - 图表、表格、workspace、trajectory、eval 可稳定接入

4. **未来是否接 CopilotKit 成为可选题，而不是前置依赖**

---

## 13. 建议的后续动作

### 建议动作 A：先写迁移设计，不直接开工

下一份文档应更具体，落到实现层，内容包括：

1. React 新前端目录结构
2. 现有 `hermes-webui` API 对应的 typed client 设计
3. `useHermesStream()` 的事件模型
4. approval / clarify 的 React 状态机
5. 第一批从 `ai_sandbox` 迁哪些组件、怎么改接口
6. 验收与回归测试方案

### 建议动作 B：第一轮实现只做“等价替换”

第一轮不要混入：
- A2UI 通用协议
- CopilotKit runtime
- 大而全的工作台 DSL

先做最小可验证方案。

---

## 14. 最终建议

**我当前支持的路线是：**

- **以 `hermes-webui` 为后端与协议基座**
- **以 React 化为前端演进方向**
- **以 `ai_sandbox/frontend` 为组件与交互参考库**
- **以“先复刻、后增强、再评估 CopilotKit”为迁移顺序**

这条路线的优点是：
- 不丢 Hermes 现有资产
- 不被旧前端继续拖死
- 不把系统重建成另一套东西
- 复杂度最低，验证路径最清楚

---

## 15. 给 Claude Code / 实现者的一句话摘要

> 不要把 `ai_sandbox/frontend` 整壳迁进 Hermes；要把 `hermes-webui` 当成后端与协议事实源，新建 React 前端渐进替代 `static/*.js`，并从 `ai_sandbox` 有选择地迁移图表、表格、workspace、trajectory、eval 等工作台组件；CopilotKit 暂不作为主链路依赖。
