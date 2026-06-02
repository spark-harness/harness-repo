# Commands

Command 是稳定入口，把自由聊天收敛成标准流程。

建议先实现以下命令语义：

```text
/requirement:new
/requirement:continue
/requirement:next
/requirement:gate-check
/service:deps
/knowledge:extract-experience
```

Command 只定义入口和参数，不复制完整流程。完整流程应引用对应 Skill。
