# LEN-99 Argo Path Governance Evidence

## Scope

- Requirement: LEN-99
- Verified at: `2026-06-25T14:18:08+08:00`
- GitOps repo branch: `feature/LEN-99-business-monorepo-layout`
- GitOps HEAD: `2beea0e`

## Result

PASS for static Argo path governance updates.

Live Argo Workflow and GitHub status results remain pending until the GitOps and business PRs are pushed and the cluster receives GitHub events.

As of `2026-06-25T14:18:08+08:00`, the `gitops-repo` LEN-99 branch push completed, but GitHub API POST / GET calls intermittently fail with TLS / EOF errors from this host. Live Argo status evidence remains pending until the GitOps PR is created or verified through a stable GitHub API / browser session.

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
| `git diff --check` in `gitops-repo` | PASS |
| Old active path scan outside historical review docs | PASS; no old business paths remain in active GitOps workflow files |

## Residual Follow-Up

- Push GitOps changes and confirm Argo creates `spark/applicant-api-ci` alongside existing business repo gates.
- Confirm required GitHub status contexts include `spark/applicant-api-ci` before relying on the new Java gate for branch protection.
- Confirm business image release workflows build from new Dockerfile directories after merge.
