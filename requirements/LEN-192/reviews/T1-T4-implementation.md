---
requirement_id: "LEN-192"
task_id: "T1-T4"
reviewer: "codex"
base_revision: "origin/master"
diff_scope: "harness-repo requirements/LEN-192, business-repo apps/fides-bff, gitops-repo apps/fides-bff"
conclusion: "ready-for-gate"
updated_at: "2026-07-05T07:46:42+08:00"
---

# Code Review Report

## Scope

- Repository: `harness-repo`, `business-repo`, `gitops-repo`
- Base revision: `origin/master` per repo
- Changed files:
  - `requirements/LEN-192/**`
  - `apps/fides-bff/.env.example`
  - `apps/fides-bff/cmd/fides-bff/config_loader_test.go`
  - `apps/fides-bff/cmd/fides-bff/wire.go`
  - `apps/fides-bff/cmd/fides-bff/wire_gen.go`
  - `apps/fides-bff/configs/config.yaml`
  - `apps/fides-bff/go.mod`
  - `apps/fides-bff/go.sum`
  - `apps/fides-bff/internal/conf/conf.go`
  - `apps/fides-bff/internal/data/origination_client.go`
  - `apps/fides-bff/internal/data/origination_client_test.go`
  - `apps/fides-bff/internal/data/origination_draft_client.go`
  - `apps/fides-bff/base/env-configmap.yaml`
- Task ID: `T1-T4`

## Findings

| Severity | Dimension | Location | Issue | Impact | Required Fix | Status |
|---|---|---|---|---|---|---|
| P0 | 契约兼容 | `apps/fides-bff/internal/data/origination_client.go:253` | `ORIGINATION-PARAM-0001` 曾按本地启发式推断为 `amount_out_of_range`。 | 可能改变 BFF 对外 HTTP 错误契约，把通用参数错误暴露为金额越界。 | formal `ORIGINATION-PARAM-0001` 保守映射为 `validation_error`；仅保留明确 legacy `amount_out_of_range` 消息映射。 | closed |
| P1 | 安全与错误处理 | `apps/fides-bff/internal/data/origination_client.go:379` | `AdvanceApplicationStep` 的 gRPC `Unauthenticated` 曾落到 `origination_unavailable`。 | 认证或 metadata 问题会被误报为依赖不可用。 | 将 `Unauthenticated` 与 `PermissionDenied` 一并映射为 BFF `forbidden`，并补回归测试。 | closed |
| P1 | 追溯与范围 | `requirements/LEN-192/tasks.json` | 初始 review 未声明当前任务切片，且 T4 当时仍为 `todo`。 | 无法判断当前 review 是否覆盖 GitOps 渲染验收。 | 本报告声明为 `T1-T4` 合并切片 review；T4 已完成并记录 dev-1/sta-1 渲染证据。 | closed |
| P2 | 安全与错误处理 | `apps/fides-bff/internal/data/origination_client.go:226` | origination gRPC span 原先只有 `rpc.grpc.status_code`，缺少稳定映射后的 `error_code`；data 层也没有统一 dependency log/metric 模式。 | 故障聚合和跨日志/trace 排障能力不足。 | 本次补充 span `error_code`；dependency log/metric 需要按 BFF data 层统一模式后续补齐。 | closed with residual risk |

## Dimension Coverage

| Dimension | Checker | Result | Checked Scope |
|---|---|---|---|
| 追溯与范围 | code_review_traceability_checker | findings closed | `requirements/LEN-192`, service matrix, `apps/fides-bff`, GitOps fides-bff |
| 契约兼容 | code_review_contract_checker | findings closed | protobuf consumption, external BFF HTTP compatibility, idl-go-repo version, error mapping, GitOps config |
| 数据与并发 | code_review_data_concurrency_checker | no findings | create/get/update/advance paths, idempotency, metadata, timeout, rollback |
| 安全与错误处理 | code_review_security_error_checker | findings closed | applicant metadata, no PII/token leakage, gRPC error mapping, trace attributes |
| 架构边界 | backend_architecture_reviewer | no findings | generated contract imports confined to `internal/data`; `internal/biz` remains contract-clean |
| 测试价值与复杂度 | code_review_reporter | no blocking findings | adapter tests cover create/get/update/advance metadata and error mapping |

## Tests Inspected

- `GOPRIVATE=github.com/spark-harness/* GONOSUMDB=github.com/spark-harness/* go test ./internal/data -run 'TestOriginationClient' -count=1`: PASS
- `GOPRIVATE=github.com/spark-harness/* GONOSUMDB=github.com/spark-harness/* go test ./... -count=1` from `apps/fides-bff`: PASS
- `python3 scripts/contract_dependency_scan.py --mode master --path apps/fides-bff/go.mod --path apps/fides-bff/go.sum`: PASS
- `kubectl kustomize apps/fides-bff/overlays/dev-1`: PASS, no `ORIGINATION_HTTP_*`
- `kubectl kustomize apps/fides-bff/overlays/sta-1`: PASS, no `ORIGINATION_HTTP_*`
- `git diff --check origin/master -- apps/fides-bff`: PASS
- `golangci-lint run ./...` from `apps/fides-bff`: PASS

## Open Questions

- Live trace evidence depends on deployment after merge and image promotion.

## Residual Risk

- Dependency log/metric fields for gRPC clients are not yet standardized in `fides-bff` data adapters. LEN-192 adds `error_code` to origination gRPC error spans and keeps live trace validation for deployment evidence.

## Conclusion

`ready-for-gate`：all P0/P1 findings are closed, tests pass, GitOps rendering proves origination HTTP env removal, and remaining risk is non-blocking observability follow-up.
