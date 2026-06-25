# LEN-99 Argo Path Governance Evidence

## Scope

- Requirement: LEN-99
- Verified at: `2026-06-25T16:45:48+08:00`
- GitOps repo branch: `feature/LEN-99-business-monorepo-layout`
- GitOps HEAD: `5c8985f`

## Result

PASS for static Argo path governance updates and live Argo validation against business-repo PR #21.

As of `2026-06-25T16:45:48+08:00`, the `gitops-repo` LEN-99 branch is pushed at commit `5c8985f` and PR #8 is available at https://github.com/spark-harness/gitops-repo/pull/8.

## Updated Gate Paths

| Gate | Path selector / command | Result |
|---|---|---|
| `spark/fides-ci` | `apps/fides-web/**`; command runs in `apps/fides-web` | Updated |
| `spark/fides-bff-ci` | `apps/fides-bff/**`, `packages/go/bffkit/**`; commands run in `apps/fides-bff` and `packages/go/bffkit` | Updated |
| `spark/applicant-api-ci` | `apps/applicant-api/**`, `packages/java/**`; commands run Maven tests for `packages/java/money`, `packages/java/spring-starter`, and `apps/applicant-api` | Added |
| `spark/contract-dependency-scan` | self-test and scanner run from `tooling/contract-dependency-scan` | Updated |

## Updated Image Release Paths

| Service | dockerfile-dir |
|---|---|
| applicant-api | `apps/applicant-api` |
| fides-bff | `apps/fides-bff` |
| fides | `apps/fides-web` |

## Static Verification

| Command | Result |
|---|---|
| YAML parse for `workflows/templates/github-repo-gate-workflow-template.yaml` | PASS |
| YAML parse for `workflows/ci/github-repo-gates-sensor.yaml` | PASS |
| YAML parse for `workflows/ci/business-image-release-sensor.yaml` | PASS |
| YAML parse for `apps/applicant-api/base/networkpolicy.yaml` and `clusters/lendora-sta/namespaces.yaml` | PASS |
| `kubectl kustomize apps/applicant-api/overlays/lendora-sta` | PASS, 5 documents rendered |
| `git diff --check` in `gitops-repo` | PASS |
| Old active path scan outside historical review docs | PASS; no old business paths remain in active GitOps workflow files |

## Live Cluster Governance Objects

| Object | Namespace | Generation / value | Result |
|---|---|---|---|
| `WorkflowTemplate/github-repo-gate` | `argo` | generation `11`, `janus-image=registry.cn-shenzhen.aliyuncs.com/love-is-pain/janus-runner:LEN-99-e5c6388-20260625-1455` | Applied |
| `Sensor/github-repo-gates` | `argo-events` | generation `4` | Applied; includes `applicant-api-ci` route |
| `Sensor/business-image-release` | `argo-events` | generation `3` | Applied; uses `apps/applicant-api`, `apps/fides-bff`, `apps/fides-web` Dockerfile directories |

## Live Argo Workflow Results

Business PR #21 commit under test: `eccb6c593dcb7fafca944c397f7e6c7d790126f9`.

| Workflow | GitHub status context | Phase | Started | Finished |
|---|---|---|---|---|
| `len99-business-pr21-pr-metadata-4grxp` | `spark/pr-metadata` | Succeeded | `2026-06-25T08:15:24Z` | `2026-06-25T08:16:54Z` |
| `len99-business-pr21-fides-x5fjn` | `spark/fides-ci` | Succeeded | `2026-06-25T08:15:25Z` | `2026-06-25T08:16:55Z` |
| `len99-business-pr21-fides-bff-nn7qx` | `spark/fides-bff-ci` | Succeeded | `2026-06-25T08:15:27Z` | `2026-06-25T08:18:45Z` |
| `len99-business-pr21-contract-scan-d4l2j` | `spark/contract-dependency-scan` | Succeeded | `2026-06-25T08:15:28Z` | `2026-06-25T08:16:58Z` |
| `len99-business-pr21-applicant-api-r2-qmds9` | `spark/applicant-api-ci` | Succeeded | `2026-06-25T08:22:32Z` | `2026-06-25T08:26:09Z` |
| `len99-business-pr21-delivery-r2-8wb6h` | `spark/business-delivery-readiness` | Succeeded | `2026-06-25T08:22:32Z` | `2026-06-25T08:24:02Z` |

## Live Fixes Applied During Verification

| Finding | Fix | Evidence |
|---|---|---|
| `business-delivery-readiness` needed the LEN-99 Janus verifier because the old runner could not resolve the same-branch Janus checkout. | `github-repo-gate` now checks out `janus` as a peer repo and uses runner image `LEN-99-e5c6388-20260625-1455`. | `len99-business-pr21-delivery-r2-8wb6h` succeeded. |
| `applicant-api-ci` Maven tests require Redis. | `applicant-api-ci` now runs with a Redis sidecar in the Argo template. | `len99-business-pr21-applicant-api-r2-qmds9` succeeded. |
| `applicant-api` HTTP target port is `8080`; the service exposes HTTP as `80`. | NetworkPolicy includes `8080` and `fides-bff` namespace carries `lendora.io/applicant-api-client=true`; applicant-api remains ClusterIP-only. | Kustomize rendered successfully; live network policy and namespace labels verified in `k3s-rollout-smoke.md`. |

## Residual Follow-Up

- After merge, confirm branch protection includes `spark/applicant-api-ci` if it is not already required on the protected branch.
