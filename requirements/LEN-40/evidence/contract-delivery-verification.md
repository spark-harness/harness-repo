# LEN-40 Contract Delivery Verification Evidence

## Scope

- Requirement: LEN-40
- Branch: `feature/LEN-40-delivery-flow`
- Harness repo: `/Users/forest/Code/spark/.worktrees/LEN-40/harness-repo`
- Janus repo: `/Users/forest/Code/spark/.worktrees/LEN-40/janus`
- Business repo: `/Users/forest/Code/spark/.worktrees/LEN-40/business-repo`
- IDL repo: `/Users/forest/Code/spark/.worktrees/LEN-40/idl-repo`
- Verified at: `2026-06-21T01:28:28+08:00`

## Result

PASS.

Implementation tests, scanner tests, workflow syntax checks, actionlint checks, gate JSON
validation, formal evidence unit tests, diff checks, PR-stage delivery readiness checks, and
merge-target requirement verification passed.

## Commands

| Command | Repo | Result | Notes |
|---|---|---|---|
| `go test ./...` | `janus` | PASS | Covers CLI, delivery verifier, open release PR evidence, formal evidence checks, gate, and requirement packages. |
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
| `/tmp/janus-len40 delivery verify --requirement LEN-40 --repo harness-repo --workspace /Users/forest/Code/spark/.worktrees/LEN-40 --base master --head feature/LEN-40-delivery-flow` | PASS | Peers are accepted by release merge evidence or `release_pr_open` PR-stage evidence. |
| `/tmp/janus-len40 delivery verify --requirement LEN-40 --repo janus --workspace /Users/forest/Code/spark/.worktrees/LEN-40 --base master --head feature/LEN-40-delivery-flow` | PASS | Peers are accepted by release merge evidence or `release_pr_open` PR-stage evidence. |
| `/tmp/janus-len40 delivery verify --requirement LEN-40 --repo business-repo --workspace /Users/forest/Code/spark/.worktrees/LEN-40 --base master --head feature/LEN-40-delivery-flow` | PASS | Contract scan passed `formal-only`; peers are accepted by release merge evidence or `release_pr_open` PR-stage evidence. |
| `/tmp/janus-len40 delivery verify --requirement LEN-40 --repo idl-repo --workspace /Users/forest/Code/spark/.worktrees/LEN-40 --base master --head feature/LEN-40-delivery-flow` | PASS | Peers are accepted by release merge evidence or `release_pr_open` PR-stage evidence. |

## Contract / IDL Boundary

- No `.proto` file was modified.
- No generated Java or Go contract source was modified.
- This requirement changes contract delivery governance, scanner modes, and CI readiness checks.
- Formal publishing remains human-operated.
- Artifact registry validation is implemented for changed formal contract dependency files. It requires read-only GitHub package / generated-contract repo credentials in CI.

## PR-Stage Peer Evidence

`release_pr_open` is valid only for PR-stage readiness. It proves the peer repo has an open
`related_branch -> release_branch` PR for the same requirement. After merge, final release
readiness continues to require merge evidence plus Formal tag / artifact evidence where
contract dependency files changed.
