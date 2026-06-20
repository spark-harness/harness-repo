---
requirement_id: "LEN-41"
owner: "Codex"
current_stage: "4.4"
status: "draft"
created_at: "2026-06-21"
related_branch: "feature/LEN-41-lendora-applicant-idl"
---

# [BE] Lendora applicant IDL namespace 迁移

## Summary

LEN-41 修正 Lendora applicant 身份契约的项目归属：将 applicant protobuf 从 `vesta/spark/applicant/v1` 迁移到 `vesta/lendora/applicant/v1`，并同步 protobuf package、Java package 和 Go import path 的 namespace。

Maven artifact 和 Go module 不新建、不改名：继续使用 `spark-harness/idl-java-repo` 发布 `com.spark.contract:spark-idl-java`，继续使用 `spark-harness/idl-go-repo` / `github.com/spark-harness/idl-go-repo` 发布 Go 生成物。这里修正的是 applicant 契约 namespace，不是生成仓库或 artifact 的产品拆分。

先说不是什么：本需求不迁移 `vesta/spark/user/*`，因为 user 后续会移除；也不改变 `ApplicantAuthService` 的 OTP、verify 或 refresh 行为。

## Links

- JIRA: LEN-41（Subtask）← LEN-2（手机验证登录）← LEN-1。
- Parent business story: LEN-2。
- Related implementation: LEN-12 applicant-api。
- Branch: `feature/LEN-41-lendora-applicant-idl`
- Worktree: `.worktrees/LEN-41/{harness-repo,idl-repo,idl-java-repo,idl-go-repo,business-repo}`

## Lifecycle Artifacts

- requirement.md
- impact-analysis.md
- design.md
- tasks.json
- gates/
- reviews/
- evidence/
