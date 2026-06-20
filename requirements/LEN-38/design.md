---
requirement_id: "LEN-38"
owner: "Codex"
status: "approved"
updated_at: "2026-06-20"
approved_by: "Forest"
approved_at: "2026-06-20T18:01:18+08:00"
decision: "批准 LEN-38 design，允许进入任务拆分阶段。"
---

# Design

## Requirement Traceability

| Requirement Item | Design Decision | Notes |
|---|---|---|
| R1, AC1-AC3 | 初始化 `spark-harness/idl-go-repo` 为 Go module 仓库，默认分支为 `master`，module path 为 `github.com/spark-harness/idl-go-repo`。 | 远端仓库已创建但为空仓，实现阶段补齐默认分支和 `go.mod`。 |
| R2-R4, AC4-AC7 | 在 `idl-repo` 新增 Go branch sync workflow，复用 Java 同步链路的跨仓 checkout、目标分支选择、生成、校验、提交和 push 模式。 | workflow 名称建议为 `.github/workflows/sync-go-idl.yml`。 |
| R5, AC8, AC10 | RC 发布支持 `workflow_dispatch` 输入 RC tag 和冻结的 IDL ref，也支持 RC tag push；生成后在 `idl-go-repo` 创建不可覆盖 tag。 | 第一版不使用 PR label 或 comment 触发。 |
| R6, AC9-AC10 | Formal 发布由 `idl-repo` SemVer tag push 触发，并在 `idl-go-repo` 创建同名 Go module tag。 | 与 LEN-35 的 formal tag 事实来源一致。 |
| R7, BR15-BR16 | tag 创建前检查 `idl-go-repo` 远端 tag 是否已存在；存在即失败。 | 不提供覆盖、移动或删除 tag 的 workflow。 |
| R8, AC6-AC7 | 生成和发布统一执行 `buf generate --template buf.gen.go.yaml`、`go mod tidy`、`go test ./...`。 | Go message 与 gRPC stub 先写入 staging 目录，再同步到 `idl-go-repo`，避免清理 `.git`、`go.mod` 或 README。 |
| R9, AC11 | 所有跨仓写操作使用 `IDL_GO_REPO_TOKEN`。 | `GITHUB_TOKEN` 只用于当前仓读操作，不作为跨仓写依据。 |
| R10, BR17, AC12 | workflow 输出和证据记录 `idl-repo` ref / commit、`idl-go-repo` commit、tag 和 CI run。 | 后续 evidence 文件保存验证命令和 run 结果。 |

## Summary

本设计补齐 Go IDL 生成物的三条发布链路：

1. branch sync：`idl-repo` 任意分支修改 proto / Buf 配置后，同步 Go 生成物到 `idl-go-repo` 同名分支。
2. RC publish：人工触发 RC 发布，使用冻结 IDL ref 生成 Go 代码，并创建不可覆盖 RC tag。
3. formal publish：`idl-repo` formal SemVer tag push 触发正式 Go module tag 发布。

设计不改变业务 proto 语义，不修改 Java 发布链路，不修改 `business-repo` 消费侧门禁。

## Affected Services

| Service | Change | Reason |
|---|---|---|
| IDL contract publishing (`idl-repo`) | 新增 Go branch sync workflow 和 Go tag publish workflow。 | 需要从 IDL commit 生成并发布 Go contract module。 |
| Go generated contract repo (`idl-go-repo`) | 初始化 `master`、`go.mod`、生成物目录和 tag 发布目标。 | Go 消费者通过 module path 和 tag 消费生成契约。 |
| user-api | 不修改业务服务；其 proto 生成的 Go 文件进入 `idl-go-repo`。 | 当前服务矩阵已有 `vesta/spark/user/v1` proto。 |
| Harness governance (`harness-repo`) | 保存 LEN-38 生命周期文档、门禁和证据。 | 支持需求追溯和阶段推进。 |

## API / Contract Design

- Protobuf IDL required: Yes，生成物发布链路涉及 protobuf，但不修改 wire contract。
- Proto files: 当前覆盖 `idl-repo/vesta/spark/user/v1/*.proto`，后续自动覆盖 `idl-repo` 中新增 proto。
- Buf module: `local/spark-user`。
- Buf config version: v2。
- Generated outputs: Go 专用生成模板 `buf.gen.go.yaml` 写入 `../.generated/idl-go`，包含 message 与 gRPC stub，workflow 再同步生成物到 `idl-go-repo`。
- Breaking check baseline: `master`。本需求不改变 proto，设计阶段不需要新增 breaking 结论；实现证据需要记录是否运行以及不适用原因。
- Compatibility strategy: additive infrastructure change。生成物内容必须完全来自 `buf generate`，不手写或改写 `.pb.go`。

### Go Module Layout

`idl-go-repo` 使用单 module：

```text
module github.com/spark-harness/idl-go-repo
```

生成目录保持 proto source relative 输出，例如：

```text
vesta/spark/user/v1/auth.pb.go
vesta/spark/user/v1/ping.pb.go
vesta/spark/user/v1/profile.pb.go
```

第一版只支持 `v0` / `v1` module path，不在 module path 中加入 `/v1`。如果未来进入 `v2+`，必须按 LEN-35 更新 module path、import path、tag major 和消费证据。

### Branch Sync Workflow

新增 `idl-repo/.github/workflows/sync-go-idl.yml`：

- trigger:
  - push branches `**`
  - paths: `**/*.proto`、`buf.yaml`、`buf.gen.yaml`、workflow 自身
  - `workflow_dispatch`
- concurrency: `sync-go-idl-${{ github.ref_name }}`
- permission: `contents: read`
- env:
  - `GO_IDL_REPOSITORY=spark-harness/idl-go-repo`
  - `BRANCH_NAME=${{ github.ref_name }}`

步骤：

1. checkout `idl-repo` 到 `idl-repo/`。
2. 检查 `IDL_GO_REPO_TOKEN` 是否存在。
3. checkout `spark-harness/idl-go-repo` 到 `idl-go-repo/`。
4. 如果目标分支存在，checkout `origin/$BRANCH_NAME`；否则从当前默认分支或空分支创建 `$BRANCH_NAME`。
5. 设置 Go 和 Buf。
6. 从 `idl-repo` 执行 `buf generate --template buf.gen.go.yaml`，输出到 `../.generated/idl-go`。
7. 使用同步步骤把 staging 目录中的生成物复制到 `idl-go-repo`，同时保留 `.git`、`go.mod`、`go.sum`、README 和 workflow 目录。
8. 在 `idl-go-repo` 执行 `go mod tidy` 和 `go test ./...`。
9. `git add -A`，没有 diff 且目标分支不存在时仍 push 创建分支；没有 diff 且分支已存在时退出成功。
10. 有 diff 时提交 `chore(idl): sync go generated code from <idl-sha>` 并 push 到同名分支。

### RC Publish Workflow

新增或合并到 `idl-repo/.github/workflows/publish-go-idl.yml`，RC 支持两种触发：

- `workflow_dispatch`
- `push` 符合格式的 RC tag

输入：

- `workflow_dispatch` 输入 `idl_ref`: 冻结 IDL ref，必须能解析为 commit。
- `workflow_dispatch` 输入 `go_tag`: RC tag，例如 `v1.8.0-rc.LEN-38.20260620.<short-sha>`。
- tag push 使用 tag 指向的 IDL commit 作为冻结 IDL ref。

规则：

- `go_tag` 必须匹配 RC tag 格式，并与 `idl_ref` 短 SHA 可追溯。
- checkout `idl-repo` 的 `idl_ref`。
- checkout `idl-go-repo` 的 `master` 或发布基线分支。
- 通过 `buf.gen.go.yaml` 生成到 staging，随后同步、tidy、测试、提交。
- 创建 `idl-go-repo` tag 前必须执行 `git ls-remote --tags origin "$go_tag"`；已存在则失败。
- push commit 到发布基线分支或发布专用分支后，再 push tag。

第一版不从任意分支名自动推断 RC。RC 必须由显式输入的冻结 ref 或显式 RC tag 决定。

### Formal Publish Workflow

formal 发布由 `idl-repo` tag push 触发：

```yaml
on:
  push:
    tags:
      - "v*.*.*"
```

规则：

- tag 必须是 SemVer formal tag。
- GitHub Actions tag filter 使用 glob 触发候选 tag，workflow 内部再用正则严格校验 SemVer。
- workflow 使用 tag 指向的 IDL commit 作为唯一输入。
- Go module tag 与 `idl-repo` tag 同名，例如 `v1.8.0`。
- 创建 tag 前检查 `idl-go-repo` 远端 tag 是否存在；存在则失败。
- 不从 proto diff、commit message、分支名或业务仓依赖推断版本。

## Data / Config / Permission

- Data model: 无数据库或运行时数据变更。
- Config:
  - `idl-repo` 需要配置 `IDL_GO_REPO_TOKEN`。
  - `idl-go-repo` 需要默认分支 `master`。
  - `idl-go-repo` 需要 `go.mod`。
- Permission:
  - `IDL_GO_REPO_TOKEN` 需要 `spark-harness/idl-go-repo` contents write 权限。
  - 如果组织策略限制 tag 创建，该 token 还需要能创建 tag。
  - workflow 不记录 token 内容，只报告缺失或权限不足。

## Observability

- Logs:
  - workflow 输出触发 ref、解析后的 `idl-repo` commit、目标 branch 或 tag。
  - 失败信息区分 secret 缺失、checkout 失败、Buf 生成失败、Go 校验失败、tag 已存在和 push 失败。
- Metrics: 不新增运行时指标。
- Tracing: 无运行时 tracing。
- Events: 无业务事件。

## Testing Strategy

- 本地验证：
  - 在 `idl-repo` 运行 `buf generate`，确认 Go 输出进入 `../idl-go-repo/`。
  - 在 `idl-go-repo` 运行 `go mod tidy` 和 `go test ./...`。
- workflow 静态验证：
  - 检查 `sync-go-idl.yml` 和 `publish-go-idl.yml` 的触发条件、secret 检查和 tag 存在检查。
  - 检查 Go 生成使用 staging 目录，不能直接清理 `idl-go-repo` 仓库根目录。
- branch sync 验证：
  - 推送 `feature/LEN-38-go-idl-publishing` 后，确认 `idl-go-repo` 出现同名分支。
- RC 发布验证：
  - 以冻结 IDL commit 手动触发 RC publish。
  - 记录 Go module RC tag、`idl-repo` commit、`idl-go-repo` commit 和 workflow run。
- formal 发布验证：
  - 使用测试 SemVer tag 或受控 formal tag 验证 formal publish。
  - 重复触发同一 tag 必须失败。

## Rollout And Rollback

- Gray release:
  - 先初始化 `idl-go-repo` 的 `master` 和 Go module。
  - 再合入 branch sync workflow。
  - 最后启用 RC / formal tag publish workflow。
- Kill switch:
  - 禁用 workflow 或移除触发条件可停止新同步和新发布。
  - 不移动、不删除、不覆盖已发布 tag。
- Rollback:
  - 回滚 `idl-repo` workflow 变更。
  - 保留 `idl-go-repo` 仓库和已发布 tag。
  - 若 Go module 初始化内容错误，通过后续提交修复，不重写 tag。

## Risks

| Risk | Mitigation | Owner |
|---|---|---|
| 空仓没有默认分支导致 checkout 失败 | 实现第一步先初始化 `idl-go-repo` `master` 和 `go.mod`，再启用同步 workflow。 | Codex |
| `IDL_GO_REPO_TOKEN` 权限不足 | workflow 起始阶段检查 secret，并在 checkout / push 失败时输出目标仓库和权限说明。 | Codex |
| RC tag 格式与 LEN-35 不一致 | workflow 校验 RC tag 格式，不合规则失败。 | Codex |
| Formal tag 被重复发布 | 创建 tag 前查询远端 tag；存在即失败。 | Codex |
| branch sync 与 tag publish 生成内容不一致 | 三条链路都从 `idl-repo` 的指定 ref 执行同一 `buf generate --template buf.gen.go.yaml` + staging 同步 + Go 校验步骤。 | Codex |
| Go v2+ 未来升级破坏 module path | 第一版限定 v1 module path；v2+ 作为后续需求，必须同步更新 module path 和消费规则。 | Codex |
