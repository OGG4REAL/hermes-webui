# RM Workbench V0 Roadmap

路径：`docs/ui-ux/rm-workbench-v0-roadmap.md`
状态：`active / sequencing`
更新时间：`2026-05-06`
入口：`docs/ui-ux/rm-workbench-v0-index.md`

---

## 0. Roadmap 目标

这份 roadmap 只回答三件事：

1. V0 现在已经做到哪一步。
2. 接下来应该先补哪条技术链。
3. 哪些事情现在不要提前做。

---

## 1. 当前已完成的阶段

### Phase 0: 技术骨架 + mock 到 real bridge

已完成：

- `MYM-24` Backend Adapter
- `MYM-25` Pending Interaction Backend
- `MYM-26` Frontend Smoke Workbench
- `MYM-27` Backend Mock Stream Integration
- `MYM-28` Real Hermes Stream Boundary Evaluation
- `MYM-29` Real Stream Bridge
- `MYM-30` Review RM Workbench V0 Real Stream Bridge
- `MYM-31` Hermes Agent rm_workbench_emit_contract Tool Registration
- `MYM-32` Review Hermes Agent rm_workbench_emit_contract Tool Registration

这一阶段结束后，已经确认：

- Hermes Agent 继续做 runtime。
- `hermes-webui` 继续做 backend source of truth。
- `/api/chat/stream` 保留现有 top-level SSE protocol。
- `rm_workbench` SSE event 是前端 workbench 的 hook point。
- `CUSTOM name = a2ui.surface.messages` 继续承载 A2UI message。
- 前端只消费 `event: rm_workbench` 且 `data.kind === "agui_events"`。
- Memory 继续是 proposal-first，不自动写入。

当前已经打通的最小链路：

- Hermes Agent 能真实暴露 `rm_workbench_emit_contract`
- Hermes WebUI real chat runs 会在支持时自动补上 `rm_workbench` toolset
- `MYM-29` 的 bridge 已经可以消费该 tool 的 completion

---

## 2. 下一步主线

### Phase 1: Runtime Alignment + Real Stream Readiness

建议作为 **Issue 7.5**。

目标：

```text
Align the Hermes Agent runtime path with the development repo, then prove the rm_workbench path through a real WebUI chat smoke before adding workflow logic.
```

为什么现在先做它：

- 双目录复盘显示真实 runtime 仍加载 `~/.hermes/hermes-agent`，而 MYM-31 改动落在 `~/hermes-agent`。
- unit test / mock-stream 已经证明协议形状，但没有证明真实 WebUI runtime 跑到同一份代码。
- 不先补这个，Issue 8 会一边修基础设施一边写 workflow，验收会继续混乱。

退出标准：

- runtime venv import 的 `tools` / `toolsets` 来自预期 agent 目录。
- `validate_toolset("rm_workbench") == True`。
- WebUI 真实 chat 能观察到 `rm_workbench_emit_contract` 可见，或观察到 `event: rm_workbench`。
- issue comment 中保留截图、SSE log、browser console log 或 server log。
- 修掉真实 stream 立刻会撞的 readiness 问题。

### Phase 2: First Real RM Workflow

建议作为 **Issue 8**。

目标：

```text
Implement one real RM workflow path driven by RM Skill.md + rm_workbench_emit_contract.
```

为什么现在轮到它：

- Issue 7.5 先证明 runtime 与 WebUI 真实链路可用。
- 之后最值得验证的是第一条真实 workflow，而不是继续停留在基础设施层。
- 这一阶段要验证 RM Skill.md、tool 调用时机、以及用户交互闭环是否真的成立。

退出标准：

- RM Skill.md 能指导 Agent 在正确节点 emit contract。
- 前端能看到真实 run 触发的 `CustomerProfileCard`。
- 前端能看到真实 run 触发的 `ProductFitTable`。
- 用户选择后能把结构化输入送回 run，Agent 继续下一步。

建议只做一个场景：

- `pre_meeting_brief`

### Phase 3: Memory Review Path

建议作为 **Issue 9**。

目标：

```text
Turn proposal-first memory into a reviewable human workflow, still without automatic writes.
```

这阶段才处理：

- `MemoryDiffCard` 的 review UX
- proposal approve / reject 状态
- 后续写入目标系统边界

### Phase 4: Productization

这阶段才考虑：

- 多 workflow 扩展
- 更完整的 chart / table / report catalog
- 真实客户数据接入
- artifact / export 深化
- CopilotKit frontend utility 是否有局部复用价值

---

## 3. 建议的 Issue 序列

### Issue 7

`Hermes Agent rm_workbench_emit_contract Tool Registration`

### Issue 7.5

`RM Workbench V0 Runtime Alignment + Real Stream Readiness`

### Issue 8

`RM Workbench V0 First Real Pre-Meeting Brief Workflow`

### Issue 9

`RM Workbench V0 Memory Proposal Review Flow`

### Issue 10+

- 多 workflow
- 真实数据
- artifact/export 深化
- 前端产品化

---

## 4. 当前不要提前做的事

- CopilotKit runtime takeover
- 完整 RM 工作台视觉重做
- 多 workflow 并行扩展
- 真实客户数据 / 真实产品池接入
- 自动 Memory 写入
- 为了 UI 去改 Hermes 整体 runtime loop

原因：

- 当前主风险不是协议形状，而是 **runtime path 与真实 WebUI smoke 是否对齐**。
- 真实 runtime 没被点亮前，继续堆业务功能只会放大回退成本。

---

## 5. Runtime / Streaming Issue 完成门槛

凡是改动以下任一层的 issue：

- Hermes Agent runtime / tools / toolsets
- Hermes WebUI streaming bridge
- `/api/chat/stream` 或 SSE event
- 前端真实 stream 消费路径

完成标准必须包含一次真实 WebUI smoke：

```text
从 WebUI 真实 chat 触发
  -> 观察到预期 tool call 或 SSE event
  -> 观察到预期 UI 渲染或明确的错误 surface
```

验收记录必须进入 issue comment，至少包含其一：

- 截图
- SSE log
- browser console log
- server log 中的 `event: rm_workbench` / tool call 证据

mock-stream、unit test、文档 review 只能证明协议形状，不能单独证明 runtime integration 已完成。

每个涉及 Hermes Agent 的 issue 还必须先过开发环境对齐 checklist：

```text
1. which hermes 指向预期 venv
2. runtime venv import 的 tools/toolsets 来自预期 agent 目录
3. 新增 tool 可在 runtime venv 中 import
4. WebUI 启动时 HERMES_WEBUI_AGENT_DIR / discover_agent_dir 指向同一目录
5. WebUI 真实 chat 中模型能看见新增 tool
```

---

## 6. 当前主线结论

```text
先补 Issue 7.5：runtime alignment + real WebUI smoke + high-risk readiness fixes。
再进入第一条真实 RM workflow。
```
