---
requirement_id: "LEN-113"
owner: "Forest"
status: "approved"
created_at: "2026-06-25T21:23:21+08:00"
related_branch: "chore/LEN-113-governance-drift"
target_branch: "master"
release_branch: "master"
contract_gate_mode: "auto"
affected_repositories:
  - harness-repo
  - business-repo
  - janus
approved_by: "Forest"
approved_at: "2026-06-25T21:27:13+08:00"
decision: "批准 LEN-113 需求与影响分析，允许进入设计阶段。"
---

# 修复 Spark 工作区治理与主干事实漂移

## Background

先说不是什么：这不是业务功能开发票，也不是 business-repo 三目录迁移重构票。

它是 Spark 主工作区治理漂移修复票。当前风险是 Harness 文档、AGENTS 指令、业务仓状态判断、Janus 交付仓库推断和 runtime mirror 检查可能继续引用过时事实，导致后续需求被错误路径、缺失仓库或本地残留误导。

## Goals

- 修正 Harness 模板路径说明，使团队和 Agent 都指向 `context/harness-framework/templates/`。
- 重新扫描 business-repo 当前目录，证明服务路径以 `apps/*` 和服务矩阵为准，旧 `services/*` 不再是有效事实源。
- 校准 Janus 交付检查或仓库推断，使治理相关仓库不会被旧生成仓假设遗漏。
- 验证 runtime mirror 无漂移，并把检查结果作为交付证据。

## Non-Goals

- 不修改业务功能行为。
- 不发布新的 IDL 契约。
- 不修改 protobuf、Buf 配置或 generated contracts。
- 不重构 business-repo 三目录迁移方案。
- 不把更大范围技术债或治理重构塞进本票。

## User / Business Scenarios

### Scenario 1: 查找可复用模板

Given:

- 研发或 Agent 阅读 Harness 文档和 AGENTS 指令。

When:

- 需要查找需求生命周期模板。

Then:

- 文档指向 `context/harness-framework/templates/` 这一事实源。
- 文档不再要求不存在的 `harness-repo/templates`。

### Scenario 2: 判断 business-repo 服务路径

Given:

- business-repo 当前目录结构已经迁移到 `apps/`、`packages/`、`tooling/` 和 `config/`。

When:

- 研发或 Agent 执行 `git status`、扫描目录和定位服务路径。

Then:

- 主 checkout 不被旧 `services/*` 残留污染。
- 服务路径以 `.service-matrix/dependencies.yaml` 和 business-repo README 中的 `apps/*` 为准。
- 如果 `services/*` 不存在，记录为正确状态，不创建 business-repo 代码改动。

### Scenario 3: Janus 推断治理相关仓库

Given:

- 需求文本或交付证据提到治理相关仓库。

When:

- Janus 根据文本推断受影响仓库，或执行相关交付检查。

Then:

- 推断覆盖当前治理相关仓库集合。
- 生成契约仓缺失时按需求影响范围明确处理，不把缺失生成仓误判为本票必须修改。

### Scenario 4: 检查 runtime mirror 漂移

Given:

- Harness 治理资产、skills、agents、commands 或 rules 已完成修复。

When:

- 运行 `harness-repo/scripts/install.sh --check`。

Then:

- 检查通过。
- 验证结果记录为验收证据。

## Business Rules

- BR1: Harness 模板说明只能指向当前真实存在的模板事实源，不能继续声明不存在的根 `templates` 目录。
- BR2: 服务路径以服务矩阵和 business-repo 当前 README 为准，旧 `services/*` 残留不得继续污染主 checkout 的状态判断。
- BR3: Janus 交付检查和仓库推断应覆盖当前实际参与治理和交付的仓库集合，不能只保留旧生成仓假设。
- BR4: runtime mirror 修复后必须通过 `install.sh --check` 证明无漂移。

## Acceptance Criteria

| AC | Given | When | Then |
|---|---|---|---|
| AC1 | Harness 文档和 AGENTS 指令描述模板位置 | 研发或 Agent 查找可复用模板 | 文档指向 `context/harness-framework/templates/`，不再要求不存在的 `harness-repo/templates` |
| AC2 | business-repo 当前目录已迁移，`services/*` 不存在 | 执行 git status、目录扫描和服务路径定位 | 记录扫描验证结果；不创建 business-repo 代码改动；服务路径仍以 `apps/*` 和服务矩阵为准 |
| AC3 | Janus 根据需求文本或交付证据推断受影响仓库 | 执行相关交付检查或代码审查 | 仓库推断覆盖当前治理相关仓库，并明确生成契约仓缺失时的处理方式 |
| AC4 | 完成治理资产或 runtime mirror 相关修复 | 运行 `harness-repo/scripts/install.sh --check` | 检查通过并记录为验收证据 |

## Open Questions

| Question | Owner | Deadline | Status |
|---|---|---|---|
| Draft PR #21 和 #6 是否在 requirement-review、design-review、dev-entry 通过后恢复 Ready for review | Forest | 合并前 | open |

## Notes

- 2026-06-25 用户已批准 Requirement Brief，允许创建需求文档进入下一阶段。
- 2026-06-25 已将错误提前创建的 PR 转为 Draft，防止未经过生命周期门禁的变更被合并。
- 2026-06-25 重新扫描确认 `business-repo/services/*` 不存在是正确状态，AC2 应记录扫描验证而不是制造 business-repo diff。
