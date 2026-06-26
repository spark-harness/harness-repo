---
requirement_id: "LEN-126"
owner: "core"
status: "approved"
created_at: "2026-06-27"
related_branch: "docs/LEN-126-team-engineering-docs"
target_branch: "master"
release_branch: "master"
contract_gate_mode: "auto"
affected_repositories:
  - harness-repo
approved_by: "forest"
approved_at: "2026-06-27T00:31:10+08:00"
decision: "用户明确授权允许编写各类所需文档直至 PR 通过；批准 LEN-126 第一版团队工程文档范围、设计和任务拆分，范围限定为 harness-repo 文档治理，不涉及业务代码、IDL、生成契约、学习文档新人快速开始或 .spark/skills。"
---

# 补齐第一版团队工程文档

## Background

团队已经有 Harness 上下文、Git、测试、契约和部分可观测性规范，但工程成员和 Agent 仍缺少一组完整的第一版入口文档。

这不是一次写成大而全知识库，也不是把所有经验沉淀成冗长规范。第一版只要求文档能指导真实工作：去哪看、怎么做、例外放哪里、如何验证。

## Goals

- 补齐团队工程文档索引，让团队成员能快速找到语言、测试、契约、Git、CI/CD、运行质量和本地开发规范。
- 补齐 Java、TypeScript、Go 的最小工程规范。
- 补齐服务矩阵、Harness 生命周期、门禁、模板和项目知识入口的第一版说明。
- 保持文档实用、精简、言而有物、落地性强。

## Non-Goals

- 不新增 `docs/learning-docs-repo/newcomer-quick-start.md`。
- 不新增或修改 `harness-repo/.spark/skills/...` Agent 工作指南或 skill。
- 不修改业务代码、IDL、生成契约、真实服务矩阵数据或 CI 工作流行为。
- 不追求一次性覆盖所有工程治理细节。

## User / Business Scenarios

### Scenario 1: 查找团队规范

Given: 团队成员或 Agent 进入 Harness 文档上下文。

When: 需要查找某类工程规范。

Then: 可以通过 `context/team/INDEX.md` 找到对应入口。

### Scenario 2: 修改语言相关代码

Given: 需要修改 Java、TypeScript 或 Go 代码。

When: 阅读对应语言规范。

Then: 能知道目录分层、错误处理、日志、测试、依赖和契约消费的最小团队约定。

### Scenario 3: 推进 Harness 需求

Given: 需要按 Harness 流程推进需求。

When: 阅读 lifecycle、gates 和 templates 说明。

Then: 能理解 requirement、impact-analysis、design、tasks、evidence/gate 的顺序、作用和模板入口。

## Business Rules

- BR1 文档必须优先解决真实工作中的查找、判断和执行问题，不写空泛方法论。
- BR2 每份新增或重写文档都要说明适用范围、不适用范围和最小执行规则。
- BR3 跨项目团队规范放在 `context/team/`。
- BR4 Harness 生命周期、门禁和模板口径放在 `context/harness-framework/`。
- BR5 服务特例放在 `context/project/`，服务路由放在 `.service-matrix/`。
- BR6 第一版覆盖核心文档面，但每份文档只写最小可执行内容。

## Acceptance Criteria

| AC | Given | When | Then |
|---|---|---|---|
| AC1 | 团队成员进入 Harness 文档上下文 | 查找团队工程规范入口 | 可以通过 `context/team/INDEX.md` 找到团队文档索引、Java、TypeScript、Go、测试、契约、Git、CI/CD、可观测性、安全、数据库和本地开发相关入口 |
| AC2 | 需要修改 Java、TypeScript 或 Go 代码 | 阅读对应语言规范 | 能知道包/目录分层、错误处理、日志、测试、依赖和契约消费的最小团队约定 |
| AC3 | 需要补测试、评估契约影响或判断 PR 是否可交付 | 阅读 testing、contract-versioning、git、git-workflow 和 ci-cd 文档 | 能知道必须执行或检查的最小测试、兼容性、提交、评审、门禁和交付规则 |
| AC4 | 需要处理运行质量问题 | 阅读 observability、security、database、local-development 文档 | 能知道日志/指标/告警、安全边界、数据库变更和本地启动调试的第一版团队约定 |
| AC5 | Agent 或新人需要判断某个服务应该加载哪类规范 | 阅读 `.service-matrix/README.md` | 能理解服务矩阵中 repo、language、runtime、idl、owner、deploy 等字段的路由作用 |
| AC6 | 需要按 Harness 流程推进需求 | 阅读 lifecycle、gates 和 templates | 能理解 requirement、impact-analysis、design、tasks、evidence/gate 的顺序、作用和最小模板入口 |
| AC7 | 需要记录项目或服务特例 | 阅读 `context/project/INDEX.md` 和服务级上下文示例 | 能知道项目知识入口在哪里、服务级例外应该写在哪里、哪些内容不应复制到团队通用规范 |
| AC8 | 文档评审时 | 检查内容表达 | 每份新增或更新文档都精简、实用、言而有物，包含可执行规则或最小示例，没有大而全的空泛段落 |
| AC9 | 评审交付范围时 | 检查本票排除项 | 确认没有新增新人快速开始文档，也没有新增或修改 Agent skill 工作指南 |

## Open Questions

| Question | Owner | Deadline | Status |
|---|---|---|---|
| Python 是否需要纳入第一版语言规范 | core | 后续按服务矩阵需要确认 | Deferred |

## Notes

- Jira 来源：`LEN-126`。
- 第一版文档以可用为先，后续根据真实评审和使用反馈继续拆票优化。
