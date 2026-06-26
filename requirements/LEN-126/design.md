---
requirement_id: "LEN-126"
owner: "core"
status: "approved"
updated_at: "2026-06-27"
approved_by: "forest"
approved_at: "2026-06-27T00:31:10+08:00"
decision: "用户明确授权允许编写各类所需文档直至 PR 通过；批准 LEN-126 第一版团队工程文档范围、设计和任务拆分，范围限定为 harness-repo 文档治理，不涉及业务代码、IDL、生成契约、学习文档新人快速开始或 .spark/skills。"
---

# Design

## Requirement Traceability

| Requirement Item | Design Decision | Notes |
|---|---|---|
| AC1 | 更新 `context/team/INDEX.md` | 作为团队规范入口 |
| AC2 | 新增 `java.md`、`typescript.md`、`go.md` | 语言规范只写跨项目最小约定 |
| AC3 | 新增 `ci-cd.md`，复用测试、契约、Git 既有文档 | 不重复定义已有完整规则 |
| AC4 | 新增 `observability.md`、`database.md`、`local-development.md`，扩展 `security.md` | 运行质量文档写第一版执行规则 |
| AC5 | 新增 `.service-matrix/README.md` | 说明字段、维护和路由 |
| AC6 | 新增 `lifecycle.md`、`gates.md`，补模板说明 | 对现有流程和门禁文档做可读入口 |
| AC7 | 更新 `context/project/INDEX.md` 并提供服务上下文模板 | 明确项目和服务特例位置 |
| AC8 | 所有新增文档采用短段落、表格和步骤 | 保持精简可执行 |
| AC9 | 不修改 `docs/learning-docs-repo` 和 `.spark/skills` | 交付前用 diff 验证 |

## Summary

方案以“入口清晰、规则单一来源、第一版最小可用”为原则。已有完整文档不重写，只在索引中补齐入口；缺失文档新增轻量版本；过薄文档补到能指导执行。

## Affected Services

| Service | Change | Reason |
|---|---|---|
| N/A | Harness 文档更新 | 本需求不修改业务服务 |

## API / Contract Design

- Protobuf IDL required: No
- Proto files: N/A
- Buf module: N/A
- Buf config version: unchanged
- Generated outputs: N/A
- Breaking check baseline: N/A
- Compatibility strategy: N/A

## Application Design

- `context/team/` 保存跨项目工程规范。
- `context/harness-framework/` 保存 Harness 生命周期、门禁和模板口径。
- `.service-matrix/` 保存服务矩阵说明和矩阵数据。
- `context/project/` 保存项目、领域、服务级知识入口。
- `requirements/LEN-126/` 保存本次文档治理的追溯文件。

## Data / Config / Permission

- Data model: 无
- Config: 无
- Permission: 无

## Observability

本需求不改变系统运行观测能力，但会补齐团队观测规范文档入口。

## Rollout And Rollback

- Rollout: 通过 `harness-repo` 文档 PR 合入。
- Rollback: 回滚对应文档提交。

## Risks

| Risk | Mitigation | Owner |
|---|---|---|
| 第一版文档写得过长 | 每份文档只保留最小规则、常用命令、例外位置和示例 | core |
| 新增文档与已有文档重复 | 索引引用已有文档，新增文档只补缺口 | core |
| 后续 Agent 自动加载仍不准确 | 本票只补说明；服务矩阵真实字段扩展如需自动化另拆票 | core |
