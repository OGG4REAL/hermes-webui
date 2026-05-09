# RM Workbench V0 Code Review

路径：`docs/ui-ux/rm-workbench-v0-code-review-2026-05-07.md`
状态：`reference / historical code review`
评审时间：`2026-05-07`
评审范围：MYM-24 → MYM-32 累计落地的未提交 backend + frontend 改动
评审人：Claude Code（双 reviewer 子代理：backend + frontend 并行）
入口：`docs/ui-ux/rm-workbench-v0-index.md`

注意：本文保留当时的 review 发现。后续 issue 已修复或吸收部分问题；当前进入 Issue 8 前的判断以 Architecture / ADR / Roadmap 和 Issue 7 Foundation Status 为准。

---

## 0. 一句话结论

**Verdict: fix-then-ship。**

骨架站得住，protocol seam 收敛得不错。但前端有 4 个 HIGH 会在 Issue 8 第一次跑真实 Hermes workflow 时立刻撞墙——尤其 `window.__rmWorkbenchEvent` 是死合约，等于现在的 "smoke 通过" 很大程度是 fixture 跑通，不是真实链路跑通。

建议在开 Issue 8 之前先用半天开一个小 issue 修掉下面标 🔴 的项，否则 Issue 8 会变成边修基础设施边写业务的混合 PR，违反 roadmap §4 "主风险已收敛到 tool exposure seam" 的判断。

---

## 1. 评审范围

### 1.1 已改动文件清单（未提交）

Tracked diff（`git diff --stat`）：

```text
.gitignore                                                          |   6 ++
api/routes.py                                                       | 119 +++
api/streaming.py                                                    |  84 +++
docs/ui-ux/rm-workbench-v0-spike/fixtures/rm-pre-meeting-brief.valid.json | 52 +-
static/messages.js                                                  |  12 ++
```

Untracked（新增）：

```text
api/pending_interactions.py                       (151 行)
api/rm_workbench/__init__.py
api/rm_workbench/contracts.py
api/rm_workbench/adapter.py
api/rm_workbench/mock_data.py
api/rm_workbench/emit_tool.py
frontend/                                          (Vite + React 全新子项目)
tests/test_pending_interactions.py                (126 行)
tests/test_rm_workbench_adapter.py                (116 行)
tests/test_rm_workbench_routes.py                 (114 行)
tests/test_rm_workbench_mock_stream.py            (103 行)
tests/test_rm_workbench_real_stream_bridge.py     (476 行)
```

### 1.2 评审方法

并行启动两个 reviewer 子代理（backend / frontend），分别基于以下 invariant 检查：

1. 不改 `/api/chat/stream` top-level 协议
2. Bridge 仅识别 `tool_name == "rm_workbench_emit_contract"`，不嗅探 assistant text 或任意 tool result
3. `memory_proposals` 仅展示，不自动写入
4. `/api/rm-workbench/mock-stream` 必须 loopback-only
5. Pending interaction resolve 必须结构化，独立于 clarify

---

## 2. 🔴 HIGH（必须修）

### 2.1 后端

#### H-B1. `api/streaming.py:1316` `_handle_rm_emit_tool` 静默失败

异常只 `logger.warning`，不向前端发任何信号。Agent 端继续 `blocking_wait` 直到 300s 超时，用户在 UI 上看不到任何东西。

**影响**：Issue 8 跑真实 workflow，agent 一旦 emit 出格式异常的 contract，整条链路看起来像"卡住"。最可能的真实世界 bug。

**修复建议**：

```python
except Exception as exc:
    logger.warning("rm_workbench emit failed: %s", exc)
    queue.put(("rm_workbench", {"kind": "agui_events_error", "error": str(exc)}))
```

让前端 reducer 能识别 `agui_events_error` kind 并 surface。

---

#### H-B2. `api/streaming.py:1476-1479` 桥接回调未检查 cancel

tool 完成回调里的 `queue.put` 没看 `cancel_event`，cancel 后还会继续投递；`put` 异常会回流到 agent worker。

**修复建议**：

```python
if cancel_event.is_set():
    return
try:
    queue.put((event_name, payload))
except Exception as exc:
    logger.warning("rm_workbench put after cancel: %s", exc)
```

---

#### H-B3. `api/rm_workbench/adapter.py:239-253` `STATE_DELTA` 只发 `pending_interactions[0]`

validator 允许 N 个 pending interaction，但 adapter 硬索引 `[0]`。validator 一旦放宽（或将来出现兄弟 action），UI state 会静默丢条目。

**修复建议**：二选一——
- 循环 emit，每个 entry 一个 `STATE_DELTA` op；
- 或在 validator 显式 `assert len(pending_interactions) == 1` 把 V0 不变量编码进去。

---

#### H-B4. `api/pending_interactions.py:64-68` notify 回调 swallow 异常

`except Exception: pass` 静默吞掉所有 UI 投递失败。如果 SSE queue 满或关闭，用户看不到 pending interaction 但 `submit_pending` 返回成功，agent 继续 `blocking_wait` 直到超时。

**修复建议**：

```python
except Exception as exc:
    logger.warning("pending notify failed (session=%s): %s", session_key, exc)
    # 考虑返回失败信号让 agent 层 fail-fast
```

---

### 2.2 前端

#### H-F1. `aguiReducer.ts:62-69` A2UI 处理只取最后一条 `updateDataModel`

忽略 `createSurface` / `updateComponents` / 增量 patch / 早期 `updateDataModel`。A2UI surface 本身是有序的（create → components → data，再 partial patch）。

**影响**：fixture 单帧能跑通，真实流（一旦后端开始增量 emit）UI 会静默渲染陈旧/错误数据。

**修复建议**：按 `surfaceId` 维护 map，逐条按序应用消息，支持 upsert + JSON-pointer patch on `path`。

---

#### H-F2. `aguiReducer.ts:73` surfaces 无脑 append

每个 `a2ui.surface.messages` event 都 append。重发同一 surface（真实流重试或重渲染）会出现重复面板。

**修复建议**：upsert by `surfaceId`。

---

#### H-F3. `hermesClient.ts:39-60` SSE 解析过于天真

`fetchMockStream` 用 `res.text()` + `split("\n")`，不处理 `event:` 行、多行 `data:`、CRLF、partial UTF-8，且没有 `AbortController`。

**影响**：mock 单 event 能跑，但 footer 文案声称支持真实 Hermes stream——并不支持。

**修复建议**：

```typescript
const reader = res.body!.getReader();
const decoder = new TextDecoder("utf-8");
let buf = "";
while (true) {
  const { value, done } = await reader.read();
  if (done) break;
  buf += decoder.decode(value, { stream: true });
  let idx;
  while ((idx = buf.indexOf("\n\n")) !== -1) {
    const block = buf.slice(0, idx);
    buf = buf.slice(idx + 2);
    parseSseBlock(block);
  }
}
```

并接受 `AbortSignal` 参数。

---

#### H-F4. `App.tsx:36-48` `window.__rmWorkbenchEvent` 是死合约 ⚠️

这是最要命的一条。`window.__rmWorkbenchEvent` 被声明为"真实 chat stream 的集成 seam"，但：

- 当前 `App.tsx` 自己不消费 `/api/chat/stream`
- 仓库里没有别的代码注入这个全局 hook
- footer 却在 `App.tsx:170` 显示"支持真实 Hermes stream"

**影响**：Issue 8 启动时第一刀就会撞这里。当前 smoke 通过 ≠ 真实链路通过。

**修复建议**：二选一——
- 加一个真实 chat SSE 消费者，订阅 `event: rm_workbench` 后调用 `window.__rmWorkbenchEvent`；
- 或改 footer 文案 + 加注释把它明确定位为"外部宿主集成点（hermes-webui static chat 注入）"，并在文档里写清楚谁负责注入。

---

## 3. 🟡 MED（进 Issue 8 前最好顺手修）

| ID | 位置 | 问题 | 修复要点 |
|----|------|------|----------|
| M-B1 | `api/routes.py:2387 / 2429` | mock-stream + inject 路由 loopback check 漏 IPv6（`::1`、`::ffff:127.0.0.1`），macOS 浏览器走 `localhost` 会 404 | allow set: `{"127.0.0.1", "::1", "::ffff:127.0.0.1"}` |
| M-B2 | `api/routes.py:3372` `/pending/resolve` | 不按 pending entry 的 `schema` 校验 payload，违反 roadmap §1.5 "结构化 resolve" 语义 | 查 `schema.required` + 简单类型检查 |
| M-B3 | `api/rm_workbench/contracts.py:54-61` | 不校验 `surface.id` 唯一性，重复 ID 会在前端覆盖 | `len({s["id"] for s in surfaces}) != len(surfaces)` 抛错 |
| M-B4 | `api/rm_workbench/adapter.py:88` | `ProductFitTable` ↔ `pending_interaction` 的 1:1 link 没 validator 强制，缺失时被广义 `except` 吞 | validator 加一条规则 |
| M-B5 | `api/streaming.py:1316` | `_handle_rm_emit_tool` 接 `session_id, cancel_event` 但不用，dead 参数 | 要么用，要么删 |
| M-B6 | `api/pending_interactions.py:131-151` | `blocking_wait` cancel latency 最多 1s（`min(1.0, remaining)` 轮询），cancel 响应不及时 | OR-wait `cancel_event` 与 `entry.event` |
| M-F1 | `ProductFitTable.tsx:37` | 不读 `min_selection`，fixture 恰好为 1 才掩盖 bug | 从 `surface_props.min_selection` 读取并强制 |
| M-F2 | `ProductFitTable.tsx:30, 60` | maxSelection 仅 UI 层把关，confirm 时不再校验；surface 数据更新时旧选择不清空 | submit 前 re-validate；surface 变更时 reset selection |
| M-F3 | `hermesClient.ts:97-114` | resolve payload 中 `interaction_id` 是 optional，后端按 ID 路由会静默 miss | 函数签名改为 required |
| M-F4 | `aguiReducer.ts:120 SET_PHASE` | `submitting` 时静默清掉 error 状态，状态机脆 | 只在 `SET_ERROR` / `CLEAR_ERROR` 动 error |
| M-F5 | `aguiReducer.ts:59-94` | 大量 unsafe cast (`as string`, `value!`)，无 discriminated union；一条畸形 CUSTOM event 就能让 reducer 抛错并污染状态 | 加 runtime guard + 收敛 union 类型 |
| M-F6 | `App.tsx:81` | StrictMode 下 `useEffect` 跑两次，`seedPendingInteraction` 双发；后端可能 409 / 双 seed | 后端幂等，或前端 ref guard |

---

## 4. 🟢 LOW / NIT（顺手清理）

- L1. `api/pending_interactions.py` 的 `_pending` 影子字典是 dead weight：`get_pending` 永远先读 queue 命中，fallback 实质不可达。**删掉**，`get_pending` 只读 `_gateway_queues`。（YAGNI）
- L2. `tests/test_rm_workbench_real_stream_bridge.py:339-372` 两个测试在 grep 源码字符串（"`cancel_stream` 是否清 pending" / "`_handle_rm_emit_tool` 是否含 `blocking_wait`"），不是测行为，重构会立刻挂。改成真实调用 + 计时断言。
- L3. `api/rm_workbench/emit_tool.py:39` `except (ValueError, Exception)` 冗余，`Exception` 已覆盖。
- L4. `api/rm_workbench/adapter.py:122` brief surface 的 `text` fallback 用了 `surface_type` 字符串（`"BriefExportPanel"`），是开发者侧标识符，不该给用户看。
- L5. `api/pending_interactions.py:9` 模块级 mutable dict 无 test autouse 夹具，case 间会泄漏。加一个 fixture 清三个全局 dict。
- L6. `api/routes.py:493-494` `except ImportError: lambda *a, **k: None` 静默退化，建议 import 时打一次 warning。
- N1. `frontend/tsconfig.tsbuildinfo` 被 commit 进工作区，应进 `.gitignore`。
- N2. `frontend/vite.config.ts:4` 默认 backend `127.0.0.1:8787` 没文档化。
- N3. `RmWorkbenchSSEPayload.kind` 仅 `"agui_events"` 一种，可加注释说明 V0 仅此一种 kind。
- N4. `CustomerProfileCard.tsx:21` `customer.aum.toLocaleString()` 没空值守护。
- N5. ProductFitTable 复选框无 `aria-label`（smoke 可接受）。
- ✅ XSS：干净，无 `dangerouslySetInnerHTML`，无 markdown 渲染路径。

---

## 5. 测试覆盖盲点

| 盲点 | 后果 |
|------|------|
| `_handle_rm_emit_tool` callback 的 cancel / put-after-close / 异常分支**全部未测** | H-B1 / H-B2 类回归无法被发现 |
| 多 `pending_interactions` 行为未测 | H-B3 类（validator vs adapter 口径不一致）无法被发现 |
| IPv6 loopback 未测 | M-B1 在 macOS 真实浏览器才会暴露 |
| `/pending/resolve` schema 违例未测 | 因为实现根本没校验（M-B2） |
| `blocking_wait` cancel latency 未测 | M-B6 |
| `_handle_rm_workbench_mock_stream` broken-pipe 路径未测 | V0 demo 可接受，非 loopback 暴露前需要 |
| 前端 reducer 对真实多帧 A2UI 流的处理未测 | H-F1 / H-F2 |
| 前端 SSE 多行 / CRLF / partial chunk 解析未测 | H-F3 |

---

## 6. Top 3 风险（合并后）

1. **`window.__rmWorkbenchEvent` 是死合约（H-F4）** —— footer 文案声称支持真实 stream，但前端没人订阅 `/api/chat/stream`。Issue 8 第一步会撞这里。
2. **桥接静默失败（H-B1 + H-B4）** —— emit 异常或 SSE queue 关闭时，用户看不到任何反馈，agent 等 5 分钟超时。最常见的真实世界 bug。
3. **A2UI reducer 撑不住真实流（H-F1 + H-F2）** —— append-only、last-write-wins、不支持 patch、无错误守护。fixture 通过 ≠ 真实流通过。

---

## 7. 建议节奏

```text
Issue 7.5 (新增, ~半天):  修 H-B1 H-B2 H-B3 H-B4 H-F1 H-F2 H-F3 H-F4 + 测试
                          顺手 M-F3 (interaction_id required)
                          顺手 N1 (gitignore tsbuildinfo)

Issue 8:                  First Real Pre-Meeting Brief Workflow
                          —— 此时基础设施才真的算 ready

Issue 8.x 内消化:        其余 MED（M-B1 M-B2 M-B5 M-B6, M-F4-M-F6）
                          作为该 issue 内的"顺手修"项, 不单独拆
```

---

## 8. 评审决策点

请决策以下：

1. **是否同意插入 Issue 7.5**（修 8 个 HIGH + 关键 MED + 测试）作为 Issue 8 的前置？
2. **H-F4 选哪条修法**——真的接 `/api/chat/stream` 消费者，还是改文案 + 把 `window.__rmWorkbenchEvent` 明确定位为外部宿主注入点？
3. **H-B3 选哪条修法**——adapter 改成循环 emit（保留 N>1 能力），还是 validator assert N==1（坚持当前不变量）？

---

## 9. 评审追溯

- Backend reviewer: subagent `a6bc1de3ad4ff2b97`，14 tool uses，198s
- Frontend reviewer: subagent `a9c0a26e5052f05d0`，15 tool uses，150s
- 双 reviewer 独立，无交叉提示，结论一致为 fix-then-ship
