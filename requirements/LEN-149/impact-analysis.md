---
requirement_id: "LEN-149"
analyst: "Codex"
status: "approved"
updated_at: "2026-07-02"
approved_by: "forest"
approved_at: "2026-07-02T13:52:15Z"
decision: "用户授权 Codex 批准 LEN-149 服务仓库检查；涉及 harness-repo 和 gitops-repo，IDL 无影响。"
idl_impact: "no"
idl_impact_reason: "本需求只修改 GitOps Argo WorkflowTemplate 和发布策略文档，不修改 protobuf IDL、generated contracts 或 Buf 配置。"
---

# Impact Analysis

## Summary

LEN-149 移除 business image release 中同步阻断发布的 Trivy scan 路径，让构建成功的业务镜像可以继续进入 GitOps digest promotion。

## Affected Domains

- GitOps delivery: 修改 Argo WorkflowTemplate 的 DAG 依赖和模板集合。
- Release governance: 更新 GitOps 发布策略文档，明确安全扫描不再是同步阻断步骤。
- Harness lifecycle: 保存需求、影响分析、设计、任务、验证和审查记录。

## Affected Services

| Service / Module | Repo | Reason | Protobuf Required |
|---|---|---|---|
| business image release workflow | gitops-repo | 移除阻断发布的 Trivy scan DAG 节点和模板 | no |
| image release policy docs | gitops-repo | 同步发布策略，避免文档继续声明 Trivy 阻断 | no |
| LEN-149 lifecycle | harness-repo | 保存需求追溯、设计、任务、证据和审查 | no |

## Upstream / Downstream Consumers

- Upstream:
  - `business-repo` 主干 push 触发 business image release Sensor。
- Downstream:
  - GitOps overlay digest promotion。
  - GitHub commit status `spark/business-image-release`。
  - Argo Workflow 失败状态和 onExit failure report。

## API / Contract Impact

- External API: no changes.
- Protobuf IDL: no changes.
- Generated contracts: no changes.
- Buf module/config: no changes.
- Compatibility risk: no API or contract compatibility risk.

## Data Impact

- Database schema: no changes.
- Data migration: no.
- Backfill: no.
- Cache: no changes.

## Config / Permission / Observability Impact

- Config:
  - WorkflowTemplate DAG dependency changes.
  - No new parameters, Secrets, ConfigMaps, or registry credentials.
- Permission:
  - No new Kubernetes RBAC.
  - Existing registry docker config secret remains required for BuildKit image push.
- Logs:
  - Trivy scan logs disappear from image release Workflow.
  - BuildKit, GitOps update, render validation and push logs remain.
- Metrics:
  - No new metrics.
- Tracing:
  - No tracing changes.
- Events:
  - Workflow status and GitHub commit status behavior remain.

## Rollout And Rollback

- Rollout:
  - Merge `gitops-repo` WorkflowTemplate change to `master`.
  - Argo CD syncs the updated workflow template into `argo`.
  - Next business image release uses build-to-promotion DAG without scan tasks.
- Rollback:
  - Revert the `gitops-repo` commit to restore the previous scan tasks and template.
  - Re-sync Argo CD templates.
- Kill switch:
  - No runtime kill switch; rollback is GitOps revert.

## Risks

| Risk | Impact | Mitigation | Owner |
|---|---|---|---|
| Security scanning is absent from the synchronous release path | Vulnerability signal is not produced by this workflow | Record as intentional non-goal and require a separate non-blocking or async scanning ticket | Security / Platform |
| DAG dependency is edited incorrectly | Promotion may run before all image digests exist | YAML parse and active template scan verify update depends on all build tasks | Codex |
| Documentation remains stale | Operators may expect Trivy failures to block release | Update policy and template README in the same ticket | Codex |
