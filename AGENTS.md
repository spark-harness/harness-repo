# Harness Repo Agent Instructions

本仓库保存 Harness Engineering 治理资产。Agent 在本仓库工作时，应先读取本文件，再按任务读取 `context/`、`.spark/skills/` 和 `.spark/agents/`。

## Boundaries

- 需求、设计、门禁报告、服务矩阵、团队规范、项目上下文和 Codex 协作资产放在本仓库。
- 业务实现代码不放在本仓库。
- protobuf 契约真相源不放在本仓库。
- 业务仓路径和 IDL 仓路径以 `.service-matrix/dependencies.yaml` 为准。

## Required Context

- 需求生命周期以 `context/harness-framework/main-process-numbering.md` 为阶段真相源。
- 门禁协议以 `context/harness-framework/gate-implementation.md` 为事实源。
- 文档模板口径以 `context/harness-framework/document-template-policy.md` 为事实源，模板文件保存在 `context/harness-framework/templates/`。
- 上下文收集顺序以 `context/harness-framework/context-collection.md` 为事实源。
- 团队级规则从 `context/team/INDEX.md` 进入。
- 服务级知识从 `context/project/INDEX.md` 进入，并通过服务矩阵定位具体服务。

## Gate Reports

- 门禁机器事实源使用 `requirements/{requirement-id}/gates/{gate-id}.gate.json`。
- 阶段推进只能读取门禁 JSON 结论，不能读取聊天记录、手写 Markdown 或历史 Markdown 作为放行依据。
- 历史 `requirements/{requirement-id}/gates/{gate-id}.md` 只视为旧审计快照，不再刷新、不再校验、不再作为事实来源。
- Harness 运行环境必须提供 PATH 中的 `janus` 命令；开始门禁工作前先运行 `janus version`。
- 门禁变更后必须运行 `janus gate validate`，合并前运行 `janus requirement verify --requirement <id> --target merge`。

## Editing Rules

- 面向团队的文档使用中文。
- 只写可执行、可评审、可落地的规则。
- 不复制业务代码实现细节。
- 如果修改流程、门禁、服务矩阵或上下文结构，必须考虑模板、Skill、Agent 和 Janus 校验是否同步。
