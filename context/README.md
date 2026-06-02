# Context

`context/` 保存 AI 可读取、可评审、可演进的团队知识。

它不是业务代码文档的复制仓库，而是团队规范、框架流程、服务语义和历史经验的入口。

## 三层结构

```text
context/
├── team/
├── harness-framework/
└── project/
```

- `team/`：所有项目共享的团队规范。
- `harness-framework/`：所有需求研发共享的 Harness 流程、门禁、模板口径和上下文收集规范。
- `project/`：项目、领域、服务级知识。

AI 工作时应先读团队级和框架级入口，再按服务矩阵缩小到项目级上下文。
