# CI/CD 与门禁规范

本文定义团队第一版交付检查口径。

它不是某个流水线实现说明，也不替代 `git-workflow.md` 或 Harness gate 文档。具体 Argo/GitHub 配置以 `gitops-repo` 和各仓 CI 文件为准。

## 最小规则

| 场景 | 必须检查 |
|---|---|
| 文档和 Harness 规则 | diff、链接、Janus gate 或 requirement verify |
| Java 代码 | `mvn test` 或模块等价命令 |
| TypeScript 代码 | lint、typecheck、test、build 中项目声明的必要命令 |
| Go 代码 | `go test ./...`、`go vet ./...` 或项目等价命令 |
| IDL | `buf lint`、`buf generate`、`buf breaking` |
| 契约消费 | `contract-versioning.md` 要求的版本和追溯证据 |

## PR 必填信息

PR 描述必须包含：

- ticket 或 requirement ID。
- 影响仓库和分支。
- 已运行命令和结果。
- 未运行验证和原因。
- gate/evidence 路径。
- 风险和回滚方式。

PR 标题遵守 `git.md`：

```text
[<ticket-id>] <type>(<scope>): <summary>
```

## 门禁判断

- 本地测试通过不等于交付完成。
- CI 失败必须先读失败日志，再判断是代码、权限、依赖、分支还是门禁输入问题。
- Harness gate、delivery-readiness、业务 CI 是不同信号，不能互相替代。
- 如果门禁依赖 requirement、impact、design、tasks 或 evidence，缺失源文件时必须补源文件，不用聊天结论替代。

## 失败处理

| 失败类型 | 处理方式 |
|---|---|
| 测试失败 | 先复现最小失败命令，再修代码或测试 |
| 权限失败 | 检查 token、repo/package 权限和 secret，而不是先改业务逻辑 |
| 契约失败 | 检查 IDL 兼容性、生成物版本和消费者依赖 |
| 分支失败 | 检查 `related_branch`、`target_branch`、`release_branch` 和 peer repo 状态 |
| 文档门禁失败 | 检查 lifecycle 文件、gate JSON 输入 hash 和审批状态 |

## 合并前检查

合并前至少确认：

- 目标 PR 只包含当前 ticket 范围。
- 所有必需测试或明确豁免已记录。
- Gate JSON 或 CI 状态能追溯到当前 commit。
- 需要的项目知识、服务矩阵或团队规范已同步更新。
- 回滚方式明确。
