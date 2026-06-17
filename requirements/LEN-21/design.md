---
requirement_id: "LEN-21"
owner: "Backend / Harness"
status: "approved"
updated_at: "2026-06-15"
approved_by: "forest"
approved_at: "2026-06-15T00:00:00+08:00"
decision: "设计满足进入任务拆分阶段的最低要求；遵循 Kratos 布局并保持干净架构边界。"
---

# Design — fides-bff（前端 BFF：REST /api/v1 + 横切约定）

## Requirement Traceability

| Requirement Item | Design Decision | Notes |
|---|---|---|
| R1 BFF / Go / Kratos / REST /api/v1 | 用 Kratos 起 `fides-bff`，HTTP 暴露 `/api/v1` | Kratos 标准布局 `internal/{conf,server,service,biz,data}` |
| R2 + BR2 统一错误信封 | adapter/inbound 错误映射中间件 + 统一错误模型 | 422 + details[] |
| R3 + BR4 幂等 | 幂等中间件 + `IdempotencyStore` 端口 | T1 可内存，后替 Redis |
| R4 + BR5 可观测 | OTel + 结构化日志 + traceId 透传 gRPC metadata | 依 team/logging,tracing,metrics |
| R5 可运行 | `cmd/fides-bff` + `/api/v1/health` + Makefile + Go CI | T1 范围 |
| R6 + BR3 gRPC 客户端 + status→REST 映射 | infrastructure 出站 gRPC 端口 + 映射表；下游未就绪用桩 | 延后到首个业务端点 |
| BR6 横切可复用 | 横切放共享中间件包，不绑死单服务 | 供后续多 BFF 复用 |

## Summary

`fides-bff` 是前端 `fides` 的 BFF：Kratos 框架 + 团队干净架构分层；对前端 REST `/api/v1`，对内 gRPC 调领域服务。本设计覆盖整个 LEN-21（骨架 + 横切约定）；实现按 `tasks.json` 切片，**T1 = 可运行骨架（无下游、无契约）**，横切与映射为后续任务。

## Affected Services

| Service | Change | Reason |
|---|---|---|
| fides-bff | 新建 | BFF 入口 + 横切约定 |
| fides | 不改（上游调用方） | 消费 `/api/v1` |
| 领域服务（user-api 等） | 不改（下游被调） | T1 不调；后续经 gRPC，未就绪用桩 |

## API / Contract Design

- Protobuf IDL required: **no**（本需求不新增/修改 `.proto`）。
- REST 契约：`/api/v1`、JSON、资源名复数；统一错误信封 `{ error: { code, message, field?, traceId } }`，字段校验 `422` + `details[]`。
- 健康检查：`GET /api/v1/health` → `{ status, version }`。
- gRPC status → REST 映射表（BR3 / AC6）：

| gRPC status | HTTP | 信封 code 取向 |
|---|---|---|
| INVALID_ARGUMENT | 422 | validation_error |
| NOT_FOUND | 404 | not_found |
| ALREADY_EXISTS / ABORTED | 409 | conflict |
| PERMISSION_DENIED | 403 | forbidden |
| UNAUTHENTICATED | 401 | unauthorized |
| 其余 | 500 | internal |

错误码取值遵 `team/error-codes`。

## Application Design

分层（**遵循 Kratos 标准布局**，并保持团队干净架构的依赖方向与职责边界）：

```text
services/backend/fides-bff/
  cmd/fides-bff/       bootstrap：main + wire 装配
  api/                 本服务对外 API 定义（BFF 暴露 REST；如需 openapi/proto 放此）
  configs/             配置 yaml
  internal/
    conf/              配置结构
    server/            transport：http(/api/v1) + 中间件注册（错误信封/幂等/可观测）
    service/           handler：/api/v1 路由、req/resp 映射、错误信封映射
    biz/               业务：BFF 用例 + 出站端口接口（下游 gRPC、幂等存储）
    data/              出站实现：gRPC 客户端(实现 biz 端口)、幂等存储
```

横切中间件（错误信封 / 幂等 / traceId）做成**共享 Go 包**（`business-repo/packages/...`，类比 Java 的 spring-starter），各 BFF 的 `server` 装配它（BR6）。

**Kratos 包 ↔ 团队干净架构职责**（用于满足设计门禁的边界 / 依赖检查）：

| Kratos 包 | 干净架构职责 | 依赖约束 |
|---|---|---|
| `service` | adapter/inbound | 仅协议适配，不放业务规则；依赖 `biz` |
| `biz` | application(用例) + domain + 端口接口 | 不依赖 `service`/`data`/`server`；端口由 `biz` 定义 |
| `data` | infrastructure | 实现 `biz` 端口；不反向污染 `biz` |
| `server` / `cmd` | transport / bootstrap | 装配、注册中间件 |
| `conf` | config | — |

依赖方向：`service → biz`，`data → biz`（端口在 `biz` 定义、`data` 实现），`server`/`cmd` 装配。Kratos 默认即此倒置方向，符合 `backend-clean-architecture` 的依赖约束。

**开放问题 1（Kratos 布局 vs 团队干净架构）→ 决议**：**遵循 Kratos 标准布局** `internal/{conf,server,service,biz,data}`。BFF 领域很薄，按团队「小服务不强行拆包」原则，`biz` 合并领域与用例即可；关键约束是保持依赖倒置（端口在 `biz`、实现在 `data`）与 `service` 只做协议适配。

**开放问题 2（idl-go-repo 契约消费）→ 决议**：T1 骨架**不调下游、不依赖任何契约**。下游 gRPC 客户端在「首个业务端点」任务才引入；届时 `idl-go-repo` 作为 Go module 消费（补 `go.mod` + 版本；本地开发用 `go.mod` replace 指向本地路径）。本设计列为后续任务前置 + 风险，**不阻塞 T1**。

**开放问题 3（下游未就绪）→ 决议**：出站 gRPC 端口在 `application/port` 定义；`infrastructure` 提供真实 gRPC 实现 + 桩实现，按 config 选择。领域服务未在 service-matrix 就绪时用桩。T1 无业务端点，按裁剪原则**不创建任何下游 port / infrastructure/external**。

横切（共享中间件，BR6）：

- 错误信封中间件：捕获用例 / 下游错误 → 统一信封；gRPC status→HTTP 映射（BR2/BR3）。
- 幂等中间件：读 `Idempotency-Key` → 经共享包 `IdempotencyStore` 端口原子占位、校验请求指纹、去重 / 回放首次结果（BR4）。`fides-bff` 只在 bootstrap 注入具体 store，`server` 只注册中间件。MVP 内存实现必须限制 key 格式 / 长度、请求体指纹读取上限和进程内记录数，避免横切层成为无界资源入口。
- 可观测中间件：每请求生成 traceId/correlationId，注入 context + 结构化日志 + 透传下游 gRPC metadata（BR5）。日志、metric、span 使用低基数 route/operation，并在错误响应上记录稳定 `error_code`。

## Data / Config / Permission

- Data model：BFF 无自有业务持久化。幂等需 `IdempotencyStore`（key + 请求指纹 → 首次响应 + TTL）：候选 Redis（与 user-api 既有 Redis 对齐）；MVP 可先在共享 `bffkit` 中提供内存实现（端口隔离、后替换），由 bootstrap 注入到 `server`。T1 可用内存 / noop。
- Config：服务端口、下游 gRPC 地址、幂等存储连接、日志 / OTel 配置（Kratos conf）。
- Permission：本需求不含鉴权（属 LEN-22）；BFF 是其挂载点。

## Observability

- Logs：结构化（`team/logging`），每条带 traceId/correlationId；错误请求带稳定 `error_code`；不打印 PII / 密钥。
- Metrics：RED 基线（请求量 / 错误率 / 时延），命名与标签遵 `team/metrics`；route/operation 标签保持低基数。
- Tracing：OpenTelemetry（`team/tracing`），server span 并透传到下游 gRPC metadata；错误 span 带稳定 `error_code`。
- Events：无。

## Error Codes

| Error Code | HTTP / gRPC Mapping | Meaning | Retryable | User Visible | Owner | Status |
|---|---|---|---:|---:|---|---|
| `BFF-PARAM-0001` | HTTP 400/422；gRPC `INVALID_ARGUMENT` | 前端 BFF 请求参数或字段校验失败，包括缺少必需 `Idempotency-Key` | No | Yes | backend | Active |
| `BFF-STATE-0001` | HTTP 404；gRPC `NOT_FOUND` | 请求资源不存在或下游返回 not found | No | Yes | backend | Active |
| `BFF-CONFLICT-0001` | HTTP 409；gRPC `ALREADY_EXISTS` / `ABORTED` | 请求冲突，包括相同幂等 key 搭配不同请求指纹 | Depends | Yes | backend | Active |
| `BFF-PERMISSION-0001` | HTTP 403；gRPC `PERMISSION_DENIED` | 当前主体无权限执行该操作 | No | Yes | backend | Active |
| `BFF-AUTH-0001` | HTTP 401；gRPC `UNAUTHENTICATED` | 未认证或认证失效 | No | Yes | backend | Active |
| `BFF-SYSTEM-0001` | HTTP 500；其余 gRPC status | BFF 内部或未分类下游错误 | Yes | No | backend | Active |

## Testing strategy

按 `backend-clean-architecture` 测试要求 + `team/testing`，并遵 `spark-test-first`（先写失败测试再实现）：

- adapter/inbound：`/api/v1/health`（AC1）、错误信封 + 422 details（AC2）、gRPC status→REST 映射（AC6/BR3）。
- application：幂等编排——相同 `Idempotency-Key` 回放首次结果（AC3）。
- infrastructure / 集成：幂等存储（下游 gRPC 客户端在后续任务）。
- 可观测：traceId 贯穿日志 + gRPC metadata 的断言（AC4）。
- 全链路 E2E 属 LEN-32，不在本需求。

## Rollout And Rollback

- Gray release：全新服务先测试环境；前端 `fides` 切 BFF 可灰度。
- Kill switch：不需要（新服务、无存量流量）。
- Rollback：回滚 `business-repo` 的 `fides-bff` + `.service-matrix` 登记。

## Risks

| Risk | Mitigation | Owner |
|---|---|---|
| `idl-go-repo` 非 git 仓、未 Go module 化 | 首个下游调用任务前补 `go.mod` + replace；T1 不依赖 | backend |
| 仓内第一个 Go/Kratos 服务、无样板、Go CI 缺失 | T1 先打通 Kratos 骨架 + Go CI(lint/test) | backend |
| 幂等存储 MVP 用内存不持久 | 端口隔离、后替 Redis；设计已留 `IdempotencyStore` 端口 | backend |
| 遵循 Kratos 布局时 biz/data 边界被淡化 | 评审检查依赖倒置（端口在 biz、实现在 data）、service 不含业务规则 | backend |
