---
requirement_id: "LEN-129"
owner: "Codex"
status: "approved"
updated_at: "2026-06-27"
approved_by: "Forest"
approved_at: "2026-06-27T21:05:01+08:00"
decision: "批准 LEN-129 设计，允许进入开发阶段。"
---

# Design

## Requirement Traceability

| Requirement Item | Design Decision | Notes |
|---|---|---|
| R1, AC1, AC6 | D1：保留 `configs/config.yaml` 为第一配置源；Consul 未启用时只加载文件源和环境映射源 | 本地默认启动不依赖外部服务 |
| R2, AC2, AC3 | D2：启动最早阶段读取 `.env`，只写入当前进程不存在的 key | 真实 shell、CI、K8s 环境变量优先 |
| R3, AC5 | D3：实现无前缀环境变量 allowlist source，逐项映射到 Kratos config path | 不使用全量环境扫描注入配置树 |
| R4, AC4, AC7 | D4：实现 Consul KV YAML 启动期 source；启用后加载失败或 YAML 无效即启动失败 | 不做 watch 或热更新 |
| R5, BR4 | D5：Consul bootstrap 使用本地环境变量或平台 Secret；bootstrap 值不从 Consul 读取 | 防止自举循环和 secret 泄露 |
| R6, AC7, BR7 | D6：配置加载错误只输出 source、key/path 和错误类别，不输出 token 或原始配置内容 | 满足安全和日志边界 |
| R7, AC9 | D7：补充 `.env.example` 和 README 配置章节 | 说明优先级、路径、secret 边界和非热更新 |

## Summary

在 `apps/fides-bff/cmd/fides-bff` 启动路径中增加一个小型配置加载层。该层只负责启动期配置来源装配和合并，不进入 `biz`、`service` 或协议处理层。

配置优先级为：

1. P0：`configs/config.yaml` 本地默认值。
2. P1：`.env` 在进程内补充不存在的环境变量。
3. P2：allowlist 内无前缀环境变量映射到配置树。
4. P3：Consul KV YAML 远程配置覆盖前面来源。
5. P4：Consul bootstrap 地址、路径、token 来自本地环境或平台 Secret，不从 Consul 自举读取。

## Affected Services

| Service | Change | Reason |
|---|---|---|
| fides-bff | 修改启动期配置加载，新增配置 source、测试、示例和文档 | 支持本地、STA、生产共用配置模型 |

## API / Contract Design

- Protobuf IDL required: No。
- Proto files: 无。
- Buf module: 不变。
- Buf config version: v2。
- Generated outputs: 无。
- Breaking check baseline: 不适用。
- Compatibility strategy: 不改变 HTTP 路由、错误信封、protobuf 或 generated contract。

## Application Design

### D1：配置加载入口

`main.go` 不直接构造单一 file source，而是调用一个本地配置加载函数构造 Kratos config。该函数负责：

- 加载 `.env` 到进程环境，缺失文件返回成功。
- 构造 `file.NewSource(flagconf)`。
- 构造 allowlist 环境 source。
- 如果 bootstrap 环境变量启用 Consul 配置源，则追加 Consul KV YAML source。
- 执行 `Load()` 和 `Scan()`。

### D2：`.env` 加载

`.env` 文件只用于本地启动。解析规则保持保守：

- 默认读取工作目录下 `.env`，可通过本地环境变量覆盖路径。
- 支持 `KEY=value` 和可选引号。
- 空行和 `#` 注释忽略。
- 只调用“不存在时设置”的逻辑，不覆盖已经存在的进程环境变量。
- 缺失 `.env` 不失败；语法错误失败。

### D3：无前缀环境变量 allowlist

环境变量 key 不加统一服务前缀，但必须出现在显式 allowlist。首批覆盖四组：

- `server`：HTTP 地址、超时、CORS。
- `applicant`：Consul scheme、address、service name、超时。
- `registry`：Consul 注册开关、scheme、address、discovery address、metadata 和健康检查参数。
- `observability`：OTel 开关、endpoint、protocol、insecure、headers、resource environment。

实现上把 allowlist 转成 Kratos 可读取的 map source。未出现在 allowlist 的宿主环境变量不会进入配置树。

### D4：Consul KV YAML source

Consul 配置源通过 bootstrap 环境变量启用：

- 是否启用。
- Consul address / scheme。
- KV path，默认建议 `config/lendora/fides-bff/config.yaml`。
- ACL token 或凭据来源。

远程 KV value 必须是 YAML 结构，并整体映射到 Bootstrap 配置树。启用后：

- Consul 不可访问时启动失败。
- KV key 不存在时启动失败。
- YAML 无效或无法映射时启动失败。
- 错误只包含路径和错误类别，不包含 token 或原始 YAML 内容。

### D5：配置验证

`Scan()` 后执行轻量启动配置验证：

- Consul 注册启用时，沿用现有 `registry.consul.discovery_addr` 校验。
- Consul 配置源启用时，bootstrap address/path 必须存在且格式可用。
- 不在本需求新增业务配置语义校验。

## Data / Config / Permission

- Data model: 无。
- Config:
  - 新增 `.env.example`，只放变量名和非密占位值。
  - 新增 Consul KV YAML 示例片段，只包含非密运行配置。
  - `.env`、真实 secret、token 和本地私有配置不提交。
- Permission:
  - 无用户权限变化。
  - Consul ACL token 如需使用，只能来自平台 Secret 或本地私有环境。

## Observability

- Logs:
  - 启动失败说明配置源和错误类别。
  - 不输出 `.env` 原文、Consul token、Authorization header、密码或远程 YAML 内容。
- Metrics:
  - 不新增运行时指标。
- Tracing:
  - 不新增业务 trace。
- Events:
  - 无事件变化。

## Testing Strategy

- 单元测试覆盖 `.env` 缺失、加载、真实环境优先和语法错误。
- 单元测试覆盖 allowlist 映射、无关环境变量忽略和类型转换。
- 单元测试覆盖 file + env + Consul 优先级合并。
- 单元测试覆盖 Consul 未启用、本地 mock Consul KV 成功、Consul 不可访问、KV 缺失和 YAML 无效。
- 单元测试覆盖错误文本不包含 token、Authorization 或远程配置原文。
- 保留并运行 `go test ./...`，必要时运行 `make lint` 或等价检查。

## Rollout And Rollback

- Gray release:
  - 本地先使用默认配置和 `.env.example` 验证。
  - STA 启用 Consul config source 前，先写入非密 YAML 并通过平台 Secret 注入 bootstrap 值。
  - 生产沿用同一 KV 路径约定和平台 Secret 注入方式。
- Kill switch:
  - 关闭 Consul config source 环境变量即可回退到本地文件和环境映射。
  - 删除 `.env` 不影响默认配置启动。
- Rollback:
  - 回滚 `apps/fides-bff` 配置加载代码和文档。
  - 移除部署环境中的 Consul config enable/bootstrap 变量。

## Risks

| Risk | Mitigation | Owner |
|---|---|---|
| 无前缀变量误伤宿主环境 | 只接受显式 allowlist，并用测试覆盖无关变量忽略 | BFF |
| `.env` 覆盖平台环境 | 只在 key 不存在时写入，测试验证真实环境优先 | BFF |
| Consul 配置泄露 secret | 文档和示例明确 Consul 只保存非密配置；错误不输出原始值 | Platform / BFF |
| 远程配置格式错误导致启动失败 | 启动失败是预期策略；错误信息保留 source/path 便于排障 | BFF |
