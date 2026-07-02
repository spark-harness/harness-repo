---
requirement_id: "LEN-149"
owner: "core"
status: "approved"
created_at: "2026-07-02"
related_branch: "chore/LEN-149-remove-trivy-blocking-scan"
target_branch: "master"
release_branch: "master"
contract_gate_mode: "auto"
affected_repositories:
  - harness-repo
  - gitops-repo
approved_by: "forest"
approved_at: "2026-07-02T13:52:15Z"
decision: "用户授权 Codex 批准 LEN-149 需求和影响分析；范围限定为移除发布链路中的同步阻断式 Trivy 扫描，不包含替代安全扫描平台。"
---

# 移除发布链路中的 Trivy 阻断扫描

## Background

业务镜像发布链路当前在构建后执行 Trivy image scan。Java 镜像分析可能超时，并阻断后续 GitOps digest promotion，导致镜像已经构建成功但无法稳定进入 GitOps 发布流程。

这条需求不是什么：它不是降低生产安全治理要求，也不是删除未来安全扫描能力。

它是什么：它只移除当前同步阻断镜像发布的 Trivy 扫描步骤，保留构建、推送、GitOps 渲染和 GitOps push 的失败阻断能力。后续安全扫描应以独立票据定义非阻断或异步告警方案。

## Goals

- 移除 business image release 工作流中的 Trivy image scan DAG 节点。
- 移除发布模板中执行 Trivy 的可复用模板。
- 让 GitOps digest promotion 只依赖所有业务镜像 build/push 成功。
- 保留构建失败、推送失败、GitOps digest 更新失败、GitOps render 失败和 GitOps push 失败的阻断能力。
- 更新 GitOps 发布策略文档，明确安全扫描不再是同步阻断步骤。

## Non-Goals

- 不引入新的安全扫描工具。
- 不设计漏洞 SLA、漏洞豁免或告警策略。
- 不修改业务服务 Dockerfile、应用代码、protobuf IDL 或生成契约。
- 不调整 Argo Sensor、GitHub status context 或 required check 名称。
- 不改变 GitOps overlay 的 digest promotion 目标环境。

## User / Business Scenarios

### Scenario 1: 构建成功后进入 promotion

Given: business image release 工作流已成功构建并推送所有业务镜像。

When: 工作流进入 digest promotion 阶段。

Then: promotion 不再等待 Trivy scan 节点，也不会因为 Trivy 超时失败。

### Scenario 2: 构建或推送失败仍阻断发布

Given: 任一业务镜像构建或推送失败。

When: 工作流执行发布 DAG。

Then: GitOps digest promotion 不执行，Workflow 失败并回写 GitHub failure status。

### Scenario 3: GitOps promotion 失败仍阻断发布

Given: 镜像构建和推送都成功。

When: GitOps digest 更新、render validation 或 push promotion 失败。

Then: Workflow 失败并回写 GitHub failure status。

### Scenario 4: 后续安全扫描方案单独治理

Given: 团队需要恢复安全扫描治理。

When: 设计新的扫描方案。

Then: 必须用独立票据定义非阻断或异步告警方式，不把同步 Trivy 阻断步骤直接恢复进主发布链路。

## Business Rules

- BR1: 镜像构建成功后，发布链路不应因为 Trivy 超时而阻断 GitOps promotion。
- BR2: 所有阻断发布的 Trivy scan DAG 节点必须移除。
- BR3: 所有执行 Trivy 的发布模板步骤必须移除。
- BR4: build/push、GitOps digest update、render validation 和 GitOps push 失败仍必须阻断发布。
- BR5: 文档必须说明移除的是同步阻断路径，不是取消安全治理。
- BR6: 后续安全扫描恢复必须由独立票据定义非阻断或异步方案。

## Acceptance Criteria

- AC1: `github-image-release` WorkflowTemplate 不再包含 `scan-*` DAG 节点。
- AC2: `github-image-release` WorkflowTemplate 不再包含 `scan-image` 模板、`aquasec/trivy` 镜像或 `trivy image` 命令。
- AC3: `update-gitops-digests` 依赖所有 `build-*` 任务，而不是依赖扫描任务。
- AC4: `validate-gitops-render` 和 `push-gitops-promotion` 仍位于 digest update 之后，并保留失败阻断路径。
- AC5: GitOps 文档不再声明 Trivy 是发布阻断门禁，并说明后续安全扫描必须单独设计。
- AC6: YAML 文件能被解析，仓库扫描确认 active 发布路径没有 Trivy 引用。

## Open Questions

| Question | Owner | Deadline | Status |
|---|---|---|---|
| 是否另起安全扫描非阻断或异步告警票据 | Security / Platform | 后续规划 | open |

## Notes

- 需求来源为 Jira LEN-149。
- 本次实现只涉及 `harness-repo` 和 `gitops-repo`。
