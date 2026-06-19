---
requirement_id: "LEN-35"
owner: "Codex"
current_stage: "5.1"
status: "approved"
created_at: "2026-06-20"
related_branch: "feature/LEN-35-contract-versioning"
---

# 治理 IDL 契约依赖版本发布与消费

## Summary

LEN-35 定义 Spark Java / Go IDL 生成契约的版本发布、冻结、消费和门禁规范，避免并发开发时共享 `SNAPSHOT`、本地 `replace`、branch dependency、pseudo-version 或未冻结依赖互相污染。

先说不是什么：它不修改具体业务 `.proto`，不设计业务 API，不规定团队 Git branching 模型，也不要求 Traceability Manifest。

## Links

- JIRA: LEN-35（Story）
- Branch: `feature/LEN-35-contract-versioning`
- Worktree: `.worktrees/LEN-35/{harness-repo,idl-repo,business-repo}`

## Lifecycle Artifacts

- requirement.md
- impact-analysis.md
- design.md
- tasks.json
- context/team/contract-versioning.md
- gates/requirement-review.gate.json
- gates/design-review.gate.json
- gates/dev-entry.gate.json
- gates/service-repo-check.gate.json
