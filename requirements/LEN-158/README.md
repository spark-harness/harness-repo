---
requirement_id: "LEN-158"
owner: "forest"
current_stage: "4.4"
status: "draft"
created_at: "2026-07-04"
---

# Lendora 配置中心从 Consul 迁移到 Vault/VSO

## Lifecycle Artifacts

- requirement.md
- impact-analysis.md
- design.md
- tasks.json
- gates/
- reviews/
- evidence/

## Jira Scope

- Epic: LEN-158
- Stories: LEN-159, LEN-162, LEN-165, LEN-168, LEN-172
- Sub-tasks: LEN-160, LEN-161, LEN-163, LEN-164, LEN-166, LEN-167, LEN-169, LEN-170, LEN-171, LEN-173, LEN-174

## Execution Order

1. Platform and Vault runtime foundation.
2. Parallel service code migration.
3. GitOps VSO Secret integration.
4. dev-1 verification.
5. sta-1 verification and Consul KV bootstrap cleanup.
