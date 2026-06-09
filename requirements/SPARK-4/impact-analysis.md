---
requirement_id: "SPARK-4"
analyst: "Codex"
status: "approved"
updated_at: "2026-06-09"
approved_by: "Forest"
approved_at: "2026-06-09T00:10:20+08:00"
decision: "影响分析已获批准，可以进入设计确认和后续 IDL 变更准备。"
idl_impact: "yes"
idl_impact_reason: "新增 user-api 修改用户名 gRPC API，需要新增 protobuf RPC 和消息。"
---

# Impact Analysis

## Summary

本需求影响 `user-api` 服务、`vesta.spark.user.v1` protobuf 契约和生成契约仓；`aegis` 作为潜在上游调用方记录影响，本次不修改前端代码。

## Affected Domains

- 用户域
- 前端体验域只作为上游调用方记录，不在本需求内修改。

## Affected Services

| Service | Repo | Reason | Protobuf Required |
|---|---|---|---|
| user-api | `{business-repo}/services/backend/user-api` | 实现修改用户名 gRPC 入口和业务用例 | yes |
| aegis | `{business-repo}/services/frontend/aegis` | 作为潜在上游调用方记录，不修改代码 | no |

## Upstream / Downstream Consumers

- Upstream: `aegis` 未来可以调用修改用户名 API。
- Downstream: no external downstream service in this stage.
- Generated contract consumers: Java consumer in `user-api` depends on `idl-java-repo` output.

## API / Contract Impact

- Does this change involve protobuf IDL or external contracts: yes
- Contract repo: `{idl-repo}`
- Proto files: `{idl-repo}/vesta/spark/user/v1/profile.proto`
- Buf module: local/spark-user
- Buf config version: v2
- Required buf checks: lint / generate / breaking
- Breaking baseline: `.git#branch=master`
- Compatibility risk: 低；新增 Profile 类服务和消息，不删除或修改现有 `PingService`、`AuthService` 字段和 RPC。

## Generated Contract Impact

- Java generated contracts: yes, sync to `{idl-java-repo}` through `buf generate`.
- Go generated contracts: generated output follows `buf.gen.yaml` if configured.
- Manual generated-file edits: not allowed.

## Data Impact

- Database schema: no
- Data migration: no
- Backfill: no
- Cache: no
- Runtime storage: 当前用户仓储为内存实现。本需求会扩展运行时用户对象支持用户名，但服务重启后数据仍会丢失，持久化留给后续需求。

## Config / Permission / Observability Impact

- Config: gRPC 端口由服务 starter 默认配置负责，不新增配置项。
- Permission: no service-specific permission in this stage.
- Metrics: 依赖现有 gRPC server 基础指标。
- Logs: 不记录完整手机号或验证码；用户名错误以 gRPC 状态返回，不要求新增业务日志。
- Tracing: 依赖现有 gRPC 拦截器或后续接入。
- Events: no

## Rollout And Rollback

- Gray release: 本地或测试环境先通过单元测试、gRPC adapter 测试和 grpcurl 验证。
- Kill switch: 不需要独立开关。
- Rollback steps: 回滚 Harness SPARK-4 产物、IDL 契约变更、生成契约变更和 `user-api` 修改用户名实现。

## Risks

| Risk | Impact | Mitigation | Owner |
|---|---|---|---|
| API 未做真实鉴权被误认为生产安全能力 | 产品和研发对安全边界理解不一致 | Non-Goals、设计和证据明确本阶段直接接收 `user_id`，鉴权另建需求 | Harness Team |
| 当前内存仓储不具备生产持久性 | 服务重启后用户名丢失 | 影响分析和设计明确运行时存储边界，后续持久化需求替换仓储实现 | Harness Team |
| 用户名规则过宽 | 后续产品规则调整可能需要兼容 | 本阶段只做非空校验，不做唯一性和审核承诺 | Harness Team |
| IDL 生成物与业务仓依赖不同步 | 编译失败或运行时契约不一致 | IDL 任务单独拆分，必须记录 Buf 和 Maven 测试证据 | Harness Team |
