# RM Workbench V0 Adapter Spike Harness

路径：`docs/ui-ux/rm-workbench-v0-spike/`
状态：`draft / executable mock`
目的：用最小 mock 链路验证 RM Skill structured output 能否被 adapter 映射成 AG-UI-compatible events、A2UI-like surfaces，以及 pending interaction resolve payload。

---

## 0. 这不是生产实现

这组文件只验证技术边界：

- RM Skill 从 V0 起输出结构化 contract。
- Adapter 只做 contract -> event/surface/action 映射。
- Adapter 不从自然语言里猜产品、按钮、图表或业务语义。
- 前端交互返回结构化 payload，而不是自然语言补充说明。

---

## 1. 文件说明

- `fixtures/rm-pre-meeting-brief.valid.json`
  - mock RM Skill output contract。
  - 覆盖 customer、memory references、product candidates、surfaces、pending interaction。

- `fixtures/product-selection.resolve.json`
  - mock RM 在 UI 中选择产品后的结构化返回。

- `mock_adapter_check.py`
  - 纯 Python 标准库脚本。
  - 校验 contract 基本字段。
  - 校验 surface/action 边界。
  - 模拟生成 AG-UI-compatible event transcript。
  - 校验 pending interaction resolve payload。

- `schemas/rm.pre_meeting_brief.v0.1.0.schema.json`
  - RM Skill output contract schema draft。

- `schemas/pending_interaction.resolve.v0.1.0.schema.json`
  - 前端 UI action resolve payload schema draft。

---

## 2. 怎么运行

在 `hermes-webui` repo 根目录运行：

```bash
python3 docs/ui-ux/rm-workbench-v0-spike/mock_adapter_check.py
```

预期输出：

```text
OK: validated RM Skill contract
OK: mapped 3 surfaces
OK: produced 9 AG-UI-compatible events
OK: resolved pending interaction pi_001 with 2 selected products
```

---

## 3. 这个 spike 验证什么

### 后到前

`rm-pre-meeting-brief.valid.json` 里的 `surfaces` 会被映射成 AG-UI `CUSTOM` events，其中 payload 是 A2UI-like `createSurface` / `updateComponents` / `updateDataModel` messages。

这验证的是：

```text
RM Skill structured contract -> adapter -> A2UI-like surface payload -> React renderer
```

### 前到后

`product-selection.resolve.json` 会被校验为 `pending_interaction.resolve` payload。

这验证的是：

```text
React UI action -> structured payload -> pending interaction resolve -> agent resumes
```

---

## 4. Spike 成功后再做什么

如果这条 mock 链路成立，下一步才进入正式 implementation plan：

1. 把 contract schema 放到正式目录。
2. 把 mock adapter 变成 hermes-webui 后端 adapter。
3. 把 mock surfaces 变成 React renderer catalog。
4. 把 pending interaction 从 mock state machine 变成后端状态模型。
5. 再评估 CopilotKit 哪些前端能力可以局部接入。
