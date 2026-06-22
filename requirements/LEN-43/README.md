---
requirement_id: "LEN-43"
status: "draft"
related_branch: "feature/LEN-43-fides-bff-mobile-verification"
target_branch: "master"
release_branch: "master"
current_stage: "2"
---

# [FE+BFF] 手机验证端到端接入 fides-bff

## Summary

将 Lendora 手机验证从前端 mock / 可配置 REST adapter 推进到真实
`fides-bff` 接入：前端调用 BFF，BFF 通过带 HTTP 注解的 BFF-facing
protobuf 暴露 OTP RPC，并经 Consul 发现调用 `applicant-api`。

## Scope

- `harness-repo`：维护 LEN-43 需求、影响分析、设计、任务、证据和门禁。
- `idl-repo`：新增 `vesta/lendora/fides-bff/v1/auth.proto`，RPC 带
  `google.api.http` 注解。
- `business-repo`：实现 `fides-bff` 手机验证 REST / gRPC 映射、Consul
  applicant client、错误映射和 trace metadata；更新 `fides` 真实接入与测试。

## Non-Goals

- 不实现 `applicant-api` OTP 业务规则。
- 不修改 PostgreSQL / Redis 持久化细节。
- 不接真实短信供应商。
- 不把 `fides-bff` 合入 master 时依赖临时本地生成物。
