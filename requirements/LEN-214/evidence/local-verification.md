# Local Verification Evidence

Requirement: LEN-214

Date: 2026-07-06

## Commands

| Scope | Command | Result |
|---|---|---|
| `business-repo/packages/go/bffkit` | `go test ./... -count=1` | PASS |
| `business-repo/apps/fides-bff` | `make test` | PASS |
| `business-repo/apps/fides-bff` | `go vet ./...` | PASS |
| `business-repo/apps/fides-bff` | `make lint` | PASS |
| `business-repo/apps/fides-bff` | `make build && make clean` | PASS |
| `gitops-repo` | `kubectl kustomize apps/fides-bff/overlays/dev-1 >/tmp/len214-fides-bff-dev-1.yaml` | PASS |
| `gitops-repo` | `kubectl kustomize apps/fides-bff/overlays/sta-1 >/tmp/len214-fides-bff-sta-1.yaml` | PASS |
| `idl-repo` | `test -d vesta/lendora/fides-bff/v1 && git diff --quiet -- vesta/lendora/fides-bff/v1` | PASS |
| `business-repo` | `rg --hidden -n "OBSERVABILITY_OTEL" apps/fides-bff packages/go/bffkit -g '!.git'` | PASS, no matches |
| `gitops-repo` | `rg -n "OBSERVABILITY_OTEL|transformation:|templates:" apps/fides-bff` | PASS, no matches |
| `business-repo` | `git diff --check` | PASS |
| `gitops-repo` | `git diff --check` | PASS |
| `harness-repo` | `git diff --check` | PASS |

## Key Assertions

- `fides-bff` stdout JSON logger emits `service.name`, `service.version`, `level`, `timestamp` and `message`.
- `bffkit.TraceFilter` emits low-cardinality access log fields with `trace_id`, `request_id`, `span_id` when available, route-pattern operation, status, latency and deployment environment.
- Unsafe external `X-Trace-Id` / `X-Correlation-Id` values are rejected and regenerated or replaced before entering logs.
- `fides-bff` config uses standard `OTEL_*` fields; target scope contains no `OBSERVABILITY_OTEL_*` references.
- `OTEL_EXPORTER_OTLP_TRACES_HEADERS` parser decodes escaped header values.
- GitOps `fides-bff-runtime` VaultStaticSecret uses raw passthrough, not per-key transformation templates.
- Rendered dev-1 and sta-1 Deployment keep `envFrom` with `fides-bff-env` then `fides-bff-runtime`.
- `idl-repo/vesta/lendora/fides-bff/v1` exists and is unchanged.

## Deferred Evidence

- dev-1 smoke request and live K8s stdout log evidence require merged image, GitOps sync and live Vault keys. This evidence should be captured after PR merge and deployment.
