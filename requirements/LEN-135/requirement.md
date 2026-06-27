---
requirement_id: "LEN-135"
owner: "core"
status: "approved"
created_at: "2026-06-28"
related_branch: "feature/LEN-135-fides-bff-downstream-config"
target_branch: "master"
release_branch: "master"
contract_gate_mode: "auto"
affected_repositories:
  - harness-repo
  - gitops-repo
approved_by: "forest"
approved_at: "2026-06-28T06:27:11+08:00"
decision: "用户授权 Agent 批准所有文档；批准 LEN-135 requirement 和 impact-analysis 更新，增加 fides-bff runtime token Secret 引用以支持受保护接口 smoke，Secret 值不入仓。"
---

# fides-bff quote/origination 下游配置

## Background

LEN-132 已交付 `fides-bff` pricing facade，LEN-133 已交付 loan application create/get/patch facade。当前 lendora-sta 的 `fides-bff` runtime ConfigMap 只配置 applicant 下游和自注册，缺少 quote/origination 下游发现配置，导致真实运行时不能稳定调用 `quote-api` 和 `origination-api`。

这条需求不是什么：它不是新增 BFF facade，不是改 quote/origination 业务逻辑，不是前端贷款请求屏接入。

它是什么：它把 `fides-bff` 在 lendora-sta 的 quote/origination 下游地址、端口、服务发现和超时写入 GitOps 目标状态，并用运行时 smoke 证明 BFF 能通过受保护接口访问真实下游。

## Goals

- 在 `gitops-repo` 配置 `fides-bff` 的 quote-api 下游 Consul service name、Consul address 和 HTTP timeout。
- 在 `gitops-repo` 配置 `fides-bff` 的 origination-api 下游 Consul service name、Consul address 和 HTTP timeout。
- 在 `gitops-repo` 配置 `fides-bff` 的 HMAC token mode、TTL 和 runtime Secret 引用，使受保护接口可被真实 smoke。
- 保持 `base_url` 为空，使 BFF 通过 Consul 健康服务发现下游，而不是硬编码静态地址。
- 验证 fides-bff namespace 具备访问 quote-api/origination-api 的 NetworkPolicy namespace label。
- 部署后验证 `fides-bff /api/v1/health`、pricing quote 和 loan application create/get/patch smoke。
- 验证身份和 trace 从 BFF 传播到下游，并且请求不依赖前端直连 Java 服务。
- 记录当前集群 Argo CD 缺口，不伪造 Healthy/Synced。

## Non-Goals

- 不修改 `fides-bff` Go 业务代码。
- 不修改 protobuf IDL 或 generated contracts。
- 不修改 `quote-api` 或 `origination-api` 业务逻辑。
- 不修改 frontend `fides-web`。
- 不新增公网入口。
- 不提交真实 Secret、token、OTLP header 或敏感配置；只提交 Secret 引用。
- 不修复 business image release 模板漂移；只在 evidence 中记录是否需要运行时镜像刷新。

## User / Business Scenarios

### Scenario 1: BFF pricing facade 可访问真实 quote-api

Given: lendora-sta 已部署包含 pricing facade 的 `fides-bff` 镜像，且 ConfigMap 配置 quote-api Consul discovery。

When: 已认证请求调用 `POST /api/v1/pricing/quotes`。

Then: BFF 通过 Consul 发现 quote-api，向下游传播 applicant principal 和 trace headers，并返回包含 `quoteId` 的试算结果。

### Scenario 2: BFF origination facade 可访问真实 origination-api

Given: lendora-sta 已部署包含 origination facade 的 `fides-bff` 镜像，且 ConfigMap 配置 origination-api Consul discovery。

When: 已认证请求调用 loan application create/get/patch。

Then: BFF 通过 Consul 发现 origination-api，向下游传播 applicant principal、trace headers 和 Idempotency-Key，并返回草稿结果。

### Scenario 3: 下游不可发现时 BFF 明确失败

Given: Consul 没有 passing 的 quote-api 或 origination-api。

When: BFF 调用对应 facade。

Then: BFF 返回稳定的下游不可用错误，不暴露内部异常或连接细节。

## Business Rules

- BR1: `fides-bff` 必须通过 Consul `passing=true` 健康服务发现 quote-api 和 origination-api。
- BR2: quote-api service name 必须为 `quote-api`，origination-api service name 必须为 `origination-api`。
- BR3: Consul address 必须使用集群内 service DNS `consul.lendora-sta-consul.svc.cluster.local:8500`。
- BR4: quote/origination HTTP timeout 必须显式配置，STA 默认 3s。
- BR5: `base_url` 必须保持空值，除非后续需求明确切换到静态地址。
- BR6: `fides-bff` namespace 必须具备 `lendora.io/quote-api-client=true` 和 `lendora.io/origination-api-client=true`。
- BR7: GitOps manifest 不得提交真实 secret、token 或敏感 header。
- BR8: runtime smoke 必须经过 BFF 受保护接口，不能用前端直连 Java 服务替代。
- BR9: 如果当前运行镜像不包含 LEN-133 facade，必须先刷新 fides-bff 镜像再执行 origination smoke。
- BR10: `fides-bff` token secret 必须来自 Kubernetes Secret，不得写入 ConfigMap 或仓库。

## Acceptance Criteria

- AC1: `kubectl kustomize apps/fides-bff/overlays/lendora-sta` 通过，并渲染出 quote/origination 下游配置。
- AC2: `kubectl kustomize clusters/lendora-sta` 通过。
- AC3: `fides-bff-config` runtime ConfigMap 包含 quote/origination Consul service name、Consul address、3s timeout、auth token mode 和 TTL。
- AC4: `fides-bff` Pod Ready，`/api/v1/health` 可访问。
- AC5: BFF pricing smoke 返回 `quoteId`，并由 quote-api 持久化。
- AC6: BFF loan application create/get/patch smoke 成功，Continue 保存路径使用 BFF facade。
- AC7: Consul 中 quote-api、origination-api、fides-bff 均可发现。
- AC8: traceparent、tracestate、x-applicant-id 和 Idempotency-Key 传播结果有证据。
- AC9: 若 vincent-k3s 缺少 Argo CD，evidence 记录 WARN，不声称 Healthy/Synced。

## Open Questions

| Question | Owner | Deadline | Status |
|---|---|---|---|
| 当前 fides-bff 镜像是否已包含 LEN-133 origination facade？ | core | 2026-06-28 | resolved: 初始扫描显示运行镜像仍是旧 digest；本票 smoke 前必须刷新镜像或记录阻塞 |
| 下游连接使用静态 Service URL 还是 Consul discovery？ | core | 2026-06-28 | resolved: 本票使用 Consul discovery，`base_url` 保持空 |
| 是否需要新增 GitOps NetworkPolicy？ | core | 2026-06-28 | resolved: 现有 namespace labels 和下游 NetworkPolicy 已允许 fides-bff 访问 quote/origination |
| 受保护接口 smoke 的 token secret 从哪里来？ | core | 2026-06-28 | resolved: GitOps 只引用 `fides-bff-runtime/token-secret`，STA Secret 由 runtime bootstrap 创建 |

## Notes

- LEN-135 依赖 LEN-132、LEN-133、LEN-131、LEN-134 已合并。
- 当前集群为 vincent-k3s。
- Argo CD 当前不在 vincent-k3s 中；相关验收只能记录环境 WARN。
