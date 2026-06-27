---
requirement_id: "LEN-130"
owner: "core"
status: "approved"
updated_at: "2026-06-27"
approved_by: "forest"
approved_at: "2026-06-27T19:19:00+08:00"
decision: "用户明确授权：授权你批准所有文档；批准 LEN-130 fides 运行时配置中心和 .env 覆盖的需求、影响分析、设计和任务拆分，范围限定为 fides-web 运行时配置硬切、GitOps 部署配置更新、测试和文档，不涉及 fides-bff API、protobuf/IDL 或 NEXT_PUBLIC 兼容层。"
---

# Design

## Requirement Traceability

| Requirement Item | Design Decision | Notes |
|---|---|---|
| BR1, AC7 | 从 `fides-web` Dockerfile 和 build 流程移除环境差异 `NEXT_PUBLIC_*` 构建参数 | 构建产物不绑定 OTP、BFF 或 tracing 环境值 |
| BR2, AC1, AC2 | 新增服务端 runtime config loader，合并默认值、Consul JSON、运行时 env / `.env*` | 覆盖顺序为 env / `.env*` > Consul > 默认值 |
| BR3, AC3 | 新增旧变量检测并在校验阶段明确失败 | 硬切，不保留兼容层 |
| BR4, BR6, AC6 | 新增受控 public runtime config 入口，仅输出白名单字段 | Client Component 不直接读运行时环境变量 |
| BR5 | 区分生产必需配置校验和非生产默认值 | 避免生产静默落到错误默认值 |
| AC4, AC5 | Browser tracing 从 public runtime config 初始化，空 endpoint 关闭导出 | tracing 配置异常不阻断页面和请求 |
| AC1 | OTP gateway 从 public runtime config 选择 real/mock/disabled 和 BFF base URL | 保留既有 gateway 和 UI 行为 |

## Summary

方案在 `fides-web` 内建立服务端 runtime config 边界：服务端读取配置并输出白名单 public config；浏览器只消费 public config，不直接读取运行时环境变量。`fides` 镜像构建不再需要环境差异变量，GitOps 部署只提供运行时配置源和覆盖值。

这不是把 secret 放进前端配置。runtime public config 只承载浏览器必须知道的非 secret 字段，例如 BFF base URL、OTP adapter mode、browser tracing endpoint 和公开 headers。

## Affected Services

| Service | Change | Reason |
|---|---|---|
| fides | 新增 runtime config loader、public config 入口、OTP/tracing 读取改造和测试 | 支持同一镜像跨环境复用 |
| fides GitOps | 移除旧 `NEXT_PUBLIC_*`，补充 Consul 地址、config key 和 runtime override 配置 | 部署配置从构建期变量切换为运行时变量 |

## API / Contract Design

- Protobuf IDL required: No
- Proto files: N/A
- Buf module: N/A
- Buf config version: v2 unchanged
- Generated outputs: N/A
- Breaking check baseline: N/A
- Compatibility strategy: 不修改 `fides-bff` API 或 generated client。

## Application Design

### Runtime Config Model

配置分为 internal runtime config 和 public runtime config。

Internal runtime config 可以包含配置源信息，例如 Consul URL、Consul key、当前环境和校验模式。Public runtime config 只包含浏览器可读取字段：

| Field | Public | Purpose |
|---|---|---|
| `otpAdapter` | Yes | `real`、`mock` 或 `disabled` |
| `bffBaseUrl` | Yes | 浏览器访问 `fides-bff` 的 base URL |
| `browserTracing.endpoint` | Yes | OTLP HTTP traces endpoint；为空时关闭导出 |
| `browserTracing.headers` | Yes | 公开 header map，不允许 secret |

非白名单字段即使出现在 Consul JSON 或 env 中，也不得出现在 public config 响应中。

### Config Source And Precedence

加载顺序：

1. 默认值提供非生产可运行的最小配置。
2. Consul JSON 使用默认 key `spark/lendora/{env}/fides-web/runtime-config` 读取环境级配置。
3. 运行时环境变量或 Next 已加载 `.env*` 覆盖 Consul。

运行时 env 建议使用非 `NEXT_PUBLIC_*` 名称：

| Env | Purpose |
|---|---|
| `FIDES_RUNTIME_ENV` | 当前环境名，用于默认 Consul key |
| `FIDES_RUNTIME_CONFIG_CONSUL_URL` | Consul HTTP base URL |
| `FIDES_RUNTIME_CONFIG_CONSUL_KEY` | Consul KV key |
| `FIDES_OTP_ADAPTER` | OTP adapter mode |
| `FIDES_BFF_BASE_URL` | BFF base URL |
| `FIDES_BROWSER_TRACING_ENDPOINT` | Browser OTLP traces endpoint |
| `FIDES_BROWSER_TRACING_HEADERS` | Browser OTLP traces public headers |

### Public Config Entry

`fides` 服务端提供 public runtime config 入口。浏览器启动时读取该入口，再初始化 OTP gateway 和 browser tracing。读取失败时页面应给出明确配置错误或进入安全降级路径；tracing 配置为空只关闭导出，不阻断 OTP 请求。

### Legacy Variable Validation

启动或配置校验时检测以下旧变量：

- `NEXT_PUBLIC_FIDES_OTP_ADAPTER`
- `NEXT_PUBLIC_FIDES_BFF_BASE_URL`
- `NEXT_PUBLIC_OTEL_EXPORTER_OTLP_TRACES_ENDPOINT`
- `NEXT_PUBLIC_OTEL_EXPORTER_OTLP_TRACES_HEADERS`

检测到任一旧变量时返回明确失败，避免旧变量继续影响构建或运行。

## Data / Config / Permission

- Data model: 无数据库模型变化。
- Config: 新增 runtime config schema、Consul key、非 `NEXT_PUBLIC_*` 环境变量和 public config 白名单。
- Permission: 无用户权限变化；运行环境读取 Consul 的权限由部署环境提供。

## Observability

- Logs: 配置加载失败、旧变量检测失败、Consul JSON 解析失败需要输出明确错误类别；日志不得输出 secret 或完整 header 值。
- Metrics: 本次不新增指标。
- Tracing: browser tracing 从 public runtime config 初始化；endpoint 为空时不注册 exporter，配置错误不阻断页面请求。
- Events: 无事件变更。

## Rollout And Rollback

- Gray release: 在 `lendora-sta` 先部署新镜像和 GitOps 配置，验证 public config、OTP real/mock/disabled、tracing 开关和旧变量失败路径。
- Kill switch: 将 `FIDES_OTP_ADAPTER` 设为 `disabled` 或 `mock` 可止血 OTP；清空 tracing endpoint 可关闭 browser trace 导出。
- Rollback: 回滚 `fides` 镜像和 GitOps 配置；保留的 Consul KV 不影响旧镜像。

## Risks

| Risk | Mitigation | Owner |
|---|---|---|
| Client 初始化依赖 public config，加载失败影响首屏 | 提供明确错误状态；测试覆盖 public config 失败路径 | core |
| Consul JSON schema 漂移 | 使用 runtime config parser 做字段校验和默认值合并 | core |
| 旧变量残留导致部署失败 | GitOps 同步移除旧变量，测试覆盖 legacy env 检测 | core |
| headers 被误用作 secret | 文档和字段命名强调 public headers，安全规范禁止 secret 进入 public config | core |
