---
requirement_id: "LEN-128"
owner: "core"
status: "approved"
created_at: "2026-06-27"
related_branch: "feature/LEN-128-applicant-api-config-precedence"
target_branch: "master"
release_branch: "master"
contract_gate_mode: "auto"
affected_repositories:
  - harness-repo
  - business-repo
  - gitops-repo
approved_by: "forest"
approved_at: "2026-06-27T18:30:50+08:00"
decision: "用户授权 Agent 批准 LEN-128 Requirement Brief、requirement.md 与 impact-analysis.md，并直接进入执行。"
---

# applicant-api 多配置来源与覆盖优先级

## Background

`applicant-api` 已经接入真实 PostgreSQL、Redis、Consul 和 Kubernetes 部署配置，但当前配置模型仍混合使用短环境变量别名和 profile 文件默认值。

这条能力不是什么：它不是新增 `applicant-api` 的业务接口，也不是修改 OTP、会话或申请人身份规则。

它是什么：它统一 `applicant-api` 的运行时配置来源，让默认配置、中心配置和环境覆盖之间有可预测、可测试的优先级。

## Goals

- 定义并实现稳定的配置来源优先级：默认配置低于中心配置，中心配置低于环境覆盖。
- 让本地开发、STA 和生产环境使用同一套 Spring Boot canonical property 命名模型。
- 明确中心配置只保存可共享的非密运行配置，secret 仍通过本地私有配置或平台 Secret 注入。
- 在 STA、生产或类生产环境缺少关键配置时 fail fast，并输出不包含敏感值的明确错误。
- 补充本地示例配置、README 和测试，说明 canonical env 命名规则和覆盖行为。
- 按需调整 `applicant-api` GitOps ConfigMap / Secret 注入方式，使部署清单与配置模型一致。

## Non-Goals

- 不修改 protobuf、generated contracts 或 IDL 发布流程。
- 不新增或修改 `applicant-api` 业务行为、OTP 规则、会话规则或申请人身份规则。
- 不支持运行时热更新；中心配置只在启动期参与配置装配。
- 不把真实 secret 写入 Git、Jira、Harness 文档或 Consul 示例。
- 不为 `APPLICANT_DB_URL` 等短变量名提供长期兼容别名；如需迁移兼容，应单独批准范围。

## User / Business Scenarios

### Scenario 1: 无外部覆盖时使用本地默认配置

Given: `applicant-api` 没有加载中心配置，也没有 `.env` 或 K8s 环境变量覆盖。

When: 开发人员在本地启动服务。

Then: 服务使用 `application.yml` 中的默认配置，并能从 README 看出哪些默认值仅适用于本地开发。

### Scenario 2: 中心配置覆盖默认配置

Given: Consul 中存在 `applicant-api` 的 YAML 配置。

When: 服务启动并加载中心配置。

Then: Consul 配置覆盖 `application.yml` 默认值。

### Scenario 3: 环境覆盖优先于中心配置

Given: 同一配置项同时存在于 Consul 和 `.env` 或 K8s 环境变量。

When: 服务启动。

Then: 环境变量值覆盖 Consul 值。

### Scenario 4: 开发人员使用 canonical env 命名覆盖配置

Given: 开发人员查看本地示例配置。

When: 开发人员按示例创建本地私有配置。

Then: 可以使用 Spring Boot canonical property 对应的 relaxed binding 环境变量覆盖 `applicant-api` 配置，且不需要维护字段级别名表。

### Scenario 5: 类生产环境缺少关键配置时启动失败

Given: STA 或生产环境缺少关键 secret 或连接配置。

When: 服务启动。

Then: 启动失败，并给出不包含敏感值的明确错误。

### Scenario 6: 合并前验证配置和部署清单

Given: 运行部署配置渲染和 `applicant-api` 测试。

When: 执行合并前验证。

Then: 配置优先级、Secret 注入和 GitOps 清单均通过验证范围。

## Business Rules

- BR1: `applicant-api` 必须有明确的配置来源优先级：默认值低于中心配置，中心配置低于环境覆盖。
- BR2: 本地开发、STA 和生产环境应使用同一套配置命名模型，避免每个字段维护一张人工别名映射表。
- BR3: 中心配置只保存可共享的非密运行配置；密钥、密码和 token 仍由本地私有配置或平台 Secret 注入。
- BR4: 环境覆盖应使用 Spring Boot canonical property 对应的 relaxed binding 命名规则，避免 `APPLICANT_DB_URL` 这类短别名成为新的隐式契约。
- BR5: 生产或类生产环境缺少关键配置时必须启动失败，不能静默回退到不安全默认值。
- BR6: 配置加载、校验、日志和文档不得暴露真实 secret。

## Acceptance Criteria

- AC1: 无外部配置覆盖时，`applicant-api` 使用 `application.yml` 默认配置，README 明确本地开发默认值边界。
- AC2: Consul 中存在 `applicant-api` YAML 配置时，服务启动期加载中心配置，并使中心配置覆盖默认配置。
- AC3: 同一配置项同时存在于 Consul 和 `.env` / K8s 环境变量时，环境变量值覆盖 Consul 值。
- AC4: 本地示例配置使用 canonical env 命名，开发人员不需要字段级短别名表即可覆盖配置。
- AC5: STA 或生产环境缺少关键 secret 或连接配置时，服务 fail fast，错误信息不包含敏感值。
- AC6: 合并前验证覆盖 `applicant-api` 测试、配置优先级测试、Secret 注入检查和 GitOps 清单渲染。

## Open Questions

| Question | Owner | Deadline | Status |
|---|---|---|---|
| 中心配置实现采用 Spring Cloud Consul Config 还是轻量启动期 Consul YAML loader？ | core | 2026-06-27 | resolved: 优先采用 Spring Cloud Consul Config，除非依赖或启动顺序验证失败 |
| 是否需要短期兼容旧 `APPLICANT_*` 变量名？ | core | 2026-06-27 | resolved: 默认不兼容 |

## Notes

- 用户已授权 Agent 直接推进并批准所有文档；Harness 文档仍保持 draft 元数据，正式审批记录通过 Janus 命令生成。
- 本需求只统一运行时配置模型，不改变业务契约和业务行为。
