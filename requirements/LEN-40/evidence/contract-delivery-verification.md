# LEN-40 Contract Delivery Verification Evidence

## Scope

- Requirement: LEN-40
- Branch: `feature/LEN-40-delivery-flow`
- Harness repo: `/Users/forest/Code/spark/.worktrees/LEN-40/harness-repo`
- Janus repo: `/Users/forest/Code/spark/.worktrees/LEN-40/janus`
- Business repo: `/Users/forest/Code/spark/.worktrees/LEN-40/business-repo`
- IDL repo: `/Users/forest/Code/spark/.worktrees/LEN-40/idl-repo`
- Verified at: `2026-06-21T00:52:58+08:00`

## Result

PARTIAL PASS.

Implementation tests, scanner tests, workflow syntax checks, actionlint checks, gate JSON
validation, formal evidence unit tests, and diff checks passed. `janus delivery verify` correctly reports a current
release-bound peer-state blocker for `idl-repo` when run from `harness-repo`, `janus`, and
`business-repo`; this is expected real-state evidence because `idl-repo` has not yet been
merged to `release_branch`.

## Commands

| Command | Repo | Result | Notes |
|---|---|---|---|
| `go test ./...` | `janus` | PASS | Covers CLI, delivery verifier, formal evidence checks, gate, and requirement packages. |
| `python3 -m unittest tests/test_contract_dependency_scan.py` | `business-repo` | PASS | 17 tests cover `rc-or-formal`, `formal-only`, and legacy modes. |
| `bash -n .github/workflows/branch-coherence.yml` | `harness-repo` | PASS | Workflow shell syntax check. |
| `bash -n .github/workflows/branch-coherence.yml && bash -n .github/workflows/contract-dependency-scan.yml` | `business-repo` | PASS | Workflow shell syntax check. |
| `bash -n .github/workflows/branch-coherence.yml` | `idl-repo` | PASS | Workflow shell syntax check. |
| `actionlint .github/workflows/branch-coherence.yml` | `harness-repo` | PASS | GitHub Actions lint. |
| `actionlint .github/workflows/branch-coherence.yml .github/workflows/contract-dependency-scan.yml` | `business-repo` | PASS | GitHub Actions lint. |
| `actionlint .github/workflows/branch-coherence.yml` | `idl-repo` | PASS | GitHub Actions lint. |
| `git diff --check` | `harness-repo` | PASS | Whitespace check. |
| `git diff --check` | `janus` | PASS | Whitespace check. |
| `git diff --check` | `business-repo` | PASS | Whitespace check. |
| `git diff --check` | `idl-repo` | PASS | Whitespace check. |
| `/tmp/janus-len40 gate validate requirements/LEN-40/gates/requirement-review.gate.json` | `harness-repo` | PASS | Gate JSON schema. |
| `/tmp/janus-len40 gate validate requirements/LEN-40/gates/design-review.gate.json` | `harness-repo` | PASS | Gate JSON schema. |
| `/tmp/janus-len40 gate validate requirements/LEN-40/gates/dev-entry.gate.json` | `harness-repo` | PASS | Gate JSON schema. |
| `/tmp/janus-len40 gate validate requirements/LEN-40/gates/service-repo-check.gate.json` | `harness-repo` | PASS | Gate JSON schema. |

## Delivery Readiness

| Command | Result | Evidence |
|---|---|---|
| `/tmp/janus-len40 delivery verify --requirement LEN-40 --repo harness-repo --workspace /Users/forest/Code/spark/.worktrees/LEN-40 --base master --head feature/LEN-40-delivery-flow` | BLOCKED | `idl-repo has no acceptable peer state for related="feature/LEN-40-delivery-flow" target="master" release="master"`. |
| `/tmp/janus-len40 delivery verify --requirement LEN-40 --repo janus --workspace /Users/forest/Code/spark/.worktrees/LEN-40 --base master --head feature/LEN-40-delivery-flow` | BLOCKED | `idl-repo has no acceptable peer state for related="feature/LEN-40-delivery-flow" target="master" release="master"`. |
| `/tmp/janus-len40 delivery verify --requirement LEN-40 --repo business-repo --workspace /Users/forest/Code/spark/.worktrees/LEN-40 --base master --head feature/LEN-40-delivery-flow` | BLOCKED | Contract scan passed `formal-only`; peer status blocks on `idl-repo`. |
| `/tmp/janus-len40 delivery verify --requirement LEN-40 --repo idl-repo --workspace /Users/forest/Code/spark/.worktrees/LEN-40 --base master --head feature/LEN-40-delivery-flow` | PASS | Peers `business-repo`, `harness-repo`, and `janus` are detected as `related_merged_to_release`. |

## Contract / IDL Boundary

- No `.proto` file was modified.
- No generated Java or Go contract source was modified.
- This requirement changes contract delivery governance, scanner modes, and CI readiness checks.
- Formal publishing remains human-operated.
- Artifact registry validation is implemented for changed formal contract dependency files. It requires read-only GitHub package / generated-contract repo credentials in CI.

## Current Blocking Finding

`release-readiness` currently blocks in repos that depend on `idl-repo` as a peer until
`idl-repo` has merge evidence into `release_branch` or the verifier can query equivalent PR /
tag evidence. This is not a gate implementation failure; it is the intended release-bound
peer-state rule.
