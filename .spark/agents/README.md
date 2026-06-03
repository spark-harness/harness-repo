# Agents

Agent 是可以被主会话委派的专业角色。每个 Agent 只负责一个清晰检查面，避免一次性“大而全”审查。

推荐分组：

```text
agents/
├── Init/
├── Definition/
├── DetailDesign/
├── Implementation/
├── Acceptance/
└── KnowledgeMaintenance/
```

新增 Agent 时应说明：

- 输入文件。
- 检查范围。
- 输出文件。
- 通过、阻塞、警告的判定口径。

## 门禁 Agent 输出协议

门禁 Agent 不能只在对话中给出口头结论。

执行门禁时必须：

- 读取 `context/harness-framework/gate-implementation.md`。
- 按门禁 JSON 模板写入 `requirements/{requirement-id}/gates/{gate-id}.gate.json`。
- 运行 `janus gate validate <gate-json>`。
- 运行 `janus gate render --input <gate-json> --output <gate-md>`。
- 使用固定字段 `result` 和 `blocks_next_stage`。
- 在 `checklist` 中列出检查项、结果和证据。
- 在 `blocking_issues` 中列出所有阻塞项。
- 在 `warnings` 中列出非阻塞风险和后续动作。
- 如使用 `WAIVED`，必须补齐 `Waiver` 区块。

对话中的简短结论只用于提示用户，不能替代门禁 JSON。
