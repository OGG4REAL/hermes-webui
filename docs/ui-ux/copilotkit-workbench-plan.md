# 理财经理工作台：技术方案决策分析

> 状态：`historical / early decision memo / superseded for V0 execution`
> 用途：供团队讨论决策，非实施文档
> 日期：2026-04-27
> V0 入口：`docs/ui-ux/rm-workbench-v0-index.md`

> 注意：本文是早期 A/B/X/Y 方案讨论。当前 V0 的协议边界与 CopilotKit 接入深度，以 `rm-workbench-v0-technical-skeleton.md` 与 `rm-workbench-v0-agui-a2ui-alignment.md` 为准。

---

## 背景

我们要在 Hermes 生态上做一个理财经理工作台，核心能力是 **AI 生成 UI**：agent 在对话中推送图表、表格、交互式组件（产品选择、行动确认），理财经理操作后结果回传 agent 继续推理。目标用户不是开发者，需要可视化的交互界面而非纯文本。

当前涉及三个项目：

| 项目 | 是什么 | 技术栈 |
|---|---|---|
| Hermes Agent | AI agent 引擎，核心能力来源 | Python, 10000+ 行, 40+ tools |
| Hermes WebUI | 给 agent 套的 Web 壳（聊天界面 + 管理） | Python 后端 14000 行 + vanilla JS 前端 16000 行 |
| Hermes Agent web/ | agent 自带的管理后台（无聊天） | React 19 + Vite 7 + Tailwind 4, 6500 行 |

需要做两个决策：
1. 前端基座选谁？
2. CopilotKit 用不用？

---

## "AI 生成 UI"到底需要什么

```
步骤 1：Agent 产出结构化 UI 描述     → Hermes agent tool 结果（JSON）     ✅ 已有
步骤 2：把描述传给前端               → hermes-webui SSE 通道              ✅ 已有
步骤 3：前端根据描述渲染对应组件     → ？？？ 这是要补的                  ❌ 缺失
步骤 4：用户交互，结果回传 agent     → hermes-webui clarify 通道          ✅ 已有
```

四步里 #1 #2 #4 已有。争论的焦点是 **#3 怎么做**，以及 #4 在 React 里的写法。

### 概念关系

```
A2UI = UI 组件描述规范（Google 出品，JSON schema 定义组件长什么样）
AG-UI = 传输协议（CopilotKit 出品，~16 种 SSE event type）
CopilotKit = 端到端框架（AG-UI + A2UI + React SDK + renderAndWait + state sync）
```

hermes-webui 已有自己的传输协议（14 种 SSE event type）和 renderAndWait（approval/clarify）。

---

## 决策 1：前端基座

### 选项 A：改造 hermes-webui（把 vanilla JS 换成 React）

在 hermes-webui 项目内新建 React 前端，替代 static/*.js。后端 api/*.py 完全不动。

```
~/hermes-webui/
  ├── api/*.py          ← 保留不动（SSE、session、approval/clarify 全在这）
  ├── server.py         ← 加路由把 /app 指向 React 构建产物
  ├── static/*.js       ← 过渡期保留，React 覆盖后废弃
  └── frontend/         ← 新建 React 项目
```

| 优势 | 劣势 |
|---|---|
| 聊天后端现成（SSE 14 种 event、session、approval/clarify、cancel/steer、model routing、title 生成、workspace） | 管理页面（config、cron、skills、logs）需后续新建 |
| 同一个项目、同一个端口（8787） | React 组件库需从零搭建 |
| 只换前端皮，后端零改动风险 | |
| 过渡期两套前端并存，不断档 | |

### 选项 B：扩展 hermes-agent web/（在 React 管理后台上加聊天）

在 hermes-agent 已有的 React 管理后台上新增 ChatPage，跨项目连接 hermes-webui 后端。

```
~/projects/agents-*/web/       ← React 前端（已有 8 个管理页面）
  └── ChatPage.tsx             ← 新增，通过 proxy 调 hermes-webui 后端

~/hermes-webui/api/*.py        ← 聊天后端（被跨项目调用）
```

| 优势 | 劣势 |
|---|---|
| 8 个管理页面现成 | 跨项目对接：两个仓库、两个端口（9119 + 8787） |
| React 组件库已有（Card、Badge 等 9 个） | Vite proxy 需配两个 upstream |
| i18n（中英）、typed API client 已有 | 部署需两个 Python 进程 |
| 不用从零搭 React 项目 | 聊天 API client 需要新增 |

### 对比

| 维度 | A：改造 hermes-webui | B：扩展 agent web/ |
|---|---|---|
| 聊天后端 | ✅ 现成，同项目 | ⚠️ 跨项目对接 |
| 管理页面 | ❌ 需后续新建 | ✅ 现成 8 个 |
| 开发复杂度 | 低（单项目单端口） | 中（双项目双端口） |
| 部署复杂度 | 低（一个进程） | 高（两个进程） |
| 核心产品诉求 | ✅ 聊天 + GenUI 优先 | ⚠️ 聊天是后加的 |

---

## 决策 2：CopilotKit 用不用

### 选项 X：用 CopilotKit

**前端代码示例：**
```tsx
// 只读组件：agent 推图表
useCopilotAction("show_portfolio", {
  parameters: z.object({ items: z.array(z.object({ label: z.string(), value: z.number() })) }),
  render: ({ data }) => <PortfolioChart data={data} />
});

// 交互式组件：renderAndWait，用户选完结果自动回传 agent
useFrontendTool("compare_products", {
  parameters: z.object({ products: z.array(...), prompt: z.string() }),
  render: ({ args, result, status }) => (
    <ProductCompare
      products={args.products}
      onSelect={(selected) => result(selected)}  // 一行搞定回传
      status={status}                             // inProgress/complete 自动管理
    />
  ),
});
```

**后端改动：** 在 hermes-webui 后端新增 `/api/copilotkit` endpoint（adapter），内部复用 streaming.py 的 agent 执行逻辑，输出格式从 hermes SSE → AG-UI 协议。

不是两套后端——是同一个后端多一个出口格式：
```
/api/chat/stream   → hermes SSE 格式（给 vanilla JS 用，过渡期）
/api/copilotkit    → AG-UI 格式（给 CopilotKit React 前端用）
```

**新增依赖：** CopilotKit React SDK + CopilotKit Python runtime

---

### 选项 Y：不用 CopilotKit（A2UI 渲染器 + 自定义 hook）

**前端代码示例：**
```tsx
// 自定义 hook 直接消费 hermes-webui SSE
const { messages, uiBlocks, clarify, approval } = useHermesStream(streamId);

// 组件注册表
const REGISTRY = {
  portfolio_chart: PortfolioChart,
  product_compare: ProductCompare,
  // ...
};

// 渲染分发
{uiBlocks.map(block => {
  const Comp = REGISTRY[block.type];
  return block.interactive
    ? <Comp {...block.data} onSubmit={r => postClarify(block.interaction_id, r)} />
    : <Comp {...block.data} />;
})}
```

**后端改动：** streaming.py 加两个 SSE event type（ui_render、ui_interact），clarify.py 的 result 支持 JSON。各改几行。

**新增依赖：** 无（只需 recharts 图表库）。

---

### 对比

| 维度 | X：用 CopilotKit | Y：不用 CopilotKit |
|---|---|---|
| GenUI 注册方式 | 声明式 hook | 手动注册表 |
| renderAndWait | 内置，一行 `result(data)` | 自己写：SSE → 渲染 → POST → 清理 |
| 后端改动 | 中（adapter ~4-5 天） | 小（两个文件各几行 ~2 天） |
| 前端工作量 | ~2 周 | ~2.5 周 |
| **总工作量** | **~3 周** | **~3 周** |
| 翻译层 | 有（hermes SSE ↔ AG-UI） | 无（直连） |
| 概念复杂度 | 中（两套协议） | 低（一套协议） |
| 6 个组件时 | 略 overkill | 刚好 |
| 20+ 个组件时 | 声明式优势明显 | switch/case 膨胀 |
| Phase 2 shared state | ✅ 内置 | ❌ 自己实现 |
| 生态兼容 | ✅ AG-UI / A2UI 标准 | ⚠️ 自有协议 |
| 自主可控 | ⚠️ 依赖 CopilotKit 版本 | ✅ 完全自主 |

---

## 组合矩阵

| | X：用 CopilotKit | Y：不用 CopilotKit |
|---|---|---|
| **A：改造 hermes-webui** | 聊天后端现成 + GenUI 体验好。后端多一个 adapter endpoint。 | **最简架构。** 后端直连前端，无翻译层。GenUI 胶水代码自己写。 |
| **B：扩展 agent web/** | 组件库现成 + GenUI 体验好。但跨项目 + adapter = 最高复杂度。 | 跨项目 + 自写胶水。复杂度高，收益不对称。 |

---

## 无论选哪条路，不变的部分

1. **Hermes Agent 不动** — 所有 AI 能力的来源
2. **hermes-webui Python 后端保留** — SSE、session、approval/clarify、model routing
3. **金融组件自己写** — PortfolioChart, ProductCompare, ClientBrief, RiskAlert, ActionChecklist, MeetingPrep
4. **右侧 workspace panel 做 GenUI 主承载区**
5. **ui_blocks JSON 格式遵循 A2UI 规范** — 保持未来兼容性
6. **Phase 1 → Phase 2 演进** — 先验证聊天内 GenUI，再做工作台多面板

---

## 建议讨论顺序

1. **先定前端基座**（A vs B）— 决定项目结构和开发流程
2. **再定 CopilotKit**（X vs Y）— 决定 GenUI 开发方式
3. **定了之后** — 写实施计划和任务拆分
