---
requirement_id: "LEN-38"
analyst: "Codex"
status: "approved"
updated_at: "2026-06-20"
approved_by: "Forest"
approved_at: "2026-06-20T18:09:32+08:00"
decision: "批准 LEN-38 service-repo-check，允许进入实现阶段。"
idl_impact: "yes"
idl_impact_reason: "本需求不修改具体 .proto 语义，但新增 Go IDL 生成物仓库化、同名分支同步、RC tag 发布和 formal tag 发布能力，影响 protobuf 生成契约发布链路。"
---

# Impact Analysis

## Summary

本需求影响 `idl-repo` 的生成物发布 workflow 和 `idl-go-repo` 的仓库结构，使 Go IDL 生成物能够按同名分支、RC tag 和 formal tag 发布。

## Affected Domains

- shared / contract governance：Go IDL 生成物发布和版本追溯能力。
- user：当前服务矩阵中 `user-api` 使用 `{idl-repo}/vesta/spark/user/v1`，其 Go 生成物会进入 `idl-go-repo`。

## Affected Services

| Service | Repo | Reason | Protobuf Required |
|---|---|---|---|
| user-api | business-repo (services/backend/user-api) | 当前服务矩阵登记的 protobuf 契约来源；本需求生成链路会处理其 Go contract 代码，但不修改业务服务 | Yes |
| IDL contract publishing | idl-repo | 新增 Go branch sync、RC tag publish、formal tag publish workflow | Yes |
| Go generated contract repo | idl-go-repo | 初始化 Go module 仓库，并作为 Go 生成物 branch 和 tag 发布目标 | Yes |
| Harness governance | harness-repo | 新增 LEN-38 生命周期产物和后续门禁证据 | No |

## API / Contract Impact

- Does this change involve protobuf IDL or external contracts: Yes，生成物发布链路，不改变 wire contract。
- Contract repo: `idl-repo`。
- Proto files: 不修改具体 proto；现有生成物来自 `idl-repo/vesta/spark/user/v1/*.proto` 及后续新增 proto。
- Buf module: `local/spark-user`。
- Buf config version: v2。
- Required buf checks: `buf lint`、`buf generate`、`buf breaking --against '.git#branch=master'`。本需求实现 workflow 时至少需要在证据中记录 `buf generate`；若未修改 proto，breaking 检查可说明不适用。
- Breaking baseline: `master`。
- Compatibility risk: wire 兼容风险低；发布链路、跨仓权限、Go module path 和 tag 不可变性风险中等。

## Generated Contract Impact

- `idl-go-repo`: 直接影响。需要初始化远端仓库、默认分支、`go.mod`、生成物目录和 tag 发布目标。
- `idl-repo`: 直接影响。需要新增或调整 GitHub Actions workflow，用于 Go 同名分支同步、RC tag 发布和 formal tag 发布。
- `idl-java-repo`: 不直接影响。Java 同步链路只作为行为参照。
- `business-repo`: 不直接修改。后续消费侧依赖检查由 LEN-36 覆盖。

## Data Impact

- Database schema: 无。
- Data migration: 无。
- Backfill: 无。
- Cache: 无。

## Config / Permission / Observability Impact

- Config: `idl-repo` 需要配置 `IDL_GO_REPO_TOKEN` 或等价 secret，用于跨仓写入 `spark-harness/idl-go-repo`。
- Permission: token 需要具备 `spark-harness/idl-go-repo` contents write 权限；如 tag 发布需要同一 token 可创建 tag。
- Metrics: 不新增运行时指标。
- Logs: GitHub Actions run log 是同步和发布追溯证据的一部分。
- Tracing: 无运行时 tracing 影响。
- Events: 无业务事件影响。

## Rollout And Rollback

- Gray release: 不适用；本需求是生成物发布基础设施。
- Kill switch: 可通过禁用 Go 同步 / 发布 workflow 或移除触发条件阻断新发布，但不得移动或删除已发布 RC / formal tag。
- Rollback steps: 回滚 `idl-repo` workflow 变更；保留已创建的 `idl-go-repo` 仓库和不可变 tag。若默认分支初始化错误，应通过新提交修正，不得重写已发布 tag。

## Risks

| Risk | Impact | Mitigation | Owner |
|---|---|---|---|
| `IDL_GO_REPO_TOKEN` 缺失或权限不足 | branch sync 或 tag publish 失败 | workflow 启动阶段显式检查 secret，并输出目标仓库和权限缺口 | Codex |
| `idl-go-repo` 为空仓且没有默认分支 | 无法基于目标分支更新生成物或发布 tag | 实现阶段先初始化 `master`、`go.mod` 和首个生成物提交 | Codex |
| RC / formal tag 被重复发布 | 下游无法确认依赖是否不可变 | workflow 在创建 tag 前检查远端 tag 是否存在，存在则失败 | Codex |
| Go module path 与 tag major 不一致 | 下游 Go 消费者解析失败或产生 `+incompatible` | 需求和设计中强制 module path、import path、tag major 一致，并在校验中检查 | Codex |
| branch sync 与 tag publish 共享生成逻辑不一致 | 同一 IDL commit 生成不同 Go 内容 | 设计阶段抽取同一生成校验步骤，发布证据记录 `idl-repo` commit 和 `idl-go-repo` commit | Codex |
| Go 生成物同步失败被误认为业务 proto breaking | 排查方向错误 | workflow 失败信息区分 Buf 生成失败、Go module 校验失败、跨仓权限失败和 tag 已存在 | Codex |
