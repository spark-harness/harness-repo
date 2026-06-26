# Local Verification

## Summary

LEN-116 本地验证和 PR 验证均按 ticket 分开执行。LEN-117 image release workflow 不包含在本证据中。

## Commands

| Command | Repo | Result | Notes |
|---|---|---|---|
| `python3 -m unittest tooling/java-quality/tests/test_java_quality.py` | business-repo | PASS | Java quality config loading and dependency validation |
| `pnpm lint:deps && pnpm lint && pnpm exec vitest run --exclude '**/*.smoke.test.*' && pnpm build` | business-repo/apps/fides-web | PASS | Non-smoke frontend gate; ESLint warning was non-blocking |
| `go test ./...` | business-repo/packages/go/bffkit | PASS | bffkit module check |
| `go test ./...` | business-repo/apps/fides-bff | PASS | fides-bff module check |
| `mvn -f apps/applicant-api/pom.xml -Dtest=RedisTraceExportTest test` | business-repo | PASS | Redis trace export waits for Redis span payload |
| `kubectl kustomize workflows/templates` | gitops-repo | PASS | Repo gate template renders |
| `janus delivery verify --workspace /Users/forest/Code/spark/.worktrees/LEN-116 --requirement LEN-116 --repo business-repo --base master --head chore/LEN-116-pr-gate-hard-cut` | janus | PASS | business-repo delivery-readiness passed with gitops merged and Harness peer evidence |
| `git diff --check` | business-repo / gitops-repo / harness-repo | PASS | No whitespace errors |

## PR Evidence

| PR | Ticket | Repo | Result |
|---|---|---|---|
| `spark-harness/gitops-repo#13` | LEN-116 | gitops-repo | MERGED |
| `spark-harness/business-repo#24` | LEN-116 | business-repo | MERGED |

## Out Of Scope

- Smoke tests remain out of scope by explicit user direction.
- LEN-117 image release workflow was delivered separately in `spark-harness/gitops-repo#12`.
