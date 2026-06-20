---
requirement_id: "LEN-38"
owner: "Codex"
status: "approved"
created_at: "2026-06-20"
related_branch: "feature/LEN-38-go-idl-publishing"
approved_by: "Forest"
approved_at: "2026-06-20T17:56:29+08:00"
decision: "批准 LEN-38 requirement 与 impact-analysis，允许进入设计阶段。"
---

# 实现 Go IDL 生成物发布链路

## Background

Spark 当前已有 `idl-repo` 和 `idl-java-repo` 的生成物同步链路：`idl-repo` 在任意分支 push 修改 `.proto` 或 Buf 配置后，会执行 `buf generate`，编译 Java 生成物，并把 `idl-java-repo` 推送到同名分支。

先说不是什么：本需求不是业务 `.proto` 语义变更，不新增业务 RPC、message 或 field；也不是 `business-repo` 消费侧依赖扫描门禁，消费侧规则由 LEN-36 承担。

它是什么：本需求补齐 Go 生成物仓库和发布链路。`idl-go-repo` 必须成为真实 Go module 仓库，module path 为 `github.com/spark-harness/idl-go-repo`。`idl-repo` 必须支持 Go 生成物同名分支同步，并支持 RC tag 和 formal tag 发布，使业务 Go 消费者能够按 LEN-35 的契约版本治理规则消费 Go module tag。

当前状态中，`idl-repo/buf.gen.yaml` 已将 Go 输出配置到 `../idl-go-repo/`，但本地 `idl-go-repo` 不是 git repo；远端 `spark-harness/idl-go-repo` 已按本需求创建为私有仓库，但仍为空仓，没有默认分支、`go.mod`、生成物提交或 tag 发布流水线。

## Goals

- R1: 初始化 `spark-harness/idl-go-repo` 为真实 Go module 仓库，module path 为 `github.com/spark-harness/idl-go-repo`。
- R2: 在 `idl-repo` 中新增 Go 生成物同名分支同步能力。
- R3: `idl-repo` feature 分支 push 修改 `.proto`、`buf.yaml`、`buf.gen.yaml` 或 Go 同步 workflow 时，能生成并推送 `idl-go-repo` 同名分支。
- R4: Go 同名分支同步必须能创建不存在的目标分支，也能更新已存在的目标分支。
- R5: 第一版支持 RC tag 发布，并将冻结 IDL commit 对应的 Go 生成物发布为不可移动的 RC Go module tag。
- R6: 第一版支持 formal tag 发布，并由 `idl-repo` SemVer tag 触发正式 Go module tag 发布。
- R7: RC / formal tag 不得覆盖、移动、删除或重复发布。
- R8: Go 发布链路必须执行 `buf generate` 和 Go module 校验。
- R9: Go 发布链路必须使用具备 `spark-harness/idl-go-repo` 写权限的专用 secret，不依赖 `idl-repo` 的默认 `GITHUB_TOKEN` 跨仓写。
- R10: 发布和同步结果必须可追溯到触发的 `idl-repo` branch、tag、commit 和 CI run。

## Non-Goals

- 不修改具体业务 `.proto` 语义。
- 不新增业务 Go 服务。
- 不修改 `business-repo` 的依赖扫描门禁。
- 不改变 LEN-35 已定义的契约版本治理规则。
- 不把 Go 生成物提交到 `business-repo`。
- 不引入 Buf BSR Generated SDK 作为 Go 分发模型。
- 不要求 Java 生成物发布链路在本需求中重构。
- 不允许 RC tag 或 formal tag 覆盖既有发布。

## User / Business Scenarios

### Scenario 1: feature 分支同步 Go 生成物

Given: 开发者在 `idl-repo` 的 `feature/LEN-38-go-idl-publishing` 或其他需求分支修改 `.proto` 或 Buf 配置。

When: 该分支 push 到远端并触发 Go 同步 workflow。

Then: workflow 生成 Go 代码，校验 Go module，并把 `idl-go-repo` 推送到与 `idl-repo` 触发分支同名的分支。

### Scenario 2: 目标 Go 分支不存在时自动创建

Given: `idl-repo` feature 分支已经存在，但 `idl-go-repo` 中没有同名分支。

When: Go 同步 workflow 首次运行。

Then: workflow 创建 `idl-go-repo` 同名分支，并提交当前 Go 生成物状态。

### Scenario 3: 发布 RC Go module tag

Given: 某个 IDL commit 已被冻结用于 RC 验证。

When: 发布人触发 RC 发布流程。

Then: workflow 使用冻结的 IDL commit 生成 Go 代码，校验 module，并在 `idl-go-repo` 发布符合 LEN-35 规则的 RC tag；如果 tag 已存在，发布失败。

### Scenario 4: 发布 formal Go module tag

Given: 发布人在 `idl-repo` 创建 formal SemVer tag，例如 `v1.8.0`。

When: tag push 触发 formal 发布流程。

Then: workflow 使用该 tag 指向的 IDL commit 生成 Go 代码，校验 module，并在 `idl-go-repo` 发布同版本 formal Go module tag；如果 tag 已存在，发布失败。

### Scenario 5: 跨仓权限缺失时明确失败

Given: `idl-repo` 未配置写入 `spark-harness/idl-go-repo` 的专用 secret。

When: Go 同步或发布 workflow 运行。

Then: workflow 失败，并明确指出缺少跨仓写权限配置，而不是静默跳过 Go 发布。

## Business Rules

- BR1: Go module path 固定为 `github.com/spark-harness/idl-go-repo`。
- BR2: `spark-harness/idl-go-repo` 必须是私有远端仓库，并有可被 CI clone、commit、push 和 tag 的默认分支。
- BR3: `idl-go-repo` 必须包含 `go.mod`，且 module directive 必须与 Go module path 一致。
- BR4: `idl-repo` 的 Go 同步 workflow 必须监听任意分支中 `.proto`、`buf.yaml`、`buf.gen.yaml` 或 workflow 自身变化。
- BR5: 同名分支同步的目标分支必须等于 `idl-repo` 触发分支名。
- BR6: 目标 Go 分支不存在时，workflow 必须创建目标分支。
- BR7: 目标 Go 分支存在时，workflow 必须基于远端目标分支更新生成物。
- BR8: Go 生成物只能由 `buf generate` 产生，不得手写生成代码。
- BR9: Go 同步和发布 workflow 必须执行 Go module 校验。
- BR10: Go 同步和发布 workflow 必须使用专用 secret，例如 `IDL_GO_REPO_TOKEN`。
- BR11: `GITHUB_TOKEN` 默认不得被视为可跨仓写 `idl-go-repo`。
- BR12: RC tag 必须来自冻结的 IDL commit，且 tag 格式必须符合 LEN-35 的 RC 规则。
- BR13: Formal tag 必须由 `idl-repo` 中人工创建的 SemVer tag 触发。
- BR14: Formal Go module tag 必须与 `idl-repo` formal SemVer tag 对齐。
- BR15: RC / formal Go tag 已存在时，workflow 必须失败，不得覆盖。
- BR16: RC / formal Go tag 不得移动、删除或 force-push。
- BR17: 发布记录必须能追溯到 `idl-repo` commit、触发 branch 或 tag、`idl-go-repo` commit、Go module tag 和 CI run。
- BR18: Go `v0` 和 `v1` module path 不得包含 `/v0` 或 `/v1`。
- BR19: Go `v2+` module path、require path、import path 和 tag major version 必须一致，并且不得使用 `+incompatible`。

## Acceptance Criteria

- AC1: `spark-harness/idl-go-repo` 已创建为私有仓库。
- AC2: `idl-go-repo` 初始化出 `master` 默认分支和 `go.mod`。
- AC3: `go.mod` 的 module directive 为 `github.com/spark-harness/idl-go-repo`。
- AC4: `idl-repo` 新增 Go 同名分支同步 workflow。
- AC5: feature 分支 push 修改 `.proto` 或 Buf 配置后，workflow 可以创建或更新 `idl-go-repo` 同名分支。
- AC6: 同步 workflow 执行 `buf generate`，并只提交生成后的 Go contract 代码和必要 Go module 文件。
- AC7: 同步 workflow 执行 Go module 校验，并在失败时阻断 push。
- AC8: `idl-repo` 支持手动或 tag 驱动的 RC Go module tag 发布。
- AC9: `idl-repo` formal SemVer tag push 可以触发 formal Go module tag 发布。
- AC10: 已存在的 RC / formal Go tag 不会被覆盖，重复发布会失败。
- AC11: 缺少 `IDL_GO_REPO_TOKEN` 或等价 secret 时，workflow 输出明确错误并失败。
- AC12: 需求证据记录至少包含一次 branch sync 验证、一次 RC tag 发布验证和一次 formal tag 发布验证。

## Open Questions

| Question | Owner | Deadline | Status |
|---|---|---|---|
| `IDL_GO_REPO_TOKEN` 的 secret 名称是否固定为该名称 | Codex | 设计阶段 | 默认使用 `IDL_GO_REPO_TOKEN` |
| RC tag 第一版采用 `workflow_dispatch` 输入版本，还是由特定 `idl-repo` tag 前缀触发 | Codex | 设计阶段 | 待设计阶段决策 |
| Go module 校验命令使用 `go test ./...` 还是更小的 `go list ./...` + `go test ./...` | Codex | 设计阶段 | 默认至少执行 `go test ./...` |

## Notes

- 用户已确认 Go module path 使用 `github.com/spark-harness/idl-go-repo`。
- 用户已要求由 Codex 创建 `spark-harness/idl-go-repo`。
- 用户已要求第一版同时支持 branch sync、RC tag publish 和 formal tag publish。
- `spark-harness/idl-go-repo` 已创建为私有空仓；后续实现阶段需要初始化默认分支和 Go module。
