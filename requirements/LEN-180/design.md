---
requirement_id: "LEN-180"
owner: "forest"
status: "approved"
updated_at: "2026-07-05"
approved_by: "forest"
approved_at: "2026-07-05T02:30:00+08:00"
decision: "用户本轮明确要求完成 LEN-180 实现和证据。"
---

# Design

## Requirement Traceability

| Requirement Item | Design Decision | Notes |
|---|---|---|
| R1, AC1 | D1：使用 `vesta.lendora.origination.v1.OriginationLoanApplicationService`。 | 包含 Create/Get/Update/Advance。 |
| R2, AC2 | D2：通过 Buf 生成 Java contract，不手写生成物。 | 业务仓依赖 `spark-idl-java:0.2.7`。 |
| R3, AC3 | D3：新增 `OriginationLoanApplicationGrpcAdapter implements BindableService`。 | 复用现有 use case。 |
| R4, AC4 | D4：保留 `LoanApplicationHttpAdapter` 和 HTTP error handler。 | 最终清理归 `LEN-196`。 |
| R5, R6, AC5, AC6 | D5：GitOps 和 Consul 配置显式声明 gRPC 9090。 | Service/Deployment/NetworkPolicy/ConfigMap 一起验证。 |

## Summary

方案采用 contract-first 形态：origination protobuf 作为服务边界，Java contract 由 Buf 生成。origination-api 新增 gRPC 入站 adapter，保持业务规则在 application/domain 层。

## Affected Services

| Service | Change | Reason |
|---|---|---|
| origination-api | 新增 gRPC adapter，保留业务 HTTP | 服务端先提供能力，调用方后续硬切 |
| origination-api GitOps | 暴露 9090 和 Consul `grpc_port` | gRPC discovery 和 NetworkPolicy 一致 |
| service matrix | 标记 origination-api 需要 IDL | 让 Harness gate 能追踪 proto path |

## API / Contract Design

- Protobuf package: `vesta.lendora.origination.v1`.
- Service: `OriginationLoanApplicationService`.
- RPC: `CreateLoanApplication`、`GetLoanApplication`、`UpdateLoanApplication`、`AdvanceApplicationStep`.
- Identity: `x-applicant-id` gRPC metadata.
- Idempotency: `idempotency_key` request field.
- Amount: decimal string.
- Compatibility: additive service-side capability; business HTTP deferred to `LEN-196`.

## Error Code Design

| Error Code | gRPC Mapping | Meaning | Retryable | User Visible | Owner | Status |
|---|---|---|---:|---:|---|---|
| `ORIGINATION-PARAM-0001` | `INVALID_ARGUMENT` | 请求字段缺失、金额/期限/步骤非法或幂等键缺失 | No | Yes | applicant | Active |
| `ORIGINATION-AUTH-0001` | `UNAUTHENTICATED` | 请求缺少有效申请人身份 | No | Yes | applicant | Active |
| `ORIGINATION-PERMISSION-0001` | `PERMISSION_DENIED` | 申请人无权访问该申请或报价 | No | Yes | applicant | Active |
| `ORIGINATION-STATE-0001` | `NOT_FOUND` | 申请不存在 | No | Yes | applicant | Active |
| `ORIGINATION-STATE-0002` | `ALREADY_EXISTS` | 幂等键与不同请求冲突 | No | Yes | applicant | Active |
| `ORIGINATION-QUOTE-0001` | `NOT_FOUND` | 引用报价不存在 | No | Yes | applicant | Active |
| `ORIGINATION-QUOTE-0002` | `FAILED_PRECONDITION` | 引用报价已过期或与贷款条款不匹配 | No | Yes | applicant | Active |
| `ORIGINATION-QUOTE-0003` | `UNAVAILABLE` | quote 依赖不可用 | Yes | No | applicant | Active |
| `ORIGINATION-SYSTEM-0001` | `UNKNOWN` | origination-api 未分类系统错误 | Yes | No | applicant | Active |

## Application Design

- `OriginationLoanApplicationGrpcAdapter` maps protobuf request/response to existing command/result types.
- Create uses `CreateLoanApplicationUseCase`.
- Get uses `GetLoanApplicationUseCase`.
- Update uses `PatchLoanApplicationUseCase`.
- Advance uses `AdvanceApplicationStepUseCase` and applicant metadata.
- Adapter maps domain/application exceptions to gRPC status and stable descriptions.

## Data / Config / Permission

- Data model: no schema change.
- Config:
  - `SPARK_GRPC_SERVER_PORT=9090`
  - `SPARK_ORIGINATION_CONSUL_GRPC_PORT=9090`
- Permission: NetworkPolicy allows 9090 from same environment namespace and Consul namespace.

## Observability

- Logs: no new sensitive fields.
- Metrics: existing starter behavior.
- Tracing: OpenTelemetry starter remains configured.
- Health: `/health` and `/ready` HTTP remain.

## Testing Strategy

- Buf lint, Java generate and breaking checks.
- idl-java compile test.
- gRPC adapter test for Create/Get/Update/Advance and error mappings.
- origination-api full Maven test.
- GitOps dev-1/sta-1 kustomize render inspection for 9090.

## Rollout And Rollback

- Rollout: publish Java contract first, then business-repo, then GitOps.
- Rollback: revert business image or GitOps overlay; HTTP remains available during rollback.

## Risks

| Risk | Mitigation | Owner |
|---|---|---|
| Contract artifact unavailable | Publish `spark-idl-java:0.2.7` before business merge | forest |
| gRPC port discovery mismatch | Verify Consul metadata, Service and NetworkPolicy together | forest |
| HTTP cleanup scope creep | Keep HTTP files and document `LEN-196` boundary | forest |
