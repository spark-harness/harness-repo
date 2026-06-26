# LEN-114 Local And CI Verification Evidence

## Scope

- Harness worktree: `/Users/forest/Code/spark/.worktrees/LEN-114/harness-repo`
- Business worktree: `/Users/forest/Code/spark/.worktrees/LEN-114/business-repo`
- GitOps worktree: `/Users/forest/Code/spark/.worktrees/LEN-114/gitops-repo`
- Janus worktree: `/Users/forest/Code/spark/.worktrees/LEN-114/janus`
- Live Argo namespace: `argo`

## Commands And Results

| Command / Check | Working Directory / Target | Result | Notes |
|---|---|---|---|
| `python3 -m unittest tooling/java-quality/tests/test_java_quality.py` | `business-repo` | PASS | 9 tests passed after removing retry/fallback behavior. |
| `python3 tooling/java-quality/java_quality.py run-project money` | `business-repo` | PASS | Local money gate passed before final CI submit. |
| `kubectl kustomize workflows/templates` | `gitops-repo` | PASS | WorkflowTemplate manifests rendered successfully. |
| `kubectl kustomize workflows/ci` | `gitops-repo` | PASS | Sensor manifests rendered successfully. |
| `docker run --rm registry.cn-shenzhen.aliyuncs.com/love-is-pain/janus-runner:LEN-114-400554b-20260626-0056 'java -version && mvn -version && janus version && buf --version'` | local Docker | PASS | Verified JDK 21.0.11, Maven 3.9.11, Janus 0.1.0, Buf 1.47.2. |
| `go test ./...` | `janus` | PASS | Janus no-fallback delivery verify support passed before PR merge. |
| `go run ./cmd/janus delivery verify --workspace /Users/forest/Code/spark/.worktrees/LEN-114 --requirement LEN-114 --repo business-repo --base master --head feature/LEN-114-java-ci` | `janus` | PASS | Local delivery-readiness verification passed after Janus fix and peer worktree setup. |
| `business-repo-java-ci-prwz2` | Argo Workflow | PASS | money, spring-starter and applicant-api all succeeded with the JDK 21 runner. |
| `spark/java-ci` | business-repo PR #23 | PASS | GitHub status succeeded for head `76b8149f33c739a420035318a439297ee048fc4d`. |
| `spark/argo-smoke` | gitops-repo PR #11 | PASS | GitOps runner follow-up smoke passed before merge. |

## Merged PRs

| Repo | PR | Merge Commit | Result |
|---|---|---|---|
| janus | https://github.com/spark-harness/janus/pull/7 | `400554b` head merged | MERGED |
| gitops-repo | https://github.com/spark-harness/gitops-repo/pull/9 | `c8a33d0` head merged | MERGED |
| gitops-repo | https://github.com/spark-harness/gitops-repo/pull/10 | `2119927` head merged | MERGED |
| gitops-repo | https://github.com/spark-harness/gitops-repo/pull/11 | `ea277f1` merge commit | MERGED |
| business-repo | https://github.com/spark-harness/business-repo/pull/23 | `8fb4ba3` merge commit | MERGED |

## Result

LEN-114 implementation is merged for Janus, GitOps and business-repo. The live
`github-repo-gate` WorkflowTemplate uses
`registry.cn-shenzhen.aliyuncs.com/love-is-pain/janus-runner:LEN-114-400554b-20260626-0056`,
and the Java CI workflow has passed against business-repo PR #23.
