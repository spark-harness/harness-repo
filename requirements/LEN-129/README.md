---
requirement_id: "LEN-129"
status: "draft"
related_branch: "feature/LEN-129-fides-bff-startup-config"
target_branch: "master"
release_branch: "master"
current_stage: "2"
---

# [FE+BFF] fides-bff 启动期配置接入 .env 与 Consul

## Summary

补齐 `fides-bff` 启动期配置来源：最低优先级使用本地
`configs/config.yaml`，本地 `.env` 只补充未存在的进程环境变量，无前缀环境变量
通过显式 allowlist 映射到配置树，Consul KV YAML 作为远程启动期配置源覆盖本地
默认值和环境映射值。

## Scope

- `harness-repo`：维护 LEN-129 需求、影响分析、设计、任务、证据和门禁。
- `business-repo`：修改 `apps/fides-bff` 启动配置加载、测试、`.env.example`
  和运行说明。

## Non-Goals

- 不做运行时热更新。
- 不修改 protobuf、generated contracts、OTP 业务逻辑或 HTTP 契约。
- 不把真实 secret 写入 Git、Jira、Harness 文档或 Consul 示例。
- 不无过滤读取全部宿主环境变量并直接合并到 Kratos 配置树。
