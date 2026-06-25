---
requirement_id: "LEN-99"
owner: "forest"
status: "approved"
created_at: "2026-06-25"
related_branch: "feature/LEN-99-business-monorepo-layout"
target_branch: "master"
release_branch: "master"
contract_gate_mode: "auto"
affected_repositories:
  - harness-repo
  - business-repo
  - gitops-repo
  - janus
approved_by: "forest"
approved_at: "2026-06-25T13:41:47+08:00"
decision: "用户已授权批准所有门禁；批准 LEN-99 需求定义与影响分析，包含 business-repo 三目录迁移、gitops-repo 路径治理和 Janus delivery verifier 路径修正。"
---

# business-repo 三目录 monorepo 迁移

## Background

business-repo 目前同时使用 `services/`、根 `packages/`、根 `scripts/` 和根 `tests/` 承载可部署应用、共享库和仓库工具。随着 fides-web、fides-bff、applicant-api、Go / Java 共享库和 contract dependency scan 同时存在，开发者、评审者、CI path selector 和 Agent 上下文加载需要更稳定的目录语义。

它不是什么：本需求不是运行时行为变更，不新增业务 API，不修改 protobuf IDL，也不把 applicant-api 暴露到公网。

它是什么：把 business-repo 中的可部署应用、跨应用复用库和仓库工具迁移到固定三目录结构，并同步 Harness 治理路径和验证证据。

## Goals

- R1：可部署应用统一位于 `apps/`，包括 fides-web、fides-bff 和 applicant-api。对应 `LEN-100`、`LEN-101`。
- R2：共享库统一位于 `packages/` 并按语言分组，包括 `packages/go/bffkit`、`packages/java/money`、`packages/java/spring-starter`。对应 `LEN-100`、`LEN-102`。
- R3：仓库工具统一位于 `tooling/`，contract dependency scan 迁移到 `tooling/contract-dependency-scan/`。对应 `LEN-100`、`LEN-103`。
- R4：business-repo README 明确 `apps/`、`packages/`、`tooling/` 的用途、边界和放置规则。对应 `LEN-100`、`LEN-104`。
- R5：Harness 服务矩阵和 CI / Argo path-based gate 使用迁移后的新路径。对应 `LEN-105`、`LEN-106`、`LEN-107`。
- R6：迁移需求证据、Janus delivery verifier、delivery-readiness、本地验证矩阵、CI / Argo gate 和 vincent k3s rollout / smoke 证据完整。对应 `LEN-105`、`LEN-108`、`LEN-109`、`LEN-110`、`LEN-111`、`LEN-112`。

## Non-Goals

- 不修改 protobuf IDL、Buf 配置、生成契约仓或契约版本策略。
- 不改变 fides-web、fides-bff、applicant-api 的用户可见行为或接口语义。
- 不新增根级 `tests/`、`versions/`、`config/` 治理概念；只迁移本需求范围内的现有对象。
- 不把 applicant-api 改为公网访问；vincent k3s 验证只证明目录迁移没有破坏部署链路。
- 不清理历史需求文档中的旧路径审计记录；只更新 active 事实源和本需求后续使用的路径。

## User / Business Scenarios

### Scenario 1：开发者定位可部署应用

Given：开发者或 Agent 需要修改 fides-web、fides-bff 或 applicant-api。

When：读取 business-repo 顶层目录。

Then：能在 `apps/` 下定位可部署应用，不再依赖旧 `services/frontend` 或 `services/backend` 结构作为事实源。

### Scenario 2：开发者定位共享库

Given：开发者需要修改跨应用复用库。

When：读取 business-repo 顶层 `packages/`。

Then：能按语言定位 Go 与 Java 共享库，避免可部署应用和共享库混放。

### Scenario 3：维护者运行 contract dependency scan

Given：PR 修改了契约依赖文件或 scanner 自身。

When：CI / Argo 或本地验证执行 contract dependency scan。

Then：执行入口来自 `tooling/contract-dependency-scan/`，自测和 changed-file scan 仍可运行。

### Scenario 4：Harness 按服务矩阵定位业务路径

Given：delivery-readiness 或 Agent 上下文加载需要解析 fides、fides-bff、applicant-api 和共享库路径。

When：读取 `.service-matrix/dependencies.yaml`。

Then：repo_path 指向迁移后的新路径，且路径在 business-repo 中存在。

### Scenario 5：交付负责人验证迁移闭环

Given：目录迁移和路径治理已完成。

When：运行本地验证矩阵、查看 CI / Argo gate，并在 vincent k3s 执行 rollout / smoke。

Then：TS、Go、Java、tooling、delivery-readiness 和部署链路均有证据证明迁移未破坏现有能力。

## Business Rules

- BR1：`apps/` 只放可部署应用：fides-web、fides-bff、applicant-api。
- BR2：`packages/` 只放跨应用复用库，并按语言分组：`go/bffkit`、`java/money`、`java/spring-starter`。
- BR3：`tooling/` 只放仓库工具，本次只迁移 contract dependency scan。
- BR4：旧 `services/`、根 `scripts/` 和旧 contract-scan `tests/` 路径不再作为 active 事实源。
- BR5：服务路径以 Harness 服务矩阵为治理事实源；目录名不能替代服务矩阵。
- BR6：CI / Argo path-based gate 必须使用新路径触发 TS、Go、Java 和 tooling 检查。
- BR7：本需求不修改 IDL，所有 protobuf 契约兼容性风险保持不变。
- BR8：vincent k3s 回归不扩大公网暴露范围，applicant-api 仍按既有约束保持内网访问。

## Acceptance Criteria

- AC1：fides-web、fides-bff、applicant-api 位于 `business-repo/apps/`，旧可部署应用路径不再作为 active 事实源。
- AC2：bffkit、money、spring-starter 位于 `business-repo/packages/go/` 与 `business-repo/packages/java/`，原有测试仍可运行。
- AC3：contract dependency scan 位于 `business-repo/tooling/contract-dependency-scan/`，工具自测通过。
- AC4：business-repo README 明确 `apps/`、`packages/`、`tooling/` 的用途和边界。
- AC5：服务矩阵中 fides、fides-bff、applicant-api 和共享库 repo_path 指向新路径，且路径存在。
- AC6：CI / Argo path-based gate 使用新路径触发对应 TS、Go、Java 或 contract-scan gate。
- AC7：本地验证矩阵覆盖 fides-web、fides-bff、applicant-api、packages 和 tooling，并记录结果。
- AC8：delivery-readiness 和 Janus contract dependency scan 能基于 LEN-99 同名分支、服务矩阵和 business-repo 新 tooling 路径定位迁移后的对象。
- AC9：迁移 PR 的必需 CI / Argo gate 全绿，且触发路径来自新目录。
- AC10：vincent k3s 中 fides、fides-bff、applicant-api rollout 成功，最小 smoke 可证明路径迁移没有导致镜像启动、404 或服务发现失败。
- AC11：验证证据明确 applicant-api 不因本迁移新增公网访问。

## Open Questions

| Question | Owner | Deadline | Status |
|---|---|---|---|
| 旧 `services/` 目录是否完全删除，还是保留仅含迁移说明的空目录 | Forest | 目录迁移实现前 | 默认删除旧代码事实源 |
| CI / Argo path selector 的实际事实源是否只在 business-repo / harness-repo，还是还需要 gitops-repo 同步 | Forest | 治理路径切换前 | 已确认：gitops-repo 是 Argo repo gate 和 image release 事实源 |
| vincent k3s 当前访问方式是否可用 | Forest | 回归验证前 | Open |

## Notes

- Jira 树以 LEN-99 为 Epic，LEN-100、LEN-105、LEN-109 为三个执行 Story。
- 执行顺序：先完成 `LEN-100` 代码目录迁移，再做 `LEN-105` 治理路径切换，最后用 `LEN-109` 收口验证。
- 用户已在 2026-06-25 授权批准所有门禁；机器批准字段仍通过 `janus requirement approve` 记录。
