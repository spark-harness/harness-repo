---
requirement_id: "LEN-115"
owner: "forest"
status: "approved"
updated_at: "2026-06-25"
approved_by: "forest"
approved_at: "2026-06-25T22:30:46+08:00"
decision: "用户已授权直接批准；批准 LEN-115 设计，确认使用 loggercheck、sloglint 和 depguard lax 规则覆盖 fides-bff 内部依赖边界并保留 cmd/fides-bff composition root。"
---

# Design

## Requirement Traceability

| Requirement Item | Design Decision | Notes |
|---|---|---|
| R1, AC1 | D1: 启用 `loggercheck` | 检查结构化日志 key/value 参数形状 |
| R2, AC1 | D2: 启用 `sloglint` | 约束未来 `log/slog` 使用风格 |
| R3, BR1-BR4, AC2 | D3: 使用 `depguard` 按内部层拆分规则 | 每个层级独立输出违反原因 |
| R4, BR5 | D4: 不为 `cmd/fides-bff` 设置禁止规则 | 保留 composition root 装配职责 |
| R5, AC3-AC7 | D5: 只引入低噪声规则并用现有 lint 命令验证 | 不启用 Jira 排除的风格规则 |

## Summary

方案只修改 fides-bff 的 `golangci-lint` 配置。新增 `loggercheck`、`sloglint` 和 `depguard`，其中 depguard 采用 lax 模式，只禁止明确违反架构边界的 import。这样可以在不扩大风格噪声的前提下，把日志调用质量和内部依赖方向纳入本地与 CI lint。

## Affected Services

| Service | Change | Reason |
|---|---|---|
| fides-bff | 更新 `apps/fides-bff/.golangci.yml` | 增强 Go lint 和内部依赖方向约束 |

## API / Contract Design

- Protobuf IDL required: No.
- Proto files: none changed.
- Buf module: unchanged.
- Buf config version: v2.
- Generated outputs: unchanged.
- Breaking check baseline: not applicable.
- Compatibility strategy: no external contract change; lint only affects development and CI feedback.

## Application Design

### D1：loggercheck

在 `linters.enable` 中加入 `loggercheck`。该规则检查常见日志库的 key/value 参数形状，避免结构化日志调用在编译通过后产生运行时不可读或不一致的字段。

### D2：sloglint

在 `linters.enable` 中加入 `sloglint`。该规则为未来 `log/slog` 使用提供静态约束，降低 Kratos v3 迁移过程中日志风格漂移的风险。

### D3：depguard 分层规则

使用 `linters.settings.depguard.rules` 定义四组规则：

| Rule | Files | 禁止方向 |
|---|---|---|
| `biz_layer` | `**/internal/biz/**/*.go` | data、service、server、observability、conf、protobuf DTO、Kratos、gRPC、OTel |
| `service_layer` | `**/internal/service/**/*.go` | data、server、observability、applicant 下游契约 |
| `data_layer` | `**/internal/data/**/*.go` | service、server |
| `server_layer` | `**/internal/server/**/*.go` | data |

规则使用 `list-mode: lax`。它不尝试列举所有允许依赖，只阻止本需求明确禁止的依赖方向，避免第一批引入高噪声误报。

### D4：composition root

`cmd/fides-bff` 继续作为 composition root。它可以依赖 `biz`、`data`、`server`、`service`、`conf` 和基础设施装配所需包，不纳入 depguard 禁止列表。

## Data / Config / Permission

- Data model: no change.
- Config: only lint configuration changes.
- Permission: no change.

## Observability

- Logs: no runtime log output change; lint only validates future log call shape.
- Metrics: no change.
- Tracing: no change.
- Events: no change.

## Testing Strategy

- `golangci-lint config verify` 验证配置 schema。
- `golangci-lint run ./...` 验证新增 linter 和 depguard 规则可加载，且当前代码没有误报。
- `make lint` 验证服务现有 lint 入口通过。
- `git diff --check` 验证没有空白格式问题。

## Rollout And Rollback

- Gray release: branch / PR level only.
- Kill switch: CI 出现不可接受误报时回退 `.golangci.yml` 修改。
- Rollout: 合并后由现有 lint CI 自动加载新增规则。
- Rollback: revert lint 配置提交并重跑 lint。

## Risks

| Risk | Mitigation | Owner |
|---|---|---|
| 文件 glob 与 depguard 绝对路径匹配不一致 | 使用 `**/internal/.../**/*.go` 并运行真实 lint 命令验证 | Codex |
| 新规则对当前测试代码误报 | 本地运行 `golangci-lint run ./...` 和 `make lint`，不加宽泛 nolint | Codex |
| 未来层级新增后规则未扩展 | 在新增内部包时同步更新 depguard 规则和需求设计 | Forest |
