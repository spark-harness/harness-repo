---
requirement_id: "LEN-133"
evidence_type: "local-verification"
verified_by: "Codex"
verified_at: "2026-06-28T06:13:00+08:00"
status: "pass"
---

# Local Verification

## Scope

本证据覆盖 `fides-bff` origination facade 的 test-first、单元/集成测试、vet、build 和本地 BFF smoke。

## Test-First Evidence

Command:

```bash
go test ./internal/server -run 'LoanApplication'
```

Expected failing result before implementation:

```text
undefined: service.OriginationService
undefined: biz.OriginationClient
undefined: biz.CreateLoanApplicationCommand
undefined: biz.GetLoanApplicationCommand
undefined: biz.PatchLoanApplicationCommand
undefined: biz.LoanApplicationSummary
undefined: biz.LoanApplicationDetail
```

结论：失败原因是 origination facade 类型、route 和 usecase 尚未实现，符合 test-first 预期。

## Commands And Results

| Command | Result |
|---|---|
| `go test ./internal/server -run 'LoanApplication'` | PASS |
| `go test ./internal/server ./internal/data` | PASS |
| `go test ./...` | PASS |
| `go vet ./...` | PASS |
| `go build ./cmd/fides-bff` | PASS |

## Coverage Notes

- Server tests cover missing token, invalid token, create/get/patch success, principal applicantId propagation, trace propagation, Idempotency-Key propagation, and error mapping.
- Data client tests cover downstream headers, detail response mapping, 400/403/404/410/422/5xx mapping, and Consul service URL resolution.
- `go test ./...` covers config loader, command bootstrap, observability, server, biz and data packages.

