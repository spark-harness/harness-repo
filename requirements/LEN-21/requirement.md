---
requirement_id: "LEN-21"
owner: "Backend / Harness"
status: "approved"
created_at: "2026-06-14"
related_branch: "feature/fides-bff/LEN-21"
approved_by: "forest"
approved_at: "2026-06-15T00:00:00+08:00"
decision: "需求定义满足进入设计阶段的最低要求。"
---

# Lendora 申请 BFF 骨架与 REST API 约定（fides-bff）

## Background

Lendora MVP 的前端 `fides` 需要一个稳定、一致、可联调的后端入口来接入申请漏斗各能力。领域能力将以 gRPC 提供，但前端要的是 REST/JSON。当前没有这样的入口。

先说「不是什么」：这一需求不实现任何业务功能（不发 OTP、不试算、不提交、不查状态），也不是领域服务本身；它只立「所有前端请求共同遵守的后端入口与约定」并把这个 BFF 服务跑起来。缺了它，每个业务能力会各搭一套、错误/幂等/可观测各不相同、前端无法统一接入。

## Goals

- R1：提供前端 BFF 服务 `fides-bff`（Go / Kratos），对前端暴露 REST `/api/v1`。
- R2：统一错误信封——所有错误返回一致结构（错误码 + 可读信息 + traceId）；字段校验错误逐字段返回。
- R3：幂等——非幂等写操作支持 `Idempotency-Key`，重复请求返回首次结果。
- R4：可观测基线——每请求贯穿 traceId / correlationId 并落结构化日志。
- R5：可运行——本地一键启动 + 健康检查 + CI（lint / test）。
- R6：对内 gRPC 调用能力就位（客户端装配 + gRPC status → REST 信封映射）；领域服务未就绪时可暂以桩 / 缺省下游。

## Non-Goals

- 不实现任何业务领域逻辑（OTP / 试算 / 资料 / 提交 / 状态，各属其需求）。
- 不建领域 gRPC 服务本体（随各业务需求与契约一起做）。
- 不含会话鉴权与越权防护（属兄弟需求 `LEN-22`）。
- 不接真实第三方；不做生产部署 / CD。
- 不预建多个 BFF（一个前端体验对应一个 BFF）。

## User / Business Scenarios

### Scenario 1

Given：`fides-bff` 已本地启动。

When：客户端请求 `GET /api/v1/health`。

Then：返回健康状态与版本信息。

### Scenario 2

Given：某接口触发错误（业务错误或字段校验失败）。

When：客户端收到响应。

Then：响应体是统一错误信封（含 `code` 与 `traceId`）；字段校验错误返回 `422` 且含逐字段 `details`。

### Scenario 3

Given：客户端以相同 `Idempotency-Key` 重复发送同一写请求。

When：第二次请求到达。

Then：返回首次结果，不重复执行。

### Scenario 4

Given：一次请求经 BFF 转发到领域 gRPC。

When：BFF 处理该请求。

Then：traceId / correlationId 贯穿日志并透传到 gRPC metadata。

## Business Rules

- BR1：REST 风格——`/api/v1` 前缀、JSON、资源名复数。
- BR2：错误信封固定结构 `{ error: { code, message, field?, traceId } }`；字段校验错误用 `422` + `details[]`。
- BR3：gRPC status 必须映射为对应 REST 错误信封，不可把裸 gRPC 错误透传给前端。
- BR4：非幂等写操作要求 `Idempotency-Key`；按 key 去重并回放首次结果。
- BR5：每请求生成 / 透传 traceId，写入结构化日志并透传到 gRPC metadata。
- BR6：横切能力（错误信封 / 幂等 / 可观测 / 映射）以可复用方式实现，供后续多个 BFF 复用，不绑死单一服务。

## Acceptance Criteria

- AC1：`GET /api/v1/health` 返回成功及健康 / 版本信息（覆盖 S1、R5）。
- AC2：触发错误时返回统一错误信封含 `code` + `traceId`；字段校验错误返回 `422` + `details[]`（覆盖 S2、BR2）。
- AC3：相同 `Idempotency-Key` 重复写返回首次结果、不重复执行（覆盖 S3、BR4）。
- AC4：贯穿 BFF→gRPC 的一次请求，traceId 在日志与 gRPC metadata 中可见（覆盖 S4、BR5）。
- AC5：本地一键启动成功、健康检查通过、CI 跑通 lint + test（覆盖 R5）。
- AC6：gRPC status → REST 信封映射有测试覆盖（覆盖 BR3）。

> 与 JIRA 对齐：AC2→LEN-21/AC1，AC3→LEN-21/AC3，AC5→LEN-21/AC5；鉴权 / 越权（LEN-21/AC2、AC4）属兄弟需求 LEN-22。

## Open Questions

| Question | Owner | Deadline | Status |
|---|---|---|---|
| Kratos 默认布局（cmd/internal/{biz,service,data}）与团队 `backend-clean-architecture` 如何对齐 | Backend | 设计阶段 | Open |
| `fides-bff` 如何消费 Go 契约（`idl-go-repo` 当前非 git 仓 / 模块路径未定） | Backend | 设计阶段 | Open |
| 领域服务尚未就绪时，下游用桩还是缺省实现 | Backend | 设计阶段 | Open |

## Notes

- 关联 JIRA 子任务 `LEN-21`（父 Story `LEN-3` / Epic `LEN-1`）；兄弟需求 `LEN-22`（鉴权 / 越权）独立成需求、串行在后。
- `requirement.md` 与 `impact-analysis.md` 同属需求定义阶段；`requirement-review` 门禁待二者就绪并获批后生成。
- 最优先实现 task = T1（`fides-bff` 可运行骨架），其余横切（错误信封 / 幂等 / 可观测 / 映射）为后续 task，详见 `tasks.json`（阶段 4.1）。
