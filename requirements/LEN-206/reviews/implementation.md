---
requirement_id: "LEN-206"
task_id: "implementation"
reviewer: "code_review_reporter"
base_revision: "origin/master"
diff_scope: "business-repo origin/master...0dbdef4 plus the uncommitted P0 fixes; synchronized LEN-206 Harness requirement/design/tasks"
conclusion: "ready-for-gate"
updated_at: "2026-07-12"
---

# Code Review Report

## Scope

- Repository: `business-repo` at `/Users/forest/Code/spark/.worktrees/LEN-206/business-repo`; Harness inputs from `harness-repo/requirements/LEN-206/`.
- Base revision: `origin/master` (`1f6129d`). The reviewed implementation includes original commit `0dbdef4` and the current uncommitted P0 fixes.
- Changed files: `fides-bff` HTTP and gRPC observability wiring; `packages/go/bffkit` TraceFilter and metadata helpers; `origination-api` quote gateway wiring; Java spring starter gRPC tracing, response metadata, Principal interceptor and tests; applicant-api test adaptation.
- Task ID: `implementation`; requirement tasks covered are `LEN-207`, `LEN-208`, `LEN-209`, and the runtime residual `LEN-210`.

## Findings

| Severity | Dimension | Location | Issue | Impact | Required Fix | Status |
|---|---|---|---|---|---|---|
| P0 | 契约兼容 / `code_review_contract_checker` | `packages/java/spring-starter/src/main/java/com/spark/common/spring/cleanarchitecture/grpc/GrpcServerMetadataInterceptor.java:30` | `x-trace-id` response metadata 被删除。 | Existing gRPC clients that consume response `x-trace-id` lose a compatibility behavior. | Restore `x-trace-id` response metadata through `GrpcServerMetadataInterceptor` and cover it in `GrpcServerLifecycleTest`. | resolved；已恢复并由 `GrpcServerLifecycleTest.java:114` 断言 |
| P0 | 安全与错误处理 / `code_review_security_error_checker` | `packages/java/spring-starter/src/main/java/com/spark/common/spring/security/RequestPrincipalGrpcClientInterceptor.java:25` | 无 Principal 时未清理已有 `x-applicant-id`。 | Reused metadata could forward a stale applicant identity across an outbound call. | Unconditionally remove all existing applicant metadata, then add it only when an authenticated Principal exists; test the stale-header case. | resolved；已无条件 `removeAll` 并由 `RequestPrincipalGrpcClientInterceptorTest.java:38` 覆盖 |
| P1 | 追溯与范围 / `code_review_traceability_checker` | `requirements/LEN-206/design.md:7` | R1 文档不一致：HTTP instrumentation 与 Kratos v3 transport filter 接入方式未与实现和任务统一。 | Requirement/design/task traceability was ambiguous for the primary BFF server tracing slice. | Synchronize R1/AC1 across requirement, design and tasks to require `otelhttp` through the Kratos v3 transport filter. | resolved；`requirement.md:29`、`design.md:7`、`tasks.json:9` 已同步 |
| P1 | 追溯与范围 / `code_review_traceability_checker` | `requirements/LEN-206/impact-analysis.md:16` | applicant-api 未列入受共享 starter 变更影响的服务范围。 | The shared Java starter change could miss an affected consumer and its test adaptation. | Add applicant-api to the affected-services analysis and keep its compatibility test in review scope. | resolved；已列入影响分析并保留 `ApplicantAuthGrpcAdapterTest` 变更 |
| P1 | 架构边界 / `backend_architecture_reviewer` | `packages/go/bffkit/trace.go:95` | TraceFilter 丢失 span error enrich。 | Official HTTP instrumentation could produce spans without the existing `error`、`error_code` and error status attributes, reducing failure observability. | Enrich the current span with error/status/error_code and preserve span_id in access-log context while leaving span creation to `otelhttp`. | resolved；当前实现已在 `trace.go:95-104` 恢复 |
| P1 | 架构边界 / `backend_architecture_reviewer` | `packages/java/spring-starter/src/main/java/com/spark/common/spring/cleanarchitecture/grpc/GrpcServerMetadataInterceptor.java:36` | Java server error enrich 丢失。 | Replacing the self-written tracing interceptor could stop failed server calls from recording `StatusCode.ERROR` and stable `error_code`. | Keep error enrichment in the independent server metadata interceptor alongside official `GrpcTelemetry`. | resolved；当前实现已在 `GrpcServerMetadataInterceptor.java:39-42` 恢复 |
| P1 | 安全与错误处理 / `code_review_security_error_checker` | `apps/origination-api/src/main/java/com/spark/origination/infrastructure/GrpcQuoteGateway.java:92` | 业务 `error_code` 统一性/完整性存在 checker 指出的风险。 | Error-code coverage across business failure paths may remain inconsistent. This is existing business error handling, not introduced by the LEN-206 tracing/metadata change. | Track and resolve as a separate business error-code contract/observability task; do not expand this tracing slice. | out-of-scope/pre-existing；非本次新增问题 |
| P2 | 追溯与范围 / `code_review_traceability_checker` | `requirements/LEN-206/tasks.json:51` | LEN-210 runtime 未验证。 | Unit and integration tests do not prove the deployed Sentry topology or exporter/runtime configuration for `quote-api GetQuote`. | After deployment, issue a real request and attach a Sentry trace proving `fides-bff rpc -> origination-api server/client -> quote-api GetQuote` is in one trace. | open-residual |
| P2 | 架构边界 / `backend_architecture_reviewer` | `requirements/LEN-206/design.md:32` | `x-trace-id` 的兼容语义与 W3C trace propagation 的边界需要明确。 | Treating the correlation response metadata as transport propagation could reintroduce hand-written W3C header injection or confuse trace identity with correlation identity. | Keep W3C propagation owned by official instrumentation and retain `x-trace-id` only as the documented compatibility/correlation metadata behavior. | resolved；策略已写入 `design.md:32,44` 与 requirement scenarios |
| P2 | 安全与错误处理 / `code_review_security_error_checker` | `packages/go/bffkit/trace.go:105` | metrics 语义/覆盖存在 checker 指出的残余风险。 | Current metrics may not provide complete business failure coverage or consistent correlation with all error paths. This was not newly introduced by this change. | Track metric semantics and business failure coverage separately; keep this review limited to the instrumentation handoff. | out-of-scope/pre-existing；非本次新增问题 |
| P2 | 安全与错误处理 / `code_review_security_error_checker` | `packages/java/spring-starter/src/main/java/com/spark/common/spring/cleanarchitecture/autoconfigure/GrpcServerAutoConfiguration.java:60` | 架构相关的 error/observability ownership 存在 checker 指出的残余风险。 | Further business-level observability ownership may need clarification beyond the shared starter boundary. This is not a new regression in the reviewed slice. | Track the ownership decision separately; keep tracing in official instrumentation and metadata/error compatibility in the starter component. | out-of-scope/pre-existing；非本次新增问题 |
| P2 | 测试价值与复杂度 / `code_review_reporter` | `packages/go/bffkit/trace_test.go:85`; `packages/java/spring-starter/src/test/java/com/spark/common/spring/cleanarchitecture/grpc/GrpcServerLifecycleTest.java:118` | Failure-path tests assert logs or official span status, but do not directly assert all restored span/server metadata `error_code` enrich behavior. | A future regression in the restored enrich can pass the current tests while losing failure diagnostics. | Add exporter/metadata assertions for Go span `error`/status/`error_code` and Java server metadata interceptor `error_code` behavior. | open-residual |

Severity 口径：

- `P0`：正确性、数据丢失、安全或契约破坏。
- `P1`：大概率生产 Bug、缺少必需证据或门禁阻塞项。
- `P2`：可维护性、测试、可观测性或灰度风险。
- `P3`：不应阻塞的小问题。

Resolved and out-of-scope findings are retained with their original severity and source. Only `open-residual` findings are counted as open findings for this implementation review; none is P0 or P1.

## Dimension Coverage

| Dimension | Checker | Result | Checked Scope |
|---|---|---|---|
| 追溯与范围 | `code_review_traceability_checker` | findings；R1 文档与 applicant-api 影响范围已修复；LEN-210 runtime residual remains | `requirements/LEN-206/requirement.md`、`impact-analysis.md`、`design.md`、`tasks.json`、evidence、business-repo `origin/master...0dbdef4` plus uncommitted fixes |
| 契约兼容 | `code_review_contract_checker` | findings；P0 response metadata deletion resolved | gRPC generated-contract consumers, Java server response metadata, `x-applicant-id` metadata behavior, HTTP/protobuf/error-code contract no-change scope |
| 数据与并发 | `code_review_data_concurrency_checker` | no findings | No persistence, transaction, cache, retry, idempotency, rollback-data or concurrency changes in the reviewed diff; gRPC context/metadata propagation paths checked |
| 安全与错误处理 | `code_review_security_error_checker` | findings；P0 stale Principal metadata resolved；其他 P1/P2 为 pre-existing/out-of-scope residuals | Principal derivation and cleanup, metadata trust boundary, error handling, error_code, metrics and sensitive logging/tracing paths in BFF and Java starter |
| 架构边界 | `backend_architecture_reviewer` | findings；TraceFilter error enrich、Java server error enrich、x-trace semantics 已修复 | Kratos HTTP filter wiring, Go shared `bffkit`, Java starter auto-configuration/interceptors, origination quote gateway and dependency direction |
| 测试价值与复杂度 | `code_review_reporter` | findings；P2 failure-path assertion gap recorded | Changed tests and their failure assertions, duplicated tracing responsibility removal, reviewability of wiring, generated/build artifact scan |

No checker was skipped. The `data/concurrency` checker explicitly returned no findings; no skipped result is treated as a pass by default.

## Tests Inspected

| Command / Evidence | Result |
|---|---|
| `go test ./...` in `apps/fides-bff` | PASS |
| `go test ./...` in `packages/go/bffkit` | PASS |
| `mvn -q -Dtest=GrpcServerAutoConfigurationTest,GrpcServerLifecycleTest,RequestPrincipalGrpcClientInterceptorTest,RequestPrincipalGrpcServerInterceptorTest test` in `packages/java/spring-starter` | PASS |
| `mvn -DskipTests install` in `packages/java/spring-starter` | PASS |
| Install current starter, then `mvn -q -Dtest=GrpcQuoteGatewayTest test` in `apps/origination-api` | PASS |
| `git diff --check` for the reviewed changes | PASS |
| `requirements/LEN-206/requirement.md`, `impact-analysis.md`, `design.md`, `tasks.json`, `evidence/local-verification.md` | Inspected; local verification evidence matches the latest PASS results |

The tests exercise official Go/Java instrumentation wiring, W3C trace context propagation, `x-trace-id` response compatibility, Principal metadata injection and stale-header removal, stable gRPC status mapping, and malformed quote failure handling. The current tests do not fully prove the restored Go/Java `error_code` enrich paths, as noted in the P2 test-value finding.

## Open Questions

- LEN-210 remains open: after deployment, can a real Sentry trace prove the required BFF -> origination-api -> quote-api child topology in the target project?

## Residual Risk

- Runtime exporter, sampling, service-resource and propagation configuration can still prevent the expected Sentry topology even though local tests pass.
- Business `error_code` consistency, metrics coverage and broader observability ownership remain separate pre-existing risks recorded by the security checker.
- Failure-path test assertions should be strengthened for the restored span and server metadata `error_code` enrichment.
- No generated or build artifacts were found mixed into the reviewed business-repo diff; the implementation remains concentrated in shared instrumentation/metadata wiring and its tests.

## Conclusion

- `ready-for-gate`: no unclosed P0/P1 findings. P2 residual risks and the LEN-210 runtime open question remain explicitly recorded.

本报告不是门禁结论。阶段推进仍以 Janus 门禁 JSON 和人工审批为准。
