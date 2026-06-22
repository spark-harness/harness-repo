---
requirement_id: "LEN-44"
status: "draft"
related_branch: "feature/LEN-44-applicant-api-local-runtime"
target_branch: "master"
release_branch: "master"
current_stage: "5.1"
---

# applicant-api 本地真实运行时接入

## Summary

让 `applicant-api` 能在本地通过 PostgreSQL、Redis 和 Consul 组成真实运行时，
并把对应业务仓 PR 接入 delivery-readiness CI，完成 LEN-44 的交付闭环。

## Scope

- `business-repo/services/backend/applicant-api`：本地运行时配置、迁移、健康检查、注册、脚本和测试。
- `harness-repo/requirements/LEN-44`：提供 CI 可读取的需求事实源。

## Non-Goals

- 不修改 protobuf IDL。
- 不发布新的 generated contract。
- 不在本票处理 Redis 幂等原子性、Consul 生命周期和架构分层等技术债；这些后续单独开 Ticket。
