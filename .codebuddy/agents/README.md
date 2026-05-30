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
