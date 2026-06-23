---
requirement_id: "LEN-54"
analyst: "Codex"
status: "draft"
updated_at: "2026-06-23"
approved_by: ""
approved_at: ""
decision: ""
idl_impact: "no"
idl_impact_reason: "本需求删除 idl-repo 的 GitHub Actions 自动化，但不修改 protobuf 源契约。"
---

# Impact Analysis

## Summary

LEN-54 影响 GitOps 运行时、三仓 PR 门禁、IDL 发布 / 同步入口、branch protection、
runner 镜像和 webhook 域名。它不改变业务运行时行为，也不修改 protobuf IDL。

## Affected Domains

- GitOps repo：Argo Workflows、Argo Events、Caddy ingress、runner image。
- Harness repo：需求生命周期、门禁文档、PR metadata 规则、GitHub Actions 删除。
- Business repo：Fides / BFF / contract scan GitHub Actions 删除和 Argo status 接管。
- IDL repo：PR gate、publish、sync GitHub Actions 删除和 Argo workflow 接管。
- GitHub repo settings：webhook、required status checks、branch protection。
- Kubernetes runtime：`argo`、`argo-events`、Caddy、registry pull secret。

## Affected Services

| Service | Repo | Reason | Protobuf Required |
|---|---|---|---|
| repo gates | `gitops-repo` | 新增 Argo WorkflowTemplate、EventSource、Sensor 和 ingress | No |
| harness gates | `harness-repo` | 删除 GitHub Actions，改由 Argo 执行 Janus / PR metadata | No |
| fides | `business-repo` | 删除 GitHub Actions 前端 CI，改由 Argo 执行 | No |
| fides-bff | `business-repo` | 删除 GitHub Actions BFF CI，改由 Argo 执行 | No |
| contract dependency scan | `business-repo` | 删除 GitHub Actions contract scan，改由 Argo 执行 | No |
| idl automation | `idl-repo` | 删除 GitHub Actions publish / sync，改由 Argo workflow 处理 | No |

## Upstream / Downstream Consumers

- GitHub PR：仍是评审和 merge 入口。
- Argo Events：接收 GitHub webhook 并触发 Sensor。
- Argo Workflows：运行仓库门禁和 IDL 发布 / 同步工作流。
- GitHub commit status：作为 branch protection 的事实输入。
- Docker registry：提供 Janus runner 镜像。

## API / Contract Impact

- Does this change involve protobuf IDL or external contracts: No。
- Contract repo: `idl-repo` 仅删除 GitHub Actions 自动化，不改 `.proto`。
- Proto files: none。
- Buf module: unchanged。
- Buf config version: v2。
- Required buf checks: `buf lint` 用于确认 IDL 仓删除 workflow 后源契约仍有效。
- Breaking baseline: not applicable。
- Compatibility risk: none for protobuf schema。

## Generated Contract Impact

- Java generated contracts: none。
- Go generated contracts: none。
- IDL publish / sync 工作流入口迁移到 Argo，不改变生成物内容。

## Data Impact

- Database schema: none。
- Data migration: none。
- Backfill: none。
- Cache: none。
- Runtime storage: none。

## Config / Permission / Observability Impact

- Config: GitHub webhook URL、branch protection required status checks、Caddy route、Argo Sensor parameters、runner image tag。
- Permission: Kubernetes image pull secret、GitHub status token、GitHub source token。
- Metrics: none in this ticket。
- Logs: Argo workflow logs and EventSource delivery logs become CI troubleshooting source。
- Tracing: none。
- Events: GitHub pull_request and IDL push events enter Argo Events。

## Rollout And Rollback

- Rollout:
  - Apply GitOps repo workflow templates, sensors and ingress.
  - Build and push runner image to the currently logged-in Docker registry.
  - Configure repo webhooks and branch protection to Argo status contexts.
  - Delete GitHub Actions workflow files from affected repos.
  - Validate with real PRs.
- Rollback:
  - Revert the workflow deletion commits in affected repos.
  - Restore GitHub Actions required checks in branch protection.
  - Keep Argo resources intact until GitHub Actions recovery is verified.

## Risks

| Risk | Impact | Mitigation | Owner |
|---|---|---|---|
| Runner image pull fails | All Argo gates fail before tests run | Use current machine Docker login, push linux/amd64 image, create `aliyun-registry` pull secret, run smoke workflow | Platform |
| Webhook DNS or TLS fails | GitHub events do not reach Argo | Use `api.fuzzytails.fun` A record, Caddy HTTPS route and GitHub delivery evidence | Platform |
| PR metadata rejects temporary commits | Required status remains failure | Squash / rewrite trigger commits before final PR validation | Harness |
| delivery readiness cannot prove peer repo state | Multi-repo PRs blocked | Use same `related_branch` across repos and keep PRs open until merge | Harness |
| GitHub Actions removed too early | Temporary gap if Argo route is broken | User accepts hard cut; final branch protection points at Argo status contexts only | Forest |
