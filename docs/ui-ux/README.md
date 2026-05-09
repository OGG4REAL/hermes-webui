# UI/UX Docs

状态：`directory guide`
更新时间：`2026-05-09`

---

## RM Workbench V0

RM Workbench V0 的唯一入口是：

```text
docs/ui-ux/rm-workbench-v0-index.md
```

默认只读三份 core docs：

- `rm-workbench-v0-architecture.md`
- `rm-workbench-v0-adr.md`
- `rm-workbench-v0-roadmap.md`

其它 RM Workbench 文档都是 working / reference / historical material。除非 issue 明确要求，不要把它们当作当前工程事实源。

---

## Maintenance Rule

文档和代码尽量分开提交。

当系统事实变化时，更新 Architecture。

当技术取舍变化时，更新 ADR。

当执行顺序变化时，更新 Roadmap。

当新增 issue-specific 文档时，必须在 `rm-workbench-v0-index.md` 登记。

