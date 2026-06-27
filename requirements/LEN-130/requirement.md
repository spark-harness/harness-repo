---
requirement_id: "LEN-130"
owner: "core"
status: "approved"
created_at: "2026-06-27"
related_branch: "feature/LEN-130-fides-runtime-config"
target_branch: "master"
release_branch: "master"
contract_gate_mode: "auto"
affected_repositories:
  - harness-repo
  - business-repo
  - gitops-repo
approved_by: "forest"
approved_at: "2026-06-27T19:19:00+08:00"
decision: "用户明确授权：授权你批准所有文档；批准 LEN-130 fides 运行时配置中心和 .env 覆盖的需求、影响分析、设计和任务拆分，范围限定为 fides-web 运行时配置硬切、GitOps 部署配置更新、测试和文档，不涉及 fides-bff API、protobuf/IDL 或 NEXT_PUBLIC 兼容层。"
---

# [FE] fides 支持运行时配置中心和 .env 覆盖

## Background

`fides` 当前仍在镜像构建阶段注入 `NEXT_PUBLIC_FIDES_*`，部署配置也直接注入旧 `NEXT_PUBLIC_*` 变量。这会把环境差异配置绑定到 Next build 产物，导致同一个镜像无法在不同环境按运行时配置调整 BFF 地址、OTP adapter 和浏览器 tracing。

这不是新增业务页面，也不是修改 `fides-bff` 或后端接口契约。它是 `fides` 前端运行配置方式的硬切：环境差异配置不再绑定到构建产物，也不再依赖 `NEXT_PUBLIC_*` 进入浏览器 bundle。

Next.js 16 已移除 `serverRuntimeConfig` 和 `publicRuntimeConfig`。对于同一个 Docker image 跨环境复用，服务端应在运行时动态读取环境变量；对于浏览器必须使用的 public 配置，应由 `fides` 服务端读取运行时配置后，通过受控 public config 入口提供给浏览器。

## Goals

- 让同一个 `fides` 镜像可以部署到不同环境，并读取对应环境的运行时配置。
- 支持默认值、Consul JSON 配置源、运行时环境变量或 Next 已加载 `.env*` 的覆盖顺序。
- 只暴露明确白名单中的 public 配置给浏览器。
- 移除旧 `NEXT_PUBLIC_*` 配置路径，并在检测到旧变量时明确失败。
- 让浏览器 tracing 在配置为空时关闭导出，在配置存在时使用运行时 public config 初始化。
- 更新 GitOps 部署配置、测试和文档，证明构建不再依赖环境差异变量。

## Non-Goals

- 不修改 `fides-bff` API。
- 不修改 protobuf / IDL。
- 不引入前端 secret 暴露。
- 不保留 `NEXT_PUBLIC_*` 兼容层。
- 不使用 `next/config` 或 `next.config.ts` 作为运行时配置入口。
- 不把 runtime config 当作 secret 管理方案。

## User / Business Scenarios

### Scenario 1: 同一镜像部署到不同环境

Given: 运维人员使用同一个 `fides` 镜像部署到不同环境。

When: 每个环境提供不同的运行时配置。

Then: 页面连接到对应环境的 BFF，并按配置启用真实、mock 或禁用 OTP adapter。

### Scenario 2: 运行时环境变量覆盖 Consul

Given: Consul 中已存在 `fides` runtime config，运行时环境变量或 `.env*` 中也设置了同名配置。

When: `fides` 服务端加载配置。

Then: 最终生效值来自运行时环境变量或 `.env*`，覆盖 Consul 中的值。

### Scenario 3: 旧 public 变量被拒绝

Given: 部署配置中仍存在旧 `NEXT_PUBLIC_*` 变量。

When: `fides` 启动或配置校验执行。

Then: 系统明确失败或报告配置错误，不静默忽略旧变量。

### Scenario 4: 浏览器 tracing 可空

Given: 浏览器 tracing 配置为空。

When: 用户打开 `fides` 页面。

Then: 页面可正常使用，trace 导出关闭，请求链路不因 tracing 配置缺失而失败。

### Scenario 5: 浏览器 tracing 按 public config 初始化

Given: 浏览器 tracing 配置已提供 endpoint 和公开 header。

When: 用户打开 `fides` 页面并触发请求。

Then: 浏览器按运行时 public config 初始化 tracing 导出，不需要重新构建镜像。

## Business Rules

- BR1 `fides` 镜像构建不得依赖 OTP adapter、BFF base URL 或浏览器 tracing 目标地址等环境差异配置。
- BR2 `fides` 运行时配置以默认值为基础，Consul 配置中心提供环境级配置，进程运行时环境变量或 Next 已加载的 `.env*` 覆盖 Consul。
- BR3 本次为硬切，不兼容旧 `NEXT_PUBLIC_FIDES_OTP_ADAPTER`、`NEXT_PUBLIC_FIDES_BFF_BASE_URL`、`NEXT_PUBLIC_OTEL_EXPORTER_OTLP_TRACES_ENDPOINT`、`NEXT_PUBLIC_OTEL_EXPORTER_OTLP_TRACES_HEADERS`。
- BR4 只允许明确白名单中的 public 配置暴露给浏览器。
- BR5 如果生产环境缺少必需运行配置或检测到旧变量，应给出明确失败结果，避免静默使用错误配置。
- BR6 Client Component 不直接读取运行时环境变量；浏览器所需配置必须来自服务端提供的 public runtime config。
- BR7 runtime config 可以包含浏览器可见配置，但不得保存真实 secret。

## Acceptance Criteria

| AC | Given | When | Then |
|---|---|---|---|
| AC1 | 使用同一个 `fides` 镜像部署到不同环境 | 为每个环境提供不同运行时配置 | 页面连接到对应环境的 BFF，并按配置启用真实、mock 或禁用 OTP adapter |
| AC2 | Consul 中已存在 `fides` runtime config，且运行时环境变量或 `.env*` 中设置了同名配置 | `fides` 服务端加载配置 | 最终生效值来自运行时环境变量或 `.env*`，覆盖 Consul 中的值 |
| AC3 | 部署配置中仍存在旧 `NEXT_PUBLIC_*` 变量 | `fides` 启动或配置校验执行 | 系统明确失败或报告配置错误，不静默忽略旧变量 |
| AC4 | 浏览器 tracing 配置为空 | 用户打开 `fides` 页面 | 页面可正常使用，trace 导出关闭，且请求链路不因 tracing 配置缺失而失败 |
| AC5 | 浏览器 tracing 配置已提供 endpoint 和公开 header | 用户打开 `fides` 页面并触发请求 | 浏览器按运行时 public config 初始化 tracing 导出，不需要重新构建镜像 |
| AC6 | 运行配置中包含非白名单字段 | `fides` 暴露 public runtime config | 非白名单字段不会出现在浏览器可读取配置中 |
| AC7 | 构建 `fides` 镜像 | 执行 `next build` 或 Docker build | 构建过程不需要 OTP adapter、BFF base URL 或 tracing endpoint/header 等环境差异变量 |

## Open Questions

| Question | Owner | Deadline | Status |
|---|---|---|---|
| Consul runtime config key 最终路径是否采用 `spark/lendora/{env}/fides-web/runtime-config` | core | 实现前 | Proposed |
| GitOps 是否负责 seed 初始 Consul KV，还是由环境初始化流程写入 | core | GitOps 变更前 | Proposed |

## Notes

- Jira 来源：`LEN-130`。
- 服务矩阵确认：`fides` 位于 `business-repo/apps/fides-web`，`idl_required: false`。
- 本需求涉及 `business-repo` 的 `fides-web`、`gitops-repo` 的 `fides` 部署配置，以及 `harness-repo` 生命周期文件。
