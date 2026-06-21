---
requirement_id: "LEN-45"
status: "draft"
related_branch: "feature/LEN-45-cleanup-old-spark-assets"
target_branch: "master"
release_branch: "master"
current_stage: "4.4"
---

# 清理旧 Spark user/aegis 示例资产

## Summary

移除旧 Spark user/aegis 示例资产及其注册入口，让当前工作区只暴露
Lendora applicant/fides 主线服务和仍有效的公共治理资产。

## Scope

- `harness-repo`：服务矩阵、`SPARK-*` 需求目录、`spark/user` 项目上下文。
- `business-repo`：`user-api`、`aegis`、`user-api-ci` 和服务索引。
- `idl-repo`：`vesta/spark` 旧 protobuf 源契约。

## Non-Goals

- 不修改 `learning-docs-repo`。
- 不手工清理 `idl-java-repo` 或 `idl-go-repo` 生成物；生成仓由生产同步流程清理。
- 不修改 `applicant-api`、`fides` 或 `fides-bff` 行为。
