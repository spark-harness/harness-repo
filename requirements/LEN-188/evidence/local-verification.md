# Local Verification

## 2026-07-05T04:16:00+08:00

Worktree: `/Users/forest/Code/spark/.worktrees/LEN-188/business-repo`

### Go Tests

Command:

```bash
cd apps/fides-bff && GOPRIVATE=github.com/spark-harness/* GONOSUMDB=github.com/spark-harness/* go test ./...
```

Result: PASS

Observed packages:

- `github.com/spark/fides-bff/cmd/fides-bff`: PASS
- `github.com/spark/fides-bff/internal/biz`: PASS
- `github.com/spark/fides-bff/internal/data`: PASS
- `github.com/spark/fides-bff/internal/observability`: PASS
- `github.com/spark/fides-bff/internal/server`: PASS

### Contract Dependency Scan

Command:

```bash
python3 scripts/contract_dependency_scan.py --mode master --path apps/fides-bff/go.mod
```

Result: PASS

Observed output:

```text
No contract dependency violations found.
```

### GitOps Rendering

Worktree: `/Users/forest/Code/spark/.worktrees/LEN-188/gitops-repo`

Commands:

```bash
kubectl kustomize apps/fides-bff/overlays/dev-1 > /tmp/len188-fides-bff-dev.yaml
kubectl kustomize apps/fides-bff/overlays/sta-1 > /tmp/len188-fides-bff-sta.yaml
rg -n "QUOTE_GRPC_TIMEOUT|QUOTE_GRPC_PLAINTEXT|QUOTE_HTTP_BASE_URL|QUOTE_HTTP_TIMEOUT|quote\\.http|QuoteHTTP" /Users/forest/Code/spark/.worktrees/LEN-188/business-repo/apps/fides-bff apps/fides-bff /tmp/len188-fides-bff-dev.yaml /tmp/len188-fides-bff-sta.yaml
```

Result: PASS

Observed rendered values:

- dev-1 and sta-1 include `QUOTE_GRPC_TIMEOUT: 3s`.
- dev-1 and sta-1 include `QUOTE_GRPC_PLAINTEXT: "true"`.
- No `QUOTE_HTTP_BASE_URL`, `QUOTE_HTTP_TIMEOUT`, `quote.http`, or `QuoteHTTP` remains in the quote client/config path.
- Remaining `acceptedQuoteHTTPResponse` references are in `origination_client.go`, which belongs to LEN-192 scope.

### Hard Cut Contract Checks

- `apps/fides-bff/go.mod` consumes `github.com/spark-harness/idl-go-repo v0.2.6`.
- `QuoteClient` calls `QuoteService.CreateQuote` over gRPC.
- `QuoteGRPCConsulResolver` uses Consul `grpc_port`.
- gRPC error descriptions are mapped from quote-api server values:
  - `QUOTE-PARAM-0002` -> `amount_out_of_range`
  - `QUOTE-PARAM-0001` -> `validation_error`
  - `UNAVAILABLE`, `DEADLINE_EXCEEDED`, and unknown statuses -> `quote_unavailable`

Live trace evidence is deployment-stage evidence: after the image is promoted to dev-1, verify BFF quote flow has a gRPC client/server trace and no BFF-to-quote business HTTP span.

## 2026-07-05T07:12:33+08:00

### Runtime State

GitOps PRs:

- PR #45 merged as `7a992f754bfd0aa608d2d181e2a499c1b7eef1bb` to configure fides-bff quote gRPC client.
- PR #46 merged as `c92cbed9420a457c8272129f271e39ad31bcbb7f` to promote sta-1 quote-api to the gRPC-capable digest.
- PR #47 merged as `cae5a3ae5bdd8ff69160adedc50a2c824f0e55a1` to promote sta-1 fides-bff and origination-api to the dev-1 verified gRPC-capable digests.

Argo applications:

```text
lendora-dev-1-quote-api         Synced Healthy cae5a3ae5bdd8ff69160adedc50a2c824f0e55a1
lendora-dev-1-fides-bff         Synced Healthy cae5a3ae5bdd8ff69160adedc50a2c824f0e55a1
lendora-sta-1-quote-api         Synced Healthy cae5a3ae5bdd8ff69160adedc50a2c824f0e55a1
lendora-sta-1-fides-bff         Synced Healthy cae5a3ae5bdd8ff69160adedc50a2c824f0e55a1
```

Live fides-bff ConfigMaps:

- dev-1 and sta-1 have `QUOTE_GRPC_TIMEOUT=3s`, `QUOTE_GRPC_PLAINTEXT=true`, and environment-specific `QUOTE_CONSUL_SERVICE_NAME`.
- dev-1 and sta-1 no longer have `QUOTE_HTTP_BASE_URL` or `QUOTE_HTTP_TIMEOUT`.
- `ORIGINATION_HTTP_*` remains for LEN-192 and is not part of LEN-188 cleanup.

Live images:

```text
dev-1 quote-api  ghcr.io/spark-harness/quote-api@sha256:a76b53a88483f110b289778612d9fa70ace0531a0fd5afb60e90ff4efee770b4
dev-1 fides-bff  ghcr.io/spark-harness/fides-bff@sha256:2f6ebf56ca721ad1f3dbbd35b61ffcaa7aeadc2af37f71facc3031bcf02392e2
sta-1 quote-api  ghcr.io/spark-harness/quote-api@sha256:a76b53a88483f110b289778612d9fa70ace0531a0fd5afb60e90ff4efee770b4
sta-1 fides-bff  ghcr.io/spark-harness/fides-bff@sha256:2f6ebf56ca721ad1f3dbbd35b61ffcaa7aeadc2af37f71facc3031bcf02392e2
```

### Smoke

dev-1 BFF quote smoke:

```text
POST /api/v1/pricing/quotes trace_id=11111111111111111111111111111111 status_code=200
quoteId=quote_b8626e59-b216-49fd-a8ed-5fc635aa8dff
```

sta-1 BFF quote smoke:

```text
POST /api/v1/pricing/quotes trace_id=bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb status_code=200
quoteId=quote_fba0620a-a36b-4b6c-8e32-0dbf119ef8c1
```

Result: PASS. BFF quote runtime is configured for quote gRPC in dev-1 and sta-1. BFF external HTTP remains by design; final internal HTTP cleanup remains LEN-196.
