# Git Workflow

Git workflow 定义一个需求从创建分支到合并完成的标准路径。

## 它不是什么

Git workflow 不是个人操作习惯，也不是强制所有项目使用同一种发布节奏。

它不替代需求流程、设计门禁或 CI。它负责把这些工程产物和 Git 分支、提交、合并动作串起来。

## 它是什么

Git workflow 规定：

- 什么时候创建分支。
- 多仓需求如何保持分支一致。
- 每个阶段应该提交什么。
- 合并前必须确认哪些门禁。
- hotfix 如何最小化风险。

## 分支类型

| Type | 用途 | 示例 |
|---|---|---|
| `feature` | 新需求或能力 | `feature/order-checkout/TAPD-12345` |
| `fix` | 普通缺陷修复 | `fix/payment-timeout/TAPD-23456` |
| `hotfix` | 线上紧急修复 | `hotfix/order-status/TAPD-34567` |
| `docs` | 学习文档或规范文档 | `docs/git-workflow/TAPD-45678` |
| `chore` | 脚手架、配置、工具维护 | `chore/harness-scripts/TAPD-56789` |

## 标准流程

### 1. 创建需求分支

在 Harness 仓创建需求分支：

```text
harness-repo: feature/{workstream}/{ticket-id}
```

如果需求涉及业务代码，同步在业务仓创建同名分支：

```text
business-repo: feature/{workstream}/{ticket-id}
```

如果需求涉及 protobuf 契约，同步在 IDL 仓创建同名分支：

```text
idl-repo: feature/{workstream}/{ticket-id}
```

学习文档仓只有在需要沉淀培训材料或方法论时才创建分支。

### 2. 需求和设计阶段

只应修改 Harness 仓：

```text
harness-repo/requirements/{requirement-id}/
harness-repo/context/
harness-repo/context/harness-framework/templates/
```

此阶段禁止提前修改业务代码，除非需求明确进入技术预研，并在需求目录中记录预研范围。

### 3. 通过需求和设计门禁

进入开发前必须满足：

```text
2.2 requirement review = PASS
3.3 design review = PASS
```

门禁结果应保存在：

```text
harness-repo/requirements/{requirement-id}/gates/
```

### 4. 开发阶段

开发阶段按影响面修改对应仓库：

| 影响类型 | 修改仓库 |
|---|---|
| 流程、需求、门禁、上下文 | `harness-repo` |
| 服务代码、测试、配置 | `business-repo` |
| `.proto`、buf 配置、生成代码 | `idl-repo` |
| 学习材料、培训文档 | `learning-docs-repo` |

如果涉及 protobuf，IDL 仓应先通过：

```text
buf lint
buf generate
buf breaking --against '.git#branch=main'
```

业务仓再消费明确的契约版本、commit 或生成产物。

### 5. 提交

提交应按仓库职责拆分：

```text
harness-repo: docs(requirement): define checkout eligibility
idl-repo: feat(order): add checkout eligibility fields
business-repo: feat(order): enforce checkout eligibility
learning-docs-repo: docs(harness): explain checkout workflow
```

禁止把业务代码、protobuf 契约和 Harness 规范混进同一个仓库提交。

### 6. 合并顺序

推荐顺序：

1. `idl-repo`：先合并契约变化。
2. `business-repo`：再合并消费契约的业务实现。
3. `harness-repo`：确认门禁、设计、任务和项目知识已更新。
4. `learning-docs-repo`：最后合并学习材料。

如果业务仓必须和 IDL 仓一起灰度，合并顺序应在设计文档中说明。

### 7. 收尾

合并后必须确认：

- 需求状态已进入交付或完成。
- 门禁报告和验收证据完整。
- 相关 `context/project/` 项目知识或经验已更新。
- 多仓分支已删除或标记归档。

## Hotfix 流程

hotfix 可以跳过完整设计文档，但不能跳过记录。

最低要求：

- 创建 `hotfix/{workstream}/{ticket-id}` 分支。
- 在 Harness 仓记录问题、影响范围、修复方案和回滚方式。
- 修改范围只覆盖线上问题。
- 合并后补齐门禁报告和经验沉淀。

hotfix 禁止顺手重构、顺手升级依赖或夹带无关需求。

## 门禁检查

Dev 进入门禁必须检查：

- 所有关联仓库分支名是否一致。
- 是否存在未记录的业务仓或 IDL 仓变更。
- 涉及 protobuf 时是否完成 buf 检查。
- 是否存在未关联需求 ID 的提交。

服务仓库检查门禁必须检查：

- `.service-matrix/dependencies.yaml` 中涉及服务是否存在。
- `repo_path` 是否能定位到业务仓服务目录。
- `proto_path` 是否能定位到 IDL 仓 `.proto` 目录。
- 当前分支是否与 Harness 仓需求分支一致。
