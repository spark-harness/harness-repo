---
requirement_id: "LEN-38"
owner: "Codex"
status: "draft"
created_at: "2026-06-20"
related_branch: "feature/LEN-38-go-idl-publishing"
approved_by: ""
approved_at: ""
decision: ""
---

# LEN-38 实现 Go IDL 生成物发布链路

## Purpose

补齐 Go IDL 生成物的仓库化、同名分支同步、RC tag 发布和 formal tag 发布能力，使 Go 契约生成物具备与 Java 生成物一致的可追溯发布入口。

## Source

- JIRA: LEN-38
- 规则来源: LEN-35 `context/team/contract-versioning.md`
- Go module path: `github.com/spark-harness/idl-go-repo`
- 分支: `feature/LEN-38-go-idl-publishing`

## Scope

- `harness-repo`: 需求、影响分析、设计、任务、门禁和证据。
- `idl-repo`: Go 生成物同步和 tag 发布 workflow。
- `idl-go-repo`: Go module 仓库初始化、生成物目录、校验和 tag 发布目标。

## Worktrees

```text
.worktrees/LEN-38/harness-repo
.worktrees/LEN-38/idl-repo
.worktrees/LEN-38/idl-go-repo
```
