---
requirement_id: "LEN-133"
owner: "core"
status: "draft"
created_at: "2026-06-28"
related_branch: "feature/LEN-133-fides-bff-origination-facade"
target_branch: "master"
release_branch: "master"
contract_gate_mode: "auto"
affected_repositories:
  - harness-repo
  - business-repo
---

# fides-bff origination facade

本需求让前端通过 `fides-bff` 创建、读取、静默保存 loan application draft。

它不是 `origination-api` 的业务实现，不是 GitOps 下游配置，也不是前端接入。

它是什么：在 `fides-bff` 暴露受保护的 loan application facade，由 BFF 读取 LEN-22 principal，调用 `origination-api`，传播身份和 tracing，并统一错误信封。

## 范围

- `business-repo/apps/fides-bff`
- `harness-repo/requirements/LEN-133`

## 非范围

- 不修改 `origination-api` 业务规则和 DB schema。
- 不修改 protobuf IDL 或 generated contracts。
- 不修改 GitOps runtime 下游地址；LEN-135 负责。
- 不修改前端第二页；LEN-11 负责。

