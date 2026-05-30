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
- 合并前必须确认哪些门禁。

## 分支

同一个需求在 Harness 仓、业务仓和 IDL 仓中应使用一致分支名。

推荐格式：

```text
feature/{workstream}/{ticket-id}
```

示例：

```text
feature/order-checkout/TAPD-12345
fix/payment-timeout/TAPD-23456
hotfix/order-status/TAPD-34567
docs/harness-gates/TAPD-45678
```

### 强制规则

- 业务需求必须从 `main` 或团队指定集成分支拉出。
- 同一个需求涉及多个仓库时，分支名必须一致。
- 禁止直接在 `main` 上提交需求变更。
- 禁止把多个无关需求混在一个分支。
- 需求分支名必须能追溯到需求 ID 或工单 ID。

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

- 摘要说明“改了什么”，正文说明“为什么这样改”。
- 涉及门禁修复时，正文记录对应门禁报告路径。
- 涉及 protobuf 契约时，正文记录 `.proto` 路径和 breaking check 结果。
- 禁止只写 `update`、`fix bug`、`wip` 作为最终提交信息。

## 评审

评审时至少确认：

- 变更是否可追溯到需求。
- 是否涉及 protobuf IDL 或外部契约。
- 是否需要更新 `context/project/` 的现状或经验。
- 是否通过当前阶段要求的门禁。
- 是否存在跨仓分支不一致。

## 合并前检查

合并前必须满足：

- 需求目录中存在对应需求、设计、任务或门禁产物。
- 当前阶段门禁为 `PASS`。
- 涉及 protobuf 时，`buf lint`、`buf generate`、`buf breaking` 有结果记录。
- 涉及关键业务状态、错误码或日志字段时，已更新对应现状文档或说明不需要更新的原因。
