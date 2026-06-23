---
requirement_id: "LEN-54"
owner: "forest"
status: "approved"
created_at: "2026-06-23"
related_branch: "chore/LEN-54-argo-repo-gates"
target_branch: "master"
release_branch: "master"
contract_gate_mode: "auto"
affected_repositories:
  - harness-repo
  - business-repo
  - idl-repo
approved_by: "forest"
approved_at: "2026-06-23T18:21:00+08:00"
decision: "批准 LEN-54 需求定义和影响分析，执行仓库门禁硬切到 Argo。"
---

# Argo 仓库门禁硬切

## Background

Spark 多仓当前同时存在 GitHub Actions 门禁和 Argo GitOps / CI 基础设施。继续保留
GitHub Actions 会让门禁事实源分裂：同一个 PR 同时受 GitHub workflow、Argo workflow、
Janus gate 和 branch protection 影响。

先说不是什么：本需求不是增加一套 Argo 旁路校验，也不是让 GitHub Actions 与 Argo
长期并行。

它是什么：将 `harness-repo`、`business-repo` 和 `idl-repo` 的仓库门禁执行面硬切到
Argo，由 GitHub Webhook 触发 Argo Events，由 Argo Workflows 运行 Janus、测试和发布
检查，并把结果写回 GitHub commit status。

## Goals

- R1：`gitops-repo` 管理 Argo repo gate workflow、webhook EventSource、Sensor、runner 镜像和 webhook ingress。
- R2：`harness-repo` 不再保留 GitHub Actions 门禁 workflow，PR 必需状态由 Argo 写回。
- R3：`business-repo` 不再保留 GitHub Actions CI / contract scan workflow，Fides、BFF、contract scan 和 delivery readiness 由 Argo 执行。
- R4：`idl-repo` 不再保留 GitHub Actions branch coherence、publish 和 sync workflow，PR gate 与发布 / 同步入口由 Argo 执行。
- R5：GitHub branch protection 只要求 Argo commit status context，不再要求 GitHub Actions check run。
- R6：Argo runner 镜像从当前可用 Docker 仓库拉取，并具备 Janus、Go、Buf、Java、Maven、jq 和 Python 等门禁运行依赖。
- R7：真实 PR E2E 证明 webhook、Argo workflow、GitHub status 和 branch protection 能串成闭环。

## Non-Goals

- 不在 GitHub Actions 中保留长期 fallback。
- 不把密钥、Docker 凭据或 GitHub token 写入 Git。
- 不改变业务服务行为、protobuf 契约内容或前端功能。
- 不在本需求中实现 GitHub App 替换 PAT。
- 不手写 Janus gate JSON 作为门禁事实源。

## User / Business Scenarios

### Scenario 1：Harness 仓 PR 门禁

Given：维护者打开 `harness-repo` 的 LEN-54 PR。

When：GitHub 发送 pull_request webhook。

Then：Argo 运行 harness gates、delivery readiness 和 PR metadata，并把
`spark/harness-gates`、`spark/harness-delivery-readiness`、`spark/pr-metadata` 写回
GitHub commit status。

### Scenario 2：Business 仓 PR 门禁

Given：维护者打开 `business-repo` 的 LEN-54 PR。

When：GitHub 发送 pull_request webhook。

Then：Argo 运行 Fides CI、Fides BFF CI、contract dependency scan、delivery readiness
和 PR metadata，并把对应 `spark/*` status 写回 GitHub。

### Scenario 3：IDL 仓 PR 门禁与发布入口

Given：维护者打开或更新 `idl-repo` 的 LEN-54 PR，或推送 IDL 发布 / 同步分支。

When：GitHub 发送 pull_request 或 push webhook。

Then：Argo 运行 IDL PR gate、delivery readiness、PR metadata，发布 / 同步入口由
Argo workflow 处理，不再依赖 GitHub Actions workflow。

### Scenario 4：分支保护阻塞不合格 PR

Given：PR 缺少必需 Argo status 或 status 为 failure。

When：维护者尝试合并到 `master`。

Then：GitHub branch protection 阻止合并。

## Business Rules

- BR1：GitHub Actions 不再作为仓库门禁执行面。
- BR2：GitHub 只负责 PR、Webhook、commit status 和 branch protection。
- BR3：Argo status context 名称必须稳定，branch protection 只能引用这些稳定名称。
- BR4：PR metadata 规则由 `harness-repo` 的脚本定义，各仓复用，不复制实现。
- BR5：delivery readiness 通过 `janus delivery verify` 读取 Harness requirement front matter 和 peer repo 状态。
- BR6：runner 镜像必须使用集群可拉取的镜像仓库和 `imagePullSecrets`。
- BR7：Webhook endpoint 必须使用公开 HTTPS 域名，GitHub delivery 成功后才视为触发链路成立。
- BR8：临时 trigger commit 必须在交付前清理，最终 commit subject 使用纯 Conventional Commits。

## Acceptance Criteria

- AC1：`gitops-repo` 包含 repo gate WorkflowTemplate、EventSource、Sensor、runner image 和 `api.fuzzytails.fun` webhook ingress。
- AC2：`harness-repo` 删除 `.github/workflows/branch-coherence.yml`、`harness-gates.yml` 和 `pr-metadata.yml`。
- AC3：`business-repo` 删除 `.github/workflows/branch-coherence.yml`、`contract-dependency-scan.yml`、`fides-ci.yml` 和 `fides-bff-ci.yml`。
- AC4：`idl-repo` 删除 `.github/workflows/branch-coherence.yml`、`publish-go-idl.yml`、`publish-java-idl.yml`、`sync-go-idl.yml` 和 `sync-java-idl.yml`。
- AC5：`harness-repo` master branch protection 要求 `spark/harness-gates`、`spark/harness-delivery-readiness` 和 `spark/pr-metadata`。
- AC6：`business-repo` master branch protection 要求 `spark/fides-ci`、`spark/fides-bff-ci`、`spark/contract-dependency-scan`、`spark/business-delivery-readiness` 和 `spark/pr-metadata`。
- AC7：`idl-repo` master branch protection 要求 `spark/idl-contract-gate`、`spark/idl-delivery-readiness` 和 `spark/pr-metadata`。
- AC8：runner 镜像在 `vincent-k3s` 上 smoke 成功，并输出 Janus、Go、Buf、Java、Maven、jq 和 Python 版本。
- AC9：真实 PR 更新能触发 GitHub webhook、Argo workflow 和 GitHub commit status。
- AC10：三仓 PR metadata 通过模板章节和 Conventional Commits 检查。
- AC11：三仓 delivery readiness 能识别同一 `related_branch -> master` open PR 作为 release-bound PR 阶段 peer 证据。
- AC12：GitHub Actions workflow 删除后，PR 合并仍可被 Argo status 和 branch protection 完整保护。

## Open Questions

| Question | Owner | Deadline | Status |
|---|---|---|---|
| 是否将 GitHub PAT 替换为 GitHub App token | Harness Team | 后续安全票 | Deferred |
| 是否将 runner 镜像发布流程进一步接入镜像扫描 | Harness Team | 后续镜像治理票 | Deferred |

## Notes

- JIRA Epic：LEN-54。
- 计划子票：LEN-55 至 LEN-76。
- 当前 Docker 仓库使用本机已登录的 `registry.cn-shenzhen.aliyuncs.com/love-is-pain` 命名空间。
