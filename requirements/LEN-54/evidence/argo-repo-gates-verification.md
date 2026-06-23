# LEN-54 Argo Repo Gates Verification Evidence

## Scope

- Requirement: LEN-54
- Branch: `chore/LEN-54-argo-repo-gates`
- Verified at: `2026-06-23T18:24:33+08:00`
- GitOps PR: <https://github.com/spark-harness/gitops-repo/pull/5>
- Harness PR: <https://github.com/spark-harness/harness-repo/pull/17>
- Business PR: <https://github.com/spark-harness/business-repo/pull/12>
- IDL PR: <https://github.com/spark-harness/idl-repo/pull/8>

## Result

PASS for implemented local verification, GitOps smoke, Business repo Argo statuses,
and IDL repo Argo statuses.

Harness repo Argo status requires one more run after this evidence and the generated
Janus gate JSON are pushed. The previous `spark/harness-gates` failure was caused by
missing LEN-54 gate reports before this evidence refresh.

## Local Verification

| Command | Repo | Result |
|---|---|---|
| `janus version && jq empty .spark/hooks.json && bash -n scripts/install.sh && python3 scripts/test_validate_pr_metadata.py && python3 -m json.tool requirements/LEN-54/tasks.json >/dev/null && git diff --check` | `harness-repo` | PASS |
| `python3 -m unittest tests/test_contract_dependency_scan.py && python3 scripts/contract_dependency_scan.py --mode rc-or-formal && git diff --check` | `business-repo` | PASS |
| `buf lint && git diff --check` | `idl-repo` | PASS |
| `kubectl kustomize workflows/templates >/tmp/len54-kustomize-templates.yaml && kubectl kustomize workflows/ci >/tmp/len54-kustomize-ci.yaml && kubectl kustomize platform/ingress >/tmp/len54-kustomize-ingress.yaml && git diff --check` | `gitops-repo` | PASS |

## GitHub PR Status

| Repo | PR | Required contexts | Result |
|---|---:|---|---|
| `gitops-repo` | #5 | `spark/argo-smoke` | SUCCESS |
| `business-repo` | #12 | `spark/fides-ci`, `spark/fides-bff-ci`, `spark/contract-dependency-scan`, `spark/business-delivery-readiness`, `spark/pr-metadata` | SUCCESS |
| `idl-repo` | #8 | `spark/idl-contract-gate`, `spark/idl-delivery-readiness`, `spark/pr-metadata` | SUCCESS |
| `harness-repo` | #17 | `spark/harness-delivery-readiness`, `spark/pr-metadata` | SUCCESS |
| `harness-repo` | #17 | `spark/harness-gates` | PENDING RERUN AFTER GATE PUSH |

## Argo Workflow Evidence

| Workflow | Result |
|---|---|
| `gitops-pr-smoke-mlvfg` | Succeeded |
| `business-repo-fides-m6zr5` | Succeeded |
| `business-repo-fides-bff-zn99w` | Succeeded |
| `business-repo-contract-scan-thnm2` | Succeeded |
| `business-repo-delivery-qbdm7` | Succeeded |
| `business-repo-pr-metadata-8k27j` | Succeeded |
| `idl-repo-contract-sbrgk` | Succeeded |
| `idl-repo-delivery-swsxj` | Succeeded |
| `idl-repo-pr-metadata-vm595` | Succeeded |
| `idl-repo-release-4lw57` | Succeeded |
| `harness-repo-delivery-pv5q7` | Succeeded |
| `harness-repo-pr-metadata-zrp57` | Succeeded |

## Branch Protection

- `harness-repo` requires `spark/harness-gates`, `spark/harness-delivery-readiness`, and `spark/pr-metadata`.
- `business-repo` requires `spark/fides-ci`, `spark/fides-bff-ci`, `spark/contract-dependency-scan`, `spark/business-delivery-readiness`, and `spark/pr-metadata`.
- `idl-repo` requires `spark/idl-contract-gate`, `spark/idl-delivery-readiness`, and `spark/pr-metadata`.

## Contract / IDL Boundary

- No protobuf source contract was changed.
- No generated Java or Go contract source was changed.
- IDL automation moved from GitHub Actions to Argo workflow entry points only.

## Residual Follow-Up

- Push this Harness evidence and gate refresh.
- Re-trigger Harness Argo gates and confirm `spark/harness-gates` changes from failure to success.
- Merge PRs only after the required GitHub commit statuses are green on the final commits.
