---
requirement_id: "LEN-129"
owner: "Codex"
status: "approved"
created_at: "2026-06-27"
related_branch: "feature/LEN-129-fides-bff-startup-config"
target_branch: "master"
release_branch: "master"
contract_gate_mode: "auto"
affected_repositories:
  - harness-repo
  - business-repo
approved_by: "Forest"
approved_at: "2026-06-27T21:05:01+08:00"
decision: "批准 LEN-129 需求与影响分析，允许进入设计阶段。"
---

# [FE+BFF] fides-bff 启动期配置接入 .env 与 Consul

## Background

`fides-bff` 当前以 `configs/config.yaml` 作为本地启动配置入口。Lendora 本地、
STA 和生产环境需要同一套可预测的启动期配置模型，以便运行维护和 BFF 开发人员
可以清楚判断每个配置最终来自本地默认值、进程环境变量还是远程配置。

这条能力不是什么：它不是运行时热更新，不改变 OTP、会话、HTTP 契约或
`fides-bff` 业务行为。

它是什么：它补齐 Go/Kratos BFF 的启动期配置来源，让默认配置、本地环境和远程
Consul 配置之间有明确、可测试、可运维的优先级。

## Goals

- R1：保留 `configs/config.yaml` 作为最低优先级默认配置，现有本地启动路径不被破坏。
- R2：启动时加载本地 `.env`，缺失 `.env` 不报错，且 `.env` 不覆盖已经存在的真实进程环境变量。
- R3：定义无前缀环境变量 allowlist，并把 allowlist 内变量显式映射到 Kratos config path。
- R4：接入 Consul KV YAML 启动期远程配置源，使远程配置按定义优先级覆盖本地默认值和环境映射值。
- R5：Consul bootstrap 所需地址、路径和凭据只来自本地环境或平台 Secret，不从 Consul 自举读取。
- R6：缺少必需配置、Consul bootstrap 错误或远程 YAML 格式错误时启动失败，并给出不包含敏感值的明确错误。
- R7：补充 `.env.example`、Consul KV 路径约定、配置优先级、secret 边界和热更新不支持说明。

## Non-Goals

- 不做运行时热更新，启动型配置变更需要重启生效。
- 不修改 protobuf、generated contracts、OTP 业务逻辑或 HTTP 契约。
- 不把真实 secret 写入 Git、Jira、Harness 文档或 Consul 示例。
- 不无过滤读取全部宿主环境变量并直接合并到 Kratos 配置树。
- 不把 token、密码或其他 secret 放入 Consul 示例或共享 KV 配置。

## User / Business Scenarios

### Scenario 1：仅使用默认配置启动

Given：没有 `.env`、无前缀环境变量或 Consul 配置。

When：`fides-bff` 启动。

Then：服务使用 `configs/config.yaml` 默认值完成配置加载，现有本地启动路径不被破坏。

### Scenario 2：本地 `.env` 覆盖默认值

Given：本地存在 `.env` 文件，且包含 allowlist 内的无前缀配置键。

When：开发人员本地启动 `fides-bff`。

Then：`.env` 被加载为进程环境变量，并按 allowlist 映射覆盖本地默认配置。

### Scenario 3：真实环境变量优先于 `.env`

Given：`.env` 和启动前真实进程环境变量存在同名配置键。

When：`fides-bff` 启动。

Then：真实环境变量优先，`.env` 不覆盖已经存在的值。

### Scenario 4：Consul 远程配置参与合并

Given：Consul KV 中存在 `fides-bff` 的 YAML 配置，且 Consul 配置源已启用。

When：`fides-bff` 启动。

Then：远程 YAML 配置按定义优先级参与合并，最终 Bootstrap 配置符合预期。

### Scenario 5：宿主环境变量噪声被忽略

Given：宿主环境中存在大量无关变量。

When：`fides-bff` 加载配置。

Then：只有 allowlist 中的无前缀变量会进入配置映射，无关变量被忽略。

### Scenario 6：Consul 未启用

Given：Consul 配置源未启用。

When：`fides-bff` 启动。

Then：服务仍可依靠 `config.yaml` 与本地环境配置启动。

### Scenario 7：Consul 错误路径失败

Given：Consul 已启用但不可访问，或远程 YAML 格式无效。

When：`fides-bff` 启动。

Then：启动失败，并输出不包含 secret 的明确错误。

## Business Rules

- BR1：配置合并顺序必须明确、可测试，任一字段冲突时可以解释最终值来自哪个来源。
- BR2：环境变量不采用框架统一前缀方案；服务只接受显式 allowlist 中的无前缀配置键。
- BR3：`.env` 只服务本地开发和调试，不提交真实 secret，不覆盖 shell、CI 或 K8s 已注入的同名变量。
- BR4：Consul KV 只保存可共享的非密运行配置；token、密码和其他 secret 仍由本地私有配置或平台 Secret 注入。
- BR5：Consul 配置 key 必须能被 Kratos 识别格式，远程配置内容应保持 YAML 结构，避免每个字段散落成不可审查的碎片键。
- BR6：启动型配置变更需要重启生效；本需求不承诺运行时热更新。
- BR7：失败日志和错误信息不得包含 secret、token、Authorization header、密码或完整凭据值。

## Acceptance Criteria

- AC1：没有 `.env`、环境变量或 Consul 配置时，`fides-bff` 使用 `configs/config.yaml` 默认值完成配置加载。
- AC2：存在 `.env` 且包含 allowlist 内无前缀配置键时，`.env` 被加载并按映射覆盖本地默认配置。
- AC3：`.env` 和真实进程环境变量存在同名配置键时，真实环境变量优先。
- AC4：Consul KV 中存在 `fides-bff` YAML 配置且启用 Consul 配置源时，远程配置按优先级参与合并。
- AC5：宿主环境存在大量无关变量时，只有 allowlist 中变量会进入配置映射。
- AC6：Consul 未启用时，服务仍可依靠 `config.yaml` 与本地环境配置启动。
- AC7：Consul 已启用但不可访问，或远程 YAML 格式无效时，启动失败且错误信息不包含敏感值。
- AC8：单元测试覆盖 `.env` 加载、无前缀映射、优先级合并、Consul 缺失/错误路径和 secret 不落日志边界。
- AC9：开发人员可以在 `.env.example`、README 或运行说明中找到配置优先级、Consul KV 路径约定、bootstrap 来源、secret 边界和热更新不支持说明。

## Open Questions

| Question | Owner | Deadline | Status |
|---|---|---|---|
| Consul KV 生产路径命名是否采用 `config/lendora/fides-bff/config.yaml` | Platform / BFF | 设计阶段 | Proposed |
| allowlist 第一批字段是否覆盖 `server`、`applicant`、`registry`、`observability` 四组配置 | BFF | 设计阶段 | Proposed |

## Notes

- JIRA：`LEN-129`。
- 已批准的 Requirement Brief 使用 `config/lendora/fides-bff/config.yaml` 作为默认 Consul KV 路径约定。
- 已批准的 Requirement Brief 将第一批 allowlist 范围限定为 `server`、`applicant`、`registry`、`observability` 四组配置。
- 当前项目上下文缺少 `lendora/frontend/fides-bff` 的 `context/project` 入口；本需求以服务矩阵作为服务路径事实源。
