# Git 规范

本规范适用于所有项目仓库，包括 Harness 仓、业务仓、protobuf 契约仓和学习文档仓。

## 它不是什么

Git 规范不是为了统一个人提交习惯，也不是为了把所有变化拆成机械的小提交。

它的目标是让需求、设计、代码、契约和门禁结果能够稳定追溯。

## 它是什么

Git 规范定义：

- 分支如何命名。
- 多仓需求如何保持同名分支。
- 提交信息如何表达意图。
- Agent 如何留下可追溯的提交上下文。
- 合并前必须确认哪些门禁。

## 分支

同一个需求在 Harness 仓、业务仓和 IDL 仓中应使用一致分支名。

推荐格式：

```text
{type}/{ticket-id}-{brief-description}
```

示例：

```text
feature/LEN-33-user-api-skeleton
fix/LEN-21-ci-package-auth
hotfix/LEN-35-order-status
docs/LEN-34-agentic-git-workflow
chore/LEN-36-harness-scripts
```

当团队需要表达业务流或模块边界时，可以使用旧格式：

```text
{type}/{workstream}/{ticket-id}
```

两种格式都必须包含 ticket ID。正式需求或治理优化的 worktree 目录仍以
ticket ID 为准，例如 `.worktrees/LEN-34/harness-repo`，不得从完整分支名
派生 worktree ID。

### 强制规则

- 业务需求必须从 `main` 或团队指定集成分支拉出。
- 同一个需求涉及多个仓库时，分支名必须一致。
- 禁止直接在 `main`、`master` 或其他受保护集成分支上提交或推送需求变更。
- 禁止把多个无关需求混在一个分支。
- 需求分支名必须能追溯到需求 ID 或工单 ID。
- `agent/<task-id>-<description>` 只用于没有正式 ticket 的临时探索；一旦有
  ticket，必须改用包含 ticket ID 的分支名。

## 提交

提交信息应使用 Conventional Commits 风格：

```text
<type>(<scope>): <summary>
```

常用类型：

| Type | 使用场景 |
|---|---|
| `feat` | 新增用户可见能力 |
| `fix` | 修复缺陷 |
| `docs` | 文档变化 |
| `refactor` | 不改变行为的结构调整 |
| `test` | 测试变化 |
| `chore` | 构建、脚手架、工具或仓库维护 |

示例：

```text
feat(order): add checkout eligibility check
fix(payment): handle provider timeout retry
docs(harness): document service repo gate
chore(idl): initialize buf v2 config
```

### 提交要求

- 一个提交只表达一个逻辑变更，并且应能独立理解、构建、测试和回滚。
- 不要把功能开发、重构、格式化、生成文件、依赖升级和文档更新混在同一
  个提交里，除非它们不可分割。
- 提交前必须检查未暂存和已暂存 diff：

```bash
git diff
git diff --staged
git status --short
```

- 暂存必须有意选择文件或 hunk，避免把本地噪声、临时文件或无关变更带入
  提交：

```bash
git add -p
git add <specific-files>
```

- 摘要说明“改了什么”，正文说明“为什么这样改”。
- 涉及门禁修复时，正文记录对应门禁报告路径。
- 涉及 protobuf 契约时，正文记录 `.proto` 路径和 breaking check 结果。
- 涉及 AI / Agent 生成、拆分、交付或风险决策时，正文可以追加 Git trailer：

```text
Agent-Task: LEN-34
Agent-Decision: split Git delivery from worktree isolation because they govern different stages
Agent-Limitation: no business code or IDL changes included
```

- 不知道模型、任务来源或限制时不要编造 trailer；缺失事实应省略。
- 禁止只写 `update`、`fix bug`、`wip` 作为最终提交信息。
- `[WIP]` 只允许作为长任务检查点提交，合并或交接前必须 squash、改写或删除。

### PR 标题

PR 标题必须同时包含 ticket ID 和 Conventional Commits 摘要：

```text
[<ticket-id>] <type>(<scope>): <summary>
```

示例：

```text
[PROJ-38] docs(harness): add PR metadata policy
```

规则：

- ticket ID 必须放在标题开头的方括号中，便于 PR 列表、通知、合并提交和
  Jira 自动关联稳定追溯。
- ticket ID 使用 `{字符串}-{数字}` 格式，不限定项目 key；例如 `LEN-38`、
  `SPARK-1`、`OPS_foo-123`。
- 方括号后的摘要必须符合提交信息的 Conventional Commits 格式。
- PR 标题不能使用 `[WIP]`、`update`、`fix bug`、`wip` 等最终交付禁用表达。
- commit message 仍保持纯 Conventional Commits；不要为了 PR 标题规则给每个
  commit subject 额外加 `[<ticket-id>]` 前缀。

## 不得提交

- 密钥、token、证书、`.env`、`*.local` 和个人 IDE 配置。
- 构建产物、依赖目录、缓存目录、临时调试文件。
- 与当前 ticket 无关的 Finder / Python / Node 噪声文件，例如 `.DS_Store`、
  `__pycache__/`、`.pyc`、`node_modules/`。
- 未经确认的生成文件；生成物必须和生成命令、输入版本一起说明。

## 评审

评审时至少确认：

- 变更是否可追溯到需求。
- 是否涉及 protobuf IDL 或外部契约。
- 是否需要更新 `context/project/` 的项目知识或经验。
- 是否通过当前阶段要求的门禁。
- 是否存在跨仓分支不一致。

## 合并前检查

合并前必须满足：

- 需求目录中存在对应需求、设计、任务或门禁产物。
- 当前阶段门禁为 `PASS`。
- 涉及 protobuf 时，`buf lint`、`buf generate`、`buf breaking` 有结果记录。
- 涉及关键业务状态、错误码或日志字段时，已更新对应项目知识文档或说明不需要更新的原因。
