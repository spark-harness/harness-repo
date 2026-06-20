---
requirement_id: "LEN-36"
owner: "Codex"
status: "draft"
created_at: "2026-06-20"
related_branch: "feature/LEN-36-contract-dependency-ci-gates"
approved_by: ""
approved_at: ""
decision: ""
---

# LEN-36 实现 business-repo 契约依赖 CI 门禁

## Purpose

在 `business-repo` 中落地契约依赖扫描 CI，防止 master-bound PR 或 RC 候选验证使用错误阶段的 IDL 生成契约依赖。

## Source

- JIRA: LEN-36
- 规则来源: LEN-35 `context/team/contract-versioning.md`
- 分支: `feature/LEN-36-contract-dependency-ci-gates`

## Scope

- `harness-repo`: 需求、影响分析、设计、任务、门禁和证据。
- `business-repo`: 本地可执行扫描脚本、测试 fixture、GitHub Actions workflow。

## Worktrees

```text
.worktrees/LEN-36/harness-repo
.worktrees/LEN-36/business-repo
```
