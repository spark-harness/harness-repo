# Impact Analysis

## Metadata

- Requirement ID: SPARK-1
- Analyst: Harness Team
- Status: Reviewed
- Updated At: 2026-06-03

## Summary

本需求影响 `user-api` 服务、`vesta.spark.user.v1` protobuf 契约和后端 gRPC 测试证据。

## Affected Domains

- 用户域
- 前端体验域只作为上游调用方记录，不在本需求内修改。

## Affected Services

| Service | Repo | Reason | Protobuf Required |
|---|---|---|---|
| user-api | `{business-repo}/services/backend/user-api` | 实现 Ping gRPC 入口和业务用例 | yes |
| aegis | `{business-repo}/services/frontend/aegis` | 作为潜在上游调用方记录影响，不修改代码 | no |

## API / Contract Impact

- Does this change involve protobuf IDL or external contracts: yes
- Contract repo: `{idl-repo}`
- Proto files: `{idl-repo}/vesta/spark/user/v1/ping.proto`
- Buf module: local/spark-user
- Buf config version: v2
- Required buf checks: lint / generate / breaking
- Breaking baseline: `.git#branch=master`
- Compatibility risk: 低；新增最小 Ping 契约，不删除字段。

## Data Impact

- Database schema: no
- Data migration: no
- Backfill: no
- Cache: no

## Config / Permission / Observability Impact

- Config: gRPC 端口由服务 starter 默认配置负责。
- Permission: no
- Metrics: 依赖现有 gRPC server 基础指标。
- Logs: 参数错误由 adapter 层返回状态，不额外记录业务日志。
- Tracing: 依赖现有 gRPC 拦截器或后续接入。
- Events: no

## Rollout And Rollback

- Gray release: 本需求是示例服务能力，可在测试环境先验证。
- Kill switch: 不需要独立开关。
- Rollback steps: 回滚业务仓 user-api 改动和 IDL 仓 ping.proto 改动。

## Risks

| Risk | Impact | Mitigation | Owner |
|---|---|---|---|
| 业务仓、IDL 仓和 Harness 仓不在同一需求分支 | 无法安全进入编码循环 | 4.3 服务仓库检查门禁阻塞 | Harness Team |
