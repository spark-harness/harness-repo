---
requirement_id: "LEN-128"
analyst: "Codex"
status: "approved"
updated_at: "2026-06-27"
approved_by: "forest"
approved_at: "2026-06-27T18:32:44+08:00"
decision: "用户授权 Agent 批准 LEN-128 服务仓库检查并直接进入实现。"
idl_impact: "no"
idl_impact_reason: "本需求只调整 applicant-api 运行时配置来源、配置校验、文档和 GitOps 注入方式，不修改 protobuf IDL、HTTP 外部契约或 generated contracts。"
---

# Impact Analysis

## Summary

LEN-128 影响 `applicant-api` 的运行时配置装配、配置校验、本地配置文档和 Kubernetes 配置注入，不影响业务接口或 protobuf 契约。

## Affected Domains

- 申请人域：`applicant-api` 运行时配置和启动校验。
- 运行维护：STA / 生产环境配置来源、Secret 注入和 GitOps 清单渲染。

## Affected Services

| Service | Repo | Reason | Protobuf Required |
|---|---|---|---|
| applicant-api | business-repo | 调整 Spring Boot 配置加载、配置属性命名、fail-fast 校验、测试和 README | yes, existing only |
| applicant-api deployment | gitops-repo | 调整 ConfigMap / Secret 环境变量命名和中心配置注入方式 | no |
| Harness LEN-128 lifecycle | harness-repo | 保存需求、影响分析、设计、任务、门禁和证据 | no |

## Upstream / Downstream Consumers

- Upstream consumer: `fides-bff` 仍通过现有服务发现和 gRPC 契约访问 `applicant-api`，不需要契约修改。
- Downstream dependencies: PostgreSQL、Redis、Consul、OpenTelemetry endpoint 和 Kubernetes Secret 注入路径会被配置模型覆盖。
- Human consumers: 本地开发人员、STA 运维人员和生产部署维护人员需要按 canonical env 命名提供覆盖配置。

## API / Contract Impact

- Does this change involve protobuf IDL or external contracts: no.
- Contract repo: `idl-repo` 不需要修改。
- Proto files: `vesta/lendora/applicant/v1` 仅作为现有契约存在，不在本需求中修改。
- Buf module: `local/lendora-applicant` 不需要变更。
- Buf config version: v2.
- Required buf checks: 不需要新增 Buf 检查；合并证据可声明 IDL 未变更。
- Breaking baseline: 不适用。
- Compatibility risk: 外部业务契约无兼容性风险；运行时配置变量名会从短别名切换到 canonical env 命名，部署清单和 README 必须同步。

## Data Impact

- Database schema: 不修改 schema，不新增 migration。
- Data migration: 不需要。
- Backfill: 不需要。
- Cache: Redis 数据结构和 key 规则不变；仅 Redis host、port、password 等连接配置来源变化。
- Runtime storage: PostgreSQL、Redis、Consul 的连接参数将通过默认配置、中心配置和环境覆盖共同装配。

## Config / Permission / Observability Impact

- Config:
  - 默认配置保存在 `application.yml`，只承载本地开发安全边界内的默认值。
  - 中心配置使用 Consul YAML，只保存非密共享运行配置。
  - `.env` / K8s env 使用 Spring Boot canonical relaxed binding 命名，作为最高优先级覆盖来源。
  - Secret、password、token 和敏感 OTLP header 不进入 Consul 示例或 ConfigMap。
- Permission:
  - 不新增业务权限。
  - Kubernetes Secret 读取仍由现有 Pod 环境变量注入承担。
- Metrics:
  - 不新增业务指标。
  - 现有服务指标的 `service.name=applicant-api` 保持不变。
- Logs:
  - 配置缺失或无效时可输出配置键名和环境，不输出配置值。
  - 不记录 token、password、secret、Authorization 或 OTLP header 内容。
- Tracing:
  - 不改变 tracing 采集模型。
  - OTLP endpoint/header 仍通过配置提供；生产或类生产环境缺失时 fail fast。
- Events:
  - 不新增事件。

## Rollout And Rollback

- Gray release:
  - 先在 LEN-128 分支验证本地测试和 GitOps 渲染。
  - 再在 STA 使用 canonical env / Secret 注入验证启动。
  - 生产沿用同一配置模型，只替换目标环境变量值和 Secret。
- Kill switch:
  - 无运行时热更新或功能开关。
  - 如需快速回退，回滚到上一版 `applicant-api` 镜像和 GitOps 清单。
- Rollback steps:
  - 回滚 `gitops-repo/apps/applicant-api` 的 ConfigMap / Secret 注入变更。
  - 回滚 `business-repo/apps/applicant-api` 配置模型变更或部署上一版镜像。
  - 确认 Consul 中不保留 secret；必要时清理 LEN-128 新增的非密中心配置键。

## Risks

| Risk | Impact | Mitigation | Owner |
|---|---|---|---|
| 短环境变量别名移除后现有清单未同步 | STA 或生产启动失败 | GitOps 清单改为 canonical env 并增加渲染检查 | core |
| Consul 中误放 secret | secret 泄露 | 文档和示例只允许非密配置，Secret 继续通过 K8s Secret 注入 | core |
| 配置优先级测试覆盖不足 | 覆盖顺序回归不易发现 | 增加默认、中心配置、环境覆盖和 fail-fast 测试 | core |
| Spring Cloud Consul Config 引入启动顺序问题 | 服务启动失败或中心配置未加载 | 先以测试证明 property source 顺序；若依赖不可控，回退到启动期 YAML loader 设计 | core |
