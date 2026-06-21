---
requirement_id: "LEN-42"
owner: "Codex"
status: "approved"
updated_at: "2026-06-21"
approved_by: "Forest"
approved_at: "2026-06-21T13:18:10+08:00"
decision: "批准 LEN-42 design，允许进入任务拆分。"
---

# Design

## Requirement Traceability

| Requirement Item | Design Decision | Notes |
|---|---|---|
| R1, R4, AC1 | D1: 在 `buf.gen.yaml` 的 4 个 `remote` 字段后追加已确认插件版本 | 不改变输出目录、opt 或 managed mode |
| R2, R3, AC2 | D2: 在 `buf.gen.go.yaml` 中使用与 `buf.gen.yaml` 相同的 Go 插件版本 | 避免两份生成模板漂移 |
| R5, AC3, AC4 | D3: 用 Buf 命令验证配置，并在 evidence 中记录 `buf.lock` 边界 | 该需求不创建 `buf.lock` |
| BR4 | D4: 本票不写 `revision` 字段 | revision 需要独立来源，不能猜测 |

## Summary

本设计将当前已使用的 Buf 远程生成插件显式锁定到 2026-06-21 已确认的 BSR 最新版本。锁定位置只在 `idl-repo` 的生成模板中，不改 proto schema，不改 generated contract 仓库，不改业务仓。

版本基线：

| Plugin | Version |
|---|---|
| `buf.build/protocolbuffers/go` | `v1.36.11` |
| `buf.build/grpc/go` | `v1.6.2` |
| `buf.build/protocolbuffers/java` | `v35.1` |
| `buf.build/grpc/java` | `v1.82.0` |

## Affected Services

| Service | Change | Reason |
|---|---|---|
| IDL generation config | Lock remote plugin versions in `buf.gen.yaml` and `buf.gen.go.yaml` | Make code generation input reproducible |
| Harness lifecycle | Record requirement, impact, design, task, evidence, and gates for LEN-42 | Keep governance traceable |

## API / Contract Design

- Protobuf IDL required: No schema change; IDL repo config change only。
- Proto files: none。
- Buf module: current `idl-repo/buf.yaml` v2 workspace module。
- Buf config version: v2。
- Generated outputs: command may write to existing configured output paths during verification, but generated contract repos are not part of this change.
- Breaking check baseline: `origin/master` for the isolated worktree.
- Compatibility strategy: config-only compatible change. Existing proto definitions and service contracts remain unchanged.

Target `buf.gen.yaml` remote values:

```yaml
remote: buf.build/protocolbuffers/go:v1.36.11
remote: buf.build/grpc/go:v1.6.2
remote: buf.build/protocolbuffers/java:v35.1
remote: buf.build/grpc/java:v1.82.0
```

Target `buf.gen.go.yaml` remote values:

```yaml
remote: buf.build/protocolbuffers/go:v1.36.11
remote: buf.build/grpc/go:v1.6.2
```

`revision` is intentionally omitted. The current task has confirmed plugin versions from BSR pages, but not the corresponding BSR revision sequence for each plugin version. Guessing revision would create a false lock.

## Data / Config / Permission

- Data model: none。
- Config: `buf.gen.yaml` and `buf.gen.go.yaml` remote plugin refs。
- Permission: none。

## Observability

- Logs: none。
- Metrics: none。
- Tracing: none。
- Events: none。

## Rollout And Rollback

- Gray release: not applicable。
- Kill switch: not required。
- Rollback: revert the two generation template changes and rerun Buf checks.

## Risks

| Risk | Mitigation | Owner |
|---|---|---|
| Locked version exposes generated output differences compared with previous implicit latest cache | Treat output differences as review evidence; do not commit generated repos in this ticket | Platform |
| Future plugin upgrade is forgotten | Future upgrades should be explicit ticketed changes with BSR version check and Buf verification | Platform |
| Local stale `master` causes breaking check false positive | Prefer `origin/master` baseline in this isolated worktree and record exact command | Platform |
