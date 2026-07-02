---
requirement_id: "LEN-153"
owner: "forest"
status: "approved"
created_at: "2026-07-02"
related_branch: "feature/LEN-153-fides-bff-contracts"
target_branch: "master"
release_branch: "master"
contract_gate_mode: "auto"
affected_repositories:
  - harness-repo
  - idl-repo
  - idl-go-repo
  - idl-openapi-repo
  - idl-ts-repo
approved_by: "forest"
approved_at: "2026-07-02T00:00:00+08:00"
decision: "用户已授权 Agent 批准所有需要的文件；批准 LEN-153 需求定义和影响分析，按 additive fides-bff pricing / loan-application IDL 范围进入设计与开发。"
---

# [IDL] fides-bff 补齐 pricing / loan application 契约并生成 SDK

## Background

父 Story `LEN-152` 要求 fides 申请流程中的手机验证、贷款请求、申请草稿和身份资料填写都走统一 BFF 边界，并能在一次用户操作中形成可追踪链路。

当前 BFF-facing IDL 已覆盖 auth 和 identity-profile，但 pricing 与 loan application 仍没有进入 fides-bff 生成契约面。前端和 BFF 后续无法只依赖生成 SDK、OpenAPI 和 Kratos HTTP binding 完成统一迁移。

它不是什么：本需求不是实现新的贷款规则，不是改写 BFF 业务编排，也不是修改前端调用方式。

它是什么：只补齐 fides-bff 前端契约和生成证据，让后续 BFF、FE、GitOps 子任务可以消费同一组生成契约。

## Goals

- R1：保留已有 fides-bff auth proto，不替换或改变现有 RPC 语义。
- R2：保留已有 fides-bff identity-profile proto，并确认其 HTTP annotation 能继续生成 BFF HTTP binding。
- R3：新增 fides-bff pricing 契约，覆盖创建贷款报价的 BFF-facing HTTP API。
- R4：新增 fides-bff loan-application 契约，覆盖创建、读取、更新贷款申请草稿的 BFF-facing HTTP API。
- R5：新增或更新 proto 后能通过 Buf lint、Go/Kratos HTTP 生成、OpenAPI 生成和 breaking 检查。
- R6：生成输出中能看到 pricing 与 loan-application 的 Go HTTP binding、OpenAPI 路径和 TypeScript SDK API class。
- R7：契约覆盖父 Story AC1-AC4、AC6 中与 BFF 前端边界有关的接口。

## Non-Goals

- 不实现 `fides-bff` service 方法或替换手写路由；`LEN-154` 负责。
- 不修改 `fides-web` adapter 或生成 TS SDK 消费方式；`LEN-155` 负责。
- 不实现 `/api/v1` 应用内代理或浏览器 fetch 自动追踪；`LEN-156` 负责。
- 不修改 dev / sta GitOps 或 Consul 配置；`LEN-157` 负责。
- 不改变 quote-api、origination-api、applicant-api 的业务规则、数据模型或部署配置。
- 不手工编辑生成物；生成仓只同步工具产出的文件。

## User / Business Scenarios

### Scenario 1：贷款请求报价契约可生成

Given：用户已登录并进入贷款请求步骤。

When：前端需要通过 BFF 请求贷款报价。

Then：fides-bff IDL 提供带 `google.api.http` annotation 的 pricing RPC，生成物能表达 `/api/v1/pricing/quotes` 的请求和响应。

### Scenario 2：贷款申请草稿契约可生成

Given：用户已获得报价并继续保存申请草稿。

When：前端需要通过 BFF 创建、读取或更新 loan application draft。

Then：fides-bff IDL 提供带 HTTP annotation 的 create、get、patch RPC，生成物能表达 `/api/v1/loan-applications` 和 `/api/v1/loan-applications/{application_id}`。

### Scenario 3：身份资料契约继续生成

Given：用户进入身份资料步骤。

When：前端读取或保存 identity profile。

Then：现有 identity-profile RPC 继续出现在生成 HTTP binding 和 OpenAPI 中，不因本次新增 pricing / loan-application 契约而回退。

### Scenario 4：后续子任务消费同一契约源

Given：BFF 和 FE 子任务开始实现。

When：它们需要生成接口、OpenAPI 或 TS SDK。

Then：它们从 fides-bff proto 生成，不再补手写 endpoint 作为契约事实源。

## Business Rules

- BR1：本次 IDL 变更必须是 additive，不删除、不重命名、不改号、不改类型已有字段。
- BR2：新增 RPC 必须带 `google.api.http` annotation。
- BR3：金额字段使用 decimal string，不使用 float 或 double。
- BR4：请求中的 applicant 身份由 BFF 从会话上下文解析，契约不接受前端传入 applicantId。
- BR5：幂等写操作必须保留 `Idempotency-Key` 的协议边界，header 由 BFF/FE 适配层传递，不放入业务请求体。
- BR6：生成物只能由 Buf / OpenAPI / SDK pipeline 产出，不允许手工编辑。
- BR7：OpenAPI 与 TS SDK 的服务命名应能区分 auth、identity-profile、pricing、loan-application。

## Acceptance Criteria

- AC1：`idl-repo/vesta/lendora/fides-bff/v1` 包含 auth、identity-profile、pricing、loan-application 四类 BFF-facing 契约。
- AC2：pricing 契约定义创建报价请求/响应，并映射到 `POST /api/v1/pricing/quotes`。
- AC3：loan-application 契约定义创建、读取、更新草稿请求/响应，并映射到 `POST /api/v1/loan-applications`、`GET /api/v1/loan-applications/{application_id}`、`PATCH /api/v1/loan-applications/{application_id}`。
- AC4：auth 与 identity-profile 现有 RPC 和字段语义保持兼容。
- AC5：`buf lint` 通过，或记录与本次变更无关的明确阻塞。
- AC6：Go/Kratos HTTP 生成能产出 pricing 与 loan-application 相关服务和 HTTP binding。
- AC7：OpenAPI 生成能看到 pricing 与 loan-application 路径。
- AC8：breaking 检查通过，或记录确切 failure 和兼容性判断。
- AC9：父 Story AC1-AC4、AC6 的 BFF 契约覆盖关系写入证据。

## Open Questions

| Question | Owner | Deadline | Status |
|---|---|---|---|
| TS SDK 是否在本仓直接生成，还是通过 OpenAPI 输出交给 `idl-ts-repo` 管线生成 | forest | LEN-153 实现阶段 | Resolved：`idl-repo` 生成 OpenAPI；`idl-ts-repo` 通过既有 Docker OpenAPI Generator 脚本从同名 `idl-openapi-repo` 分支生成并通过 build |
| 旧独立 BFF 公网域名是否保留 | forest | LEN-157 验收前 | Deferred |

## Notes

- 用户已授权 Agent 批准所有需要的文件；本需求按授权推进生命周期文件和门禁。
- 本需求只交付 `LEN-153`，合并并清理 worktree 后才能开始 `LEN-154`。
