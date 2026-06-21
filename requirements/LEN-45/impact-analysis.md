---
requirement_id: "LEN-45"
analyst: "Codex"
status: "approved"
updated_at: "2026-06-21"
approved_by: "forest"
approved_at: "2026-06-21T19:33:53+08:00"
decision: "用户在 Codex 会话中明确回复“批准”，批准 LEN-45 服务仓、IDL 仓和排除范围检查进入执行收尾阶段。"
idl_impact: "yes"
idl_impact_reason: "删除 idl-repo 中旧 vesta/spark/user protobuf 源契约；不手工修改生成契约仓。"
---

# Impact Analysis

## Summary

LEN-45 清理旧 Spark user/aegis 示例资产，影响 `harness-repo`、
`business-repo` 和 `idl-repo`。本需求删除旧服务注册、旧业务代码和旧
protobuf 源契约，不改变 Lendora applicant/fides 主线行为。

## Affected Domains

- Harness 服务矩阵和需求生命周期资产。
- 业务仓旧示例服务和前端应用。
- IDL 源契约仓。

## Affected Services

| Service | Repo | Reason | Protobuf Required |
|---|---|---|---|
| user-api | `business-repo` | 下线旧 Spark user 示例服务和 CI | Removed |
| aegis | `business-repo` | 下线旧 Spark 示例前端 | No |
| vesta.spark.user.v1 | `idl-repo` | 删除旧 user protobuf 源契约 | Removed |
| applicant-api | `business-repo` | 保留并确认服务矩阵仍可定位 | Yes |
| fides | `business-repo` | 保留并确认服务矩阵仍可定位 | No |
| fides-bff | `business-repo` | 保留并确认服务矩阵仍可定位 | No |

## Upstream / Downstream Consumers

- `user-api` 原上游 `aegis` 同时下线。
- `applicant-api` 仍以上游 `fides-bff` 为入口。
- `idl-java-repo` 和 `idl-go-repo` 的旧 user 生成物由生产同步流程清理，
  本票不手工修改。

## API / Contract Impact

- Does this change involve protobuf IDL or external contracts: Yes，删除旧
  `vesta.spark.user.v1` 源契约。
- Contract repo: `idl-repo`。
- Proto files: `vesta/spark/user/v1/{auth,ping,profile}.proto`。
- Buf module: local `idl-repo/buf.yaml`。
- Buf config version: v2。
- Required buf checks: `buf lint`；删除契约时 `buf breaking` 预期会报告
  breaking，需要作为已批准的旧示例下线风险记录。
- Breaking baseline: `origin/master`。
- Compatibility risk: 旧 user 契约消费者不可再从源契约重新生成；当前
  Lendora 主线使用 `vesta/lendora/applicant/v1/auth.proto`。

## Generated Contract Impact

- Java generated contracts: 不手工删除，等待生产同步流程。
- Go generated contracts: 不手工删除，等待生产同步流程。
- 本票验证源契约删除和服务矩阵不再引用旧契约。

## Data Impact

- Database schema: none。
- Data migration: none。
- Backfill: none。
- Cache: none。

## Config / Permission / Observability Impact

- Config: 删除 `user-api-ci`，更新服务矩阵。
- Permission: none。
- Metrics: none。
- Logs: none。
- Tracing: none。
- Events: none。

## Rollout And Rollback

- Gray release: not applicable，清理随三仓分支合并生效。
- Kill switch: not required。
- Rollback steps: 恢复对应目录、服务矩阵条目和 IDL 源文件。

## Risks

| Risk | Impact | Mitigation | Owner |
|---|---|---|---|
| 旧 SPARK 历史需求被删除后审计入口减少 | 无法从主线需求目录直接查看旧示例生命周期 | 该需求为明确下线旧资产；Git 历史仍可追溯 | Harness Team |
| 删除 `vesta.spark.user.v1` 是 breaking change | 旧消费者无法继续从源契约生成 | 当前 Lendora 主线不依赖该契约；生成仓清理由生产流程承接 | Platform |
| learning docs 仍有旧示例 | 教程可能出现旧名称 | 用户明确本票不包含 learning-docs-repo，后续单独处理 | Harness Team |
