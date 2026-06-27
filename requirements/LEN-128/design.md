---
requirement_id: "LEN-128"
owner: "core"
status: "approved"
updated_at: "2026-06-27"
approved_by: "forest"
approved_at: "2026-06-27T18:31:59+08:00"
decision: "用户授权 Agent 批准 LEN-128 设计文档并直接进入任务拆分和实现。"
---

# Design

## Requirement Traceability

| Requirement Item | Design Decision | Notes |
|---|---|---|
| BR1, AC1, AC2, AC3 | 使用 Spring Boot ConfigData 和 Spring Cloud Consul Config 建立默认配置、中心配置、环境变量覆盖链路 | 依赖 Spring 原生 property source 顺序，避免自定义优先级规则 |
| BR2, BR4, AC4 | 所有环境覆盖改用 canonical property 对应的 relaxed binding 环境变量 | 不维护 `APPLICANT_DB_URL` 这类字段级短别名表 |
| BR3, BR6 | Consul YAML 和 ConfigMap 只保存非密配置；Secret 继续由本地私有文件或 K8s Secret 注入 | 文档和日志只记录配置键名，不记录值 |
| BR5, AC5 | 统一启动期配置校验，STA / prod 缺关键连接、secret 或 OTLP 配置时 fail fast | 错误信息说明缺失键名和 profile，不包含敏感值 |
| AC6 | 增加配置优先级测试、fail-fast 测试和 GitOps 渲染检查 | 合并前证据覆盖业务仓和 GitOps 仓 |

## Summary

LEN-128 在 `applicant-api` 中建立一套 Spring Boot 原生配置模型。

它不是什么：不是为每个字段写一套自定义别名和覆盖规则，也不是引入运行时热更新。

它是什么：让服务启动时按可预测顺序装配配置：classpath 默认配置作为底座，Consul YAML 提供共享非密中心配置，`.env` 或 K8s 环境变量使用 canonical relaxed binding 作为最高优先级覆盖。

## Affected Services

| Service | Change | Reason |
|---|---|---|
| applicant-api | 增加 Consul Config 依赖、配置导入、配置校验测试和 README 示例 | 满足多配置来源和覆盖优先级 |
| applicant-api deployment | 更新 ConfigMap / Secret env 命名和 Consul 中心配置注入方式 | 让 GitOps 清单与 canonical env 模型一致 |

## API / Contract Design

- Protobuf IDL required: no.
- Proto files: no changes.
- Buf module: no changes.
- Buf config version: v2.
- Generated outputs: no changes.
- Breaking check baseline: not applicable.
- Compatibility strategy: 业务契约不变；配置变量名按 LEN-128 明确不兼容旧短别名，部署和文档同步迁移。

## Application Design

### 配置来源

`application.yml` 保存本地开发默认值和通用配置结构。默认值只能用于本地开发或安全的测试场景。

Consul Config 使用 YAML 格式保存共享非密运行配置。服务启动期通过 Spring ConfigData 导入 Consul 配置，使中心配置覆盖 classpath 默认值。

`.env` 或 K8s 环境变量使用 Spring Boot relaxed binding 命名。例如：

```text
SPARK_APPLICANT_AUTH_JDBC_URL
SPARK_APPLICANT_AUTH_JDBC_USERNAME
SPARK_APPLICANT_AUTH_TOKEN_SECRET
SPRING_DATA_REDIS_HOST
SPRING_DATA_REDIS_PASSWORD
```

环境变量作为最高优先级覆盖来源，覆盖 Consul 和默认配置。

### 启动期校验

现有 `ApplicantAuthConfiguration` 的 runtime policy 校验继续作为启动期 fail-fast 入口。

设计要求：

- local/dev 可以使用显式本地默认值。
- sta/prod 必须提供 JDBC URL、Redis host、Consul URL、Consul service address、token secret、Redis password、OTLP endpoint 和 OTLP header。
- 错误信息只输出缺失配置键名和 profile，不输出配置值。

### `.env` 支持

本地 `.env` 只作为开发体验入口，文件本身不提交。仓库提交 `.env.example`，说明 canonical env 命名、用途和占位值。

## Data / Config / Permission

- Data model: 不修改数据库表、migration 或 Redis key 结构。
- Config:
  - `application.yml`：保留本地开发默认值，移除短 env 别名占位。
  - `application-sta.yml` / `application-prod.yml`：使用 canonical property 占位或交给 ConfigData/env 注入。
  - Consul YAML：只保存非密共享运行配置。
  - K8s ConfigMap：只保存非密 canonical env。
  - K8s Secret env：保存 password、token secret 和敏感 OTLP header。
- Permission: 不新增业务权限；K8s Secret 访问沿用 Pod 环境变量注入。

## Observability

- Logs:
  - 配置缺失错误不得包含 secret 值。
  - README 明确排障时查看配置键名和 profile，不打印完整环境变量。
- Metrics:
  - 不新增业务指标。
  - 保持 `service.name=applicant-api`。
- Tracing:
  - OTLP 配置继续由 OpenTelemetry Spring Boot instrumentation 读取。
  - sta/prod 缺 OTLP endpoint/header 时 fail fast。
- Events:
  - 不新增事件。

## Testing Strategy

- 增加配置绑定测试，证明默认配置可绑定到 `ApplicantAuthProperties`。
- 增加 Consul property source 覆盖测试，证明中心配置覆盖默认值。
- 增加环境变量覆盖测试，证明 canonical env 覆盖中心配置。
- 扩展 fail-fast 测试，覆盖 sta/prod 缺 secret、Redis password、Consul URL、service address 和 OTLP 配置。
- 运行 `mvn test` 验证 `applicant-api`。
- 使用 `kustomize build` 或等价命令验证 GitOps applicant-api 清单渲染。

## Rollout And Rollback

- Gray release:
  - 先在本地运行配置优先级测试和服务测试。
  - 再渲染 `lendora-sta` applicant-api 清单并确认 env / Secret 注入。
  - STA 验证启动后再推广到生产 overlay。
- Kill switch:
  - 无运行时开关。
  - 通过回滚 GitOps 清单和镜像版本恢复旧配置模型。
- Rollback:
  - 回滚 `business-repo/apps/applicant-api` 配置变更。
  - 回滚 `gitops-repo/apps/applicant-api` ConfigMap / Secret env 命名变更。
  - 清理 Consul 中 LEN-128 新增的非密中心配置键。

## Risks

| Risk | Mitigation | Owner |
|---|---|---|
| Spring Cloud Consul Config 依赖引入后测试或启动顺序不符合预期 | 用配置优先级测试证明；如失败，退回轻量启动期 YAML loader 方案 | core |
| 旧短别名环境变量仍在部署清单中残留 | 使用 `rg APPLICANT_` 和 GitOps 渲染检查确认迁移完成 | core |
| 文档示例误导用户提交 secret | `.env.example` 只使用占位值，并明确 `.env` 不提交 | core |
| fail-fast 错误暴露敏感值 | 测试断言错误信息不包含 secret 内容 | core |
