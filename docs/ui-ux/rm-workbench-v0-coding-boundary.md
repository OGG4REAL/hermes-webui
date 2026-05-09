# RM Workbench V0 Coding Boundary

路径：`docs/ui-ux/rm-workbench-v0-coding-boundary.md`
状态：`active / coding boundary`
更新时间：`2026-05-09`
入口：`docs/ui-ux/rm-workbench-v0-index.md`

---

## 0. 这份文档负责什么

这份文档约束 RM Workbench V0 后续 issue 的代码改动边界。

它回答：

- 哪些目录负责哪些能力。
- runtime / streaming / frontend host 改动有哪些红线。
- structured UI contract 的入口在哪里。
- generic UI 与 RM semantic UI 怎么分层。
- 每类改动必须怎么验收。

它不负责：

- 重复 Architecture 的系统图。
- 重复 ADR 的技术取舍。
- 记录每个 issue 的过程。
- 指定完整业务 workflow 细节。

后续 Multica issue 如果涉及 RM Workbench 代码改动，默认需要引用这份文档。

---

## 1. Directory Ownership

### 1.1 Hermes Agent

路径：

```text
/Users/hywl/hermes-agent
```

职责：

- 注册模型可见 tools。
- 暴露 `rm_workbench_emit_contract` toolset。
- 维护 Hermes runtime / tool registry / Skill loading。

边界：

- 不在 hermes-agent 中实现 WebUI renderer。
- 不在 hermes-agent 中写 React / A2UI 组件。
- 不为每种 UI primitive 新增独立 tool。

### 1.2 hermes-webui backend

路径：

```text
/Users/hywl/hermes-webui/api/
```

职责：

- `api/streaming.py` 保留主 chat stream。
- `api/rm_workbench/` 负责 contract validation / adapter / emit helper。
- `api/pending_interactions.py` 负责 structured UI interaction pending / resolve。
- `api/routes.py` 只暴露必要的 debug / mock / resolve endpoints。

边界：

- backend 不从 assistant text 猜 UI。
- backend 不渲染 UI。
- backend 不等待前端交互；阻塞语义属于 runtime/tool execution 层。
- streaming callback 只做轻量 bridge，不能引入长阻塞。

### 1.3 React structured-UI host

路径：

```text
/Users/hywl/hermes-webui/frontend/src/
```

职责：

- `a2ui/` 负责通用 declarative UI renderer。
- `a2ui/primitives/` 负责 generic UI blocks。
- `agui/` 负责 AG-UI event reduce / state update。
- `rm/surfaces/` 负责 RM semantic surfaces。
- `api/` 负责与 hermes-webui backend 的 frontend client。

边界：

- mock app 和真实 WebUI chat path 必须共享 renderer。
- 不允许只在 mock path 能渲染，主 WebUI chat path 不可见。
- 不执行 LLM 生成的任意 JSX / HTML / remote JS。

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

V0 唯一 structured UI emit entrypoint：

```text
rm_workbench_emit_contract
```

工具参数形态：

```json
{
  "contract": {
    "surfaces": [],
    "pending_interactions": [],
    "memory_proposals": [],
    "ui": {
      "blocks": []
    }
  }
}
```

允许：

- RM semantic surfaces 进入 `surfaces`。
- generic UI primitives 进入 `ui.blocks`。
- pending interaction 只通过 `pending_interactions` 声明。
- memory 只通过 `memory_proposals` 声明。

禁止：

- 新增 `render_table` / `render_chart` / `render_form` / `render_card` tools。
- 让 frontend 从 assistant markdown 中抽表格或图表。
- 让 frontend 执行 contract 内的任意代码。
- 自动写 memory。

中期可以新增通用别名：

```text
emit_ui_contract
```

但 V0 继续以 `rm_workbench_emit_contract` 为主，避免 bridge 和 tool registry 同时漂移。

---

## 4. UI Layering

### 4.1 Generic primitives

generic primitives 是跨业务复用底座。

当前 allowlist：

- `MetricCard`
- `DataTable`
- `LineChart`
- `BarChart`
- `PieChart`
- `ChoiceList`

规则：

- generic primitive 不包含 RM 业务语义。
- generic primitive props 必须 schema-friendly。
- generic primitive 必须能从 mock fixture 和真实 `event: rm_workbench` 共同驱动。

### 4.2 RM semantic surfaces

RM semantic surfaces 是业务层。

当前 V0 surfaces：

- `CustomerProfileCard`
- `ProductFitTable`
- `BriefExportPanel`
- `MemoryDiffCard`

规则：

- RM surface 可以组合 generic primitives。
- RM surface 可以定义业务交互，例如 product selection、memory proposal review。
- RM surface 的 interaction payload 必须结构化，并通过 pending interaction resolve 返回。

### 4.3 Frontend host rule

后续 issue 不能只证明：

```text
frontend/ mock app 可以渲染
```

还必须逐步证明：

```text
主 WebUI chat path 可以渲染同一套 renderer
```

Issue 8 前的关键目标是把这个 host rule 做成立。

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
- 是否违反 ADR。
- 是否越过本 coding boundary。
- 是否只在 mock path 成立。
- 是否漏掉真实 WebUI smoke。
- 是否把 RM semantic logic 塞进 generic primitive。
- 是否引入了多 render tools。
- 是否让 memory 自动写入。

如果实现本身可运行，但违反边界，应该要求 rework，而不是把问题留给后续 workflow issue。
