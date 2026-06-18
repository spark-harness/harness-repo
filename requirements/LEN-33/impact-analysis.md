---
requirement_id: "LEN-33"
analyst: "Codex"
status: "approved"
updated_at: "2026-06-17"
approved_by: "Forest"
approved_at: "2026-06-17T21:38:22+08:00"
decision: "批准 LEN-33 impact-analysis 与服务仓库检查，允许进入编码循环。"
idl_impact: "no"
idl_impact_reason: "本票只补 user-api Java + Spring 服务骨架、测试和 CI，不新增或修改 protobuf IDL、生成契约或外部 API。"
---

# Impact Analysis

## Summary

在现有 `business-repo/services/backend/user-api` 内补齐 Java 21 + Spring Boot 后端业务服务骨架、Clean Architecture 分层、最小健康检查/启动验证、架构边界测试和 CI；不新增服务、不修改 IDL、不引入业务规则或数据存储。

## Affected Domains

- `user`（module）：`user-api` 是当前服务矩阵中唯一后端服务。本票只建立后端业务服务地基，供 LEN-9 等后续业务票落地。

## Affected Services

| Service | Repo | Reason | Protobuf Required |
|---|---|---|---|
| user-api | business-repo (`services/backend/user-api`) | 补齐 Java 21 + Spring Boot 服务骨架、分层目录、最小健康检查、测试入口、架构边界测试和 CI | Yes（服务既有属性）；本票不改 IDL |
| —（harness-repo） | harness-repo | 新增 LEN-33 生命周期产物、门禁和证据 | No |

## Upstream / Downstream Consumers

- 上游：服务矩阵中 `aegis` 是 `user-api` upstream；本票不新增或变更运行时 API，因此不影响前端调用契约。
- 下游：LEN-9（申请单聚合：创建 + 草稿读写）被 LEN-33 阻塞；本票完成后解除其 Java + Spring 工程骨架前置阻塞。
- 公共包：复用 `packages/spring-starter`；默认不修改 `packages/money`。

## API / Contract Impact

- Does this change involve protobuf IDL or external contracts: **No**。
- Contract repo: 不修改 `idl-repo`。
- Proto files: 不适用。
- Buf module: `local/spark-user` 是 `user-api` 既有配置；本票不触碰。
- Buf config version: v2。
- Required buf checks: 不适用；无需 `buf lint/generate/breaking` 作为本票实现证据。
- Breaking baseline: 不适用。
- Compatibility risk: 无外部契约兼容风险；若实现中发现必须新增 API，应停止并转入 IDL change protocol。

## Data Impact

- Database schema: 无。
- Data migration: 无。
- Backfill: 无。
- Cache: 无。
- Runtime storage: 无；不引入真实 repository、表结构或外部系统。

## Config / Permission / Observability Impact

- Config: `user-api` 增加 Spring Boot 应用配置、健康检查配置、Java 21 编译配置、测试依赖和 CI 工作流；可能新增架构测试依赖。
- Permission: CI 使用只读仓库权限即可。
- Metrics: 不新增业务指标；Actuator 健康检查仅用于 smoke。
- Logs: 默认 Spring Boot 启动日志；不新增业务日志字段。
- Tracing: 不新增追踪逻辑；LEN-3 的 trace/correlation 约定由横切票承接。
- Events: 无。

## Rollout And Rollback

- Gray release: 不适用；这是工程骨架和质量门，不改变生产业务行为。
- Kill switch: 如 CI 误阻断，可临时禁用新增 CI job 或架构测试，并在证据中记录原因与恢复计划。
- Rollback steps: 删除 `user-api` 新增源码/测试/配置和 CI 工作流即可回退；无数据、契约或运行时状态残留。

## Risks

| Risk | Impact | Mitigation | Owner |
|---|---|---|---|
| `user-api` 依赖 GitHub Packages 的 `spark-idl-java`，本地无凭据时测试解析依赖失败 | 无法完成本地验证 | 优先保持本票不消费新契约；验证失败时记录为环境凭据问题，并补充不依赖私有包的模块级测试证据 | Codex |
| Java 21 与现有 `packages/spring-starter`/`money` Java 17 配置不一致 | 构建矩阵漂移 | 本票只将 `user-api` 编译 release 升到 21；公共包升级另开需求 | Codex |
| 架构测试过宽导致后续业务票频繁误报 | 开发阻塞 | 测试只约束核心红线：domain 不依赖外层技术，包层级存在且方向清晰 | Codex |
| 误把骨架票扩展成业务 API 或持久化实现 | 范围蔓延 | 需求和设计明确 Non-Goals；实现阶段只做 skeleton、health、tests、CI | Codex |
