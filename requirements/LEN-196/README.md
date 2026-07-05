---
requirement_id: "LEN-196"
owner: "forest"
status: "draft"
created_at: "2026-07-05"
related_branch: "feature/LEN-196-dev-sta-grpc-http-cleanup"
target_branch: "master"
release_branch: "master"
contract_gate_mode: "auto"
affected_repositories:
  - harness-repo
  - business-repo
  - gitops-repo
---

# LEN-196 dev-1 / sta-1 整体切换并清理内部 HTTP 包袱

## 摘要

验证 dev-1 和 sta-1 的 Lendora 内部业务链路已经整体硬切到 gRPC，并删除最后遗留的内部业务 HTTP controller、NetworkPolicy client HTTP ingress 和 Consul KV bootstrap。

## 范围

- Harness lifecycle: `requirements/LEN-196/`
- Business: `business-repo/apps/quote-api`、`business-repo/apps/origination-api`
- GitOps: `gitops-repo/apps/{quote-api,origination-api,applicant-api,fides-bff}`
- IDL: 不修改。

## 分支

```text
feature/LEN-196-dev-sta-grpc-http-cleanup
```

## 依赖

- `LEN-176` quote-api gRPC 服务端已完成。
- `LEN-180` origination-api gRPC 服务端已完成。
- `LEN-184` origination-api -> quote-api 已硬切 gRPC。
- `LEN-188` fides-bff -> quote-api 已硬切 gRPC。
- `LEN-192` fides-bff -> origination-api 已硬切 gRPC，并已完成 dev-1 / sta-1 smoke。
