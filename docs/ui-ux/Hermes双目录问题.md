# Hermes Agent 双目录问题分析

**日期**：2026-05-07
**状态**：待决策

---

## 问题陈述

你最近在 `~/hermes-agent` 里加了 `rm_workbench_emit_contract` 工具（含实现、注册、tests），代码层面看一切正常。但 webui 里问 Hermes "你有这个工具吗"，它说没有。

排查后发现：**runtime 实际加载的根本不是 `~/hermes-agent`，而是另一份代码 `~/.hermes/hermes-agent`**。

---

## 关键事实

### 两份独立的代码

| 路径 | git 状态 | rm_workbench_tool.py | 角色 |
|---|---|---|---|
| `~/.hermes/hermes-agent` | 有 `mine`(OGG4REAL fork) + `origin`(Nous) 两个 remote，本地 commit `c34e8bb9a`，与 origin/main 已差 3275 commit | **没有** | runtime 实际加载这个 |
| `~/hermes-agent` | 只有 `origin`(Nous)，本地 commit `677f1227`，4-14 日期 | **有**（你最近在这里改） | 你以为 runtime 加载这个 |

两个目录是两次独立的 `git clone`，**没有任何同步关系**。

### 为什么 runtime 一定加载 `~/.hermes/hermes-agent`

`which hermes` 显示的 launcher script：

```python
#!/Users/hywl/.hermes/hermes-agent/venv/bin/python3
import sys
from hermes_cli.main import main
```

shebang **硬编码**了 venv 路径。这是 `pip install -e .` 在 `~/.hermes/hermes-agent` 里跑时自动生成的。

后果：

- 无论你在哪个目录敲 `hermes gateway run`，都会用这个 Python
- 这个 venv 的 `hermes_cli` 包通过 editable install 指向 `~/.hermes/hermes-agent/hermes_cli`
- 所以 `import hermes_cli` 永远拿到 `~/.hermes/hermes-agent` 的代码

WebUI 也类似：bootstrap 脚本通过 `discover_agent_dir()` 找 hermes-agent，候选顺序是：

```python
candidates = [
    os.getenv("HERMES_WEBUI_AGENT_DIR", ""),     # 环境变量优先
    str(home / "hermes-agent"),                    # ~/.hermes/hermes-agent ← 命中
    str(REPO_ROOT.parent / "hermes-agent"),
    str(Path.home() / ".hermes" / "hermes-agent"),
    str(Path.home() / "hermes-agent"),             # 你的 dev 目录在这才会被找到
]
```

`HERMES_HOME=~/.hermes` 的默认行为下，第二项就命中了，根本走不到第五项。

### 历史推断

- **4-17**：你（或安装脚本）在 `~/.hermes/hermes-agent` 第一次设置好 hermes-agent，做了 `pip install -e .` 和 `git remote add mine`，从此这里成为 runtime 入口
- **4 月某天**：你又在 `~/hermes-agent` 单独 clone 了一份 upstream 代码（只有 `origin` remote）
- **5-6 / 5-7**：你在 `~/hermes-agent` 写 rm_workbench 相关代码、tests
- **5-7 今天**：你在 webui 里测试，发现工具没注册，因为 runtime 加载的是 4-17 的旧目录

### 你之前的疑问澄清

> "gateway 为啥会是 `~/.hermes/hermes-agent` 的，我直接从 hermes-agent 启动的 gateway 吧"

你印象里"从 `~/hermes-agent` 启动" 的那次，命令实际是 `hermes gateway run`（或类似的 CLI）。这个 CLI 命令背后由 `which hermes` 那个 launcher 触发，shebang 硬编码使其无论 CWD 在哪都用 `~/.hermes/hermes-agent` 的 venv 和代码。**所以从来就没真正从 `~/hermes-agent` 启动过 gateway。**

---

## 影响范围

| 组件 | 启动方式 | 实际加载 |
|---|---|---|
| Gateway（飞书） | `hermes gateway run` 或 `python -m hermes_cli.main gateway` | `~/.hermes/hermes-agent` |
| WebUI server | `python ~/hermes-webui/server.py` → bootstrap 找 agent_dir | `~/.hermes/hermes-agent` |
| WebUI 内 AIAgent 跑 session | webui 起的子进程 | `~/.hermes/hermes-agent` |
| 你跑的 pytest（在 `~/hermes-agent` 下） | `pytest tests/` | `~/hermes-agent` ✅ |

测试和实际运行用的是不同代码——这就是为什么 unit test 全过、UI 里却跑不起来。

---

## 解决方案对比

### 方案 1：用环境变量重定向 webui（最初提议）

```bash
export HERMES_WEBUI_AGENT_DIR=~/hermes-agent
```

- ✅ 改动最小
- ❌ 只解决 webui，gateway 还在用旧代码
- ❌ 飞书 / WebUI 行为不一致，二开调试时容易混乱
- ❌ 没解决 `hermes` CLI 命令的硬编码问题

### 方案 2：让 venv 切到 `~/hermes-agent`（推荐方向）

```bash
~/.hermes/hermes-agent/venv/bin/pip install -e ~/hermes-agent
```

`pip install -e`（editable install）让 venv 的 `hermes_cli` 包重新指向 `~/hermes-agent`：

- ✅ 一处改动，gateway + webui + `hermes` CLI 全部统一
- ✅ 以后你改 `~/hermes-agent` 的代码，重启对应进程就生效
- ✅ 同时设 `HERMES_WEBUI_AGENT_DIR=~/hermes-agent` 让 webui bootstrap 也指过去（避免它仍然在 `discover_agent_dir()` 时找到老目录）
- ⚠️ 动到 venv，需谨慎；如果 `~/hermes-agent` 缺某些 dependency（比如它的 `pyproject.toml` 和老目录有差），可能要额外 `pip install`
- ⚠️ `~/.hermes/hermes-agent` 仍然在磁盘上，建议保留一周作备份再删

### 方案 3：合并 git 历史

把 `~/hermes-agent` 的 rm_workbench 提交 cherry-pick / merge 到 `~/.hermes/hermes-agent`，统一在那个目录开发。

- ✅ 保留 `~/.hermes/hermes-agent` 的 fork 远端（OGG4REAL/hermes-agent）
- ❌ 两个目录的 commit 历史已经分叉（一个 4-14，一个 4-17，且都各自往前走），merge 会很痛苦
- ❌ 你后面要持续二开，每次新 feature 还得切回 `.hermes/hermes-agent` 写，改变工作习惯

### 方案 4：symlink

```bash
mv ~/.hermes/hermes-agent ~/.hermes/hermes-agent.old
ln -s ~/hermes-agent ~/.hermes/hermes-agent
```

- ✅ 最暴力简单，所有路径自动指过去
- ⚠️ venv 还在 `~/.hermes/hermes-agent.old/venv`，需要把 venv 先挪到 `~/hermes-agent/venv` 或保持原位（symlink 后路径会变成 `~/hermes-agent/venv`，但 venv 内部的硬编码路径还是老的，可能影响）
- ⚠️ 比 `pip install -e` 更脆弱（venv 路径硬编码 + symlink 解析行为）

---

## 我的推荐

**方案 2**：`pip install -e ~/hermes-agent` + `HERMES_WEBUI_AGENT_DIR=~/hermes-agent`

理由：

1. 你说要持续二开 hermes-agent → 必须有一个清晰的"权威开发目录"，方案 2 让 `~/hermes-agent` 名副其实
2. 一行 `pip install -e` 就让 `hermes` CLI 命令、gateway、webui 全部统一指向新目录，没有遗漏的角落
3. 老目录 `~/.hermes/hermes-agent` 留着不删，万一新目录哪个 dependency 缺了，可以快速 fallback

执行步骤建议：

1. 先确认 `~/hermes-agent` 的 `pyproject.toml` / `setup.py` 完整可装
2. `~/.hermes/hermes-agent/venv/bin/pip install -e ~/hermes-agent`
3. 把 `HERMES_WEBUI_AGENT_DIR=~/hermes-agent` 加到 `~/.zshrc` 或 `~/hermes-webui/.env`
4. 重启 gateway 和 webui
5. 在 webui 里测一下 `rm_workbench_emit_contract` 是不是出现了
6. 一周观察期没问题再删 `~/.hermes/hermes-agent`

---

## 需要你决策的事

- 选方案 1 / 2 / 3 / 4 哪个？
- 还有：`~/.hermes/hermes-agent` 那个 fork（remote `mine` = OGG4REAL/hermes-agent）后面怎么处置？要不要把 `~/hermes-agent` 也加上这个 fork remote，让你的二开工作能 push 到自己的 fork？

---

## 附录：Claude Code 补充 Review（2026-05-07，对照真实代码状态）

> 由 Claude Code 在原 MD 写完之后做的二次 review，逐条对照 runtime 真实状态验证。下面所有补充都基于已执行的命令证据，不是推断。

### A. 原 MD 事实判断的验证结果

| 论断 | 验证 | 结论 |
|---|---|---|
| `which hermes` shebang 硬编码 `~/.hermes/hermes-agent/venv` | `head -3 $(which hermes)` 第一行就是 `#!/Users/hywl/.hermes/hermes-agent/venv/bin/python3` | ✅ |
| runtime 真正加载 `~/.hermes/hermes-agent` | venv 的 editable install 文件 `__editable___hermes_agent_0_9_0_finder.py` 里 MAPPING **显式硬编码**所有顶层包指向 `~/.hermes/hermes-agent/...`（包括 `tools`、`toolsets`、`hermes_cli` 等 19 个包） | ✅ 比 shebang 更绝对，所有 `import tools` 都被这个 finder 拦截 |
| `~/hermes-agent` 有 `tools/rm_workbench_tool.py`，`.hermes/` 没有 | `find` 结果一致 | ✅ |
| webui `discover_agent_dir()` 候选第 2 项命中 `~/.hermes/hermes-agent` | `api/config.py:77-79` 与 MD 描述一致 | ✅ |

**直接验证证据**（在 runtime venv 里跑）：

```bash
~/.hermes/hermes-agent/venv/bin/python -c "from tools import rm_workbench_tool"
# ImportError: cannot import name 'rm_workbench_tool' from 'tools'
```

runtime 看到的 `tools` 包根本没有这个文件。

### B. 原 MD 漏掉的关键点

#### B.1 测试路径玄机：MYM-31 的 test 为什么能过

原 MD 说"unit test 全过、UI 跑不起来"，但**没解释 test 怎么过的**。事实是：

- `~/hermes-agent` **根本没有自己的 venv**（`ls ~/hermes-agent/venv` 不存在）
- 那 `pytest tests/tools/test_rm_workbench_tool.py` 是怎么过的？
- 唯一可能：从 `~/hermes-agent` 目录用 `.hermes` venv 的 python 跑 pytest，pytest 自动把 cwd 加入 sys.path → cwd 的 `tools/rm_workbench_tool.py` 比 editable install MAPPING 先命中

**所以 test 路径 ≠ runtime 路径，靠的是 pytest 的 sys.path 行为偶然让它过。**

debrief 必须把这条记下，否则下次"先写 test 再说"的工作流还会同样出事。

#### B.2 整条端到端链路从未跑通过 🚨（最大发现）

原 MD 没把这条说透。事实链：

- webui 的 `_append_rm_workbench_toolset_if_supported`（`api/streaming.py:1104`）调用：
  ```python
  from toolsets import validate_toolset
  if validate_toolset("rm_workbench") and "rm_workbench" not in toolsets:
      return list(toolsets) + ["rm_workbench"]
  ```
- runtime 的 `toolsets` 模块从 editable MAPPING 取 `~/.hermes/hermes-agent/toolsets.py`，**那份没有 rm_workbench 配置**（grep 全空）
- 所以 `validate_toolset("rm_workbench")` 静默返回 False
- toolset 不被 append，agent 永远拿不到这个工具
- agent 永远不会 emit `rm_workbench_emit_contract`
- webui 桥接里的 `_handle_rm_emit_tool` 永远不会被触发
- `/api/chat/stream` 永远不会发 `rm_workbench` SSE event

而前端那端：

- `frontend/src/App.tsx` 当前只订阅 `/api/rm-workbench/mock-stream`
- 没有任何代码订阅 `/api/chat/stream` 并把 `rm_workbench` event 转给 `window.__rmWorkbenchEvent`

**整条 MYM-29 + MYM-31 的"真实链路"自从写完那天起，前后两端都没接上，从来没真的执行过一次。**

可视化：

```
[Hermes runtime] 没注册 tool ─✗→ agent 不调
                                  ↓
[chat stream] 不会出现 rm_workbench_emit_contract tool result
                                  ↓
[webui bridge] 等不到
                                  ↓
[/api/chat/stream] 不发 rm_workbench SSE event
                                  ↓
[前端 App.tsx] 也没人订阅这个 SSE event ─✗
```

之前 reviewer 报"smoke 通过"——那是 MYM-27 的 mock-stream 路径，是平行支线，跟真实 chat 没有交集。

#### B.3 MYM-32 review 通过这件事必须算账

`rm-workbench-v0-index.md:204` 写：

> MYM-32: Review Hermes Agent rm_workbench_emit_contract Tool Registration ... 最终 review comment 结论为无阻断性 findings。

但事实是：

- reviewer（Codex）看的是 `~/hermes-agent` 的代码，跟实现者一样
- 没人打开 webui 实际问 Hermes "你有这个工具吗"
- "no blocking findings" 字面成立（代码本身无 bug），但**功能验收完全没做**

**这是验收标准的系统性漏洞，不是个案。** MYM-31 的"人工验收"如果要求"webui 启动一次 + agent 自报工具列表 + 看见 rm_workbench_emit_contract 出现"，整件事在 5 分钟内就会暴露。

#### B.4 原 MD 里关于 commit 数的小错（不影响结论）

原 MD 第 22 行说 `~/.hermes/hermes-agent` 与 `origin/main` "已差 3275 commit"。实际：

```
.hermes/ HEAD: c34e8bb9a (2026-04-17)
~/hermes-agent HEAD: 677f1227c (2026-04-14)
```

`c34e8bb9a` 只比 `677f1227c` 多一个 commit。3275 大概率是 fork remote `mine` 与 upstream 的 ahead/behind，不是本地两份的差距。不影响主结论，但联合 codex 改的时候别照抄。

### C. 推荐方案的补充

MD 推荐方案 2（`pip install -e ~/hermes-agent` + `HERMES_WEBUI_AGENT_DIR`），同意。但要补两点：

- **新 `pip install -e` 会覆盖 `__editable__.hermes_agent-0.9.0.pth` 的 MAPPING**，让 `tools`/`toolsets`/`hermes_cli` 等所有包重新指向 `~/hermes-agent`。这是好事，一步到位
- **`~/hermes-agent/toolsets.py:394` 已经有 rm_workbench 配置**（grep 验证存在），所以切过去之后这条链路才会真正跑起来
- **切完之后第一件事不是跑 test，而是打开 webui 跟 Hermes 说一句"列出你能用的工具"，看见 `rm_workbench_emit_contract` 才算验收**

补充验收 checklist：

```bash
# 1. 切换 editable install
~/.hermes/hermes-agent/venv/bin/pip install -e ~/hermes-agent

# 2. 验证 import 路径已切换
~/.hermes/hermes-agent/venv/bin/python -c "from tools import rm_workbench_tool; print(rm_workbench_tool.__file__)"
# 必须输出 /Users/hywl/hermes-agent/tools/rm_workbench_tool.py

# 3. 验证 toolsets 配置可见
~/.hermes/hermes-agent/venv/bin/python -c "from toolsets import validate_toolset; print(validate_toolset('rm_workbench'))"
# 必须输出 True

# 4. 设置 webui 环境变量
echo 'export HERMES_WEBUI_AGENT_DIR=~/hermes-agent' >> ~/.zshrc

# 5. 重启 webui，浏览器进 chat 页面，问 Hermes "你能用哪些工具"
#    必须看到 rm_workbench_emit_contract 在工具列表里
```

第 5 步是真正的验收，前 4 步只是准备。

### D. 给项目复盘的三条结构性建议（MD 没覆盖）

既然要做项目复盘，光定位双目录问题不够。把这次教训的三条结构性问题写进 debrief：

#### D.1 "完成"的定义太弱

MYM-24 ~ MYM-32 全部依赖 **代码合并 + 单测过 + 文档 review** 作为完成标准。从来没有一项要求"在真实启动的 webui 里看到效果"。

**修正建议**：每个改动 runtime / agent / streaming 协议的 issue，验收**必须**包含一次"从 webui 真实 chat 触发 → 观察到预期 SSE event / UI 渲染"的 manual smoke，截图或 SSE log 入 issue。

写进 `docs/ui-ux/rm-workbench-v0-index.md` 的"验收要求"一节。

#### D.2 Test path 与 runtime path 不对齐的风险，文档零提示

后续任何二开 hermes-agent 的 issue 都可能踩。建议在 `docs/ui-ux/rm-workbench-v0-index.md` 里加一个 §**"开发环境对齐 checklist"**：

- [ ] `which hermes` 指向预期 venv
- [ ] `~/.hermes/hermes-agent/venv/bin/python -c "import tools; print(tools.__file__)"` 输出预期目录
- [ ] runtime venv 跑 `from tools import <new_tool>` 能 import
- [ ] webui 启动后，`HERMES_WEBUI_AGENT_DIR` 与 `discover_agent_dir()` 选中的目录一致

每加一个新 hermes-agent 工具，必须先过这个 checklist 再说"功能完成"。

#### D.3 Mock-only 验证混淆了"基础设施完成"和"系统完成"

MYM-26/27 让 smoke workbench + mock-stream 跑通后，roadmap 写 "Phase 0 已完成"。但 mock-stream 本质是**前后端各跑一半**，不证明任何 runtime 集成。

这次双目录问题的爆发时间（5-7，紧接 MYM-31 完成）不是巧合——**真实链路第一次有理由被点亮的那天，问题才会暴露**。

**修正建议**：以后**不允许**任何"runtime 集成相关的 issue"在没有 real-stream 验证的情况下被标 done。Mock 只能证明协议形状，不能证明集成完成。

把这条写进 `docs/ui-ux/rm-workbench-v0-roadmap.md` 的"§4 当前不要提前做的事"对面，新增一节 §**"完成必须证明的事"**。

### E. 一句话总结

```
MYM-24 → MYM-32 是一条"形状对了，但从来没真的接通过"的链路。
代码层面 9 个 issue 全过 review，
真实端到端零次执行。
原因不是某个工程师疏忽，
是验收标准从一开始就没要求 runtime 启动后看到效果。
```

### F. 联合 Codex 修改时的建议顺序

1. 先按方案 2 切目录，跑 §C 的 5 步 checklist——把基础设施先扶正
2. 跑通真实 chat 调用 `rm_workbench_emit_contract` 一次（哪怕 agent 主动 emit 一个最简 fixture contract），证明端到端能通
3. 再回头处理之前 review 里 4 个前端 HIGH（H-F1/F2/F3/F4），让前端真的能消费 `/api/chat/stream` 的 `rm_workbench` event
4. 最后把 §D 的三条结构性建议落地到 `rm-workbench-v0-index.md` 和 `roadmap.md`
5. 重新审视 MYM-31 / MYM-32 的"已完成"状态——是降级为"代码已交付，等真实集成验证"，还是直接重开一个 issue 做 functional acceptance

把第 5 条提前想清楚，不然 Codex 那边可能直接照旧标 done。
