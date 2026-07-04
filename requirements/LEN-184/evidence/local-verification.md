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

## 2026-07-05T07:12:33+08:00

### Runtime Root Cause And Fix

Initial dev-1 loan application smoke returned HTTP 502. `origination-api` logged:

```text
quote dependency call failed error_code=ORIGINATION-QUOTE-0003 dependency=quote-api grpc_status=UNIMPLEMENTED latency_ms=4
UNIMPLEMENTED: Method not found: vesta.lendora.quote.v1.QuoteService/GetQuote
```

Root cause was stale pod environment, not missing quote-api method:

- dev-1 `origination-api-config` had `ORIGINATION_QUOTE_API_GRPC_TARGET=quote-api.lendora-dev-1.svc.cluster.local:9090`.
- The running dev-1 `origination-api` process still had old `ORIGINATION_QUOTE_API_BASE_URL` / `ORIGINATION_QUOTE_API_TIMEOUT` and no `ORIGINATION_QUOTE_API_GRPC_TARGET`.
- `GrpcQuoteGateway` defaulted to `localhost:9090`, so `QuoteService/GetQuote` was sent to `origination-api`'s own gRPC server and returned `UNIMPLEMENTED`.
- Direct `grpcurl` against dev-1 `quote-api:9090` proved `QuoteService.GetQuote` exists and returns quote data.

Fix applied:

- Restarted dev-1 `origination-api`; new process env contains `ORIGINATION_QUOTE_API_GRPC_TARGET=quote-api.lendora-dev-1.svc.cluster.local:9090`.
- Merged GitOps PR #46, commit `c92cbed9420a457c8272129f271e39ad31bcbb7f`, to promote sta-1 `quote-api` to the dev-1 verified digest.
- Merged GitOps PR #47, commit `cae5a3ae5bdd8ff69160adedc50a2c824f0e55a1`, to promote sta-1 `origination-api` and `fides-bff` to the dev-1 verified digests.
- Synced Argo apps and restarted sta-1 caller deployments so `envFrom` picked up the gRPC ConfigMaps.

### Runtime State

Argo applications:

```text
lendora-dev-1-quote-api         Synced Healthy cae5a3ae5bdd8ff69160adedc50a2c824f0e55a1
lendora-dev-1-origination-api   Synced Healthy cae5a3ae5bdd8ff69160adedc50a2c824f0e55a1
lendora-dev-1-fides-bff         Synced Healthy cae5a3ae5bdd8ff69160adedc50a2c824f0e55a1
lendora-sta-1-quote-api         Synced Healthy cae5a3ae5bdd8ff69160adedc50a2c824f0e55a1
lendora-sta-1-origination-api   Synced Healthy cae5a3ae5bdd8ff69160adedc50a2c824f0e55a1
lendora-sta-1-fides-bff         Synced Healthy cae5a3ae5bdd8ff69160adedc50a2c824f0e55a1
```

Live images:

```text
dev-1 quote-api        ghcr.io/spark-harness/quote-api@sha256:a76b53a88483f110b289778612d9fa70ace0531a0fd5afb60e90ff4efee770b4
dev-1 origination-api  ghcr.io/spark-harness/origination-api@sha256:e94c25c45363483b0931509e52b06228fd2c869f57dd0254c48616ca8284e464
dev-1 fides-bff        ghcr.io/spark-harness/fides-bff@sha256:2f6ebf56ca721ad1f3dbbd35b61ffcaa7aeadc2af37f71facc3031bcf02392e2
sta-1 quote-api        ghcr.io/spark-harness/quote-api@sha256:a76b53a88483f110b289778612d9fa70ace0531a0fd5afb60e90ff4efee770b4
sta-1 origination-api  ghcr.io/spark-harness/origination-api@sha256:e94c25c45363483b0931509e52b06228fd2c869f57dd0254c48616ca8284e464
sta-1 fides-bff        ghcr.io/spark-harness/fides-bff@sha256:2f6ebf56ca721ad1f3dbbd35b61ffcaa7aeadc2af37f71facc3031bcf02392e2
```

### Smoke

dev-1 BFF smoke:

```text
POST /api/v1/pricing/quotes      trace_id=11111111111111111111111111111111 status_code=200
POST /api/v1/loan-applications   trace_id=33333333333333333333333333333333 status_code=200
applicationId=app_a4df19d7-91ee-43e2-bc59-02a5ddbcc263
```

sta-1 BFF smoke:

```text
POST /api/v1/pricing/quotes      trace_id=bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb status_code=200
POST /api/v1/loan-applications   trace_id=dddddddddddddddddddddddddddddddd status_code=200
applicationId=app_ca30dba3-d796-4025-806d-e8a9226c9709
```

Result: PASS. `origination-api -> quote-api` now uses the gRPC target in dev-1 and sta-1. Java health/readiness HTTP remains; final broad HTTP cleanup remains LEN-196.
