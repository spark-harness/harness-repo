# Agents

Agent 是可以被主会话委派的专业角色。每个 Agent 只负责一个清晰检查面，避免一次性“大而全”审查。

Agent 定义为本目录下平铺的 `*.toml` 文件，按阶段的归属在下表声明，不使用子目录分组。

## 现有 Agent

| Agent | 阶段 | 职责 |
| --- | --- | --- |
| `requirement-reviewer` | 2.2 | 需求评审门禁 |
| `design-reviewer` | 3.3 | 设计门禁 |
| `backend-architecture-reviewer` | 3.3 / 4.4 | 后端干净架构评审 |
| `dev-entry-checker` | 4.2 | Dev 进入门禁 |
| `service-repo-checker` | 4.3 | 服务仓库检查门禁 |
| `code-review-traceability-checker` | 4.4 | 审查：追溯与任务范围 |
| `code-review-contract-checker` | 4.4 | 审查：契约兼容 |
| `code-review-data-concurrency-checker` | 4.4 | 审查：数据、事务、并发、幂等、回滚 |
| `code-review-security-error-checker` | 4.4 | 审查：安全、错误处理、可观测性 |
| `code-review-reporter` | 4.4 | 聚合各维度结论，写入 `reviews/{task-id}.md` |

## 4.4 多维并行审查

四个 `code-review-*-checker` 由 `spark-code-review` Skill 并行分发，各自独立上下文，只返回本维度 findings；`code-review-reporter` 聚合后按 `context/harness-framework/templates/review-report.md` 写入 `requirements/{requirement-id}/reviews/{task-id}.md`。

- Checker 不写报告文件，不做门禁结论。
- Reporter 必须原样保留 findings，未执行的维度记录 `skipped` 及原因。
- 审查报告不是门禁结论，阶段推进仍以 Janus 门禁 JSON 和人工审批为准。

## 新增 Agent 要求

新增 Agent 时应说明：

- 输入文件。
- 检查范围。
- 输出文件。
- 通过、阻塞、警告的判定口径。

规划中、尚未实现的角色：

- 阶段 5：`test-runner`、`delivery-checker`、`knowledge-update-checker`、`merge-readiness-checker`。
- 知识维护：`experience-extractor`、`sop-generator`、`context-index-maintainer`。

## 门禁 Agent 输出协议

门禁 Agent 不能只在对话中给出口头结论。

执行门禁时必须：

- 读取 `context/harness-framework/gate-implementation.md`。
- 按门禁 JSON 模板写入 `requirements/{requirement-id}/gates/{gate-id}.gate.json`。
- 运行 `janus gate validate <gate-json>`。
- 使用固定字段 `result` 和 `blocks_next_stage`。
- 在 `checklist` 中列出检查项、结果和证据。
- 在 `blocking_issues` 中列出所有阻塞项。
- 在 `warnings` 中列出非阻塞风险和后续动作。
- 如使用 `WAIVED`，必须补齐 `Waiver` 区块。

对话中的简短结论只用于提示用户，不能替代门禁 JSON。
