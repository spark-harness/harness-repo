---
requirement_id: "LEN-54"
owner: "Codex"
status: "draft"
updated_at: "2026-06-23"
approved_by: ""
approved_at: ""
decision: ""
---

# Design

## Requirement Traceability

| Requirement Item | Design Decision | Notes |
|---|---|---|
| R1, AC1 | D1: GitOps repo 管理 Argo repo gate templates、Sensor、EventSource、Caddy route 和 runner image | GitOps 是 CI 执行面的事实源 |
| R2, AC2, AC5 | D2: Harness 仓删除 GitHub Actions，branch protection 改为 Argo status context | 不保留双轨 |
| R3, AC3, AC6 | D3: Business 仓删除 GitHub Actions，Fides/BFF/contract scan 由 Argo 执行 | PR status 写回 GitHub |
| R4, AC4, AC7 | D4: IDL 仓删除 GitHub Actions publish/sync，Argo 接管 PR gate 与 push 触发入口 | 不修改 protobuf |
| R5, R7, AC9, AC12 | D5: GitHub webhook -> Argo Events -> Argo Workflows -> GitHub commit status -> branch protection | 用真实 PR 证明闭环 |
| R6, AC8 | D6: 构建 linux/amd64 Janus runner 镜像并配置 imagePullSecrets | 使用本机已登录 Docker 仓库 |
| AC10, AC11 | D7: 用 PR metadata policy 和 Janus delivery verifier 作为跨仓治理规则 | commit subject 不带 ticket 前缀 |

## Summary

设计采用硬切：GitHub 不再运行门禁 workflow。GitHub webhook 进入 Argo Events，
Sensor 为不同 repo 和 gate kind 创建 Workflow，Workflow 使用 Janus runner 或语言基础镜像
执行检查，并通过 GitHub Status API 写回稳定 context。

## Affected Services

| Service | Change | Reason |
|---|---|---|
| Argo repo gates | Add WorkflowTemplate and Sensor | 统一三仓门禁执行面 |
| Caddy webhook ingress | Add `api.fuzzytails.fun` repo routes | GitHub webhook 需要公网 HTTPS |
| Janus runner image | Add Dockerfile and registry pull path | Gate 需要稳定工具链 |
| harness-repo gates | Delete GitHub Actions | Argo status 接管 |
| business-repo CI | Delete GitHub Actions | Argo status 接管 |
| idl-repo automation | Delete GitHub Actions | Argo workflow 接管 |

## API / Contract Design

- Protobuf IDL required: No。
- Proto files: none。
- Buf module: unchanged。
- Buf config version: v2。
- Generated outputs: none。
- Breaking check baseline: not applicable。
- Compatibility strategy: `idl-repo` 仅迁移自动化入口，不改变契约语义。

## Application Design

### D1: GitOps repo owns Argo CI runtime

`gitops-repo` 新增：

- repo gate WorkflowTemplate。
- IDL release WorkflowTemplate。
- GitHub webhook EventSource。
- repo gate Sensor。
- Caddy webhook ingress route。
- Janus runner image build context。

### D2: Stable GitHub status contexts

Branch protection 使用以下 context：

| Repo | Required Contexts |
|---|---|
| `harness-repo` | `spark/harness-gates`, `spark/harness-delivery-readiness`, `spark/pr-metadata` |
| `business-repo` | `spark/fides-ci`, `spark/fides-bff-ci`, `spark/contract-dependency-scan`, `spark/business-delivery-readiness`, `spark/pr-metadata` |
| `idl-repo` | `spark/idl-contract-gate`, `spark/idl-delivery-readiness`, `spark/pr-metadata` |

### D3: PR metadata policy stays in Harness

PR title 带 `[LEN-54]`，commit subject 保持纯 Conventional Commits，例如：

```text
chore(harness): remove GitHub Actions gates
```

PR body 必须包含 `Task`、`What Changed`、`Key Decisions`、`Validation`、
`Gates / Evidence`、`Risks / Follow-up` 和 `Review Guidance`。

### D4: Delivery readiness uses requirement front matter

`janus delivery verify` 读取 `requirements/LEN-54/requirement.md`：

- `related_branch: chore/LEN-54-argo-repo-gates`
- `target_branch: master`
- `release_branch: master`
- `affected_repositories: harness-repo, business-repo, idl-repo`

release-bound PR 阶段允许同一 `related_branch -> master` open PR 作为 peer repo
证据。最终发布仍以 merge 后的 Git 证据为准。

## Data / Config / Permission

- Data model: none。
- Config: GitHub branch protection、webhook URL、Argo workflow parameters、runner image tag。
- Permission: GitHub source/status token、Kubernetes registry pull secret。

## Observability

- Logs: Argo workflow pod logs、EventSource logs、Caddy logs。
- Metrics: none。
- Tracing: none。
- Events: GitHub pull_request 和 IDL push events。

## Testing Strategy

- GitOps manifests:
  - `kubectl kustomize workflows/templates`
  - `kubectl kustomize workflows/ci`
  - `kubectl apply --dry-run=server -k workflows/templates`
  - `kubectl apply --dry-run=server -k workflows/ci`
- Runner:
  - Build and push linux/amd64 image.
  - Run Argo smoke workflow that prints tool versions.
- Harness:
  - `janus version`
  - `jq empty .spark/hooks.json`
  - `bash -n scripts/install.sh`
  - `python3 scripts/test_validate_pr_metadata.py`
- Business:
  - `python3 -m unittest tests/test_contract_dependency_scan.py`
  - `python3 scripts/contract_dependency_scan.py --mode rc-or-formal`
- IDL:
  - `buf lint`
- End-to-end:
  - Push real PR updates.
  - Confirm GitHub webhook deliveries.
  - Confirm Argo workflows.
  - Confirm GitHub status contexts.
  - Confirm branch protection blocks until required Argo statuses pass.

## Rollout And Rollback

- Rollout: GitOps resources first, then repo workflow deletion, then branch protection, then real PR E2E.
- Rollback: restore GitHub Actions workflow files and required check contexts, then revert repo workflow deletion PRs.

## Risks

| Risk | Mitigation | Owner |
|---|---|---|
| Argo runner toolchain drift | Pin runner image tag and smoke actual tool versions | Platform |
| GitHub API intermittent EOF | Retry GitHub API reads/writes and validate final repo settings | Harness |
| Temporary hard-cut gap | User is sole maintainer and explicitly accepts hard cut during refactor | Forest |
| PR history contains trigger commits | Rewrite branches to one Conventional Commit per repo before final validation | Codex |
