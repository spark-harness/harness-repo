---
requirement_id: "LEN-99"
owner: "forest"
current_stage: "1"
status: "draft"
created_at: "2026-06-25"
---

# business-repo 三目录 monorepo 迁移

## Summary

将 `business-repo` 从旧的 `services/`、根 `packages/`、根 `scripts/` 混合结构迁移为 `apps/`、`packages/`、`tooling/` 三类目录，并同步 Harness 服务矩阵、CI / Argo path gate、delivery-readiness 和回归验证证据。

## Lifecycle Artifacts

- requirement.md
- impact-analysis.md
- design.md
- tasks.json
- gates/
- reviews/
- evidence/

## Jira Trace

- Epic：LEN-99
- 代码目录迁移：LEN-100（LEN-101、LEN-102、LEN-103、LEN-104）
- 治理路径切换：LEN-105（LEN-106、LEN-107、LEN-108）
- 验证收口：LEN-109（LEN-110、LEN-111、LEN-112）
