# LEN-43 Implementation Checks

## Scope

- Requirement: LEN-43
- Date: 2026-06-22 / 2026-06-23
- Repositories:
  - `/Users/forest/Code/spark/.worktrees/LEN-43/business-repo`
  - `/Users/forest/Code/spark/.worktrees/LEN-43/idl-repo`
  - `/Users/forest/Code/spark/.worktrees/LEN-43/harness-repo`

## IDL

Command:

```bash
buf lint && buf generate && buf breaking --against '.git#branch=master'
```

Working directory:

```text
/Users/forest/Code/spark/.worktrees/LEN-43/idl-repo
```

Result: exit 0.

Notes:

- `buf generate` produces verification outputs outside `idl-repo` under the LEN-43 worktree root.
- Generated side-effect directories `.generated/` and `idl-java-repo/` were removed after verification because LEN-43 does not deliver generated repo changes.

## Backend

Formal generated Go contract dependency:

```text
github.com/spark-harness/idl-go-repo v0.2.1
```

Evidence:

- `spark-harness/idl-go-repo` tag `v0.2.1` resolves to commit `f6f3a4a62fa04231756a24736c68acdc831bd938`.
- Tag commit message: `chore(idl): publish go generated code for 5909aa0289eb`.
- `v0.2.1` contains `vesta/lendora/applicant/v1/auth.pb.go`, which is the generated applicant contract consumed by `fides-bff`.
- `fides-bff` no longer uses a local `replace` for `github.com/spark-harness/idl-go-repo`.
- `fides-bff-ci.yml` configures `GOPRIVATE`, `GONOSUMDB`, and a private Go module token before backend build/test and lint jobs so CI can read the private generated Go module. It prefers `IDL_GO_REPO_TOKEN` and falls back to `BRANCH_COHERENCE_TOKEN` or `github.token`.

Command:

```bash
GOPRIVATE=github.com/spark-harness/* GONOSUMDB=github.com/spark-harness/* go vet ./... && go build ./... && go test ./... -count=1
```

Working directory:

```text
/Users/forest/Code/spark/.worktrees/LEN-43/business-repo/services/backend/fides-bff
```

Result:

```text
ok  	github.com/spark/fides-bff/cmd/fides-bff	0.391s
ok  	github.com/spark/fides-bff/internal/biz	0.177s
?   	github.com/spark/fides-bff/internal/conf	[no test files]
ok  	github.com/spark/fides-bff/internal/data	0.535s
ok  	github.com/spark/fides-bff/internal/observability	0.900s
ok  	github.com/spark/fides-bff/internal/server	0.734s
?   	github.com/spark/fides-bff/internal/service	[no test files]
```

Command:

```bash
go test ./... -count=1
```

Working directory:

```text
/Users/forest/Code/spark/.worktrees/LEN-43/business-repo/packages/bffkit
```

Result:

```text
ok  	github.com/spark/bffkit	0.223s
```

Command:

```bash
python3 scripts/contract_dependency_scan.py --mode master --path services/backend/fides-bff/go.mod
```

Working directory:

```text
/Users/forest/Code/spark/.worktrees/LEN-43/business-repo
```

Result:

```text
No contract dependency violations found.
```

Coverage notes:

- HTTP auth routes map request body and `Idempotency-Key` into auth commands.
- `internal/data.ApplicantAuthClient` resolves applicant-api through Consul and calls the generated applicant gRPC client from formal `idl-go-repo v0.2.1`.
- Data-layer tests run an in-process generated `ApplicantAuthServiceServer` and verify send, verify, refresh, idempotency key propagation, response mapping, and applicant gRPC error-code mapping.
- BFF errors use the unified envelope with `traceId`.
- Cooldown and lockout-style errors carry `retryAfterSec` in the JSON envelope and `Retry-After` header.
- Consul no healthy instance maps to `applicant_unavailable` and HTTP 503.
- OpenTelemetry startup uses the official SDK and official OTLP exporters only. Unsupported vendor exporter names are rejected, and both host:port endpoints and full OTLP endpoint URLs are accepted.

## Frontend

Command:

```bash
pnpm test && pnpm lint:deps && pnpm build
```

Working directory:

```text
/Users/forest/Code/spark/.worktrees/LEN-43/business-repo/services/frontend/fides
```

Result:

```text
Test Files  12 passed | 1 skipped (13)
Tests       50 passed | 1 skipped (51)
depcruise   no dependency violations found (41 modules, 75 dependencies cruised)
next build  compiled successfully and TypeScript passed
```

Build output `.next/` was removed after verification.

## Local FE + BFF + BE Runtime Smoke

Runtime setup on 2026-06-22:

- `applicant-api` Java process listening on `*:9090` for gRPC.
- Consul `applicant-api` passing service registered as `127.0.0.1:8080` with `Meta.grpc_port=9090`.
- `fides-bff` running on `127.0.0.1:8001` with local generated `idl-go-repo` replacement and CORS enabled for `http://localhost:3001`.
- `fides` dev server running on `http://localhost:3001` with real adapter base URL `http://127.0.0.1:8001/api/v1`.

BFF REST smoke command:

```bash
curl -X POST http://127.0.0.1:8001/api/v1/auth/otp:send \
  -H 'Content-Type: application/json' \
  -H 'Idempotency-Key: smoke-send-1782086908' \
  --data '{"countryCode":"+852","phone":"913428"}'

curl -X POST http://127.0.0.1:8001/api/v1/auth/otp:verify \
  -H 'Content-Type: application/json' \
  -H 'Idempotency-Key: smoke-verify-1782086908' \
  --data '{"challengeId":"otp_126329dd-bf20-466c-91cd-14fb63dd9830","code":"123456"}'

curl -X POST http://127.0.0.1:8001/api/v1/auth/token:refresh \
  -H 'Content-Type: application/json' \
  -H 'Idempotency-Key: smoke-refresh-1782086908' \
  --data '{"refreshToken":"<refresh-token-from-verify>"}'
```

Result: send, verify, and refresh all returned HTTP 200. Verify returned a string access token, string refresh token, applicant id `applicant_d197ee50-2d33-46a0-8e6a-741bc85d59d6`, `expiresInSec=3600`, and `refreshExpiresInSec=3600`. Refresh returned a new string access token and `expiresInSec=3600`.

Browser/CORS smoke:

```bash
curl -i -X OPTIONS http://127.0.0.1:8001/api/v1/auth/otp:send \
  -H 'Origin: http://localhost:3001' \
  -H 'Access-Control-Request-Method: POST' \
  -H 'Access-Control-Request-Headers: content-type,idempotency-key'
```

Result: HTTP 204 with `Access-Control-Allow-Origin: http://localhost:3001`, `Access-Control-Allow-Headers: Content-Type, Idempotency-Key, X-Trace-Id, X-Correlation-Id`, and no duplicated CORS headers on actual POST responses.

FE real-BFF smoke command:

```bash
LEN43_REAL_BFF_SMOKE=1 \
LEN43_FIDES_BFF_BASE_URL=http://127.0.0.1:8001/api/v1 \
LEN43_SMOKE_PHONE=91989996 \
pnpm exec vitest run src/api/mobile-verification/mobile-verification-real-bff.smoke.test.tsx --reporter=verbose
```

Result:

```text
✓ src/api/mobile-verification/mobile-verification-real-bff.smoke.test.tsx > mobile verification real BFF smoke > sends and verifies OTP through the running fides-bff and applicant-api 243ms
Test Files  1 passed (1)
Tests       1 passed (1)
```

Coverage notes:

- Consul resolver now prefers `Service.Meta.grpc_port` for gRPC target selection and falls back to `Service.Port`. This matches applicant-api registering HTTP on `Port=8080` and gRPC in `grpc_port=9090`.
- `bffkit.CORSFilter` handles browser preflight before idempotency validation; `captureResponseWriter` no longer replays outer CORS headers into idempotency records.
- Chrome MCP low-level input targeting was unreliable in this session, so FE runtime verification used Testing Library + real `RestOtpAuthGateway` against the running BFF/BE stack.

## Residual Risk

- `fides-bff` currently consumes formal `idl-go-repo v0.2.1` for the existing applicant generated Go contract. The new `fides-bff` BFF-facing proto in LEN-43 is verified by Buf locally and should be published as the next formal generated-contract tag after the `idl-repo` PR merges.
- OTel export was validated at configuration/provider boundary, not against a live Collector or Sentry OTLP endpoint.
- `make generate` uses the locally installed `wire` binary, which was built with Go 1.25 and fails against `go 1.26`; `go run github.com/google/wire/cmd/wire@v0.7.0` succeeds and regenerated `wire_gen.go`.
