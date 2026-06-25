# LEN-99 Local Verification Evidence

## Scope

- Requirement: LEN-99
- Verified at: `2026-06-25T11:56:05+08:00`
- Branch: `feature/LEN-99-business-monorepo-layout`
- Harness HEAD: `4512f04`
- Business HEAD: `862a923`
- GitOps HEAD: `5839a73`
- Janus HEAD: `64a36da`
- IDL HEAD used for matrix validation: `35b627a` detached read-only worktree

## Result

PASS for local tooling, frontend, Go, Java, service matrix, YAML structure and whitespace checks.

The vincent k3s rollout / smoke portion is not covered by this evidence and remains tracked by T9.

## Commands

| Command | Repo / Path | Result |
|---|---|---|
| `python3 -m unittest tooling/contract-dependency-scan/tests/test_contract_dependency_scan.py` | `business-repo` | PASS, 17 tests |
| `python3 tooling/contract-dependency-scan/contract_dependency_scan.py --mode rc-or-formal --path apps/applicant-api/pom.xml --path apps/fides-bff/go.mod` | `business-repo` | PASS, no contract dependency violations |
| `go test ./...` | `business-repo/packages/go/bffkit` | PASS |
| `GOPRIVATE=github.com/spark-harness/* GONOSUMDB=github.com/spark-harness/* go test ./...` | `business-repo/apps/fides-bff` | PASS |
| `pnpm lint:deps` | `business-repo/apps/fides-web` | PASS |
| `pnpm test -- --run` | `business-repo/apps/fides-web` | PASS, 12 files passed, 1 skipped; 51 tests passed, 1 skipped |
| `mvn -B test` | `business-repo/packages/java/money` | PASS, 5 tests |
| `mvn -B test` | `business-repo/packages/java/spring-starter` | PASS, 8 tests |
| `mvn -B test` | `business-repo/apps/applicant-api` | PASS, 43 tests |
| `python3 scripts/validate-service-matrix.py` | `harness-repo` | PASS |
| YAML parse for `workflows/templates/github-repo-gate-workflow-template.yaml`, `workflows/ci/github-repo-gates-sensor.yaml`, and `workflows/ci/business-image-release-sensor.yaml` | `gitops-repo` | PASS |
| `git diff --check` | `business-repo`, `harness-repo`, `gitops-repo` | PASS |
| `go test ./...` | `janus` | PASS |
| `go run ./cmd/janus delivery verify --workspace /Users/forest/Code/spark/.worktrees/LEN-99 --requirement LEN-99 --repo business-repo --base master --head feature/LEN-99-business-monorepo-layout` | `janus` | PASS; contract scan used formal-only mode through the new tooling path |

## Notes

- Test-generated `node_modules` and Maven `target/` directories were removed after verification.
- `apps/applicant-api` Maven test emitted cached GitHub Packages 401 metadata warnings for the local `spark-spring-clean-architecture-starter` SNAPSHOT lookup, but build and all tests passed using the local dependency.
- A detached read-only `idl-repo` sibling worktree was created under `.worktrees/LEN-99/idl-repo` only so service matrix validation could resolve existing proto paths.
- Janus delivery verifier was updated to prefer `tooling/contract-dependency-scan/contract_dependency_scan.py` and retain legacy `scripts/contract_dependency_scan.py` fallback.

## Coverage

- AC1-AC4: covered by moved business paths, README update, old-path scan, and local tests.
- AC5: covered by service matrix validation.
- AC6: covered by GitOps path selector static validation in `argo-path-governance.md`.
- AC7: covered by the command matrix above.

## Out Of Scope For This Evidence

- AC8-AC9 live delivery-readiness and Argo status results after PR push.
- AC10-AC11 vincent k3s rollout, smoke, and applicant-api public exposure negative evidence.
