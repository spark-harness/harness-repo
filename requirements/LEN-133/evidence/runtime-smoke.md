---
requirement_id: "LEN-133"
evidence_type: "local-smoke"
verified_by: "Codex"
verified_at: "2026-06-28T06:13:00+08:00"
status: "pass"
---

# Local BFF Smoke

## Scope

本证据覆盖本地 `fides-bff` 通过 HTTP facade 调用 stub `origination-api` 的 create/get/patch 路径。

这不是 `lendora-sta` runtime smoke。真实 runtime 下游地址、服务发现和超时由 LEN-135 配置后验证。

## Setup

- Stub `origination-api`: `127.0.0.1:18081`
- BFF: `127.0.0.1:18080`
- Config override:
  - `CONFIG_CONSUL_ENABLED=false`
  - `SERVER_HTTP_ADDR=127.0.0.1:18080`
  - `ORIGINATION_HTTP_BASE_URL=http://127.0.0.1:18081`

## Results

| Check | Result |
|---|---|
| `POST /api/v1/loan-applications` via BFF | PASS; returned `{"applicationId":"app_smoke","status":"draft","currentStep":"loan_request"}` |
| `GET /api/v1/loan-applications/app_smoke` via BFF | PASS; returned loan, acceptedQuote, status and currentStep |
| `PATCH /api/v1/loan-applications/app_smoke` via BFF | PASS; returned summary |
| Principal propagation | PASS; stub received `x-applicant-id=applicant_smoke` even when inbound request carried attacker header |
| Idempotency propagation | PASS; stub received `idem-smoke-create` on POST and `idem-smoke-patch` on PATCH |
| Trace propagation | PASS; stub received inbound `traceparent` and `tracestate` on POST |

## Runtime Boundary

LEN-133 intentionally does not change GitOps runtime config. Cluster smoke for `fides-bff -> origination-api` belongs to LEN-135 after `fides-bff` downstream config is deployed.

