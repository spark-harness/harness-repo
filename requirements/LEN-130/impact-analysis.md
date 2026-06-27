---
requirement_id: "LEN-130"
analyst: "core"
status: "approved"
updated_at: "2026-06-27"
approved_by: "forest"
approved_at: "2026-06-27T19:19:00+08:00"
decision: "用户明确授权：授权你批准所有文档；批准 LEN-130 fides 运行时配置中心和 .env 覆盖的需求、影响分析、设计和任务拆分，范围限定为 fides-web 运行时配置硬切、GitOps 部署配置更新、测试和文档，不涉及 fides-bff API、protobuf/IDL 或 NEXT_PUBLIC 兼容层。"
idl_impact: "no"
idl_impact_reason: "未声明 protobuf IDL 或外部契约影响。"
---

# Impact Analysis

## Summary

本需求把 `fides` 前端运行配置从构建期 `NEXT_PUBLIC_*` 切换到服务端运行时配置，影响 `business-repo/apps/fides-web`、`gitops-repo/apps/fides` 和 Harness 生命周期文件，不影响 protobuf / IDL。

## Affected Domains

- 前端体验。
- 运行时配置。
- GitOps 部署配置。
- 浏览器可观测性初始化。

## Affected Services

| Service | Repo | Reason | Protobuf Required |
|---|---|---|---|
| fides | `business-repo/apps/fides-web` | 前端运行时配置加载、public config 暴露、OTP gateway 和 browser tracing 改造 | No |
| fides GitOps | `gitops-repo/apps/fides` | 移除旧 `NEXT_PUBLIC_*` 部署变量，补充运行时配置源和 Consul 地址 | No |

## API / Contract Impact

- Does this change involve protobuf IDL or external contracts: No
- Contract repo: N/A
- Proto files: N/A
- Buf module: N/A
- Buf config version: v2 unchanged
- Required buf checks: N/A
- Breaking baseline: N/A
- Compatibility risk: 无 protobuf 或外部 API 契约影响；BFF base URL 只是前端运行时配置。

## Data Impact

- Database schema: 无
- Data migration: 无
- Backfill: 无
- Cache: 无
- Runtime storage: Consul KV 保存环境级 runtime config JSON；该配置不得包含真实 secret。

## Config / Permission / Observability Impact

- Config: 新增 `fides` runtime config schema、默认值、Consul JSON 配置源、运行时环境变量或 `.env*` 覆盖；移除旧 `NEXT_PUBLIC_*`。
- Permission: 无用户权限模型变化；Consul 读取权限沿用运行环境配置。
- Metrics: 无新增业务指标要求。
- Logs: 配置校验失败需要输出明确错误类别，但不得输出 secret 或敏感值。
- Tracing: 浏览器 tracing endpoint/header 从 runtime public config 获取；配置为空时关闭导出但保留请求链路可用性。
- Events: 无事件变更。

## Rollout And Rollback

- Gray release: 先在 `lendora-sta` 更新 GitOps 配置并验证运行时 public config，再推广到其他环境。
- Kill switch: OTP adapter 可通过 runtime config 设置为 `disabled` 或 `mock`；browser tracing endpoint 为空即可关闭导出。
- Rollback steps: 回滚 `business-repo` 镜像版本和 `gitops-repo/apps/fides` 部署配置到旧版本；如已写入 Consul KV，可保留但旧镜像不会读取。

## Risks

| Risk | Impact | Mitigation | Owner |
|---|---|---|---|
| Consul 不可用或 key 缺失 | `fides` 启动或 public config 获取失败 | 本地默认值和生产必需字段校验分开；非生产可使用默认值，生产缺必需配置明确失败 | core |
| 非白名单字段泄漏到浏览器 | 公开内部配置或敏感信息 | public config 使用显式白名单映射，测试覆盖未知字段不会暴露 | core |
| 旧 `NEXT_PUBLIC_*` 被部署残留 | 行为继续受构建期变量影响或排障困难 | 启动/校验阶段检测旧变量并失败；GitOps 移除旧变量 | core |
| Browser tracing 配置错误导致页面不可用 | 用户页面请求失败 | 初始化捕获 tracing 错误，配置为空时关闭导出，请求链路继续可用 | core |
| Consul key 路径未最终统一 | GitOps 和应用读取位置漂移 | 采用 `spark/lendora/{env}/fides-web/runtime-config` 作为实现默认，并在文档中记录 | core |
