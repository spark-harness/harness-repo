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
- Agent 执行提交、推送和 PR/MR 时如何保持可追溯。
- 合并前必须确认哪些门禁。
- hotfix 如何最小化风险。

## 分支类型

| Type | 用途 | 示例 |
|---|---|---|
| `feature` | 新需求或能力 | `feature/LEN-33-user-api-skeleton` |
| `fix` | 普通缺陷修复 | `fix/LEN-21-ci-package-auth` |
| `hotfix` | 线上紧急修复 | `hotfix/LEN-35-order-status` |
| `docs` | 学习文档或规范文档 | `docs/LEN-34-agentic-git-workflow` |
| `chore` | 脚手架、配置、工具维护 | `chore/LEN-36-harness-scripts` |

旧格式 `{type}/{workstream}/{ticket-id}` 仍可用于需要表达业务流的需求，但同
一个 ticket 的所有仓库必须完全同名。

## 分支声明模型

多仓需求必须在 `requirement.md` front matter 中声明三类分支：

```yaml
related_branch: "feature/LEN-40-delivery-flow"
target_branch: "epic/lending"
release_branch: "master"
contract_gate_mode: "auto"
affected_repositories:
  - harness-repo
  - business-repo
  - idl-repo
```

它不是什么：这不是要求 peer repo 的 feature 分支永久存在。

它是什么：`related_branch` 表示本需求开发分支，`target_branch` 表示当前 PR
要合入的分支，`release_branch` 表示最终发布分支。

Janus 按以下规则判断交付阶段：

```text
target_branch == release_branch => release-bound => formal-only
target_branch != release_branch => integration-bound => rc-or-formal
```

integration-bound 合法 peer repo 状态：

1. peer repo 存在同名 `related_branch`。
2. peer repo 的 `related_branch` 已合入 `target_branch`。
3. peer repo 的 `target_branch` 已合入 `release_branch`。

release-bound 合法 peer repo 状态：

1. peer repo 的 `related_branch` 已合入 `release_branch`。
2. peer repo 的 `target_branch` 已合入 `release_branch`。
3. PR gate 阶段存在同一 requirement 的 `related_branch -> release_branch`
   open PR。

feature 分支被合并或清理后，只要 Git / PR / tag 证据能证明已合入 target 或
release，delivery readiness 不应失败。open PR 证据只表示待合并状态，不替代
最终发布时的 merge、Formal tag 和 artifact 证据。

## 标准流程

### 1. 创建需求分支

在 Harness 仓创建需求分支：

```text
harness-repo: feature/{ticket-id}-{brief-description}
```

如果需求涉及业务代码，同步在业务仓创建同名分支：

```text
business-repo: feature/{ticket-id}-{brief-description}
```

如果需求涉及 protobuf 契约，同步在 IDL 仓创建同名分支：

```text
idl-repo: feature/{ticket-id}-{brief-description}
```

学习文档仓只有在需要沉淀培训材料或方法论时才创建分支。

正式需求和治理优化必须先绑定 ticket ID。worktree 路径使用 ticket ID：

```text
.worktrees/{ticket-id}/harness-repo
.worktrees/{ticket-id}/business-repo
.worktrees/{ticket-id}/idl-repo
```

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

Agent 执行提交时必须先做三件事：

1. 在所有 Spark 子仓分别检查 `git status --short --branch`。
2. 只暂存当前 ticket 相关文件，并检查 `git diff --staged`。
3. 清理或排除本地噪声文件，例如 `.DS_Store`、`__pycache__/`、`.pyc`。

长任务可以使用 `[WIP]` 检查点提交记录阶段进展。检查点提交只用于临时交接，
进入 PR/MR 或最终交付前必须整理成语义提交。

### 6. PR / MR

PR / MR 标题必须使用：

```text
[<ticket-id>] <type>(<scope>): <summary>
```

示例：

```text
[PROJ-38] docs(harness): add PR metadata policy
```

PR / MR 描述必须说明行为和验证，而不只是列出文件。

建议模板：

```markdown
## Task

## What Changed

## Key Decisions

## Validation

## Gates / Evidence

## Risks / Follow-up

## Review Guidance
```

必填信息：

- ticket ID 或 requirement ID。
- 涉及的仓库和分支。
- 已运行的测试、lint、Janus gate 或 requirement verify 命令。
- 未运行的验证和原因。
- 需要人工重点评审的风险点。

`pr-metadata` CI 会在 PR 进入评审前检查：

- 标题以 `[<ticket-id>]` 开头，并且后半段符合 Conventional Commits。
- ticket ID 使用 `{字符串}-{数字}` 格式，不限定项目 key。
- 描述包含上述模板章节，并引用同一个 ticket ID。
- PR 内人工提交符合 Conventional Commits；自动生成提交允许明确例外。

`harness-repo` 保存 PR metadata policy 的脚本和 reusable workflow。其他 Spark
子仓接入时，只添加调用该 reusable workflow 的轻量 workflow，不复制规则实现。

当一个 ticket 天然需要多个可独立评审的层次时，可以使用堆叠 PR / MR。每一
层都必须有聚焦 diff，并保持中间分支可构建、可测试。

### 7. 历史清理

创建 PR/MR 或交接分支前，检查当前分支相对集成分支的提交：

```bash
git log --oneline origin/master..HEAD
```

清理目标：

- 将 `[WIP]` 检查点提交整理成有意义的语义提交。
- 改写含糊的提交信息。
- 删除临时探索提交。
- 保留的每个提交都应可评审、可追溯、可独立理解。
- 共享分支不得随意 force-push；需要改写共享历史时先给出计划并等待确认。

### 8. 合并路径和顺序

支持两类路径：

```text
feature -> master
feature -> epic/foo -> master
```

`feature -> master` 是 release-bound：contract dependency 只能使用 formal。

`feature -> epic/foo` 是 integration-bound：contract dependency 禁止 SNAPSHOT，
但可以使用 immutable RC 或 formal。

`epic/foo -> master` 重新进入 release-bound：contract dependency 只能使用 formal。

推荐顺序：

1. `idl-repo`：先合并契约变化。
2. `business-repo`：再合并消费契约的业务实现。
3. `harness-repo`：确认门禁、设计、任务和项目知识已更新。
4. `learning-docs-repo`：最后合并学习材料。

如果业务仓必须和 IDL 仓一起灰度，合并顺序应在设计文档中说明。

### 9. 收尾

合并后必须确认：

- 需求状态已进入交付或完成。
- 门禁报告和验收证据完整。
- 相关 `context/project/` 项目知识或经验已更新。
- 多仓分支已删除或标记归档。

## Hotfix 流程

hotfix 可以跳过完整设计文档，但不能跳过记录。

最低要求：

- 创建 `hotfix/{ticket-id}-{brief-description}` 分支。
- 在 Harness 仓记录问题、影响范围、修复方案和回滚方式。
- 修改范围只覆盖线上问题。
- 合并后补齐门禁报告和经验沉淀。

hotfix 禁止顺手重构、顺手升级依赖或夹带无关需求。

## 门禁检查

Dev 进入门禁必须检查：

- 所有关联仓库是否满足当前阶段的 peer repo 状态。
- 是否存在未记录的业务仓或 IDL 仓变更。
- 涉及 protobuf 时是否完成 buf 检查。
- 是否存在未关联需求 ID 的提交。

服务仓库检查门禁必须检查：

- `.service-matrix/dependencies.yaml` 中涉及服务是否存在。
- `repo_path` 是否能定位到业务仓服务目录。
- `proto_path` 是否能定位到 IDL 仓 `.proto` 目录。
- `related_branch`、`target_branch`、`release_branch` 是否能被 Janus delivery
  verifier 识别。

各仓 workflow 不应复制 peer 分支判断 bash。CI 应调用：

```bash
janus delivery verify --requirement <REQ-ID> --repo <repo-name>
```
