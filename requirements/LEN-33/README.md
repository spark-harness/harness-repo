---
requirement_id: "LEN-33"
owner: "Codex"
current_stage: "4.4"
status: "draft"
created_at: "2026-06-17"
related_branch: "feature/LEN-33"
---

# [BE] Java + Spring 业务代码骨架

## Summary

LEN-33 为 Lendora 后端业务服务建立 Java 21 + Spring Boot 工程骨架，使后续 LEN-9 等业务票可以直接落地领域、应用、适配和基础设施代码。

先说不是什么：它不是 fides-bff，不新增业务 API，不实现 LoanApplication、Pricing、OTP、KYC 或提交规则，也不创建持久化表结构。

## Links

- JIRA: LEN-33（Subtask）← LEN-3（后端服务骨架与 API 约定）← LEN-1。
- Branch: `feature/LEN-33`
- Worktree: `.worktrees/LEN-33/{harness-repo,business-repo}`

## Lifecycle Artifacts

- requirement.md
- impact-analysis.md
- design.md
- tasks.json
- gates/
- reviews/
- evidence/
