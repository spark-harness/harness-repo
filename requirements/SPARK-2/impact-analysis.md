---
requirement_id: "SPARK-2"
analyst: "Harness Team"
status: "Reviewed"
updated_at: "2026-06-03"
---

# Impact Analysis

## Summary

本需求影响 `user-api` 服务和 `vesta.spark.user.v1` protobuf 契约。`aegis` 作为潜在上游调用方记录影响，本次不修改前端代码。

## Affected Domains

- 用户域
- 前端体验域只作为上游调用方记录，不在本需求内修改。

## Affected Services

| Service | Repo | Reason | Protobuf Required |
|---|---|---|---|
| user-api | `{business-repo}/services/backend/user-api` | 实现手机号验证码注册/登录 gRPC 入口和业务用例 | yes |
| aegis | `{business-repo}/services/frontend/aegis` | 作为潜在上游调用方记录影响，不修改代码 | no |

## API / Contract Impact

- Does this change involve protobuf IDL or external contracts: yes
- Contract repo: `{idl-repo}`
- Proto files: `{idl-repo}/vesta/spark/user/v1/auth.proto`
- Buf module: local/spark-user
- Buf config version: v2
- Required buf checks: lint / generate / breaking
- Breaking baseline: `.git#branch=master`
- Compatibility risk: 低；新增 AuthService 和消息，不删除现有 Ping 契约。

## Data Impact

- Database schema: no
- Data migration: no
- Backfill: no
- Cache: no
- Runtime storage: 本阶段使用内存用户仓储，服务重启后数据丢失，后续持久化需求再替换。

## Config / Permission / Observability Impact

- Config: gRPC 端口由服务 starter 默认配置负责。
- Permission: no service-specific permission in this stage.
- Metrics: 依赖现有 gRPC server 基础指标。
- Logs: 参数错误由 adapter 层返回状态，不额外记录手机号明文日志。
- Tracing: 依赖现有 gRPC 拦截器或后续接入。
- Events: no

## Rollout And Rollback

- Gray release: 本需求可在本地或测试环境先通过 grpcurl / 单元测试验证。
- Kill switch: 不需要独立开关。
- Rollback steps: 回滚业务仓 user-api 改动和 IDL 仓 auth.proto 改动。

## Risks

| Risk | Impact | Mitigation | Owner |
|---|---|---|---|
| 真实短信发送未接入导致误认为生产可用 | 产品和研发口径不一致 | 在 Non-Goals、设计和 evidence 中明确只使用验证码端口测试实现 | Harness Team |
| 内存用户仓储不具备生产持久性 | 服务重启后用户数据丢失 | 本需求限定为最小流程验证，后续持久化需求替换仓储实现 | Harness Team |
| 手机号明文写入日志 | 泄露敏感信息 | 设计约束 adapter 不记录手机号明文 | Harness Team |

## Required Current-State Updates

- `context/project/spark/user/current-state.md`
