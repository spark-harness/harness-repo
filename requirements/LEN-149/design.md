---
requirement_id: "LEN-149"
owner: "core"
status: "approved"
updated_at: "2026-07-02"
approved_by: "forest"
approved_at: "2026-07-02T13:52:15Z"
decision: "用户授权 Codex 批准 LEN-149 设计；采用删除 scan DAG/template、build 成功后进入 GitOps promotion、保留 GitOps render/push 阻断的方案。"
---

# Design

## Requirement Traceability

| Requirement Item | Design Decision | Notes |
|---|---|---|
| BR1, BR2, AC1 | D1: 删除 `github-image-release` DAG 中所有 `scan-*` 任务 | 不保留同步 scan 节点 |
| BR1, BR3, AC2 | D2: 删除 `scan-image` 模板和 Trivy 命令 | active 发布路径不再引用 Trivy |
| BR4, AC3, AC4 | D3: `update-gitops-digests` 依赖所有 build 任务 | 保留 build/push 成功作为 promotion 前置条件 |
| BR5, BR6, AC5 | D4: 更新 GitOps 发布策略文档 | 明确安全扫描后续单独治理 |
| AC6 | D5: 用 YAML parse、grep 和 diff 审查验证 active 引用清理 | 配置变更不新增业务单测 |

## Summary

LEN-149 采用最小 GitOps 改造：删除阻断式 Trivy 扫描节点，让镜像 build/push 成功后直接进入 GitOps digest update、render validation 和 push promotion。失败路径仍由 Argo DAG 依赖和 onExit status report 保持。

## Affected Services

| Service / Module | Change | Reason |
|---|---|---|
| business image release workflow | 删除 scan DAG 节点和 scan template | 消除 Trivy 超时对 promotion 的阻断 |
| GitOps release policy docs | 将扫描章节改为安全扫描边界 | 避免文档继续要求 Trivy 阻断发布 |
| Harness LEN-149 lifecycle | 新增追溯和证据文件 | 让配置治理变更可评审 |

## API / Contract Design

- Protobuf IDL required: no.
- Proto files: none.
- Buf module: none.
- Generated outputs: none.
- Breaking check baseline: not applicable.
- Compatibility strategy: no service API, event, error-code or protobuf contract changes.

## Application Design

### GitOps WorkflowTemplate

- 删除以下 DAG tasks:
  - `scan-applicant-api`
  - `scan-fides-bff`
  - `scan-fides`
  - `scan-quote-api`
  - `scan-origination-api`
- 删除 `scan-image` reusable template。
- 将 `update-gitops-digests.dependencies` 改为全部 build tasks:
  - `build-applicant-api`
  - `build-fides-bff`
  - `build-fides`
  - `build-quote-api`
  - `build-origination-api`
- 保持后续链路不变:
  - `update-gitops-digests`
  - `validate-gitops-render`
  - `push-gitops-promotion`
  - `success`

### GitOps Documentation

- `docs/image-release-policy.md` 不再描述 Trivy 阻断条件。
- `workflows/templates/README.md` 不再把扫描列为模板目标或 Secret 使用原因。
- 文档明确后续安全扫描必须通过独立票据定义非阻断或异步方案。

## Data / Config / Permission

- Data model: no changes.
- Config:
  - WorkflowTemplate DAG dependency changes only.
  - No new Argo parameters.
- Permission:
  - No new RBAC.
  - `registry-dockerconfig` remains required for image push.

## Observability

- Logs:
  - No Trivy scan logs in business image release Workflow.
  - Existing BuildKit, GitOps update, render and push logs remain.
- Metrics: no changes.
- Tracing: no changes.
- Events:
  - GitHub commit status remains `pending`, `success`, or `failure`.
  - `report-failure` still reports Workflow failure.

## Testing Strategy

- Test-first exception: this is config/template-only work. Use YAML parse and structural grep as executable checks.
- Verify active WorkflowTemplate has no `scan-*`, `scan-image`, `aquasec/trivy`, or `trivy image` references.
- Verify `update-gitops-digests` depends on all build tasks.
- Verify `git diff --check` passes in both affected repos.

## Rollout And Rollback

- Rollout:
  - Merge `gitops-repo` branch to `master`.
  - Let Argo CD sync `workflows/templates`.
  - Trigger or wait for next business image release.
- Rollback:
  - Revert the GitOps commit and sync Argo CD.
  - The previous scan tasks and template return as part of the revert.

## Risks

| Risk | Mitigation | Owner |
|---|---|---|
| Security visibility gap after removing blocking Trivy | Track async or non-blocking scanning as separate work | Security / Platform |
| Promotion dependencies accidentally incomplete | Verify dependencies include all build tasks before merge | Codex |
| Argo template syntax drift | Parse YAML and inspect active template references | Codex |
