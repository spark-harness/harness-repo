# LEN-113 修复 Spark 工作区治理与主干事实漂移

本需求修复 Spark 工作区治理资产与当前主干事实之间的漂移。

它不是业务功能开发，也不是 business-repo 三目录迁移重构。它只处理治理文档、状态判断、Janus 交付推断和 runtime mirror 校验与当前事实不一致的问题。

## 当前状态

- Jira: `LEN-113`
- 分支: `chore/LEN-113-governance-drift`
- Worktree: `.worktrees/LEN-113/`
- 阶段: 需求定义

## 影响仓库

- `harness-repo`
- `business-repo`
- `janus`

## 生命周期文件

- `requirement.md`
- `impact-analysis.md`
