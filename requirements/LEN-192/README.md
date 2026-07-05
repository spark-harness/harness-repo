---
requirement_id: "LEN-192"
owner: "forest"
status: "draft"
created_at: "2026-07-05"
related_branch: "feature/LEN-192-fides-bff-origination-grpc-hard-cut"
target_branch: "master"
release_branch: "master"
contract_gate_mode: "auto"
affected_repositories:
  - harness-repo
  - business-repo
  - gitops-repo
---

# LEN-192 fides-bff 调 origination-api 全量硬切 gRPC

## 摘要

`fides-bff` 到 `origination-api` 的内部申请链路从 HTTP 加部分 gRPC 统一硬切为 gRPC。

## 范围

- Harness lifecycle: `requirements/LEN-192/`
- Business: `business-repo/apps/fides-bff`
- GitOps: `gitops-repo/apps/fides-bff`
- IDL: 不修改，只消费 `LEN-180` 已发布的 origination Go SDK。

## 分支

```text
feature/LEN-192-fides-bff-origination-grpc-hard-cut
```

## 依赖

- `LEN-180` 已提供 `origination-api` gRPC 服务端和 Go SDK。
- `LEN-184` 完成后，origination 内部 quote 链路已切到 gRPC。
- `LEN-188` 完成后，BFF 到 quote 链路已切到 gRPC。
