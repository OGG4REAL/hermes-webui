# RM Agent-Native Workbench V0: Adapter Spike Plan

路径：`docs/ui-ux/rm-workbench-v0-adapter-spike-plan.md`
状态：`reference / completed technical spike plan`
目的：在正式 implementation plan 之前，用最小闭环验证 Hermes runtime 主导、AG-UI/A2UI adapter、React workbench host、RM Skill structured output contract 这条路线是否成立。
V0 入口：`docs/ui-ux/rm-workbench-v0-index.md`

注意：本文保留 spike 推演过程。工程执行以 `rm-workbench-v0-implementation-plan.md` 为准。

---

## 0. 这份文档要解决什么

V0 现在不是要马上做完整理财经理工作台，也不是要把 Pre-Meeting、KYC、资产配置、报告导出都做出来。

这一步只验证一个问题：

> 在不让 CopilotKit runtime 接管 Hermes 的前提下，Hermes Agent / Skill 的结构化输出，能否通过 adapter 转成 AG-UI event + A2UI surface，并让 React workbench 完成一次双向 UI 交互。

验证通过后，再写 implementation plan。验证不通过，再决定是加深 CopilotKit runtime 接入，还是调整 adapter 边界。

---

## 1. 当前已确定前提

### 1.1 Runtime 与事实源

- Hermes Agent 继续作为 agent runtime。
- hermes-webui 继续作为后端事实源。
- React 作为新的 RM workbench host。
- CopilotKit 不作为 V0 主 runtime，只评估其 React/AG-UI/A2UI 相关能力能否局部复用。

### 1.2 协议与 adapter

- AG-UI 负责 agent run / tool / state / user interaction 的事件轨道。
- A2UI 负责后端到前端的 UI surface 描述与渲染 catalog。
- Adapter 负责把 Hermes/RM Skill structured output 映射到 AG-UI/A2UI。
- Adapter 不负责从自然语言里猜 UI，也不负责“理解业务语义”。

### 1.3 RM Skill output contract

V0 起 RM Skill 就必须返回结构化 contract。

正确边界：

```text
RM Skill decides semantic output
  -> adapter maps to AG-UI/A2UI
  -> React renders surfaces and returns interactions
  -> Hermes resumes reasoning with structured input
```

错误边界：

```text
RM Skill returns prose only
  -> adapter guesses products / charts / buttons from prose
  -> frontend renders guessed UI
```

---

## 2. Spike 总验收闭环

最小闭环只做一个 mock scenario：

> Pre-Meeting Brief with Product Fit

完整路径：

1. Mock RM Skill 返回结构化 `pre_meeting_brief` contract。
2. Adapter 把 contract 转成 AG-UI-compatible events。
3. Adapter 同时生成 A2UI surfaces：
   - `CustomerProfileCard`
   - `ProductFitTable`
   - `BriefExportPanel`
4. React workbench 渲染 surfaces。
5. RM 在 `ProductFitTable` 里选择 1-3 个产品。
6. 前端发回 `pending_interaction.resolve`。
7. Hermes/RM Skill mock runner 收到结构化 selection payload。
8. Adapter 继续发出下一段 AG-UI event，例如更新 brief 或生成导出 panel。

验收标准：

- UI 不是从自然语言解析出来的，而是从 RM Skill structured contract 映射出来的。
- 后到前 surfaces 和前到后 actions 能走同一条 run/session 关联。
- 阻塞式交互不塞进 `clarify`，而是走独立 pending interaction。
- 普通状态展示不伪装成 pending interaction。
- CopilotKit 能局部复用则记录复用点；不能复用则明确不进入 V0 主链路。

---

## 3. Spike 1：AG-UI Event Mapping

### 目标

验证 Hermes run lifecycle 能否映射到 AG-UI-compatible event stream。

### 输入

Mock Hermes raw event sequence：

```json
[
  {
    "type": "hermes.run.started",
    "run_id": "run_001",
    "thread_id": "thread_rm_001"
  },
  {
    "type": "hermes.skill.started",
    "skill": "pre_meeting_brief"
  },
  {
    "type": "hermes.skill.output",
    "skill": "pre_meeting_brief",
    "contract": {
      "kind": "rm.pre_meeting_brief",
      "version": "0.1.0"
    }
  },
  {
    "type": "hermes.pending_interaction.created",
    "interaction_id": "pi_001",
    "action": "select_products"
  }
]
```

### 输出

AG-UI-compatible stream transcript，包含：

- `RUN_STARTED` / `RUN_FINISHED`
- text or message delta
- `TOOL_CALL_*` for tool lifecycle when needed
- `STEP_STARTED` / `STEP_FINISHED` for skill lifecycle
- `CUSTOM name = a2ui.surface.messages` for surface messages
- `CUSTOM name = rm.pending_interaction.created` for pending interaction
- `STATE_DELTA` for pending interaction state
- `RUN_ERROR` for error event

### 需要验证

- AG-UI 标准事件能覆盖哪些 Hermes lifecycle。
- Hermes 独有字段放进 custom event，还是放进 metadata。
- surface events 是否跟 A2UI operation 绑定，还是只作为 state/message 的一部分。
- event ordering 是否足够表达“先展示 UI，再等待 RM 输入，再继续推理”。

### 产物

- 一份 event mapping table。
- 一份 mock transcript。
- 一个不能被标准事件覆盖的字段清单。

---

## 4. Spike 2：A2UI Surface Rendering

### 目标

验证 A2UI surface catalog 能覆盖 RM V0 首批后到前渲染。

### 输入

RM Skill structured contract：

```json
{
  "kind": "rm.pre_meeting_brief",
  "version": "0.1.0",
  "customer": {
    "id": "cust_001",
    "name": "Mock Customer",
    "risk_level": "R3",
    "aum": 3200000
  },
  "surfaces": [
    {
      "surface": "CustomerProfileCard",
      "props": {
        "customer_id": "cust_001"
      }
    },
    {
      "surface": "ProductFitTable",
      "props": {
        "selectable": true,
        "max_selection": 3
      }
    }
  ]
}
```

### 输出

A2UI operation / surface payload，并由 React renderer 渲染。

### 需要验证

- 通用 UI primitives 是否足够：
  - table
  - form
  - card
  - button
  - line chart
  - bar chart
  - pie chart
  - panel
- RM semantic surfaces 是否只保留业务语义：
  - `CustomerProfileCard`
  - `ProductFitTable`
  - `PerformanceChart`
  - `MemoryDiffCard`
  - `BriefExportPanel`
- Surface props 是否能保持稳定，不把业务逻辑塞进前端组件。
- 图表/表格是否走 common primitives，而不是每个 RM surface 重造一套图表协议。

### 产物

- 首批 common primitive catalog。
- 首批 RM semantic surface catalog。
- 两个可渲染 mock payload：
  - `CustomerProfileCard`
  - `ProductFitTable`

---

## 5. Spike 3：Pending Interaction

### 目标

验证结构化 UI 输入可以独立于 approval / clarify 工作。

### 输入

`ProductFitTable` action：

```json
{
  "action": "select_products",
  "interaction_id": "pi_001",
  "blocking": true,
  "schema": {
    "type": "object",
    "properties": {
      "selected_product_ids": {
        "type": "array",
        "items": {
          "type": "string"
        },
        "minItems": 1,
        "maxItems": 3
      }
    },
    "required": ["selected_product_ids"]
  }
}
```

### 输出

Pending interaction lifecycle：

```text
created -> rendered -> submitted -> validated -> resolved -> agent resumed
```

### 需要验证

- pending interaction store 放在 hermes-webui 后端，还是 adapter 内部先做临时实现。
- interaction 与 run/thread/session 的绑定方式。
- cancel / timeout / invalid payload 的处理。
- non-blocking UI event 和 blocking pending interaction 的区别。
- 是否可以复用 Hermes 现有 approval/clarify 的 transport、wait/resume、状态持久化能力，但不复用它们的语义模型。

### 产物

- pending interaction state machine。
- payload schema。
- cancel/timeout/error 行为定义。

---

## 6. Spike 4：RM Skill Output Contract

### 目标

把 RM Skill 的输出 contract 从概念变成可校验 schema。

### 输入

Mock `pre_meeting_brief` result，包含：

- customer summary
- memory references
- product candidates
- suitability reasons
- required RM action
- exportable brief sections

### 输出

- JSON schema。
- sample valid payload。
- sample invalid payload。
- adapter mapping rule。

### 需要验证

- Schema 放在哪里维护：
  - 先放在 hermes-webui adapter 层；
  - 还是新建 shared package；
  - 还是跟 Hermes Skill registry 绑定。
- RM Skill contract 与 A2UI surface props 的边界：
  - Skill 输出业务事实和推荐结构；
  - Surface props 只负责展示所需字段；
  - Adapter 做字段投影，不做业务判断。
- 是否需要 `contract_version` 和 `surface_version` 分开。

### 产物

- `rm.pre_meeting_brief@0.1.0` schema draft。
- contract -> AG-UI/A2UI mapping rule。
- 不允许 adapter 猜测自然语言的约束说明。

---

## 7. Spike 5：CopilotKit Boundary

### 目标

确认 CopilotKit 在 V0 中到底能局部接到哪一层。

### 要验证的接入方式

#### 方式 A：Hermes runtime 主导

CopilotKit 只作为 React/interaction 层参考或局部组件来源：

```text
Hermes runtime
  -> adapter
  -> AG-UI/A2UI-compatible stream
  -> React workbench
```

验证点：

- 是否能复用 CopilotKit 前端组件而不接管 runtime。
- 是否能复用其 AG-UI/A2UI 相关 adapter 或 hooks。
- 如果必须依赖 CopilotKit runtime，哪些能力不能进入 V0 主链路。

#### 方式 B：CopilotKit runtime sidecar

CopilotKit runtime 作为 sidecar，只接 UI interaction，不作为 Hermes 主 runtime：

```text
Hermes runtime
  -> Hermes-CopilotKit adapter
  -> CopilotKit runtime sidecar
  -> React workbench
```

验证点：

- 是否会引入双 runtime 状态不一致。
- 是否会让 Hermes 的 approval/clarify/pending interaction 被绕过。
- 是否值得为了前端集成便利承担 runtime adapter 成本。

### 产物

- CopilotKit V0 接入建议：
  - `use`
  - `reference only`
  - `defer`
- 必须接入 CopilotKit runtime 才能获得的能力清单。
- 不接 CopilotKit runtime 时仍可实现的能力清单。

---

## 8. Spike 后决策门

Spike 完成后，只需要拍板这些问题：

1. AG-UI 作为 V0 interaction/event rail 是否成立。
2. A2UI 作为 V0 surface/rendering catalog 是否成立。
3. Pending interaction 是否在 hermes-webui 后端落一个独立抽象。
4. RM Skill output contract 是否先放在 hermes-webui adapter 层维护。
5. CopilotKit 在 V0 是：
   - React 层局部复用；
   - sidecar runtime；
   - 暂时只做参考。

---

## 9. 暂不进入 Spike 的内容

这些内容重要，但不在 adapter spike 里解决：

- 完整理财经理工作台 UI 设计。
- 真实客户数据接入。
- 真实产品池与风控适配。
- 完整资产配置算法。
- Memory 写入策略。
- 报告导出的最终版式。
- Hermes Agent runtime 深层重构。
- CopilotKit runtime 全量替换 Hermes runtime。

---

## 10. 下一份文档

如果这份 spike plan 没有方向性问题，下一份应该是：

```text
rm-workbench-v0-implementation-plan.md
```

但 implementation plan 必须等 spike 的关键结论明确后再写，否则会过早绑定具体技术细节。

当前 implementation plan 已落到：

```text
docs/ui-ux/rm-workbench-v0-implementation-plan.md
```

---

## 11. 当前可执行顺序

建议顺序：

1. 写 mock RM Skill output contract。
2. 写 contract -> AG-UI/A2UI mapping table。
3. 写 pending interaction state machine。
4. 验证 CopilotKit 是否能局部接入 React/AG-UI/A2UI。
5. 再写 implementation plan。

这条顺序的核心是先验证协议边界，再进入真实工程实现。

---

## 12. 当前 Spike Harness

已经补充一个可执行 mock harness：

```text
docs/ui-ux/rm-workbench-v0-spike/
```

包含：

- `fixtures/rm-pre-meeting-brief.valid.json`
  - mock RM Skill structured output contract。
- `fixtures/product-selection.resolve.json`
  - mock RM 在 UI 中选择产品后的 pending interaction resolve payload。
- `mock_adapter_check.py`
  - 校验 contract 基本结构。
  - 校验 surface catalog 白名单。
  - 模拟生成 AG-UI-compatible event transcript。
  - 校验 pending interaction resolve payload。

运行方式：

```bash
python3 docs/ui-ux/rm-workbench-v0-spike/mock_adapter_check.py
```

当前验证输出：

```text
OK: validated RM Skill contract
OK: mapped 3 surfaces
OK: produced 9 AG-UI-compatible events
OK: resolved pending interaction pi_001 with 2 selected products
```

注意：这里的 event names 还是 spike mock，不代表已经锁定 AG-UI SDK 的最终事件名。正式实现前需要再对照 AG-UI/A2UI 当前 SDK，把 mock event transcript 收敛成真实 adapter API。

对齐记录见：

```text
docs/ui-ux/rm-workbench-v0-agui-a2ui-alignment.md
```
