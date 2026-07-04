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
