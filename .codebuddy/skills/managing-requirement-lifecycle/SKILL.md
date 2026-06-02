# Managing Requirement Lifecycle

Use this skill when a user wants to create, continue, advance, review, or close a requirement in this Harness repository.

## Goal

把需求从自然语言输入推进为可评审、可追溯、可交付的工程产物。

## Source Of Truth

- 流程阶段：`context/harness-framework/main-process-numbering.md`
- 门禁实施：`context/harness-framework/gate-implementation.md`
- 模板口径：`context/harness-framework/document-template-policy.md`
- 上下文收集：`context/harness-framework/context-collection.md`
- 服务拓扑：`.service-matrix/dependencies.yaml`
- 需求模板：`templates/requirement.md`
- 影响面模板：`templates/impact-analysis.md`
- 门禁模板：`templates/gate-report.md`

## Workflow

1. 确认需求目录是否存在于 `requirements/{requirement-id}/`。
2. 如果不存在，按模板创建需求骨架。
3. 读取 `context/team/`、`context/harness-framework/`、`context/harness-framework/context-collection.md` 和相关 `context/project/` 入口。
4. 根据 `.service-matrix/dependencies.yaml` 补齐服务影响面。
5. 在进入下一阶段前检查对应门禁报告。
6. 如果门禁报告缺失、格式不合法或 `Result: BLOCKED`，停止推进并列出阻塞项。
7. 如果 `Result: WARN`，继续推进但记录风险和后续动作。
8. 如果 `Result: WAIVED`，先校验豁免字段完整性。
9. 如果用户纠正了模式性错误，建议沉淀到 `context/project/.../experience/` 或框架规范。

## Output

每次推进都应更新需求目录中的文件，而不是只在对话中给出口头结论。
