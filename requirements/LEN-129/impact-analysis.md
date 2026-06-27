---
requirement_id: "LEN-129"
analyst: "Codex"
status: "approved"
updated_at: "2026-06-27"
approved_by: "Forest"
approved_at: "2026-06-27T21:06:04+08:00"
decision: "批准 LEN-129 服务仓库检查，确认 fides-bff 分支与无 IDL 变更范围。"
idl_impact: "no"
idl_impact_reason: "本需求只修改 fides-bff 启动期配置来源和文档，不修改 protobuf IDL、generated contracts 或 HTTP 契约。"
---

# Impact Analysis

## Summary

LEN-129 影响 `fides-bff` 启动期配置加载、测试和运行说明，不改变业务协议、数据模型或前端交互。

## Affected Domains

- `frontend`：`fides-bff` 属于前端体验模块下的 BFF 服务，启动配置模型影响本地、STA 和生产环境运行方式。
- `runtime configuration`：新增本地 `.env`、allowlist 环境映射和 Consul KV YAML 远程配置源。
- `operations`：运行维护需要可解释的配置优先级、Consul bootstrap 来源和失败策略。

## Affected Services

| Service | Repo | Reason | Protobuf Required |
|---|---|---|---|
| fides-bff | business-repo (`apps/fides-bff`) | 修改启动期配置加载、测试、`.env.example` 和 README | Yes, existing only |
| harness lifecycle | harness-repo (`requirements/LEN-129`) | 记录需求、影响、设计、任务、证据和门禁 | No |

## Upstream / Downstream Consumers

- Upstream operator: 本地开发、STA 和生产部署流程通过环境变量、平台 Secret 或 Consul KV 提供配置。
- Runtime service: `fides-bff` 读取合并后的 Bootstrap 配置。
- Downstream services: `applicant-api` 和 Consul discovery 配置值可能被覆盖，但本需求不改变调用协议。
- Future consumers: 其他 Go/Kratos 服务可参考该配置模型，但本需求只实现 `fides-bff`。

## API / Contract Impact

- Does this change involve protobuf IDL or external contracts: **No**。
- Contract repo: `idl-repo` 不修改。
- Proto files: 无。
- Buf module: 不变。
- Buf config version: v2，不修改。
- Required buf checks: 不适用。
- Breaking baseline: 不适用。
- Compatibility risk: Low。运行时配置值可能改变服务启动结果，但 HTTP / protobuf 契约不变。

## Generated Contract Impact

- Go generated contracts: 不修改、不重新生成。
- Java generated contracts: 不修改。
- TypeScript generated contracts: 不修改。

## Data Impact

- Database schema: 无。
- Data migration: 无。
- Backfill: 无。
- Cache: 无。
- Runtime storage: 无新增持久化。`.env` 只作为本地未跟踪配置文件使用。

## Config / Permission / Observability Impact

- Config:
  - 新增 `.env` 本地加载能力，缺失 `.env` 不失败。
  - 新增无前缀环境变量 allowlist 到 Kratos config path 的显式映射。
  - 新增 Consul KV YAML 启动期远程配置源，默认路径约定为 `config/lendora/fides-bff/config.yaml`。
  - Consul bootstrap 地址、路径、token 或凭据来自本地环境或平台 Secret，不从 Consul 自举读取。
  - 配置优先级为 P0 `configs/config.yaml`，P1 `.env` 注入环境，P2 allowlist 环境映射，P3 Consul KV YAML。
- Permission:
  - 不新增用户权限。
  - 如启用 Consul ACL token，token 必须由平台 Secret 或本地私有环境注入，不提交到仓库或文档示例。
- Metrics:
  - 不要求新增业务指标。
  - 如记录配置加载结果，只能记录来源启用状态和非敏感路径，不记录凭据值。
- Logs:
  - 启动失败日志应说明配置源和错误类型。
  - 禁止记录 token、Authorization header、密码、完整凭据或 `.env` 原始内容。
- Tracing:
  - 无运行时链路变化。
- Events:
  - 无业务事件变化。

## Rollout And Rollback

- Gray release:
  - 本地先验证无 `.env`、`.env`、真实环境变量、Consul 未启用和 Consul 错误路径。
  - STA 启用 Consul 配置源前，先写入非密 YAML 配置并确认平台 Secret 提供 bootstrap 值。
  - 生产启用前复用同一 KV 路径约定和 Secret 注入模型。
- Kill switch:
  - Consul 配置源可通过本地环境或平台 Secret 关闭。
  - 删除或不提供 `.env` 不影响服务使用默认配置启动。
- Rollback steps:
  - 回滚 `business-repo/apps/fides-bff` 配置加载改动。
  - 移除部署环境中的 Consul config enable 变量。
  - 保留 `configs/config.yaml` 默认启动路径作为最低优先级回退。

## Risks

| Risk | Impact | Mitigation | Owner |
|---|---|---|---|
| 无前缀环境变量与宿主变量重名 | 意外覆盖配置 | 只允许显式 allowlist；测试覆盖无关环境变量忽略 | BFF |
| `.env` 覆盖 CI / K8s 已注入变量 | 真实环境配置被本地文件污染 | `.env` 只设置不存在的变量；测试覆盖真实环境优先 | BFF |
| Consul bootstrap 值也放进 Consul | 服务无法自举或泄露 secret | bootstrap 地址、路径和凭据只来自本地环境或平台 Secret | Platform / BFF |
| Consul YAML 格式错误 | 服务启动失败 | 启动失败并输出不含敏感值的明确错误；单元测试覆盖 | BFF |
| 远程配置保存 secret | 敏感信息进入共享 KV | README 和 `.env.example` 明确 Consul 只放非密运行配置 | Platform / BFF |
| 当前项目上下文缺少 fides-bff 服务入口 | Agent 可能按目录猜测路径 | 以服务矩阵 `apps/fides-bff` 作为事实源，并记录上下文缺口 | Harness |

## Context Gaps

- `harness-repo/context/project/` 当前没有真实项目级 Lendora frontend / fides-bff `INDEX.md`。
- 服务矩阵已登记 `fides-bff` 路径为 `{business-repo}/apps/fides-bff`；本需求实施以服务矩阵为准。
