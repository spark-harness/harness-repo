# LEN-43 Implementation Review

## Scope

- Requirement: LEN-43
- Review date: 2026-06-22 / 2026-06-23
- Base scope: `.worktrees/LEN-43/{harness-repo,idl-repo,business-repo}` against `origin/master`
- Task slice reviewed: T1-T10 implementation state

## Checker Status

| Dimension | Status | Notes |
|---|---|---|
| Traceability | checked in main thread | Requirement, design, tasks, evidence, and changed files inspected. |
| Contract compatibility | checked in main thread | IDL path, HTTP annotations, Buf checks, generated-contract consumption, and contract dependency scan reviewed. |
| Data / concurrency / idempotency | checked in main thread | BFF idempotency, Consul resolution, retry-after mapping, and absence of OTP persistence reviewed. |
| Security / errors / observability | checked in main thread | Error envelope, sensitive data handling, CORS, trace metadata, and OTel exporter boundary reviewed. |
| Backend architecture | checked in main thread | Clean Architecture dependency direction and Wire assembly reviewed. |

## Findings

No P0 or P1 findings remain open.

Closed finding:

- The previous blocker was a local generated-contract replacement: `replace github.com/spark-harness/idl-go-repo => /Users/forest/Code/spark/idl-go-repo`.
- Resolution: `fides-bff` now consumes formal `github.com/spark-harness/idl-go-repo v0.2.1`; the local replace was removed; backend tests/build and contract dependency scan were rerun.
- CI support: `fides-bff-ci.yml` now configures `GOPRIVATE`, `GONOSUMDB`, and `IDL_GO_REPO_TOKEN` for jobs that need the private generated Go module.

## No Findings

- IDL: `vesta/lendora/fides-bff/v1/auth.proto` uses the user-approved path and carries `google.api.http` annotations for send, verify, and refresh.
- Contract dependency: `fides-bff/go.mod` consumes formal `idl-go-repo v0.2.1`, and `contract_dependency_scan.py --mode master --path services/backend/fides-bff/go.mod` passes.
- Error handling: `bffkit` carries `retryAfterSec` in the JSON envelope and `Retry-After` header; auth errors map cooldown/lockout to 429, token expiration to 401, and applicant unavailability to 503.
- Applicant gRPC integration: `fides-bff` resolves applicant-api through Consul, calls the generated applicant Go gRPC client, maps send/verify/refresh responses, propagates `Idempotency-Key`, and maps applicant gRPC status descriptions to BFF auth error codes.
- Observability: `fides-bff` uses official OpenTelemetry SDK plus official OTLP exporters only; unsupported vendor exporter names are rejected by tests. No Sentry SDK/exporter import was introduced.
- Frontend: `RestOtpAuthGateway` covers send, verify, refresh, unified error envelope, retry-after fallback, and timeout behavior without consuming generated proto.
- Runtime smoke: local FE + BFF + BE smoke passed with `applicant-api` gRPC on 9090, `fides-bff` on 8001, Consul `grpc_port=9090`, and `fides` real adapter exercised by `mobile-verification-real-bff.smoke.test.tsx`.
- Build artifacts: `.next/`, `.generated/`, local `fides-bff` binary, and `idl-java-repo/` side effects were removed after verification.

## Tests Inspected / Run

- `buf lint && buf generate && buf breaking --against '.git#branch=master'`
- `GOPRIVATE=github.com/spark-harness/* GONOSUMDB=github.com/spark-harness/* go vet ./... && go build ./... && go test ./... -count=1` in `business-repo/services/backend/fides-bff`
- `go test ./... -count=1` in `business-repo/packages/bffkit`
- `pnpm test && pnpm lint:deps && pnpm build` in `business-repo/services/frontend/fides`
- `python3 scripts/contract_dependency_scan.py --mode master --path services/backend/fides-bff/go.mod`
- `LEN43_REAL_BFF_SMOKE=1 LEN43_FIDES_BFF_BASE_URL=http://127.0.0.1:8001/api/v1 LEN43_SMOKE_PHONE=91989996 pnpm exec vitest run src/api/mobile-verification/mobile-verification-real-bff.smoke.test.tsx --reporter=verbose`

## Residual Risk

- The new `fides-bff` BFF-facing proto is locally verified by Buf. `buf.gen.go.yaml` disables managed overrides for the `googleapis` module so generated Go code keeps upstream `google/api` imports. It still needs normal formal generated-contract publication after the `idl-repo` PR merges.
- OTel export was validated at configuration/provider boundary, not against a live Collector or Sentry OTLP endpoint.
- `make generate` uses the locally installed `wire` binary, which was built with Go 1.25 and fails against `go 1.26`; `go run github.com/google/wire/cmd/wire@v0.7.0` succeeds and regenerated `wire_gen.go`.

## Conclusion

`ready-for-gate`

The implementation is ready for merge-readiness verification and PR CI. Remaining items are delivery sequencing and post-IDL-merge generated-contract publication, not blockers for opening the LEN-43 PRs.
