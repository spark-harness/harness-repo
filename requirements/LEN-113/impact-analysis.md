---
requirement_id: "LEN-113"
analyst: "Codex"
status: "approved"
updated_at: "2026-06-25T21:23:21+08:00"
approved_by: "Forest"
approved_at: "2026-06-25T21:35:08+08:00"
decision: "批准 LEN-113 服务仓库检查，确认本票不修改业务代码或 IDL。"
idl_impact: "no"
idl_impact_reason: "本需求不修改 protobuf、Buf 配置、生成契约仓或外部 API 契约。"
---

# Impact Analysis

## Summary

LEN-113 影响 Spark 治理文档、business-repo 目录事实验证和 Janus 交付仓库推断；不影响业务运行行为、数据、IDL 或外部契约。

## Affected Domains

- Harness lifecycle governance
- Spark multi-repo delivery checks
- Workspace structure verification

## Affected Services

| Service | Repo | Reason | Protobuf Required |
|---|---|---|---|
| N/A | `harness-repo` | 修正治理文档和 requirement lifecycle 产物 | No |
| N/A | `business-repo` | 只重新扫描并记录目录事实；不修改业务代码 | No |
| N/A | `janus` | 修正交付检查或仓库推断逻辑 | No |

## Repository Impact

| Repo | Impact | Expected Change |
|---|---|---|
| `harness-repo` | 模板路径说明、LEN-113 lifecycle 文档、后续门禁和证据 | Yes |
| `business-repo` | 目录状态和服务路径重新扫描 | No code change expected |
| `janus` | 交付仓库推断覆盖治理相关仓库 | Yes |
| `idl-repo` | 无 protobuf 或 Buf 变更 | No |
| `idl-java-repo` / `idl-go-repo` | 无生成契约发布或消费变更 | No |

## Current Workspace Scan

- `business-repo` 主 checkout: `master...origin/master`，干净。
- `.worktrees/LEN-113/business-repo`: `chore/LEN-113-governance-drift`，干净。
- 当前 business-repo 顶层目录包含 `apps/`、`packages/`、`tooling/`、`config/`。
- 当前扫描未发现 `business-repo/services/*`。
- 服务矩阵将服务路径解析为：
  - `fides`: `{business-repo}/apps/fides-web`
  - `fides-bff`: `{business-repo}/apps/fides-bff`
  - `applicant-api`: `{business-repo}/apps/applicant-api`

## API / Contract Impact

- Does this change involve protobuf IDL or external contracts: No.
- Contract repo: N/A.
- Proto files: N/A.
- Buf module: N/A.
- Buf config version: v2, unchanged.
- Required buf checks: N/A.
- Breaking baseline: N/A.
- Compatibility risk: None for IDL/API.

## Generated Contract Impact

- `idl-java-repo`: not affected.
- `idl-go-repo`: not affected.
- No generated files are edited or published by this requirement.

## Data Impact

- Database schema: none.
- Data migration: none.
- Backfill: none.
- Cache: none.

## Config / Permission / Observability Impact

- Config: no runtime service configuration change.
- Permission: no permission model change.
- Metrics: no metrics change.
- Logs: no application logging change.
- Tracing: no tracing change.
- Events: no event schema or emission change.

## Rollout And Rollback

- Gray release: not applicable for runtime services.
- Rollout: merge Harness lifecycle/docs changes and Janus changes through their own PRs after lifecycle gates pass.
- Rollback steps:
  - Revert `harness-repo` documentation/lifecycle commits if the template path correction is wrong.
  - Revert `janus` inference change if delivery checks regress.
  - No business-repo rollback is expected because no business code change is planned.

## Risks

| Risk | Impact | Mitigation | Owner |
|---|---|---|---|
| 已存在 Draft PR 早于 lifecycle 产物创建 | 可能绕过正式 requirement-review | 保持 Draft，等 requirement/design/tasks/gates 补齐后再恢复 Ready | Forest |
| Janus 文本推断仍是名称扫描 | 可能无法表达复杂否定语义 | 本票只补齐治理仓覆盖；复杂语义另开 ticket | Platform |
| business-repo 目录事实再次漂移 | 后续 Agent 路径判断错误 | 以服务矩阵和 README 为准，交付证据记录扫描命令 | Platform |
