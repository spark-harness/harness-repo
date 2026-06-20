---
requirement_id: "LEN-37"
updated_at: "2026-06-20"
owner: "Codex"
---

# Verification Evidence

## Janus Verification

| Command | Repo | Result |
|---|---|---|
| `go test ./...` | janus | PASS |
| `go test ./internal/requirement -run 'TestRunServiceRepoCheckAllowsGovernanceTaskWithoutAffectedServices\|TestRunServiceRepoCheckSkipsIDLRepoWhenImpactExplicitlyNo\|TestRunServiceRepoCheckPrefersStructuredIDLImpact' -count=1` | janus | PASS |
| `go build -o /tmp/janus-len37 ./cmd/janus` | janus | PASS |
| `/tmp/janus-len37 gate render --help` | janus | Returns `unknown gate subcommand "render"` with exit code 2 |

## Harness Verification

| Command | Repo | Result |
|---|---|---|
| `bash -n scripts/install.sh` | harness-repo | PASS |
| `python3 -m py_compile scripts/render-gates.py` | harness-repo | PASS |
| `./scripts/install.sh --check` | harness-repo | PASS |
| `rg 'gate render\|render --check\|rendered gate Markdown\|rendered Markdown\|门禁审计视图\|用 Janus 渲染\|Markdown 漂移' AGENTS.md .github scripts context .spark -g '*'` | harness-repo | No matches |

## Gate Verification

| Command | Repo | Result |
|---|---|---|
| `/tmp/janus-len37 gate validate requirements/LEN-37/gates/requirement-review.gate.json` | harness-repo | PASS |
| `/tmp/janus-len37 gate validate requirements/LEN-37/gates/design-review.gate.json` | harness-repo | PASS |
| `/tmp/janus-len37 gate validate requirements/LEN-37/gates/dev-entry.gate.json` | harness-repo | PASS |
| `/tmp/janus-len37 gate validate requirements/LEN-37/gates/service-repo-check.gate.json` | harness-repo | PASS |
| `/tmp/janus-len37 gate validate requirements/LEN-37/gates/merge-readiness.gate.json` | harness-repo | PASS |
| `/tmp/janus-len37 gate verify --input requirements/LEN-37/gates/merge-readiness.gate.json --ticket-id LEN-37` | harness-repo | PASS |
| `/tmp/janus-len37 requirement verify --requirement LEN-37 --target merge --ticket-id LEN-37` | harness-repo | PASS |

## Scope Notes

- Gate Markdown was not generated for LEN-37.
- Historical `requirements/*/gates/*.md` files were not bulk deleted.
- `tasks.json` declares no affected business services because LEN-37 is a governance and Janus CLI change, not a business service change.
