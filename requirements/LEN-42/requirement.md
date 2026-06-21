---
requirement_id: "LEN-42"
owner: "Codex"
status: "approved"
created_at: "2026-06-21"
related_branch: "feature/LEN-42-buf-plugin-version-lock"
target_branch: "master"
release_branch: "master"
contract_gate_mode: "auto"
affected_repositories:
  - harness-repo
  - idl-repo
approved_by: "Forest"
approved_at: "2026-06-21T13:18:00+08:00"
decision: "批准 LEN-42 requirement 与 impact-analysis，允许进入设计阶段。"
---

# 锁定 Buf 远程生成插件版本

## Background

当前 `idl-repo/buf.gen.yaml` 和 `idl-repo/buf.gen.go.yaml` 使用 Buf 远程生成插件，但 `remote` 字段没有声明版本号。按 Buf 规则，未声明版本会使用最新版本。

这会让同一份 protobuf 在不同时间运行 `buf generate` 时可能使用不同生成器，进而造成生成代码、运行时依赖提示或审计证据漂移。对 Spark 多仓契约治理来说，生成输入必须可追溯，否则后续 Java / Go generated contract 的发布证据不完整。

先说不是什么：这不是新增 proto 业务契约，也不是引入外部 proto deps。`buf.lock` 只锁 `buf.yaml deps` 中的外部模块依赖，不锁生成插件。本需求要锁的是 `buf.gen.yaml` 里的远程生成插件版本。

## Goals

- R1：`idl-repo/buf.gen.yaml` 中当前使用的 4 个远程插件必须显式声明版本号。
- R2：`idl-repo/buf.gen.go.yaml` 中 Go 相关远程插件必须显式声明版本号。
- R3：同一个插件在 `buf.gen.yaml` 和 `buf.gen.go.yaml` 中出现时，版本必须一致。
- R4：保留现有输出目录、managed mode、Go package prefix 和生成语言集合，不夹带发布策略或业务契约变化。
- R5：通过 Buf 校验和生成命令证明配置变更可执行，并记录 `buf.lock` 与远程插件版本锁定的边界。

## Non-Goals

- 不修改 `.proto` 文件、protobuf package、字段、RPC 或业务语义。
- 不创建 `buf.lock`，因为当前 `buf.yaml` 没有外部 `deps`。
- 不修改 `idl-java-repo`、`idl-go-repo` 或 business service 代码。
- 不改变 Java / Go generated contract 的发布、tag、artifact 或消费规则。
- 不在本需求中强制锁定 `revision`；如后续需要 revision，必须先确认每个插件版本对应的 BSR revision 来源。

## User / Business Scenarios

### Scenario 1：团队查看 IDL 生成配置

Given：工程师查看 IDL 生成配置。

When：打开 `buf.gen.yaml` 或 `buf.gen.go.yaml`。

Then：所有远程生成插件都带有明确版本号，而不是隐式使用 latest。

### Scenario 2：本地和 CI 复现生成输入

Given：同一分支在不同时间执行 `buf generate`。

When：Buf 解析远程插件。

Then：生成器版本保持一致，不因 BSR 最新版本变化而漂移。

### Scenario 3：解释依赖锁定边界

Given：Reviewer 看到本需求没有新增 `buf.lock`。

When：检查需求、设计或证据。

Then：可以明确看到 `buf.lock` 管理 proto module deps，远程生成插件由 `buf.gen.yaml` 的 `remote:<version>` 管理。

## Business Rules

- BR1：IDL 生成配置不得依赖未声明版本的远程插件。
- BR2：`protocolbuffers/go` 和 `grpc/go` 在两份生成模板中必须使用同一版本。
- BR3：本需求使用当前 BSR 最新版本作为初始锁定基线：`protocolbuffers/go v1.36.11`、`grpc/go v1.6.2`、`protocolbuffers/java v35.1`、`grpc/java v1.82.0`。
- BR4：没有明确 revision 基线时，只锁 plugin version；后续 revision 锁定必须有独立证据来源。
- BR5：配置更新后必须运行 `buf lint`、`buf generate` 和 breaking check，并记录结果。
- BR6：如果生成命令产生未预期生成物漂移，不能静默提交，必须记录差异范围和处理结论。

## Acceptance Criteria

- AC1：`buf.gen.yaml` 的 `protocolbuffers/go`、`grpc/go`、`protocolbuffers/java`、`grpc/java` 都带版本号。
- AC2：`buf.gen.go.yaml` 的 `protocolbuffers/go`、`grpc/go` 都带版本号，且与 `buf.gen.yaml` 中对应版本一致。
- AC3：需求或证据明确说明 `buf.lock` 不用于锁远程生成插件。
- AC4：`buf lint`、`buf generate` 和 breaking check 有执行结果记录。
- AC5：最终 diff 不包含 `.proto`、业务代码或 generated contract 仓库的无关变更。

## Open Questions

| Question | Owner | Deadline | Status |
|---|---|---|---|
| 是否同时锁定 remote plugin revision | Platform | 后续生成治理增强 | Deferred：本票先锁 plugin version，revision 需另行确认来源 |

## Notes

- JIRA `LEN-42` 已记录该优化目标。
- 2026-06-21 通过 BSR 插件页确认当前最新版本基线。
