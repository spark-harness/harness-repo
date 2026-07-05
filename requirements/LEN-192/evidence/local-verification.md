# Local Verification

## 2026-07-05T07:46:42+08:00

Worktree: `/Users/forest/Code/spark/.worktrees/LEN-192/business-repo`

### Go Tests

Command:

```bash
cd apps/fides-bff && GOPRIVATE=github.com/spark-harness/* GONOSUMDB=github.com/spark-harness/* go test ./... -count=1
```

Result: PASS

Observed packages:

- `github.com/spark/fides-bff/cmd/fides-bff`: PASS
- `github.com/spark/fides-bff/internal/biz`: PASS
- `github.com/spark/fides-bff/internal/conf`: no test files
- `github.com/spark/fides-bff/internal/data`: PASS
- `github.com/spark/fides-bff/internal/observability`: PASS
- `github.com/spark/fides-bff/internal/server`: PASS
- `github.com/spark/fides-bff/internal/service`: no test files

### Contract Dependency Scan

Command:

```bash
python3 scripts/contract_dependency_scan.py --mode master --path apps/fides-bff/go.mod --path apps/fides-bff/go.sum
```

Result: PASS

Observed output:

```text
No contract dependency violations found.
```

### GitOps Rendering

Worktree: `/Users/forest/Code/spark/.worktrees/LEN-192/gitops-repo`

Commands:

```bash
kubectl kustomize apps/fides-bff/overlays/dev-1 > /tmp/len192-fides-bff-dev-1.yaml
rg -n "ORIGINATION_(HTTP|GRPC|CONSUL)" /tmp/len192-fides-bff-dev-1.yaml
kubectl kustomize apps/fides-bff/overlays/sta-1 > /tmp/len192-fides-bff-sta-1.yaml
rg -n "ORIGINATION_(HTTP|GRPC|CONSUL)" /tmp/len192-fides-bff-sta-1.yaml
rg -n "ORIGINATION_HTTP|origination.*http|http.*origination" apps/fides-bff
```

Result: PASS

Observed rendered values:

- dev-1 includes `ORIGINATION_CONSUL_SERVICE_NAME: dev-1-origination-api`.
- dev-1 includes `ORIGINATION_GRPC_TIMEOUT: 3s`.
- dev-1 includes `ORIGINATION_GRPC_PLAINTEXT: "true"`.
- sta-1 includes `ORIGINATION_CONSUL_SERVICE_NAME: sta-1-origination-api`.
- sta-1 includes `ORIGINATION_GRPC_TIMEOUT: 3s`.
- sta-1 includes `ORIGINATION_GRPC_PLAINTEXT: "true"`.
- No `ORIGINATION_HTTP_BASE_URL` or `ORIGINATION_HTTP_TIMEOUT` remains in rendered dev-1 or sta-1 fides-bff config.

### Hard Cut Contract Checks

- `apps/fides-bff/go.mod` consumes `github.com/spark-harness/idl-go-repo v0.2.7`.
- `OriginationClient` calls `OriginationLoanApplicationService` over gRPC for create, get, update, and advance.
- `OriginationGRPCConsulResolver` uses Consul `grpc_port`.
- `ORIGINATION_HTTP_BASE_URL`, `ORIGINATION_HTTP_TIMEOUT`, `quote.http`, and `QuoteHTTP` are not part of the origination client/config path.
- BFF external HTTP server remains by design.
- Review finding fix: formal `ORIGINATION-PARAM-0001` now maps conservatively to `validation_error` except locally deterministic missing idempotency.
- Review finding fix: `AdvanceApplicationStep` maps gRPC `Unauthenticated` to BFF `forbidden`.
- Origination gRPC error spans include mapped stable `error_code`.

### Review Fix Regression

Command:

```bash
cd apps/fides-bff && GOPRIVATE=github.com/spark-harness/* GONOSUMDB=github.com/spark-harness/* go test ./internal/data -run 'TestOriginationClient' -count=1
```

Result: PASS

### CI Lint Regression

Command:

```bash
cd apps/fides-bff && golangci-lint run ./...
```

Result: PASS

Observed output:

```text
0 issues.
```

Note: CI initially reported unused `staticURLResolver` after origination HTTP client removal. The unused resolver was removed and lint passed locally.

Live smoke and trace evidence are deployment-stage evidence: after the LEN-192 fides-bff image and GitOps config are promoted to dev-1, verify loan application create/update/advance through BFF and confirm BFF-to-origination uses gRPC without a business HTTP span.
