---
requirement_id: "LEN-99"
analyst: "forest"
status: "approved"
updated_at: "2026-06-25"
approved_by: "forest"
approved_at: "2026-06-25T13:41:47+08:00"
decision: "用户已授权批准所有门禁；批准 LEN-99 服务仓库检查，确认 harness-repo、business-repo、gitops-repo、janus 同名分支和 idl-repo 只读校验拓扑满足当前验证。"
idl_impact: "no"
idl_impact_reason: "本需求只迁移 business-repo 目录、Harness 路径治理和验证证据，不修改 .proto、Buf 配置或生成契约。"
---

# Impact Analysis

## Summary

LEN-99 影响 business-repo 顶层目录布局、应用 / 共享库 / tooling 的相对路径、Dockerfile 和本地依赖路径、contract dependency scan 入口、Harness 服务矩阵、CI / Argo path selector、delivery-readiness 和迁移后回归证据。它不修改 protobuf IDL 或外部业务接口。

## Affected Domains

- business-repo 目录治理：`apps/`、`packages/`、`tooling/` 三目录成为 active 事实源。
- 前端应用：fides-web 从旧 `services/frontend/fides` 迁移到 `apps/fides-web`。
- Go BFF：fides-bff 从旧 `services/backend/fides-bff` 迁移到 `apps/fides-bff`。
- Java 后端：applicant-api 从旧 `services/backend/applicant-api` 迁移到 `apps/applicant-api`。
- 共享库：bffkit、money、spring-starter 按语言归入 `packages/go` 和 `packages/java`。
- 仓库工具：contract dependency scan 迁移到 `tooling/contract-dependency-scan`。
- Harness 治理：服务矩阵 repo_path、路径驱动 gate、delivery-readiness 输入和证据。
- Janus 治理：delivery verifier 的 business-repo contract dependency scan 入口需兼容 `tooling/contract-dependency-scan`。
- 回归验证：本地 TS / Go / Java / tooling 验证、CI / Argo gate、vincent k3s rollout / smoke。

## Affected Services

| Service | Repo | Reason | Protobuf Required |
|---|---|---|---|
| fides | `business-repo` / `harness-repo` / `gitops-repo` | 前端应用目录迁移，服务矩阵 repo_path、CI path 和 image release dockerfile-dir 更新 | No |
| fides-bff | `business-repo` / `harness-repo` / `gitops-repo` | Go BFF 目录迁移，Dockerfile、Go replace、服务矩阵、CI path 和 image release dockerfile-dir 更新 | Yes, reuse existing |
| applicant-api | `business-repo` / `harness-repo` / `gitops-repo` | Java 后端目录迁移，Dockerfile、Maven 相对路径、服务矩阵、CI path 和 image release dockerfile-dir 更新 | Yes, reuse existing |
| bffkit | `business-repo` | Go 共享库迁移到 `packages/go/bffkit`，fides-bff 本地 replace 需同步 | No |
| money | `business-repo` / `harness-repo` | Java 共享库迁移到 `packages/java/money`，服务矩阵 library repo_path 需同步 | No |
| spring-starter | `business-repo` | Java starter 迁移到 `packages/java/spring-starter`，applicant-api Maven / Dockerfile 路径需同步 | No |
| contract dependency scan | `business-repo` / `harness-repo` / `gitops-repo` | 工具迁移到 `tooling/contract-dependency-scan`，测试和 gate 调用路径需同步 | No |
| Janus delivery verifier | `janus` / `harness-repo` | delivery-readiness 仍要在 business-repo 新 tooling 路径运行 contract dependency scan | No |

## Upstream / Downstream Consumers

- 开发者和 Agent：通过 README、服务矩阵和目录语义定位代码对象。
- CI / Argo repo gate：gitops-repo 中的 Argo WorkflowTemplate 根据 changed paths 触发 TS、Go、Java 和 contract-scan 检查。
- Janus delivery verifier：通过 requirement front matter、服务矩阵、repo 状态和 business-repo contract dependency scanner 判断 readiness。
- fides-bff：通过本地 Go replace 消费 bffkit。
- applicant-api：通过 Maven / Dockerfile 相对路径消费 spring-starter，业务代码继续消费既有 Java generated contract。
- fides：通过现有前端 build/test/lint 入口验证迁移后路径。

## API / Contract Impact

- Does this change involve protobuf IDL or external contracts: No.
- Contract repo: `idl-repo` is not edited.
- Proto files: existing `vesta/lendora/fides-bff/v1` and `vesta/lendora/applicant/v1` are reused only through generated dependencies.
- Buf module: `local/lendora-fides-bff` and `local/lendora-applicant` remain unchanged.
- Buf config version: v2.
- Required buf checks: not required for source edits; no `.proto` or generated contract change.
- Breaking baseline: not applicable.
- Compatibility risk: directory and build-context only; wire/API compatibility risk is unchanged.

## Generated Contract Impact

- Go generated contracts consumed by fides-bff remain the same dependency/version.
- Java generated contracts consumed by applicant-api remain the same dependency/version.
- `idl-java-repo` is not part of the affected repo set for this requirement.

## Data Impact

- Database schema: none.
- Data migration: none.
- Backfill: none.
- Cache: none.
- Runtime storage: unchanged; vincent k3s smoke only verifies migrated images and service discovery still work.

## Config / Permission / Observability Impact

- Config: Dockerfile `COPY` / `WORKDIR` paths, Go local replace path, Maven `-f` paths, test runner path, CI / Argo path selector, image release dockerfile-dir, service matrix repo_path.
- Permission: no new runtime permission; CI still needs existing GitHub Packages / private module access.
- Metrics: no metrics schema change.
- Logs: no log schema change; validation evidence should not expose secrets or tokens.
- Tracing: no trace schema change.
- Events: CI / Argo gate events should reference new changed paths.

## Rollout And Rollback

- Gray release: branch and PR only; no behavior flag.
- Kill switch: revert the directory migration and service matrix / CI path updates before merge; after merge, revert the PR.
- Rollout steps:
  - Migrate business-repo directories and relative paths.
  - Update business-repo README and tooling test paths.
  - Update Harness service matrix and path governance.
  - Run local verification matrix.
  - Confirm CI / Argo gate path triggers.
  - Run vincent k3s rollout / smoke without changing public exposure boundaries.
- Rollback steps:
  - Revert moved paths to prior layout.
  - Revert service matrix repo_path and CI / Argo path selector changes.
  - Re-run local scanner and service tests to prove old layout is restored.

## Risks

| Risk | Impact | Mitigation | Owner |
|---|---|---|---|
| Dockerfile build contexts keep old paths | Images fail to build after migration | Update and test fides-web, fides-bff and applicant-api Dockerfiles | Codex |
| Go replace path for bffkit becomes invalid | fides-bff build/test fails | Update replace path after moving to `packages/go/bffkit`; run `go test ./...` | Codex |
| Maven relative paths for spring-starter become invalid | applicant-api build/test fails | Update Dockerfile and Maven command paths; run Java package/app tests | Codex |
| CI / Argo path selector misses new directories | PR can merge without required checks | Update path governance and record changed-path trigger evidence | Codex |
| Janus delivery verifier keeps old scanner path | business-repo delivery-readiness fails after moving scanner | Update Janus scanner discovery to prefer tooling path and keep legacy fallback | Codex |
| Historical docs still contain old paths | Search results may confuse active facts with audit history | Update active docs and this requirement; do not rewrite historical evidence unless it is an active gate input | Codex |
| vincent k3s access unavailable during final validation | Rollout / smoke evidence cannot be completed immediately | Record local and CI evidence first; run k3s evidence when access is available | Forest |
