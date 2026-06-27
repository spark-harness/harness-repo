---
requirement_id: "LEN-133"
owner: "core"
status: "approved"
updated_at: "2026-06-28"
approved_by: "forest"
approved_at: "2026-06-28T05:59:05+08:00"
decision: "用户授权 Agent 批准所有文档；批准 LEN-133 service-repo-check，涉及 harness-repo、business-repo 和只读 idl-repo 辅助解析，不修改 IDL。"
---

# Impact Analysis

## Summary

LEN-133 在 `fides-bff` 中新增 loan application facade。它不改变 `origination-api` 的业务能力，只让前端通过 BFF 调用现有 create/get/patch HTTP API。

## Affected Domains

| Domain | Impact |
|---|---|
| frontend | `fides-bff` 新增前端可调用的受保护 loan application API |
| applicant | `origination-api` 作为下游被调用，无代码修改 |
| pricing | accepted quote 校验仍由 `origination-api -> quote-api` 完成，本票不直接调用 quote-api |

## Affected Services And Repos

| Repo | Service | Impact |
|---|---|---|
| business-repo | fides-bff | 新增 origination usecase、HTTP service、HTTP client、config、DI wiring、测试 |
| business-repo | origination-api | 下游，无代码修改 |
| harness-repo | LEN-133 lifecycle | 新增需求、影响分析、设计、任务、证据和门禁 |

## Upstream / Downstream Consumers

- Upstream:
  - `fides-web` 后续 LEN-11 调用 BFF；本票不修改前端。
- Downstream:
  - `origination-api` HTTP create/get/patch。
  - `quote-api` 间接由 `origination-api` 校验 Quote；本票不直接调用。

## API / Contract Impact

- No protobuf IDL change.
- No generated contract change.
- BFF 新增 HTTP route：
  - `POST /api/v1/loan-applications`
  - `GET /api/v1/loan-applications/{applicationId}`
  - `PATCH /api/v1/loan-applications/{applicationId}`
- HTTP JSON shape 适配 LEN-9 已定义的 `origination-api` contract。

## Generated Contract Impact

无。`fides-bff` 现有 auth protobuf 不变。

## Data, Migration, Cache, Runtime Storage

- BFF 不新增 DB、migration 或 cache。
- BFF 不保存 application draft。
- `origination-api` application DB 已由 LEN-134 部署，本票只通过 HTTP 使用。

## Config

新增 BFF config surface：

- `origination.http.base_url`
- `origination.http.timeout`
- `origination.consul.address`
- `origination.consul.scheme`
- `origination.consul.service_name`

运行时 GitOps 配置由 LEN-135 交付；本票只提供代码默认和本地配置入口。

## Permission And Security

- loan application facade 使用 LEN-22 protected path AuthFilter。
- applicantId 只能来自 principal context。
- BFF 忽略外部 `x-applicant-id`。
- 下游请求使用 principal applicantId 设置 `x-applicant-id`。
- 不记录 Authorization、token、完整请求体或敏感字段。

## Observability, Logs, Tracing, Events

- BFF TraceFilter 继续创建/提取入口 trace。
- origination client 创建 outbound HTTP client span。
- origination client 传播 `traceparent` 和 `tracestate`。
- 不新增业务事件。
- 错误映射使用稳定 code：`origination_unavailable`、`forbidden`、`not_found`、`quote_expired`、`amount_out_of_range`、`validation_error`、`idempotency_key_required`。

## Rollout And Rollback

1. 合并 BFF facade 和测试。
2. LEN-135 配置 runtime `origination-api` 下游地址、服务发现和超时。
3. LEN-11 前端接入 BFF facade。

- Revert BFF facade code/config。
- 无 DB rollback。
- 无 IDL rollback。
- 无 `origination-api` rollback。

## Risks And Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| runtime config 未交付前 BFF 无法在集群调用 origination-api | runtime smoke 受限 | 本票只做代码和本地测试，LEN-135 交付 runtime 下游配置 |
| BFF 错误映射与 origination-api error body 不一致 | 前端处理失败 | client tests 锁定下游 status/code 到 BFF envelope |
| external `x-applicant-id` 被误信任 | 越权风险 | handler/client tests 验证只传播 principal applicantId |
| trace propagation 被遗漏 | 跨服务排障困难 | handler/client tests 验证 `traceparent` 和 `tracestate` |

## Context Gaps

- `harness-repo/context/project/` 当前没有 `lendora/frontend/fides-bff` 或 `lendora/applicant/origination-api` 的服务级 `INDEX.md`。
- 本票依据 `.service-matrix/dependencies.yaml`、LEN-9、LEN-132 和团队规范执行；项目级服务知识缺口不阻塞实现，但应在后续知识沉淀中补齐。
