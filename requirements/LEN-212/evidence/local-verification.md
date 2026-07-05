# LEN-212 Local Verification Evidence

## Environment

- Date: 2026-07-06 Asia/Shanghai.
- Branch: `feature/LEN-212-fides-bff-kratos-v3`.
- Worktree: `/Users/forest/Code/spark/.worktrees/LEN-212`.
- Formal contract dependency: `github.com/spark-harness/idl-go-repo v0.2.8`.

## Commands

| Area | Command | Result |
|---|---|---|
| `bffkit` tests | `go test ./... -count=1` from `business-repo/packages/go/bffkit` | PASS |
| `bffkit` vet | `go vet ./...` from `business-repo/packages/go/bffkit` | PASS |
| `fides-bff` generate | `make generate` from `business-repo/apps/fides-bff` | PASS, `wire_gen.go` refreshed |
| `fides-bff` tests | `GOPRIVATE=github.com/spark-harness/* GONOSUMDB=github.com/spark-harness/* GOPROXY=direct go test ./... -count=1` | PASS |
| `fides-bff` vet | `GOPRIVATE=github.com/spark-harness/* GONOSUMDB=github.com/spark-harness/* GOPROXY=direct go vet ./...` | PASS |
| `fides-bff` build | `GOFLAGS=-buildvcs=false GOPRIVATE=github.com/spark-harness/* GONOSUMDB=github.com/spark-harness/* GOPROXY=direct make build` | PASS |
| `fides-bff` lint | `GOPRIVATE=github.com/spark-harness/* GONOSUMDB=github.com/spark-harness/* GOPROXY=direct make lint` | PASS, `golangci-lint run ./...` returned `0 issues.` |
| Kratos v2 scan | `rg -n "go-kratos/kratos/v2|protoc-gen-go-http/v2" apps/fides-bff packages/go/bffkit` | PASS, no matches |

## Local Smoke

Server command:

```bash
REGISTRY_CONSUL_ENABLED=false SERVER_HTTP_ADDR=127.0.0.1:18080 AUTH_TOKEN_SECRET=local-smoke-secret GOFLAGS=-buildvcs=false GOPRIVATE=github.com/spark-harness/* GONOSUMDB=github.com/spark-harness/* GOPROXY=direct go run ./cmd/fides-bff -conf configs/config.yaml
```

Health check:

```bash
curl -i --max-time 5 http://127.0.0.1:18080/api/v1/health
```

Observed result:

```text
HTTP/1.1 200 OK
Content-Type: application/json
X-Correlation-Id: 61f9ff132669a8fe8afba500775021ce
X-Trace-Id: 61f9ff132669a8fe8afba500775021ce

{"status":"ok","version":"dev"}
```

CORS preflight:

```bash
curl -i --max-time 5 -X OPTIONS http://127.0.0.1:18080/api/v1/auth/otp:send \
  -H 'Origin: http://localhost:3000' \
  -H 'Access-Control-Request-Method: POST' \
  -H 'Access-Control-Request-Headers: Content-Type,Authorization,X-Trace-Id'
```

Observed result:

```text
HTTP/1.1 204 No Content
Access-Control-Allow-Headers: Content-Type,Authorization,X-Trace-Id
Access-Control-Allow-Methods: GET, POST, PATCH, PUT, OPTIONS
Access-Control-Allow-Origin: http://localhost:3000
Access-Control-Expose-Headers: X-Trace-Id, X-Correlation-Id, Retry-After
Access-Control-Max-Age: 600
Vary: Origin
X-Correlation-Id: 3a5c299e24a934e330d4b7ad5926b2b8
X-Trace-Id: 3a5c299e24a934e330d4b7ad5926b2b8
```

Malformed JSON:

```bash
curl -i --max-time 5 -X POST http://127.0.0.1:18080/api/v1/auth/otp:send \
  -H 'Content-Type: application/json' \
  -H 'Idempotency-Key: idem-malformed-smoke' \
  --data '{"countryCode":'
```

Observed result:

```text
HTTP/1.1 422 Unprocessable Entity
Content-Type: application/json
X-Correlation-Id: dd79b7e84759ab50df65c188da1b5765
X-Trace-Id: dd79b7e84759ab50df65c188da1b5765

{"error":{"code":"BFF-PARAM-0001","message":"invalid request body","field":"body","traceId":"dd79b7e84759ab50df65c188da1b5765","details":[{"field":"body","message":"invalid request body"}]}}
```

Server log recorded smoke requests with `service.name=fides-bff`, `operation`, `trace_id`, `request_id`, `status_code`, `latency_ms`, and `error_code` on the malformed JSON path.

## Result

Local acceptance for LEN-212 passed against the formal generated contract version. Runtime smoke proved startup, health, CORS preflight, request identifiers, access logging, and sanitized decoder errors still work after the Kratos v3 migration.
