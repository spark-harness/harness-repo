---
requirement_id: "LEN-10"
evidence_type: "local-verification"
verified_by: "Codex"
verified_at: "2026-06-28T01:54:25+08:00"
status: "pass"
---

# Local Verification

## Scope

本证据覆盖 LEN-10 quote-api 本地实现验证。

不覆盖 Kubernetes/GitOps 部署、quote DB runtime、Consul/k8s service discovery；这些属于 LEN-131。

## Commands

| Command | Working Directory | Result |
|---|---|---|
| `mvn test install` | `business-repo/packages/java/spring-starter` | PASS，11 tests，0 failures，0 errors |
| `mvn test` | `business-repo/packages/java/spring-starter` | PASS，11 tests，0 failures，0 errors |
| `mvn test` | `business-repo/apps/quote-api` | PASS，9 tests，0 failures，0 errors |
| `mvn spotless:check` | `business-repo/packages/java/spring-starter` | PASS，19 Java files clean |
| `mvn spotless:check` | `business-repo/apps/quote-api` | PASS，26 Java files clean |
| `janus requirement gate-check --requirement LEN-10 --gate service-repo-check --owner forest` | `harness-repo` | PASS |

## Behavior Evidence

| Acceptance | Evidence |
|---|---|
| AC1 | `QuoteUseCaseTest.createQuote_withValidPilRequest_persistsQuoteAndReturnsPricing` 验证 quoteId、monthly、apr、totalInterest、totalPayable、validUntil 和持久化计数。 |
| AC2 | `QuoteUseCaseTest.createQuote_withOutOfRangeAmount_doesNotPersistQuote` 与 `QuoteHttpAdapterTest.createQuote_withOutOfRangeAmount_returnsAmountOutOfRange` 验证 422 `amount_out_of_range` 和不写库。 |
| AC3 | `CreateQuoteUseCase` 每次成功请求生成新的 `quote_` UUID 并保存 Quote；本 ticket 不写草稿、不创建申请状态。 |
| AC4 | `JdbcQuoteRepositoryTest.saveAndFindById_roundTripsQuote` 验证 quote 表字段写入和按 quoteId 读取。 |
| AC5 | `QuoteUseCaseTest.getQuote_withDifferentApplicant_rejectsAccess` 与 `getQuote_withExpiredQuote_rejectsAccess` 验证归属和过期失败；`QuoteHttpExceptionHandler` 映射 not found / forbidden / expired。 |
| AC6 | `QuoteHttpAdapterTest.ready_withDatabaseAvailable_returnsReady` 验证 `/ready` 通过 DB probe；`mvn test` 和 `spotless:check` 均通过。 |
| AC7 | 代码按 `domain/application/adapter/inbound/http/infrastructure/bootstrap` 分层；公共 principal context 通过 starter filter 复用，不复制 applicant auth 业务代码。 |

## Notes

- quote-api 使用 HTTP/JDBC 边界，不修改 protobuf IDL 或 generated contracts。
- `POST /api/v1/pricing/quotes` 响应只返回创建 Quote 所需 pricing 字段；内部读取接口返回完整 Quote 快照。
- `x-applicant-id` 由公共 Spring starter HTTP filter 写入 `RequestPrincipalContext`；quote-api 不接受请求体 applicantId。
- `traceparent` 的 trace id 会写入 Quote `trace_id` 字段；缺失或非法 traceparent 时为空字符串。
