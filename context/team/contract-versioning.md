# 契约版本治理规范

本文定义 IDL 生成契约的发布、冻结、消费和门禁规则。

它不是什么：它不是 Git branching 模型，不规定团队是否使用 epic 分支；也不是契约兼容性规则的替代品。字段、RPC、HTTP、事件和错误码的兼容性仍以 `contract-compatibility.md` 为准。

它是什么：它规定业务仓消费 Java / Go 生成契约时，哪些版本可以用于开发、合并候选和 master-bound 变更，以及这些版本必须如何追溯。

## 发布阶段

契约版本分为三类：

| 阶段 | 用途 | 可进入 master | 示例 |
|---|---|---|---|
| `development` | 本地开发和 ticket 内联调 | 否 | `1.8.0-LEN-35-SNAPSHOT`、Go pseudo-version、local `replace` |
| `rc` | 冻结 IDL commit 后的合并候选验证 | 否 | `1.8.0-rc.LEN-35.20260620.a1b2c3d` |
| `formal` | master-bound 业务变更和正式发布 | 是 | `1.8.0`、Go `v1.8.0` |

`rc` 不绑定特定分支命名，但必须来自冻结的 IDL commit。

`formal` 版本事实来源是 `idl-repo` 中人工创建的 SemVer tag。发布 CI 必须使用该 tag 对应 commit 作为唯一输入。

## Java 契约版本

Java 开发期 artifact 必须使用 ticket scoped snapshot：

```text
{base-version}-{ticket-id}-SNAPSHOT
```

Java RC artifact 必须使用不可变版本：

```text
{base-version}-rc.{ticket-id}.{yyyymmdd}.{idl-short-sha}
```

Java formal artifact 必须使用 SemVer：

```text
1.8.0
1.9.0
2.0.0
```

禁止并发 feature 共享同一个普通 `SNAPSHOT`，例如 `1.8.0-SNAPSHOT`。

RC 和 formal Maven artifact 不得覆盖发布。重新发布已存在的 RC 或 formal 版本必须失败。

## Go 契约版本

Go 契约代码由 Buf 生成，但通过自有 `idl-go-repo` 的 Go module tag 分发。

Go pseudo-version 或 local `replace` 只允许用于本地开发，不得作为 merge-ready 或 master-bound 依赖。

Go `v0` 和 `v1` 的 module path 不得包含 `/v0` 或 `/v1`。

Go `v2+` 的 module path 必须包含 `/vN`。`module` directive、`require` path、import path、tag version 和消费证据中的 major version 必须一致。

禁止生成契约模块使用 `+incompatible`。

正确示例：

```go
module github.com/acme/user-contract-go/v2

require github.com/acme/user-contract-go/v2 v2.0.0-rc.len35.20260620.a1b2c3d
```

错误示例：

```go
require github.com/acme/user-contract-go v2.0.0
```

## Formal 发布

Formal 发布由人工在 `idl-repo` 创建 SemVer tag 触发，例如：

```text
v1.1.0
```

发布 CI 必须：

1. 读取 tag 指向的 `idl-repo` commit。
2. 对该 commit 执行 Buf build / generate。
3. 发布 Java Maven artifact。
4. 发布 Go module tag。
5. 保留 CI run 记录和 artifact metadata。

CI 不得从 proto diff、commit message、分支名或业务仓依赖自动推断 formal 版本。

Formal tag 不得移动、删除或 force-push。

## Master-bound 消费规则

Master-bound business change 只能消费 formal version。

以下依赖不得进入 master：

- RC。
- 普通或 ticket scoped `SNAPSHOT`。
- Go pseudo-version。
- Branch dependency。
- Local `replace`。
- 无法解析到线上 artifact 或 tag 的版本。

不设置允许 RC 进入 master 的批准例外路径。

## 追溯证据

不要求 Traceability Manifest。

最小追溯证据包括：

- `idl-repo` tag。
- tag 指向的 IDL commit。
- 发布 CI run ID 或等价链接。
- Java artifact 坐标和 artifact metadata。
- Go module path 和 module tag。
- 业务仓 consumer commit。
- 业务仓测试命令和结果。

Merge-readiness 必须记录这些证据，证明业务仓消费的契约版本可复现。

## Worktree 规则

普通 IDL 变更不自动要求 `idl-java-repo` 或 `idl-go-repo` 进入 worktree。

默认 worktree 只包含实际需要编辑的仓库。例如只定义需求和 IDL 规则时，通常只需要：

```text
.worktrees/{ticket-id}/harness-repo
.worktrees/{ticket-id}/idl-repo
```

只有需要修改生成仓发布流水线、发布脚本、仓库结构或生成物源码时，才把 `idl-java-repo` 或 `idl-go-repo` 加入 worktree。

## 门禁检查

Merge-readiness 应检查：

- Maven 文件没有共享或非允许阶段的 `SNAPSHOT`。
- `go.mod` 没有 contract local `replace`。
- 依赖没有使用 branch name。
- Master-bound 变更没有消费 RC、SNAPSHOT、pseudo-version 或 local replacement。
- Formal 版本可以解析到已发布 Java artifact 或 Go module tag。
- Formal 版本来自 `idl-repo` SemVer tag。
- Go module path 和 version major 匹配。
- 业务依赖版本、consumer commit 和测试结果已记录。

门禁输出必须是机器可读的 gate JSON；历史 gate Markdown 只作为旧审计快照。
