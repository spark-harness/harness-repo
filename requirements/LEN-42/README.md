---
requirement_id: "LEN-42"
owner: "Codex"
current_stage: "5"
status: "draft"
created_at: "2026-06-21"
related_branch: "feature/LEN-42-buf-plugin-version-lock"
---

# 锁定 Buf 远程生成插件版本

## Summary

LEN-42 将 `idl-repo` 中当前使用的 Buf 远程生成插件从隐式 latest 改为显式版本，避免不同时间运行 `buf generate` 时因为 BSR 插件最新版本漂移而生成不可追溯的代码。

先说不是什么：本需求不新增 protobuf 业务契约，不修改 `.proto`，不创建 `buf.lock`，也不改变 Java / Go generated contract 的发布策略。它只治理生成配置本身。

## Links

- JIRA: LEN-42
- Branch: `feature/LEN-42-buf-plugin-version-lock`
- Worktree: `.worktrees/LEN-42/{harness-repo,idl-repo}`

## Lifecycle Artifacts

- requirement.md
- impact-analysis.md
- design.md
- tasks.json
- gates/
- reviews/
- evidence/
