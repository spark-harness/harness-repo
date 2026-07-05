---
requirement_id: "LEN-212"
owner: "forest"
status: "approved"
created_at: "2026-07-06"
related_branch: "feature/LEN-212-fides-bff-kratos-v3"
target_branch: "master"
release_branch: "master"
contract_gate_mode: "auto"
affected_repositories:
  - harness-repo
  - idl-repo
  - business-repo
approved_by: "forest"
approved_at: "2026-07-06T00:16:30+08:00"
decision: "用户授权 Agent 批准中间文件；批准 LEN-212 requirement 与 impact-analysis，范围为 fides-bff、bffkit 和 Kratos v3 Go 契约生成链路升级，不新增业务能力。"
---

# fides-bff 升级到 Kratos v3

## Background

`fides-bff` 当前依赖 Kratos v2。Jira 要求升级到 Kratos v3，使 BFF 继续获得受支持的框架能力，同时保持手机验证、报价、贷款申请和身份资料流程不退化。

它不是什么：本需求不是新增业务流程，不调整前端页面，不改变下游服务业务规则，也不重设计配置中心。

它是什么：本需求是框架运行时升级，覆盖 `fides-bff` 进程、共享 BFF 横切包和 BFF Go 契约生成链路。

## Goals

- R1：`fides-bff` 运行时、HTTP server、配置加载、健康检查和 Consul 注册/发现升级到 Kratos v3。
- R2：`packages/go/bffkit` 的错误信封、CORS、幂等、trace、请求标识和指标过滤器继续提供同等外部行为。
- R3：BFF Go 契约生成链路产出 Kratos v3 HTTP binding，`fides-bff` 消费正式发布版本，不使用本地替换或未发布生成物作为交付结果。
- R4：手机验证、报价、贷款申请和身份资料相关 API 的可见行为保持一致。
- R5：跨服务 trace context、`X-Trace-Id`、`X-Correlation-Id` 和稳定错误分类继续可用。
- R6：本地测试、静态检查、构建和 smoke 验证通过；合并后完成 dev 与 sta 验证并保留回滚路径。

## Non-Goals

- 不新增贷款业务能力、报价规则、OTP 规则或身份资料业务字段。
- 不调整 fides-web 页面流程或用户交互。
- 不改变 applicant-api、quote-api、origination-api 的业务语义。
- 不重设计配置中心、Secret 管理或发布平台。
- 不提交真实 secret、token、OTLP endpoint 私密 header 或本地 `.env` 内容。

## User / Business Scenarios

### Scenario 1：现有申请流程保持可用

Given：用户在升级前可以执行手机验证、报价、贷款申请或身份资料相关操作。

When：`fides-bff` 升级到 Kratos v3 后处理同类请求。

Then：页面可见结果与升级前一致，不出现框架升级引入的新失败。

### Scenario 2：BFF 运行健康保持可观测

Given：`fides-bff` 使用升级后的运行时部署。

When：执行健康检查和前端到 BFF 的 smoke 验证。

Then：服务启动正常、健康检查通过，前端可以继续访问 BFF 能力。

### Scenario 3：跨服务 trace 继续串联

Given：一次请求经过 fides、fides-bff 和至少一个下游服务。

When：在可观测平台检索该请求。

Then：能够看到 fides-bff 服务标识、trace 关联、请求标识和稳定错误分类。

### Scenario 4：契约消费不依赖本地生成物

Given：BFF Go 契约生成链路已升级。

When：执行合并前质量门禁。

Then：`fides-bff`、`bffkit` 和已消费的 BFF Go 契约不再依赖 Kratos v2，且依赖来自正式版本。

## Business Rules

- BR1：升级不得改变用户可见成功路径、错误信封、HTTP status 与稳定错误码映射。
- BR2：健康检查、CORS、幂等、trace header、请求标识、Consul 注册/发现和运行时配置必须保持兼容。
- BR3：生成契约必须通过正式 Go module 版本消费；release-bound 变更不得使用 local `replace`、pseudo-version、RC 或未发布生成物。
- BR4：跨服务同步调用继续使用 W3C TraceContext 传播，日志和响应 header 继续保留可检索请求标识。
- BR5：dev 和 sta 验证失败时，必须能回滚到上一版稳定镜像，不要求前端或下游服务同步改造才能恢复。
- BR6：本需求只改框架和契约生成链路，不借机重构业务层或新增业务行为。

## Acceptance Criteria

| AC | Given | When | Then |
|---|---|---|---|
| AC1 | fides-bff 当前申请流程可用 | 用户执行手机验证、报价、贷款申请或身份资料相关操作 | 页面可见结果与升级前一致，不出现框架升级引入的新失败 |
| AC2 | fides-bff 使用 Kratos v3 运行时 | 执行本地启动、健康检查和 BFF smoke 验证 | 服务启动正常、健康检查通过，核心 BFF 能力可访问 |
| AC3 | 请求经过 fides-bff 和至少一个下游服务 | 检索 trace、日志或 smoke 输出 | fides-bff 服务标识、trace 关联、请求标识和稳定错误分类保持可见 |
| AC4 | 契约生成物和 Go 依赖已刷新 | 执行质量门禁 | fides-bff、bffkit 和 BFF Go 契约不再依赖 Kratos v2，测试、静态检查、构建和契约依赖检查通过 |
| AC5 | 升级镜像进入 dev 与 sta 验证 | 发现框架升级相关阻断问题并执行回滚 | 上一版稳定镜像可以恢复服务，前端与下游服务不需要同步改造 |

## Open Questions

| Question | Owner | Deadline | Status |
|---|---|---|---|
| dev 与 sta 验证的集群窗口和镜像发布流水线是否在本次 PR 合并后立即执行 | forest | 合并后发布前 | 默认纳入交付验证 |
| Kratos v3 版本是否只有 `v3.0.0` 可用 | forest | 实现前 | 当前 Go proxy 显示 `github.com/go-kratos/kratos/v3 v3.0.0` |

## Notes

- Jira 来源：LEN-212 `[BFF] fides-bff 升级到 Kratos v3`。
- 用户已授权 Agent 批准中间文件，最终需要本地测试通过、开 PR 并合并到 master。
