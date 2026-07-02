---
requirement_id: "LEN-154"
evidence_type: "implementation"
updated_at: "2026-07-02T16:13:19Z"
repos:
  - business-repo
  - harness-repo
---

# LEN-154 Implementation Evidence

## Formal Contract Version

| Artifact | Version | Commit | Verification |
|---|---|---|---|
| `idl-repo` | `v0.2.5` | `34c4f17456d5032bf4aecc765b641094d7ab0b5e` | `git ls-remote --tags git@github.com:spark-harness/idl-repo.git refs/tags/v0.2.5` |
| `idl-go-repo` | `v0.2.5` | `e519b232cbaa043b38a7138e926f8641be6b7a11` | `git ls-remote --tags git@github.com:spark-harness/idl-go-repo.git refs/tags/v0.2.5` |

`business-repo/apps/fides-bff/go.mod` consumes `github.com/spark-harness/idl-go-repo v0.2.5`.

## Test-First Evidence

Baseline before production edits:

```text
make test
go test ./... -count=1
ok  	github.com/spark/fides-bff/internal/server	2.278s
```

Failing test before implementation:

```text
go test ./internal/server -run 'TestHTTPServer_(PricingQuote_callsQuoteAPIWithPrincipalAndTrace|LoanApplicationCreate_callsOriginationWithPrincipalTraceAndIdempotency|LoanApplicationGet_returnsDetail|LoanApplicationPatch_propagatesIdempotency|IdentityProfile(Put_savesProfileAndAdvancesStep|Get_whenEmpty_shouldReturnEmptyResponse))' -count=1
internal/server/http_test.go:348:43: undefined: fidesbffv1pb.OperationFidesBffPricingServiceCreateQuote
internal/server/http_test.go:472:55: undefined: fidesbffv1pb.OperationFidesBffLoanApplicationServiceCreateLoanApplication
FAIL	github.com/spark/fides-bff/internal/server [build failed]
```

The failure proved `fides-bff` was still consuming `idl-go-repo v0.2.4`, which did not include LEN-153 pricing and loan application generated binding.

## Implementation Evidence

- `internal/server/http.go` registers generated auth, pricing, loan-application and identity-profile HTTP servers.
- Manual route registration remains only for `/api/v1/health` and `/api/v1/protected/session:probe`.
- `internal/service/pricing.go`, `origination.go` and `identity_profile.go` implement generated service interfaces.
- `internal/service/http_context.go` centralizes request-header extraction from generated-handler contexts.
- `internal/server/http.go` keeps identity-profile JSON compatibility for `nationality` and `currentStep` while using generated handlers.

Static route check:

```text
rg -n 'v1\.(POST|GET|PATCH|PUT)\("/(pricing|loan-applications|me/identity-profile)|RegisterFidesBff.*HTTPServer|idl-go-repo v0.2' apps/fides-bff/internal/server/http.go apps/fides-bff/go.mod apps/fides-bff/go.sum
apps/fides-bff/go.mod:52:	github.com/spark-harness/idl-go-repo v0.2.5
apps/fides-bff/internal/server/http.go:60:	fidesbffv1pb.RegisterFidesBffAuthServiceHTTPServer(srv, auth)
apps/fides-bff/internal/server/http.go:61:	fidesbffv1pb.RegisterFidesBffPricingServiceHTTPServer(srv, pricing)
apps/fides-bff/internal/server/http.go:62:	fidesbffv1pb.RegisterFidesBffLoanApplicationServiceHTTPServer(srv, origination)
apps/fides-bff/internal/server/http.go:63:	fidesbffv1pb.RegisterFidesBffIdentityProfileServiceHTTPServer(srv, identityProfile)
```

## Final Verification

```text
make test
go test ./... -count=1
ok  	github.com/spark/fides-bff/cmd/fides-bff	0.383s
ok  	github.com/spark/fides-bff/internal/biz	1.007s
ok  	github.com/spark/fides-bff/internal/data	0.575s
ok  	github.com/spark/fides-bff/internal/observability	0.733s
ok  	github.com/spark/fides-bff/internal/server	0.915s
```

```text
go vet ./...
PASS
```

```text
make build
go build -ldflags "-X main.Version=6a05f4c-dirty" -o bin/fides-bff ./cmd/fides-bff
PASS
```

`bin/` was removed after build verification.
