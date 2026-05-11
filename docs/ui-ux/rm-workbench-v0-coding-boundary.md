# Structured UI Coding Boundary (formerly "RM Workbench V0 Coding Boundary")

路径：`docs/ui-ux/rm-workbench-v0-coding-boundary.md`
状态：`active / coding boundary (realigned 2026-05-09)`
更新时间：`2026-05-09`
入口：`docs/ui-ux/rm-workbench-v0-index.md`
受约束于：`docs/ui-ux/rm-workbench-v0-adr.md`（ADR 与本文档冲突时以 ADR 为准）

---

## 0. 这份文档负责什么

这份文档约束 Hermes WebUI **结构化 UI 子系统**（即原 "RM Workbench V0"）后续 issue 的代码改动边界。

它回答：

- 哪些目录负责哪些能力。
- runtime / streaming / frontend host 改动有哪些红线。
- structured UI contract 的入口在哪里。
- Layer 0（通用 Generative UI 原子能力）与 Layer 1（RM 等业务 consumer）怎么分层。
- 每类改动必须怎么验收。

它不负责：

- 重复 Architecture 的系统图。
- 重复 ADR 的技术取舍。
- 记录每个 issue 的过程。
- 指定完整业务 workflow 细节。

后续 Multica issue 如果涉及结构化 UI 代码改动，默认需要引用这份文档。

### 0.1 与 ADR 的关系

本文档是 **执行层** 边界约束，ADR 是 **决策层** 主文件。两者冲突时一律以 ADR 为准：

- 当 ADR 演进时，本文档应同步更新对应章节。
- 不允许通过本文档绕过 ADR（例如把 ADR 已废弃的硬约束以 "coding boundary 红线" 名义重新引入）。
- 2026-05-09 的方向校准（见 ADR-009 ~ ADR-012）已在本文档相应章节落地；本文档此前明文锁定的若干 RM 化要求（如"V0 继续以 `rm_workbench_emit_contract` 为主"）已删除或改写。

---

## 1. Directory Ownership

### 1.1 Hermes Agent

路径：

```text
/Users/hywl/hermes-agent
```

职责：

- 注册模型可见 tools。
- 暴露 Layer 0 结构化 UI emit tool（规范名 `emit_ui`，见 ADR-012）。
- 维护 Hermes runtime / tool registry / Skill loading。

边界：

- 不在 hermes-agent 中实现 WebUI renderer。
- 不在 hermes-agent 中写 React / A2UI 组件。
- 不为每种 UI primitive 新增独立 tool（见 ADR-009）。

### 1.2 hermes-webui backend

路径：

```text
/Users/hywl/hermes-webui/api/
```

职责：

- `api/streaming.py` 保留主 chat stream。
- `api/rm_workbench/` 负责 Layer 0 contract validation / adapter / emit helper。
  （目录名是历史遗留，进入 deprecation 队列，见 ADR-012；本轮不改名）
- `api/pending_interactions.py` 负责 structured UI interaction pending / resolve。
- `api/routes.py` 只暴露必要的 debug / mock / resolve endpoints。

边界：

- backend 不从 assistant text 猜 UI。
- backend 不渲染 UI。
- backend 不等待前端交互；阻塞语义属于 runtime/tool execution 层。
- streaming callback 只做轻量 bridge，不能引入长阻塞。
- Layer 0 validator（`api/rm_workbench/contracts.py`）只校验最小可识别性（见 ADR-010），
  不做 per-type 字段强制。业务级严格性（如 RM 要求 `customer` / `product_candidates`
  必须存在）属于对应 Skill 的责任，不在 Layer 0 validator 中实现。

### 1.3 React structured-UI host

路径：

```text
/Users/hywl/hermes-webui/frontend/src/
```

职责：

- `a2ui/` 负责通用 declarative UI renderer（**Layer 0**）。
- `a2ui/primitives/` 负责 generic UI blocks（**Layer 0**）。
- `agui/` 负责 AG-UI event reduce / state update（**Layer 0**）。
- `rm/surfaces/` 负责 RM semantic surfaces（**Layer 1 — RM consumer**）。
- `api/` 负责与 hermes-webui backend 的 frontend client。

边界：

- mock app 和真实 WebUI chat path 必须共享 renderer。
- 不允许只在 mock path 能渲染，主 WebUI chat path 不可见。
- 不执行 LLM 生成的任意 JSX / HTML / remote JS。
- Layer 0 primitive 必须能在必填 props 缺失时优雅降级（空状态 + 警告），
  不能因为缺字段抛运行时异常或拒绝渲染（见 ADR-010）。
- Layer 1 surface 可以加严业务级 schema 校验，但只能在自己的渲染分支里抛错，
  不能反向污染 Layer 0 路径。

---

## 2. Streaming Boundary

保持现有主协议：

```text
/api/chat/stream
```

允许：

- 新增或消费 `event: rm_workbench`。
- 在 `event: rm_workbench` 的 payload 中承载 AG-UI events。
- AG-UI `CUSTOM` event 中承载 A2UI messages。

禁止：

- 把 `/api/chat/stream` 整体改成 AG-UI top-level stream。
- 改掉现有 text / tool / approval / clarify / metering event names。
- 让 RM Workbench bridge 影响普通聊天流。
- 在 SSE callback 中等待用户点击或等待 pending interaction resolve。

每个 runtime / agent / streaming / frontend host issue 都必须有一次真实 WebUI manual smoke：

```text
主 WebUI chat 触发
  -> 观察到预期 SSE event
  -> 观察到 UI 渲染或明确的 frontend hook log
```

验收证据可以是：

- screenshot
- SSE log
- browser console log
- server log
- issue comment 中的最小复现记录

---

## 3. Contract Boundary

Layer 0 唯一 structured UI emit entrypoint（见 ADR-012）：

```text
emit_ui
```

> 历史名 `rm_workbench_emit_contract` 已物理重命名为 `emit_ui`，不保留兼容别名。
> 任何 issue / 测试 / Skill 引导词中如仍出现旧名，视为待清理债务。

工具参数形态（**最小信封**，见 ADR-011）：

```json
{
  "contract": {
    "ui": {
      "blocks": []
    }
  }
}
```

允许的 contract 字段：

| 字段 | Layer | 必填性 |
|---|---|---|
| `ui.blocks` | Layer 0 | `ui.blocks` 与 `surfaces` 至少其一非空 |
| `surfaces` | Layer 1（RM 等业务） | 同上 |
| `pending_interactions` | Layer 0/1 | 可选，可空数组 |
| `memory_proposals` | Layer 0/1 | 可选，可空数组 |
| `kind` | metadata | 可选；缺省 = `"ui"`；不再做 validator 路由门禁 |
| `version` | metadata | 可选；缺省 = 当前 schema 版本 |
| `run_id` / `thread_id` / `skill` | metadata | 可选；缺省由后端补 uuid 或当前 session 信息 |

允许：

- generic UI primitives 进入 `ui.blocks`。
- 业务语义 surfaces（如 RM 的 `CustomerProfileCard`）进入 `surfaces`。
- pending interaction 只通过 `pending_interactions` 声明。
- memory 只通过 `memory_proposals` 声明。

禁止：

- 新增 `render_table` / `render_chart` / `render_form` / `render_card` 等 per-component tools（见 ADR-009）。
- 让 frontend 从 assistant markdown 中抽表格或图表。
- 让 frontend 执行 contract 内的任意代码。
- 自动写 memory。
- Layer 0 validator 对 per-type 字段（如 chart `series.key` 必须出现在 data row）抛 ValueError；
  这类校验属于 primitive 内的渲染兜底或 Skill 自己的业务校验（见 ADR-010）。

---

## 4. UI Layering

### 4.1 Layer 0 — Generic primitives（原子能力底座）

generic primitives 是跨业务复用底座，对应 ADR-009 的 Layer 0 定位。

当前 allowlist：

- `MetricCard`
- `DataTable`
- `LineChart`
- `BarChart`
- `PieChart`
- `ChoiceList`

规则：

- generic primitive **不包含任何业务语义**（RM / CFA / 投资 / 笔记 等都不写进 primitive）。
- primitive 必须能从 mock fixture、inject endpoint、真实模型 emit 三种来源共同驱动。
- primitive 必须支持 best-effort 渲染：必填 props 缺失时显示空状态/警告，不抛异常。
- 新增 primitive 需要在本文档 allowlist 内登记。catalog 演进归属独立 issue，
  不与业务 consumer 的 issue 混合提交。

### 4.2 Layer 1 — Business consumers（应以 Skill 形式存在，而非代码）

Layer 1 是 Layer 0 之上的业务 consumer（RM 是第一个，未来还会有 CFA / 投资 / 日常
AI 生成 UI 等）。**目标态**：业务 consumer 的"预制组合"以 Skill prompt 资产形式存在，
不以专用 React 组件 + 专用后端分支形式硬编码（见 ADR-013）。

#### 目标态规则

- 业务 consumer 通过自己的 Skill 教模型如何用 Layer 0 primitive 组合出业务语义。
- 业务 consumer 的 schema 严格性（哪些字段必须存在）由该 Skill 自己负责，
  不下沉到 Layer 0 validator（见 ADR-010）。
- 业务 consumer 的结构化交互通过 Layer 0 的 pending_interaction.resolve 通道
  完成，不需要新协议。
- 新增业务 consumer 的第一反应应是"写 Skill"，而不是"写新 React 组件 / 加新
  contract 字段"。如果现有 catalog 不够表达，独立提案扩充 Layer 0 catalog。

#### 当前过渡态（保留至 Skill-driven Layer 1 migration issue）

当前 RM V0 surfaces 仍以 React 组件形式存在于 `frontend/src/rm/surfaces/`：

- `CustomerProfileCard`
- `ProductFitTable`
- `BriefExportPanel`
- `MemoryDiffCard`

后端 `api/rm_workbench/adapter.py:map_surface_to_a2ui_messages` 中对应的 RM 分支
属于 transitional 代码，**不要在它的基础上为新业务 consumer 添加新分支**。新业务
应直接走 Skill + `ui.blocks` 路径。

过渡期边界：

- 现有 RM surface 在迁移 issue 完成前继续工作，不要在本轮重构中删除。
- 不要为非 RM 业务（CFA / 投资 / 日常 UI）新建类似的 `frontend/src/<domain>/surfaces/` 目录或后端分支——这会复制 Layer 1 硬编码错误。
- 现有 RM surface 的 interaction payload 仍通过 pending interaction resolve 返回。

### 4.3 Frontend host rule

后续 issue 不能只证明：

```text
frontend/ mock app 可以渲染
```

还必须逐步证明：

```text
主 WebUI chat path 可以渲染同一套 renderer
```

Issue 7.7 的 Layer 0 验收口径（见 ADR-007 修订段）：从主 WebUI chat 触发任意可达
通用 contract（mock-stream / inject endpoint / 真实模型调用），主 chat 路径里能
渲染至少 1 个 generic primitive，即满足 Layer 0 host rule。

---

## 5. Test Boundary

### 5.1 Backend adapter / contract changes

至少验证：

```bash
/Users/hywl/.hermes/hermes-agent/venv/bin/python -m pytest tests/test_rm_workbench_adapter.py tests/test_rm_workbench_routes.py -q
```

如果涉及 pending interaction：

```bash
/Users/hywl/.hermes/hermes-agent/venv/bin/python -m pytest tests/test_pending_interactions.py -q
```

### 5.2 Real stream bridge changes

至少验证：

```bash
/Users/hywl/.hermes/hermes-agent/venv/bin/python -m pytest tests/test_rm_workbench_real_stream_bridge.py -q
```

并补充真实 WebUI manual smoke。

### 5.3 Frontend renderer changes

至少验证：

```bash
cd frontend
npm run build
```

如果改真实 WebUI chat host，还必须补充真实 WebUI manual smoke。

### 5.4 Cross-repo tool registry changes

如果改 `/Users/hywl/hermes-agent` 的 tool registry / toolsets，至少验证：

```bash
cd /Users/hywl/hermes-agent
source venv/bin/activate
python -m pytest tests/tools/test_rm_workbench_tool.py tests/test_toolsets.py tests/test_model_tools.py -q
```

并在 `/Users/hywl/hermes-webui` 验证 bridge：

```bash
cd /Users/hywl/hermes-webui
/Users/hywl/.hermes/hermes-agent/venv/bin/python -m pytest tests/test_rm_workbench_real_stream_bridge.py -q
```

---

## 6. Issue Authoring Rule

后续 RM Workbench coding issue 必须写清：

- 读哪些 core docs。
- 改哪些 repo。
- 改哪些文件或目录。
- 明确不做什么。
- 要跑哪些 automated tests。
- 是否需要真实 WebUI manual smoke。
- smoke 证据贴在哪里。

推荐 issue body 最小结构：

```text
Goal
Files / ownership
Required docs
Implementation boundaries
Non-goals
Validation
Manual smoke evidence
Acceptance checklist
```

---

## 7. Review Rule

reviewer 验收时优先检查：

- 是否违反 Architecture Rules。
- 是否违反 ADR（特别是 ADR-009 ~ ADR-012 的 Layer 0 / Layer 1 分层）。
- 是否越过本 coding boundary。
- 是否只在 mock path 成立。
- 是否漏掉真实 WebUI smoke。
- 是否把 Layer 1 业务语义（RM 等）塞进 Layer 0 primitive 或 Layer 0 validator。
- 是否引入了多 render tools。
- 是否让 memory 自动写入。
- 是否在 Layer 0 路径上访问 RM 专属字段（如 `contract["customer"]`）。
- 是否在 issue body 里复制粘贴本文档已删除的 RM 化硬约束（例如重新引入
  `rm_workbench_emit_contract` 作为锁定项），违反 § 0.1 ADR 优先原则。

如果实现本身可运行，但违反边界，应该要求 rework，而不是把问题留给后续 workflow issue。
