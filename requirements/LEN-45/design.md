---
requirement_id: "LEN-45"
owner: "Codex"
status: "approved"
updated_at: "2026-06-21"
approved_by: "forest"
approved_at: "2026-06-21T19:30:08+08:00"
decision: "用户在 Codex 会话中明确回复“批准”，批准 LEN-45 设计方案进入任务拆分与执行阶段。"
---

# Design

## Requirement Traceability

| Requirement Item | Design Decision | Notes |
|---|---|---|
| R1, AC1 | D1: 从服务矩阵删除 `aegis`、`user-api` 和 `dependencies.user-api` | 保留 `fides`、`fides-bff`、`applicant-api` |
| R2, AC2 | D2: 删除业务仓旧服务、旧前端和旧 CI | 不删除 Lendora 主线服务 |
| R3, AC3 | D3: 删除 `idl-repo/vesta/spark` 源契约 | 不手工删除生成仓 |
| R4, AC4 | D4: 删除 `SPARK-*` 需求目录和 `spark/user` 项目上下文 | learning docs 不在范围内 |
| R5, AC5 | D5: 用搜索和基础命令验证 Lendora 主线仍可定位 | `buf lint`、定向 `rg`、状态检查 |

## Summary

方案采用直接下线旧资产的方式，不做兼容迁移：旧 `user-api`、`aegis` 和
`vesta.spark.user.v1` 已不属于当前 Lendora 主线。服务矩阵是拓扑事实源，
先从矩阵移除旧服务，再删除对应业务目录和 IDL 源契约。

## Affected Services

| Service | Change | Reason |
|---|---|---|
| user-api | Delete service, CI, matrix entry, project context | 旧 Spark user 示例服务下线 |
| aegis | Delete frontend app and matrix entry | 旧 Spark 示例前端下线 |
| applicant-api | Keep | Lendora applicant 主线后端 |
| fides | Keep | Lendora 前端 |
| fides-bff | Keep | Lendora 前端 BFF |

## API / Contract Design

- Protobuf IDL required: Yes，删除旧源契约。
- Proto files: remove `idl-repo/vesta/spark/user/v1/*.proto`。
- Buf module: current `idl-repo/buf.yaml` v2 workspace module。
- Buf config version: v2。
- Generated outputs: not manually changed in this ticket。
- Breaking check baseline: `origin/master`。
- Compatibility strategy: 删除旧示例契约属于明确下线。`idl-java-repo` 和
  `idl-go-repo` 由生产同步流程清理，避免手工改 generated code。

## Data / Config / Permission

- Data model: none。
- Config: service matrix and business CI only。
- Permission: none。

## Observability

- Logs: none。
- Metrics: none。
- Tracing: none。
- Events: none。

## Rollout And Rollback

- Gray release: not applicable。
- Kill switch: not required。
- Rollback: revert three repo changes and rerun validation.

## Risks

| Risk | Mitigation | Owner |
|---|---|---|
| 旧生成仓仍短暂保留 user 包 | 记录为生产同步流程清理，不在本票手工修改 | Platform |
| 文档中仍有旧示例 | 用户明确 learning-docs-repo 不在范围；后续单独处理 | Harness Team |
| 删除历史需求目录影响查阅 | Git history remains source for old audit; current requirements tree stays focused on LEN | Harness Team |
