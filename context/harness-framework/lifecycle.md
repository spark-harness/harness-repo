# Harness 生命周期

本文是需求生命周期的简明入口。

它不是新的阶段真相源。阶段编号和通过条件以 `main-process-numbering.md` 为准。

## 阶段

| 阶段 | 目标 | 最小产物 |
|---|---|---|
| 1 初始化 | 建立需求目录和来源 | `README.md`、`requirement.md` |
| 2 需求定义 | 把自然语言需求整理成可评审规格 | `requirement.md`、`impact-analysis.md` |
| 3 设计 | 形成可追溯工程方案 | `design.md` |
| 4 开发 | 拆任务、改代码、测试和审查 | `tasks.json`、review report |
| 5 交付 | 汇总证据并确认可合并 | evidence、gate JSON、PR/MR |

## 基本顺序

```text
requirement.md
-> impact-analysis.md
-> requirement-review gate
-> design.md
-> design-review gate
-> tasks.json
-> dev-entry gate
-> implementation / review
-> merge-readiness gate
```

需求和影响分析属于同一评审阶段。`impact-analysis.md` 不存在时，不生成正式 `requirement-review` 门禁。

## 什么时候停下来

- 需求目标、非目标或验收标准不清楚。
- 影响仓库、服务、IDL 或数据边界不清楚。
- 设计无法追溯到需求条目。
- 任务无法追溯到设计决策。
- 门禁输入文件缺失或 hash 过期。
- 需要人工审批但没有审批记录。

## 关联文档

- `main-process-numbering.md`：阶段真相源。
- `document-template-policy.md`：模板真相源。
- `gates.md`：门禁简明入口。
- `gate-implementation.md`：门禁执行协议。
