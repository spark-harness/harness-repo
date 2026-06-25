---
requirement_id: "LEN-114"
owner: "forest"
current_stage: "1"
status: "draft"
created_at: "2026-06-25"
---

# business-repo Java 项目按变更范围并行执行质量门禁

## Summary

将 `business-repo` 中手写 Java 项目的 PR 质量门禁统一为 `spark/java-ci`，由
Argo Workflow 在 checkout 后计算变更范围，选择受影响 Maven 项目，并按依赖
关系并行或串行执行格式、静态检查、单元测试和 SpotBugs。

## Lifecycle Artifacts

- requirement.md

## Jira Trace

- Story：LEN-114

## Delivery Notes

- 本目录当前只补齐 delivery readiness 所需的需求事实源。
- 本目录不包含人工 approval、gate JSON 或设计门禁结果。
