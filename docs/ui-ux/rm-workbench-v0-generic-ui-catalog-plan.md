# RM Workbench V0 Generic UI Catalog Plan

路径：`docs/ui-ux/rm-workbench-v0-generic-ui-catalog-plan.md`
状态：`active / issue 7.6 planning`
更新时间：`2026-05-08`
入口：`docs/ui-ux/rm-workbench-v0-index.md`

---

## 0. 结论

Issue 8 之前需要先补一张 **Generic A2UI Renderer Catalog** issue。

原因：

- V0 的目标不是只证明 RM 定制组件能渲染，而是证明 Hermes 可以通过结构化 contract 生成常规 UI。
- 常规 UI 应该是通用底座，RM semantic surfaces 只是上层业务扩展。
- Agent 不应该生成 React code；Agent 只能选择 catalog item 并填写 structured props。
- 当前链路已经打通 `rm_workbench_emit_contract -> WebUI bridge -> rm_workbench SSE -> AG-UI CUSTOM -> A2UI messages -> React renderer`，所以这一步不应该新建一堆 `render_table` / `render_chart` tools。

建议 issue 名称：

```text
RM Workbench V0 Generic A2UI Renderer Catalog
```

建议 issue 编号：

```text
Issue 7.6
```

---

## 1. 架构定位

### 1.1 两层 catalog

V0 renderer 应该分成两层：

```text
Generic UI primitives
  DataTable
  MetricCard
  LineChart
  BarChart
  PieChart
  ChoiceList

RM semantic surfaces
  CustomerProfileCard
  ProductFitTable
  BriefExportPanel
  MemoryDiffCard
```

Generic UI primitives 是所有 Agent UI 场景都能复用的基础表达能力。

RM semantic surfaces 是 RM workflow 的业务组件，可以组合 generic primitives，也可以附带 RM-specific interaction semantics。

### 1.2 工具策略

V0 继续复用现有工具：

```text
rm_workbench_emit_contract
```

不要新增：

```text
render_table
render_chart
render_form
render_card
```

原因：

- 多个 UI tools 会让 Agent tool layer 膨胀。
- UI 表达应该通过一个 declarative contract 传递，而不是把每种组件都变成 function tool。
- 已有 bridge 和 smoke 证据都围绕 `rm_workbench_emit_contract`，Issue 7.6 应复用这条已验过的 runtime 链路。

中期可以新增更通用的工具名：

```text
emit_ui_contract
```

但这不是 Issue 7.6 要做的事。Issue 7.6 只需要在文档和代码里承认：`rm_workbench_emit_contract` 当前是 V0 bridge tool，payload 可以包含 generic UI blocks；未来可以迁移为 generic emit tool，RM tool 保留为兼容 alias 或 wrapper。

---

## 2. Contract 语义拓展

当前 contract 以 RM semantic surfaces 为主：

```json
{
  "kind": "rm.pre_meeting_brief",
  "surfaces": [
    {
      "id": "surface_product_fit",
      "surface": "ProductFitTable",
      "props": {}
    }
  ]
}
```

Issue 7.6 需要允许同一 contract 中出现 generic UI blocks：

```json
{
  "kind": "rm.pre_meeting_brief",
  "version": "0.1.0",
  "run_id": "run_001",
  "thread_id": "thread_rm_001",
  "ui": {
    "blocks": [
      {
        "id": "metric_total_aum",
        "type": "MetricCard",
        "props": {
          "label": "客户 AUM",
          "value": "1200 万",
          "delta": "+8.2%",
          "tone": "positive"
        }
      },
      {
        "id": "allocation_table",
        "type": "DataTable",
        "props": {
          "columns": [
            { "key": "asset", "label": "资产类别" },
            { "key": "weight", "label": "当前占比" },
            { "key": "target", "label": "建议占比" }
          ],
          "rows": [
            { "asset": "固收", "weight": "55%", "target": "50%" },
            { "asset": "权益", "weight": "25%", "target": "30%" },
            { "asset": "现金", "weight": "20%", "target": "20%" }
          ]
        }
      },
      {
        "id": "allocation_pie",
        "type": "PieChart",
        "props": {
          "title": "建议资产配置",
          "labelKey": "asset",
          "valueKey": "target_weight",
          "data": [
            { "asset": "固收", "target_weight": 50 },
            { "asset": "权益", "target_weight": 30 },
            { "asset": "现金", "target_weight": 20 }
          ]
        }
      }
    ]
  },
  "surfaces": [
    {
      "id": "surface_product_fit",
      "surface": "ProductFitTable",
      "props": {}
    }
  ],
  "pending_interactions": []
}
```

### 2.1 V0 block allowlist

Issue 7.6 只做以下 allowlist：

- `MetricCard`
- `DataTable`
- `LineChart`
- `BarChart`
- `PieChart`
- `ChoiceList`

`Form` 暂不进最小集。原因是 Form 会自然引出 schema validation、field-level errors、draft state、submit action 等问题，容易把 Issue 7.6 扩成另一个 pending interaction project。

### 2.2 Data rules

必须验证：

- `id` 是非空 string。
- `type` 在 allowlist 内。
- `props` 是 object。
- chart 的 `data` 是 non-empty array。
- chart 的 key 字段必须存在于每条 data row。
- `DataTable.columns` 是 non-empty array，`rows` 是 array。
- `ChoiceList.options` 是 non-empty array。

不做：

- 不支持任意 JSX / HTML。
- 不支持自定义 CSS。
- 不支持远程 JS。
- 不支持用户上传图表组件。

---

## 3. Adapter Mapping

Issue 7.6 应继续使用：

```text
AG-UI CUSTOM name = a2ui.surface.messages
```

generic UI block 应映射成 A2UI message：

```json
[
  {
    "version": "v0.9",
    "createSurface": {
      "surfaceId": "generic_allocation_pie",
      "catalogId": "generic-ui-v0"
    }
  },
  {
    "version": "v0.9",
    "updateComponents": {
      "surfaceId": "generic_allocation_pie",
      "components": [
        {
          "id": "generic_allocation_pie_root",
          "component": "PieChart",
          "props": {
            "title": "建议资产配置",
            "labelKey": "asset",
            "valueKey": "target_weight"
          }
        }
      ]
    }
  },
  {
    "version": "v0.9",
    "updateDataModel": {
      "surfaceId": "generic_allocation_pie",
      "path": "/",
      "data": {
        "data": [
          { "asset": "固收", "target_weight": 50 },
          { "asset": "权益", "target_weight": 30 },
          { "asset": "现金", "target_weight": 20 }
        ]
      }
    }
  }
]
```

前端 renderer 根据 A2UI component 的 `component` 字段渲染 generic primitive，而不是根据 RM semantic surface 名称渲染。

---

## 4. 建议修改范围

### Backend

- `api/rm_workbench/contracts.py`
  - 增加 `ui.blocks` validation。
  - 增加 generic block allowlist。
  - 保留现有 RM semantic surface validation。
- `api/rm_workbench/adapter.py`
  - 将 `ui.blocks` 转成 AG-UI CUSTOM / A2UI messages。
  - 保持现有 `surfaces` mapping 不破坏。
- `api/rm_workbench/mock_data.py`
  - mock fixture loader 无需大改；只要能加载拓展后的 fixture。
- `docs/ui-ux/rm-workbench-v0-spike/fixtures/rm-pre-meeting-brief.valid.json`
  - 增加 `ui.blocks` demo 数据。
- `tests/test_rm_workbench_adapter.py`
  - 覆盖 generic blocks -> A2UI messages。
- `tests/test_rm_workbench_mock_stream.py`
  - 覆盖 mock stream 中出现 generic chart/table events。

### Frontend

- `frontend/package.json`
  - 增加一个 chart library。建议用 `recharts`，原因是 React 生态成熟、API 简单，足够 V0。
- `frontend/src/a2ui/types.ts`
  - 增加 generic component props 类型。
- `frontend/src/a2ui/A2UISurfaceRenderer.tsx`
  - 支持 generic component rendering。
  - 保持现有 RM semantic surface rendering。
- `frontend/src/a2ui/primitives/DataTable.tsx`
- `frontend/src/a2ui/primitives/MetricCard.tsx`
- `frontend/src/a2ui/primitives/LineChartBlock.tsx`
- `frontend/src/a2ui/primitives/BarChartBlock.tsx`
- `frontend/src/a2ui/primitives/PieChartBlock.tsx`
- `frontend/src/a2ui/primitives/ChoiceList.tsx`
  - 新增 minimal generic primitives。
- `frontend/src/fixtures/rmWorkbenchTranscript.ts`
  - 增加 generic UI demo events，作为 backend mock stream 不可用时的 fallback。

### Static WebUI bridge

- `static/messages.js`
  - 不需要新增协议。
  - 保留 `event: rm_workbench` -> `window.__rmWorkbenchEvent`。

### Hermes Agent

- 不需要改 runtime。
- 不需要新增 tool。
- 如有必要，只更新 `tools/rm_workbench_tool.py` 的 docstring / schema description，说明 payload 可包含 generic UI blocks。

---

## 5. 验收标准

### 自动化验收

```bash
cd /Users/hywl/hermes-webui
/Users/hywl/.hermes/hermes-agent/venv/bin/python -m pytest tests/test_rm_workbench_adapter.py tests/test_rm_workbench_mock_stream.py -q

cd /Users/hywl/hermes-webui/frontend
npm run build
```

如果改了 contract validation，再补：

```bash
cd /Users/hywl/hermes-webui
/Users/hywl/.hermes/hermes-agent/venv/bin/python -m pytest tests/test_rm_workbench_routes.py tests/test_rm_workbench_real_stream_bridge.py -q
```

### 人工 smoke

必须保留一次真实可见 UI 证据：

```text
启动 backend mock stream
启动 React workbench
观察到至少：
  1. MetricCard
  2. DataTable
  3. LineChart 或 BarChart
  4. PieChart
  5. 现有 ProductFitTable 仍可选择并 resolve
```

如果本 issue 改到真实 `/api/chat/stream` 消费路径，则还必须满足 runtime/streaming issue 门槛：

```text
从 WebUI 真实 chat 触发
  -> 观察到预期 tool call 或 SSE event
  -> 观察到预期 UI 渲染或明确错误 surface
```

Issue comment 中必须包含截图或 SSE log。

---

## 6. 明确不做

- 不实现第一条真实 `pre_meeting_brief` workflow。
- 不要求模型在真实 business prompt 下稳定调用 tool。
- 不做 Memory 自动写入。
- 不引入 CopilotKit runtime。
- 不重写 `/api/chat/stream` top-level protocol。
- 不引入任意代码生成 / JSX 执行。
- 不把 `DataTable` / `LineChart` / `PieChart` 拆成多个 Hermes tools。
- 不接真实客户数据或真实产品池。

---

## 7. 完成后的状态

Issue 7.6 完成后，V0 基建应证明：

```text
Hermes can emit structured UI parameters
  -> WebUI adapter can convert them to AG-UI/A2UI
  -> React can render generic financial UI primitives
  -> RM semantic surfaces still work
```

这时再进入 Issue 8，Issue 8 才专注验证：

```text
RM Skill.md can guide a real business workflow
  -> model chooses when to emit UI contract
  -> RM interaction returns structured input
  -> Agent continues reasoning after user selection
```

