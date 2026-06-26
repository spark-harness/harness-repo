---
requirement_id: "LEN-116"
owner: "forest"
current_stage: "5"
status: "draft"
created_at: "2026-06-26"
---

# business-repo PR 门禁硬切优化

## Summary

将 business-repo PR 门禁硬切到 Argo DAG 执行模型，补齐 fides 前端、fides-bff、
bffkit 和 Java quality 配置化项目矩阵的非 smoke 验证入口。

## Lifecycle Artifacts

- requirement.md

## Jira Trace

- Story：LEN-116
- Sub-tasks：LEN-118、LEN-119、LEN-120、LEN-121

## Delivery Notes

- 本需求只覆盖 PR gate 优化。
- 镜像发布 workflow 属于 LEN-117，必须单独交付。
