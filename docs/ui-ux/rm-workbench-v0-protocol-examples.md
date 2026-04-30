# RM Workbench V0：协议样例草案

> 路径：`docs/ui-ux/rm-workbench-v0-protocol-examples.md`
> 状态：`reference / illustrative examples`
> 前置文档：`docs/ui-ux/rm-workbench-v0-technical-skeleton.md`
> 目的：用具体 JSON/TypeScript 样例说明 V0 中 Skill、A2UI surface、AG-UI event、pending interaction、memory proposal 如何串起来。
> V0 入口：`docs/ui-ux/rm-workbench-v0-index.md`

> 注意：本文是样例参考。若与 `rm-workbench-v0-agui-a2ui-alignment.md` 或 `rm-workbench-v0-implementation-plan.md` 冲突，以后两者为准。

---

## 0. 本文原则

本文不是 implementation plan，也不是最终协议规范。

本文只做三件事：

1. 把规划文档里的抽象概念落成可讨论样例
2. 暴露 adapter 实现时需要验证的问题
3. 为下一步 implementation plan 提供输入

V0 采用：

```text
Hermes runtime
  -> hermes-webui backend
  -> AG-UI-compatible adapter
  -> A2UI fixed catalog / surfaces
  -> React workbench
```

---

## 1. Catalog 分层

V0 catalog 分为两层。

### 1.1 Common primitives

这些是通用 UI 能力，不算 RM 业务语义组件。

候选：

```text
Text
Card
Row
Column
Button
Form
Input
Select
Checkbox
Table
LineChart
BarChart
PieChart
Metric
Badge
Tabs
```

这些可以来自 A2UI Basic Catalog，也可以来自我们自己的 common catalog。

### 1.2 RM semantic surfaces

这些是 RM 工作流语义组件。

V0 第一批：

```text
CustomerProfileCard
ProductFitTable
PerformanceChart
MemoryDiffCard
BriefExportPanel
```

关系：

```text
ProductFitTable
  uses Table / Badge / Button / Metric primitives

PerformanceChart
  uses LineChart / BarChart / Metric primitives

MemoryDiffCard
  uses Card / Table / Button primitives
```

---

## 2. Skill Output Example

RM Skill 不只返回自然语言。

Adapter 不能从自然语言里猜 UI。RM Skill 必须从 V0 开始输出结构化 contract。

正确边界：

```text
RM Skill decides semantic output
        ↓
adapter maps contract to AG-UI/A2UI
        ↓
frontend renders and returns interactions
```

错误边界：

```text
RM Skill returns prose only
        ↓
adapter guesses products / surfaces / actions from prose
```

这与 `ai_sandbox` 的计算 / 展示分离逻辑一致，只是 V0 中不要求 Agent 再调用单独的 UI tool；RM Skill 直接返回 surface/action contract。

`pre_meeting_brief` 的输出应至少包含：

- summary text
- A2UI surface operations
- optional pending interaction
- optional memory proposals
- report artifact placeholder

示例：

```json
{
  "skill_id": "pre_meeting_brief",
  "run_id": "skillrun_20260428_001",
  "status": "waiting_for_input",
  "text": "已生成王总的访前准备摘要，并筛出 5 个候选产品。请确认本次拜访重点和拟纳入沟通的产品。",
  "a2ui_surfaces": [
    {
      "surface_id": "customer_profile:customer_wang",
      "catalog_id": "urn:rm-workbench:catalog:v0",
      "operations_ref": "#surface.customer_profile"
    },
    {
      "surface_id": "product_fit:customer_wang:brief_001",
      "catalog_id": "urn:rm-workbench:catalog:v0",
      "operations_ref": "#surface.product_fit_table"
    }
  ],
  "pending_interactions": [
    {
      "interaction_id": "pi_select_products_001",
      "surface_id": "product_fit:customer_wang:brief_001",
      "kind": "select_products",
      "mode": "blocking",
      "prompt": "请从候选产品中选择 1-3 个用于本次拜访沟通。",
      "expected_schema": {
        "type": "object",
        "required": ["selected_product_ids"],
        "properties": {
          "selected_product_ids": {
            "type": "array",
            "items": { "type": "string" },
            "minItems": 1,
            "maxItems": 3
          },
          "notes": { "type": "string" },
          "constraints": { "type": "object" }
        }
      }
    }
  ],
  "memory_proposals": [],
  "artifacts": [
    {
      "artifact_id": "brief_draft_001",
      "kind": "brief",
      "status": "draft"
    }
  ]
}
```

说明：

- `operations_ref` 只是本文内引用，真实实现应内联或流式发送 A2UI operations。
- `pending_interactions` 是 Hermes adapter 的抽象，不是 A2UI 本身。
- blocking interaction 类似 clarify 的泛化版，但语义不是 clarify。

---

## 3. A2UI Surface Example: CustomerProfileCard

下面是示意，不是最终 A2UI schema。

重点是表达：

- create surface
- choose catalog
- update data model
- update components
- begin rendering

```json
[
  {
    "version": "v0.9",
    "createSurface": {
      "surfaceId": "customer_profile:customer_wang",
      "catalogId": "urn:rm-workbench:catalog:v0",
      "sendDataModel": true
    }
  },
  {
    "version": "v0.9",
    "updateDataModel": {
      "surfaceId": "customer_profile:customer_wang",
      "value": {
        "customer": {
          "id": "customer_wang",
          "display_name": "王总",
          "risk_preference": "稳健型",
          "investment_goal": ["财富保值", "传承"],
          "liquidity_need": "中",
          "hidden_profile": "传统制造业企业主，对安全感和控制感要求高。",
          "communication_risks": ["反感强推销", "不希望被当成理财小白"]
        }
      }
    }
  },
  {
    "version": "v0.9",
    "updateComponents": {
      "surfaceId": "customer_profile:customer_wang",
      "components": [
        {
          "id": "root",
          "component": "CustomerProfileCard",
          "dataPath": "/customer",
          "actions": [
            {
              "id": "confirm_profile",
              "label": "确认画像可用",
              "kind": "submit"
            },
            {
              "id": "edit_profile",
              "label": "补充画像",
              "kind": "open"
            }
          ]
        }
      ]
    }
  },
  {
    "version": "v0.9",
    "beginRendering": {
      "surfaceId": "customer_profile:customer_wang"
    }
  }
]
```

实现待验证：

- A2UI v0.9 中 `updateComponents` / `updateDataModel` 字段名和 renderer 支持情况。
- `actions` 是否放在 component schema 内，还是映射为 A2UI function/action。
- `sendDataModel` 回传如何进入 AG-UI / CopilotKit metadata。

---

## 4. A2UI Surface Example: ProductFitTable

ProductFitTable 是 RM semantic surface。

它内部可由通用 primitives 组成，但对 agent 来说只暴露一个高层组件。

```json
[
  {
    "version": "v0.9",
    "createSurface": {
      "surfaceId": "product_fit:customer_wang:brief_001",
      "catalogId": "urn:rm-workbench:catalog:v0",
      "sendDataModel": true
    }
  },
  {
    "version": "v0.9",
    "updateDataModel": {
      "surfaceId": "product_fit:customer_wang:brief_001",
      "value": {
        "customer_id": "customer_wang",
        "constraints": {
          "max_risk_level": "R3",
          "liquidity": "T+1 or better",
          "preferred_horizon_months": 6
        },
        "products": [
          {
            "id": "prod_001",
            "name": "稳健添利 6 个月",
            "risk_level": "R2",
            "expected_return": 0.032,
            "max_drawdown": 0.004,
            "liquidity": "6个月封闭",
            "score": 87,
            "reasons": ["风险等级匹配", "回撤较低", "期限接近本次资金安排"]
          },
          {
            "id": "prod_002",
            "name": "现金管理增强 T+1",
            "risk_level": "R1",
            "expected_return": 0.021,
            "max_drawdown": 0.001,
            "liquidity": "T+1",
            "score": 81,
            "reasons": ["流动性好", "适合保留备用资金"]
          }
        ],
        "selected_product_ids": []
      }
    }
  },
  {
    "version": "v0.9",
    "updateComponents": {
      "surfaceId": "product_fit:customer_wang:brief_001",
      "components": [
        {
          "id": "root",
          "component": "ProductFitTable",
          "dataPath": "/",
          "actions": [
            {
              "id": "select_products",
              "label": "确认选择",
              "kind": "submit",
              "interaction_id": "pi_select_products_001"
            },
            {
              "id": "edit_constraints",
              "label": "调整约束",
              "kind": "open"
            }
          ]
        }
      ]
    }
  },
  {
    "version": "v0.9",
    "beginRendering": {
      "surfaceId": "product_fit:customer_wang:brief_001"
    }
  }
]
```

---

## 5. AG-UI Mapping Example

Hermes WebUI 现有 SSE events 不直接暴露给 React workbench。

V0 adapter 应把它们映射为 AG-UI-compatible events。

示意：

```json
[
  {
    "type": "RUN_STARTED",
    "runId": "run_001",
    "threadId": "session_abc"
  },
  {
    "type": "TEXT_MESSAGE_START",
    "messageId": "msg_001",
    "role": "assistant"
  },
  {
    "type": "TEXT_MESSAGE_CONTENT",
    "messageId": "msg_001",
    "delta": "我先读取客户画像和产品池..."
  },
  {
    "type": "TOOL_CALL_START",
    "toolCallId": "tool_001",
    "toolCallName": "pre_meeting_brief"
  },
  {
    "type": "TOOL_CALL_RESULT",
    "toolCallId": "tool_001",
    "result": {
      "a2ui_surfaces": ["customer_profile:customer_wang", "product_fit:customer_wang:brief_001"],
      "pending_interactions": ["pi_select_products_001"]
    }
  },
  {
    "type": "CUSTOM",
    "name": "a2ui.surface_operations",
    "value": {
      "surfaceId": "product_fit:customer_wang:brief_001",
      "operations": []
    }
  },
  {
    "type": "STATE_DELTA",
    "delta": {
      "current_customer_id": "customer_wang",
      "workflow_step": "select_products"
    }
  }
]
```

实现待验证：

- AG-UI event type 的准确命名，以实际 SDK 为准。
- A2UI operations 是作为 `CUSTOM` event、tool result，还是 CopilotKit render channel 发送。
- pending interaction 如何表达成 interrupt / frontend action / custom event。

---

## 6. Non-Blocking Event Example

RM 在产品表中临时选中产品、调整筛选，不要求 agent 停下。

```json
{
  "type": "CUSTOM",
  "name": "rm.product_fit.selection_changed",
  "threadId": "session_abc",
  "runId": "run_001",
  "value": {
    "surface_id": "product_fit:customer_wang:brief_001",
    "selected_product_ids": ["prod_001", "prod_002"],
    "filters": {
      "risk_level": ["R1", "R2"],
      "liquidity": "T+1 or better"
    },
    "occurred_at": "2026-04-28T10:30:00+08:00"
  }
}
```

Adapter 行为：

- 更新 workspace/page state
- 不 resume agent
- 可作为下一次 user message 或 action 的 context

---

## 7. Blocking Pending Interaction Example

Agent 等 RM 选择产品后再继续生成话术。

### 7.1 Backend creates pending interaction

```json
{
  "interaction_id": "pi_select_products_001",
  "session_id": "session_abc",
  "run_id": "run_001",
  "kind": "select_products",
  "mode": "blocking",
  "surface_id": "product_fit:customer_wang:brief_001",
  "prompt": "请从候选产品中选择 1-3 个用于本次拜访沟通。",
  "expected_schema": {
    "type": "object",
    "required": ["selected_product_ids"],
    "properties": {
      "selected_product_ids": {
        "type": "array",
        "items": { "type": "string" },
        "minItems": 1,
        "maxItems": 3
      },
      "notes": { "type": "string" },
      "constraints": { "type": "object" }
    }
  }
}
```

### 7.2 Frontend submits response

```json
{
  "interaction_id": "pi_select_products_001",
  "session_id": "session_abc",
  "surface_id": "product_fit:customer_wang:brief_001",
  "action": "select_products",
  "value": {
    "selected_product_ids": ["prod_001", "prod_002"],
    "notes": "王总更关心稳健和流动性，先不推荐波动较高的权益类产品。",
    "constraints": {
      "max_risk_level": "R2",
      "liquidity": "T+1 or 6-month lockup"
    }
  },
  "submitted_at": "2026-04-28T10:31:00+08:00"
}
```

### 7.3 Adapter resolves

Adapter 校验 schema 后，把结果交回 Hermes pending interaction：

```json
{
  "resolved": true,
  "interaction_id": "pi_select_products_001",
  "tool_result_or_resume_payload": {
    "selected_product_ids": ["prod_001", "prod_002"],
    "rm_notes": "王总更关心稳健和流动性，先不推荐波动较高的权益类产品。",
    "active_constraints": {
      "max_risk_level": "R2",
      "liquidity": "T+1 or 6-month lockup"
    }
  }
}
```

Hermes agent 随后继续生成：

- 推荐理由
- 拜访话术
- 风险提示
- brief draft

---

## 8. Memory Proposal Example

Memory 不能静默写入。

Agent 只能提出 proposal。

```json
{
  "proposal_id": "memprop_001",
  "target_type": "customer",
  "target_id": "customer_wang",
  "changes": [
    {
      "path": "/communication_risks",
      "operation": "add",
      "new_value": "反感被当成理财小白，需要以企业经营视角解释资产配置。",
      "evidence": "RM 在本次准备中确认：王总希望掌控感，不喜欢强推销。"
    },
    {
      "path": "/liquidity_preference",
      "operation": "update",
      "old_value": "未知",
      "new_value": "中等，接受部分 6 个月封闭，但需保留 T+1 备用资金。",
      "evidence": "RM 在产品选择中排除长期封闭产品，并补充流动性约束。"
    }
  ],
  "confidence": 0.78,
  "rationale": "该信息来自 RM 对客户沟通策略和产品约束的显式确认，适合写入客户画像，但仍需人工确认。",
  "source": {
    "kind": "ui_confirmation",
    "session_id": "session_abc",
    "surface_id": "product_fit:customer_wang:brief_001"
  }
}
```

前端渲染 `MemoryDiffCard`。

RM 可以：

- approve
- reject
- edit

```json
{
  "proposal_id": "memprop_001",
  "decision": "approve",
  "approved_by": "rm_demo_user",
  "responded_at": "2026-04-28T10:35:00+08:00"
}
```

---

## 9. Open Questions Before Implementation

进入 implementation plan 前必须验证：

1. AG-UI SDK 中标准 event type 的准确名称和可扩展方式
2. CopilotKit 对 AG-UI custom event / interrupt / frontend action 的支持边界
3. A2UI v0.9 renderer 是否已足够成熟，是否需要自建 React renderer
4. A2UI operations 通过 AG-UI 的最佳承载方式
5. pending interaction 应复用 Hermes clarify callback 底层，还是新增独立 callback
6. RM Skill output contract 的 JSON schema 放在哪里维护：`hermes-webui` adapter 层先维护，还是新建独立 shared package

---

## 10. Next Document

如果本文方向确认，下一份应写：

```text
rm-workbench-v0-implementation-plan.md
```

它应覆盖：

- adapter endpoint
- pending interaction store
- React workbench scaffold
- common catalog primitives
- RM semantic catalog
- first vertical slice
- test plan
