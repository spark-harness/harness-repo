# Harness Framework Context Index

框架工程级知识适用于所有需求研发流程。

## 当前入口

- `main-process-numbering.md`：五阶段流程、阶段门禁和合并就绪门禁。
- `gate-policy.md`：门禁状态和报告要求。
- `gate-implementation.md`：门禁报告字段、Agent 输出、Skill 流程、阶段推进、CI / MR 阻塞和豁免规则。
- `document-template-policy.md`：需求生命周期文档模板的真相源、使用阶段和维护规则。
- `context-collection.md`：团队、框架、项目和服务上下文的最小收集顺序。

## 维护原则

- 流程口径以 `main-process-numbering.md` 为准。
- 门禁必须能落到文件，不接受只在对话中口头通过。
- 门禁执行协议以 `gate-implementation.md` 为准。
- 模板口径以 `document-template-policy.md` 为准，模板文件保存在 `templates/` 子目录。
- 上下文收集口径以 `context-collection.md` 为准。
- 修改流程、门禁、模板或上下文结构后，应同步检查 `learning-docs-repo/docs/harness/`、`.spark/skills/`、`.spark/agents/`、`.spark/rules/` 和 Janus 校验。
