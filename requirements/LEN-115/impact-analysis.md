---
requirement_id: "LEN-115"
analyst: "forest"
status: "approved"
updated_at: "2026-06-25"
approved_by: "forest"
approved_at: "2026-06-25T22:31:44+08:00"
decision: "用户已授权直接批准；批准 LEN-115 服务仓库检查，确认仅涉及 harness-repo 与 business-repo，同名分支存在，IDL 仓无变更且 fides-bff 现有 proto 仅复用。"
idl_impact: "no"
idl_impact_reason: "本需求只增强 fides-bff golangci-lint 配置，不修改 .proto、Buf 配置或生成契约。"
---

# Impact Analysis

## Summary

LEN-115 只影响 fides-bff 的 Go lint 配置和 Harness 需求产物；它新增日志质量检查和内部包依赖方向检查，不改变运行时行为、数据、配置或契约。

## Affected Domains

- Go lint 治理：fides-bff 的 `golangci-lint` 配置新增 linter 和 depguard 规则。
- 后端架构边界：通过静态检查约束 fides-bff 内部包依赖方向。
- 日志质量：通过 `loggercheck` 和 `sloglint` 降低结构化日志和未来 `log/slog` 使用风险。
- Harness 治理：新增 LEN-115 生命周期文件、证据和门禁 JSON。

## Affected Services

| Service | Repo | Reason | Protobuf Required |
|---|---|---|---|
| fides-bff | `business-repo` / `harness-repo` | 修改 `apps/fides-bff/.golangci.yml` 并补齐需求门禁材料 | Yes, reuse existing only |

## Upstream / Downstream Consumers

- 开发者和 Agent：在本地运行 `golangci-lint run ./...` 或 `make lint` 时获得依赖方向反馈。
- CI：继续运行现有 fides-bff lint 命令，但会加载新增规则。
- fides 前端、applicant-api、IDL 仓和生成契约仓：不受影响。

## API / Contract Impact

- Does this change involve protobuf IDL or external contracts: No.
- Contract repo: `idl-repo` is not edited.
- Proto files: no `.proto` file changed.
- Buf module: existing `local/lendora-fides-bff` is reused only as dependency context.
- Buf config version: v2.
- Required buf checks: not required for this source change.
- Breaking baseline: not applicable.
- Compatibility risk: none for external API or protobuf contract.

## Generated Contract Impact

- Go generated contracts consumed by fides-bff are unchanged.
- `idl-java-repo` is not part of this requirement.

## Data Impact

- Database schema: none.
- Data migration: none.
- Backfill: none.
- Cache: none.
- Runtime storage: none.

## Config / Permission / Observability Impact

- Config: only lint configuration changes.
- Permission: no runtime or CI permission changes.
- Metrics: no metric schema change.
- Logs: no runtime log output change; lint only checks future logging call shape.
- Tracing: no tracing schema change.
- Events: no event schema change.

## Rollout And Rollback

- Gray release: branch / PR level only.
- Kill switch: revert the lint configuration commit before merge if CI reports unacceptable false positives.
- Rollout steps:
  - Add lint rules in fides-bff `.golangci.yml`.
  - Run `golangci-lint config verify`.
  - Run `golangci-lint run ./...`.
  - Run `make lint`.
  - Record evidence in Harness.
- Rollback steps:
  - Revert the `.golangci.yml` change.
  - Re-run `golangci-lint run ./...` and `make lint` to confirm prior behavior.

## Risks

| Risk | Impact | Mitigation | Owner |
|---|---|---|---|
| depguard 文件 glob 未覆盖目标目录 | 反向依赖无法在 lint 阶段发现 | 使用 `**/internal/.../**/*.go` 覆盖绝对路径匹配，并通过 lint 加载验证 | Codex |
| depguard 规则误伤当前合法测试装配 | CI lint 失败 | 先运行 `golangci-lint run ./...` 和 `make lint`，不使用宽泛 nolint | Codex |
| 未来新增包未被规则覆盖 | 依赖约束出现缺口 | 后续新增内部层时同步更新 depguard 规则和 Harness 设计 | Forest |
