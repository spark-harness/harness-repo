---
requirement_id: "LEN-135"
owner: "core"
status: "approved"
updated_at: "2026-06-28"
approved_by: "forest"
approved_at: "2026-06-28T06:27:11+08:00"
decision: "用户授权 Agent 批准所有文档；批准 LEN-135 design 更新，auth token mode/TTL 放 ConfigMap，AUTH_TOKEN_SECRET 从 fides-bff-runtime Secret 注入。"
---

# Design

## Requirement Traceability

| Requirement Item | Design Decision | Notes |
|---|---|---|
| BR1, BR2, BR3, AC3, AC7 | D1: 在 fides-bff ConfigMap 中配置 quote/origination Consul discovery | 使用 service name，不硬编码 Pod IP |
| BR4, AC3 | D2: quote/origination HTTP timeout 显式配置为 3s | 与本地默认值一致 |
| BR5 | D3: `base_url` 保持空字符串 | 让 BFF 走 Consul resolver |
| BR6, AC6 | D4: 复用 namespace label + 下游 NetworkPolicy | 不新增不必要 policy |
| BR8, AC5, AC6, AC8 | D5: runtime smoke 只走 BFF 受保护接口 | 不用前端直连 Java 服务替代 |
| BR9, AC6 | D6: smoke 前确认 fides-bff 镜像包含 LEN-133 facade | 旧镜像必须刷新 |
| BR10, AC4, AC8 | D7: `AUTH_TOKEN_SECRET` 通过 runtime Secret 注入 | ConfigMap 只保存 token mode 和 TTL |
| AC9 | D8: Argo CD 缺失时记录 WARN | 不声称 Healthy/Synced |

## Summary

LEN-135 的实现点是 GitOps runtime config。`fides-bff` 已在业务仓支持 quote/origination 配置读取和 Consul resolver，本票只把这些配置部署到 lendora-sta，并证明 BFF 到真实下游链路可用。

## Affected Services

| Service | Change | Reason |
|---|---|---|
| fides-bff | ConfigMap 增加 quote/origination 下游配置 | 让 pricing 和 loan application facade 能发现真实服务 |
| quote-api | 无代码或配置变更 | 被 BFF pricing smoke 调用 |
| origination-api | 无代码或配置变更 | 被 BFF loan application smoke 调用 |

## API / Contract Design

- Protobuf IDL required: no changes.
- Proto files: none.
- Buf module: unchanged.
- Generated outputs: none.
- Breaking check baseline: not applicable.
- Compatibility strategy:
  - 对外 BFF endpoint 已由 LEN-132/LEN-133 定义。
  - 本票不改变请求/响应结构，只改变运行时下游目标。

## Data / Config / Permission

- Data:
  - 不新增 schema。
  - Smoke 会创建 quote 和 application draft 作为证据。
- Config:
  - `quote.consul.address=consul.lendora-sta-consul.svc.cluster.local:8500`
  - `quote.consul.scheme=http`
  - `quote.consul.service_name=quote-api`
  - `quote.http.base_url=""`
  - `quote.http.timeout=3s`
  - `origination.consul.address=consul.lendora-sta-consul.svc.cluster.local:8500`
  - `origination.consul.scheme=http`
  - `origination.consul.service_name=origination-api`
  - `origination.http.base_url=""`
  - `origination.http.timeout=3s`
  - `auth.token_mode=hmac`
  - `auth.access_token_ttl=1h`
  - `AUTH_TOKEN_SECRET` from `fides-bff-runtime/token-secret`
- Permission:
  - `lendora-sta-fides-bff` namespace already has `lendora.io/quote-api-client=true` and `lendora.io/origination-api-client=true`。
  - quote-api/origination-api NetworkPolicy allows those namespace labels.

## Observability

- Logs:
  - 不输出 token、Authorization、OTLP header 或完整申请 payload。
- Metrics:
  - 不新增指标。
- Tracing:
  - Smoke 使用固定 `traceparent` / `tracestate` 验证 BFF 向下游传播。
- Events:
  - 不新增事件。

## Testing Strategy

- GitOps render:
  - `kubectl kustomize apps/fides-bff/overlays/lendora-sta`
  - `kubectl kustomize clusters/lendora-sta`
  - YAML parse for changed manifest.
- Runtime checks:
  - Pod Ready。
  - `/api/v1/health`。
  - Consul health for `fides-bff`、`quote-api`、`origination-api`。
  - BFF pricing quote smoke。
  - BFF loan application create/get/patch smoke。
  - DB evidence for quote/application writes where available.
- CI / gates:
  - Janus gate validate。
  - Janus requirement verify target merge。

## Rollout And Rollback

- Rollout:
  - Merge or apply fides-bff ConfigMap target state.
  - Bootstrap `fides-bff-runtime/token-secret` in lendora-sta.
  - Ensure fides-bff image digest contains LEN-133.
  - Restart fides-bff Deployment.
  - Run runtime smoke.
- Rollback:
  - Revert ConfigMap GitOps commit.
  - Roll back fides-bff overlay digest if image refresh caused regression.
  - Restart fides-bff Deployment.

## Risks

| Risk | Mitigation | Owner |
|---|---|---|
| fides-bff image release workflow in cluster is older than repo | Treat image refresh as runtime prerequisite and record exact workflow/digest evidence | core |
| Consul returns stale service entry | Query `passing=true` and verify endpoint smoke | core |
| ConfigMap drift from manual runtime patch | Reconcile by merging GitOps PR and recording live config hash | core |
| Argo CD unavailable | Record WARN and use kubectl-render/apply evidence only | platform/gitops |
