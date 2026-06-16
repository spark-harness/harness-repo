---
requirement_id: "LEN-21"
analyst: "Backend / Harness"
status: "approved"
updated_at: "2026-06-15"
approved_by: "forest"
approved_at: "2026-06-15T00:00:00+08:00"
decision: "影响面分析满足进入设计阶段的最低要求。"
idl_impact: "no"
idl_impact_reason: "本需求不新增/修改 .proto；fides-bff 消费现有 Go 契约生成物，protobuf 契约随各领域需求产出。本需求引入的是 HTTP/REST 契约（/api/v1），见 API / Contract Impact。"
---

# Impact Analysis

## Summary

新增前端 BFF 服务 `fides-bff`（Go / Kratos），对前端 `fides` 暴露 REST `/api/v1` 并落地全局 API 约定（错误信封 / 幂等 / 可观测 / 健康检查），对内以 gRPC 调用领域服务。不改任何现有服务、不改 protobuf 契约。

## Affected Domains

- 前端体验 / 边缘域（BFF 入口）——本需求修改对象。
- 下游领域域（identity / origination / pricing / kyc / banking 等）——仅作为被调用方记录，本需求不修改；未就绪时以桩 / 缺省下游处理。

## Affected Services

| Service | Repo | Reason | Protobuf Required |
|---|---|---|---|
| fides-bff | `{business-repo}/services/backend/fides-bff` | 新建 BFF：REST `/api/v1` + 横切约定 + gRPC 客户端装配 | no（消费契约，不定义） |
| fides | `{business-repo}/services/frontend/fides` | 上游调用方（消费 REST），本需求不改代码 | no |
| user-api 等领域服务 | `{business-repo}/services/backend/*` | 作为下游 gRPC 被调记录影响，本需求不改 | no |

> `fides-bff` 需登记进 `.service-matrix/dependencies.yaml`（`module: frontend`、`language: go`、`idl_required: false`），将在任务阶段/服务仓库检查门禁前完成。

## API / Contract Impact

- Does this change involve protobuf IDL or external contracts: 引入 **HTTP/REST 契约**（不涉及 protobuf 变更）。
- Contract repo: 无 protobuf 改动；REST 契约随 `fides-bff` 代码与 backend/05 风格演进。
- Proto files: 无（本需求不创建/修改 `.proto`）。
- Buf module / config version: 不涉及（本需求不动 Buf 配置）。
- Required buf checks: 不涉及。
- Breaking baseline: 不涉及。
- Compatibility risk: REST 契约为**新增**（`/api/v1` 首次出现），无破坏既有契约风险。
- gRPC 消费：`fides-bff` 调下游领域服务依赖 `idl-go-repo` 的 Go 生成桩——**风险：`idl-go-repo` 当前非 git 仓、Go 模块路径未定**（见 Risks，设计阶段解决）。T1 骨架不调下游，故不阻塞 T1。

## Data Impact

- Database schema: no（BFF 无自有业务持久化）。
- Data migration: no。
- Backfill: no。
- Cache / runtime storage: 幂等需要存储 `Idempotency-Key → 首次响应`；候选 Redis（与 user-api 既有 Redis 一致）或 MVP 内存实现，设计阶段定。

## Config / Permission / Observability Impact

- Config: 服务端口、下游领域 gRPC 地址、幂等存储连接。
- Permission: 本需求不含鉴权（属 `LEN-22`）；BFF 是后续鉴权 / 越权中间件的挂载点。
- Metrics: BFF 请求量 / 错误率 / 时延基线（依 `team/metrics`）。
- Logs: 结构化日志带 traceId（依 `team/logging`）。
- Tracing: OpenTelemetry，traceId / correlationId 透传到下游 gRPC metadata（依 `team/tracing`）。
- Events: no。

## Rollout And Rollback

- Gray release: 全新服务，先测试环境验证；前端 `fides` 切到 BFF 可灰度。
- Kill switch: 不需要独立开关（新服务、无存量流量）。
- Rollback steps: 回滚 `business-repo` 的 `fides-bff` 改动 + `.service-matrix` 登记；前端回退到调用方未切换状态。

## Risks

| Risk | Impact | Mitigation | Owner |
|---|---|---|---|
| `idl-go-repo` 非 git 仓、Go 契约消费路径未定 | 阻塞 BFF 调下游 gRPC（非 T1） | 设计阶段定模块路径 / 获取方式；T1 不依赖下游 | Backend |
| Kratos 默认布局与团队 `backend-clean-architecture` 不一致 | 评审与一致性风险 | 设计阶段定目录纪律映射 | Backend |
| 这是仓内第一个 Go 服务、无现成样板 | 起步成本、CI 缺失 | 设计阶段定 Kratos layout + Go CI；T1 范围小、先打通骨架 | Backend |
| 三仓分支不一致 | 过不了 4.3 服务仓库检查门禁 | harness + business 已同名分支 `feature/fides-bff/LEN-21`；idl 本需求不涉及 | Harness |
