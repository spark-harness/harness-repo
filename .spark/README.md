# Spark Source

`.spark/` 是 Spark Harness 的 AI 协作资产源目录。

这里保存的是团队级 AI 协作协议，不绑定某一个执行工具。后续可以按需要渲染到 Claude Code、Gemini CLI、Codex CLI、Continue 或内部工具的本地目录。

## 目录

```text
.spark/
├── skills/
├── agents/
├── commands/
├── hooks/
├── rules/
└── hooks.json
```

## 使用原则

- Skill 放可复用工作流。
- Agent 放可委派的专业检查或执行角色。
- Command 放稳定入口，让同一类任务有同一套流程。
- Hook 和规则放自动化校验、权限和阶段前置检查。

先在这里修改源文件，再由安装脚本或人工同步到具体 AI 工具目录，避免不同工具之间规范漂移。
