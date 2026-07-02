# Local Verification

## Summary

LEN-149 是 GitOps WorkflowTemplate 配置变更，不修改业务代码、protobuf IDL、generated contracts 或运行时 Secret。

Test-first exception: 本次没有业务行为代码。验证用 YAML parse、DAG dependency assertion、active template reference scan 和 diff whitespace check 替代业务单测。

## Commands

| Check | Command | Repo | Result |
|---|---|---|---|
| YAML parse and DAG dependency assertion | `python3 - <<'PY' ... yaml.safe_load(...); assert no scan-* tasks; assert update-gitops-digests dependencies == all build tasks; assert scan-image not in templates` | gitops-repo | PASS |
| Active image release template scan | `if rg -n "trivy\|Trivy\|aquasec\|scan-image\|scan-[a-z-]+" workflows/templates/github-image-release-workflow-template.yaml; then exit 1; else echo PASS; fi` | gitops-repo | PASS |
| GitOps whitespace check | `git diff --check` | gitops-repo | PASS |
| Harness whitespace check | `git diff --check` | harness-repo | PASS |
| Task JSON validation | `python3 -m json.tool requirements/LEN-149/tasks.json >/dev/null` | harness-repo | PASS |

## Acceptance Mapping

| Acceptance | Evidence |
|---|---|
| AC1 | Active template scan found no `scan-*` task references in `github-image-release-workflow-template.yaml`. |
| AC2 | Active template scan found no `scan-image`, `aquasec/trivy`, or `trivy image` references. |
| AC3 | YAML assertion confirmed `update-gitops-digests` depends on all five build tasks. |
| AC4 | Diff keeps `validate-gitops-render` after `update-gitops-digests` and `push-gitops-promotion` after render validation. |
| AC5 | `docs/image-release-policy.md` and `workflows/templates/README.md` no longer describe Trivy as a release-blocking gate. |
| AC6 | YAML parse, grep scan and diff checks passed. |

## Gate Note

Human approval was recorded through `janus requirement approve` after user authorization in chat.
