# Harness Framework Context Index

框架工程级知识适用于所有需求研发流程。

## 当前入口

- `main-process-numbering.md`：五阶段流程和四道门禁。
- `gate-policy.md`：门禁状态和报告要求。
- `gate-implementation.md`：门禁报告字段、Agent 输出、Skill 流程、阶段推进、CI / MR 阻塞和豁免规则。

## 维护原则

- 流程口径以 `main-process-numbering.md` 为准。
- 门禁必须能落到文件，不接受只在对话中口头通过。
- 门禁执行协议以 `gate-implementation.md` 为准。
- 修改流程后，应同步检查 `learning-docs-repo/docs/harness/`、`.codebuddy/skills/` 和模板。
