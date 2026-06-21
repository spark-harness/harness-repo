---
requirement_id: "LEN-45"
owner: "Codex"
status: "approved"
created_at: "2026-06-21"
related_branch: "feature/LEN-45-cleanup-old-spark-assets"
target_branch: "master"
release_branch: "master"
contract_gate_mode: "auto"
affected_repositories:
  - harness-repo
  - business-repo
  - idl-repo
approved_by: "forest"
approved_at: "2026-06-21T19:29:21+08:00"
decision: "用户在 Codex 会话中明确回复“批准”，批准 LEN-45 需求定义和影响分析进入下一阶段。"
---

# 清理旧 Spark user/aegis 示例资产

## Background

当前工作区已经以 `applicant-api`、`fides` 和 `fides-bff` 作为 Lendora 主线。
主干仍保留旧 Spark user/aegis 示例资产，包括 `user-api` 服务、`aegis`
前端、`vesta/spark/user` 契约源文件和 `SPARK-*` 历史需求。

先说不是什么：本需求不是重写 Lendora OTP 能力，不修改
`learning-docs-repo`，也不手工维护 Java / Go 生成契约仓。

它是什么：一次跨 `harness-repo`、`business-repo`、`idl-repo` 的旧资产下线，
生成契约仓残留由生产同步流程负责清理。

## Goals

- R1：服务矩阵不再注册 `user-api` 和 `aegis`。
- R2：`business-repo` 不再保留 `user-api` 服务、`aegis` 前端和 `user-api-ci`。
- R3：`idl-repo` 不再保留 `vesta/spark/user` 旧契约源文件。
- R4：`harness-repo` 不再保留 `SPARK-*` 历史需求目录和 `spark/user` 项目上下文入口。
- R5：清理后 `applicant-api`、`fides`、`fides-bff` 主线仍可定位。

## Non-Goals

- 不修改 `learning-docs-repo`。
- 不手工删除 `idl-java-repo` 或 `idl-go-repo` 旧生成物。
- 不修改 `applicant-api`、`fides` 或 `fides-bff` 的业务行为。
- 不删除仍被 Lendora 主线使用的 `spring-starter`、`bffkit` 或 `money`。

## User / Business Scenarios

### Scenario 1：查看服务矩阵

Given：工程师查看服务矩阵。

When：定位当前可用服务。

Then：矩阵只列出 Lendora 当前主线服务和仍有效的公共库，不再列出
`user-api` 或 `aegis`。

### Scenario 2：查看业务仓

Given：工程师查看 `business-repo`。

When：查找可运行服务和对应 CI。

Then：`user-api`、`aegis` 和 `user-api-ci` 不再存在，`applicant-api`、
`fides`、`fides-bff` 保留。

### Scenario 3：查看 IDL 源仓

Given：工程师查看 `idl-repo`。

When：查找 protobuf 契约源。

Then：`vesta/spark/user` 旧契约源不再存在，`vesta/lendora/applicant` 保留。

## Business Rules

- BR1：下线服务必须同时从服务矩阵删除。
- BR2：删除 protobuf 源契约不等于手工编辑生成契约仓。
- BR3：学习文档本次不改；如需更新教程示例，后续单独处理。
- BR4：历史 `SPARK-*` 需求目录应整体清理，避免后续需求检索漂移。

## Acceptance Criteria

- AC1：`.service-matrix/dependencies.yaml` 不再包含 `aegis`、`user-api`、
  `vesta/spark/user` 或 `local/spark-user`。
- AC2：`business-repo` 中 `services/backend/user-api`、
  `services/frontend/aegis` 和 `.github/workflows/user-api-ci.yml` 不再存在。
- AC3：`idl-repo/vesta/spark` 不再存在，且 `buf lint` 通过。
- AC4：`harness-repo/requirements/SPARK-*` 不再存在。
- AC5：`applicant-api`、`fides`、`fides-bff` 仍可通过服务矩阵定位。

## Open Questions

| Question | Owner | Deadline | Status |
|---|---|---|---|
| 是否需要单独更新 learning-docs-repo 中的旧示例 | Harness Team | 后续清理票 | Deferred |

## Notes

- JIRA ticket：LEN-45。
- 用户明确要求本票不包含 `learning-docs-repo`。
- 用户明确要求 `idl-java-repo` 和 `idl-go-repo` 由生产流程清理。
