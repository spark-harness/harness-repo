# Local Verification

## 2026-07-05T04:16:00+08:00

Worktree: `/Users/forest/Code/spark/.worktrees/LEN-184/business-repo`

### Java Tests

Commands:

```bash
mvn -B -f apps/origination-api/pom.xml -Dtest=GrpcQuoteGatewayTest test
mvn -B -f apps/origination-api/pom.xml test
```

Result: PASS

Observed results:

- `GrpcQuoteGatewayTest`: 4 tests, 0 failures, 0 errors.
- `origination-api`: 47 tests, 0 failures, 0 errors.
- `OriginationApplicationWiringTest` started Spring context and `OpenTelemetry Spring Boot starter (2.26.0)`.

### Java Quality

Command:

```bash
mvn -B -f apps/origination-api/pom.xml spotless:apply spotless:check checkstyle:check
```

Result: PASS

Observed result:

- Spotless: 54 Java files clean.
- Checkstyle: 0 violations.

### Contract Dependency Scan

Command:

```bash
python3 scripts/contract_dependency_scan.py --mode master --path apps/origination-api/pom.xml
```

Result: PASS

Observed output:

```text
No contract dependency violations found.
```

### GitOps Rendering

Worktree: `/Users/forest/Code/spark/.worktrees/LEN-184/gitops-repo`

Commands:

```bash
kubectl kustomize apps/origination-api/overlays/dev-1 > /tmp/len184-origination-dev.yaml
kubectl kustomize apps/origination-api/overlays/sta-1 > /tmp/len184-origination-sta.yaml
rg -n "ORIGINATION_QUOTE_API_GRPC_TARGET|ORIGINATION_QUOTE_API_BASE_URL|ORIGINATION_QUOTE_API_TIMEOUT|quote-api-base-url|quote-api-timeout" /tmp/len184-origination-dev.yaml /tmp/len184-origination-sta.yaml
```

Result: PASS

Observed rendered values:

- dev-1: `ORIGINATION_QUOTE_API_GRPC_TARGET: quote-api.lendora-dev-1.svc.cluster.local:9090`
- sta-1: `ORIGINATION_QUOTE_API_GRPC_TARGET: quote-api.lendora-sta-1.svc.cluster.local:9090`
- No rendered `ORIGINATION_QUOTE_API_BASE_URL`, `ORIGINATION_QUOTE_API_TIMEOUT`, `quote-api-base-url`, or `quote-api-timeout`.

### Hard Cut Search

Command:

```bash
rg "HttpQuoteGateway|ORIGINATION_QUOTE_API_BASE_URL|ORIGINATION_QUOTE_API_TIMEOUT|quote-api-base-url|quote-api-timeout" apps/origination-api /tmp/len184-origination-dev.yaml /tmp/len184-origination-sta.yaml
```

Result: PASS

Observed result: no runtime or GitOps HTTP quote fallback remains. Remaining references are negative assertions in tests only.

### Observability

- `GrpcQuoteGateway` creates a `QuoteService/GetQuote` client span through injected `OpenTelemetry`.
- The gateway injects W3C trace context into gRPC metadata and forwards applicant metadata.
- Quote dependency system failures log `error_code=ORIGINATION-QUOTE-0003`, `dependency=quote-api`, `grpc_status`, and `latency_ms`.
- Mapped application exceptions retain the original `StatusRuntimeException` cause.

Live trace evidence is deployment-stage evidence: after the image is promoted to dev-1, verify the trace contains `origination-api` gRPC client span and `quote-api` server handling for `QuoteService/GetQuote`, with no internal business HTTP quote span.
