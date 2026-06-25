---
requirement_id: "LEN-99"
owner: "forest"
status: "approved"
updated_at: "2026-06-25"
approved_by: "forest"
approved_at: "2026-06-25T13:41:47+08:00"
decision: "用户已授权批准所有门禁；批准 LEN-99 设计与影响分析一致，确认 apps/packages/tooling 路径治理、CI/Argo 和 Janus verifier 更新纳入范围。"
---

# Design

## Requirement Traceability

| Requirement Item | Design Decision | Notes |
|---|---|---|
| R1, AC1 | D1: 可部署应用迁移到 `business-repo/apps/`，并使用稳定应用名 `fides-web`、`fides-bff`、`applicant-api` | 对应 LEN-101 |
| R2, AC2 | D2: 共享库保留在 `packages/` 语义下，但增加语言分组 `go/`、`java/` | 对应 LEN-102 |
| R3, AC3 | D3: contract dependency scan 迁移为自包含 tooling 目录 | 对应 LEN-103 |
| R4, AC4 | D4: business-repo README 成为三目录规则入口，旧 services README 不再作为 active 事实源 | 对应 LEN-104 |
| R5, AC5, AC6, AC8, AC9 | D5: Harness 服务矩阵和 CI / Argo path selector 一次性切换到新路径 | 对应 LEN-106、LEN-107、LEN-108 |
| R6, AC7, AC10, AC11 | D6: 验证分三层收口：本地矩阵、CI / Argo gate、vincent k3s rollout / smoke | 对应 LEN-110、LEN-111、LEN-112 |
| BR7 | D7: IDL 零修改，Buf / generated contract 只作为复用依赖验证 | 不创建 idl-repo worktree |
| BR8, AC11 | D8: k3s 验证只证明部署链路未破坏，不扩大公网暴露范围 | applicant-api 保持内网 |

## Summary

方案按 Jira 树拆成三段：先完成 business-repo 目录迁移，再切换 Harness 服务矩阵和 CI / Argo 路径治理，最后用本地、CI / Argo 和 vincent k3s 证据收口。它是路径治理和构建上下文迁移，不改变业务接口、运行时语义或 protobuf 契约。

## Affected Services

| Service | Change | Reason |
|---|---|---|
| fides | `services/frontend/fides` -> `apps/fides-web` | 可部署前端应用进入 apps 目录，并使用 Jira 指定名称 fides-web |
| fides-bff | `services/backend/fides-bff` -> `apps/fides-bff` | 可部署 Go BFF 进入 apps 目录，Dockerfile 和 Go replace 同步修正 |
| applicant-api | `services/backend/applicant-api` -> `apps/applicant-api` | 可部署 Java 后端进入 apps 目录，Dockerfile 和 Maven 路径同步修正 |
| bffkit | `packages/bffkit` -> `packages/go/bffkit` | Go 共享库按语言分组 |
| money | `packages/money` -> `packages/java/money` | Java 共享库按语言分组 |
| spring-starter | `packages/spring-starter` -> `packages/java/spring-starter` | Java starter 按语言分组 |
| contract dependency scan | `scripts/contract_dependency_scan.py` + `tests/contract_dependency_scan/**` -> `tooling/contract-dependency-scan/` | 仓库工具自包含，便于 path gate 和本地验证 |
| Janus delivery verifier | `scripts/contract_dependency_scan.py` -> `tooling/contract-dependency-scan/contract_dependency_scan.py` with legacy fallback | 保持 business-repo delivery-readiness 在新工具路径下可运行 |

## API / Contract Design

- Protobuf IDL required: No.
- Proto files: none changed; existing `vesta/lendora/fides-bff/v1` and `vesta/lendora/applicant/v1` are only consumed through generated dependencies.
- Buf module: unchanged.
- Buf config version: v2.
- Generated outputs: unchanged.
- Breaking check baseline: not applicable.
- Compatibility strategy: keep current generated contract dependencies and run existing app tests / contract dependency scan after path migration.

## Application And Tooling Design

### D1：apps 目录

`apps/` is the deployable application boundary:

```text
business-repo/apps/
├── applicant-api/
├── fides-bff/
└── fides-web/
```

内部源码布局不做业务重构。迁移只更新路径敏感文件：

- Dockerfile `COPY`、`WORKDIR`、artifact copy path。
- service README 中的相对路径和运行命令。
- 前端 package workspace / build context。
- Go module local replace。
- Maven / Dockerfile 中的 package 路径。

### D2：packages 目录

`packages/` is the cross-application reuse boundary:

```text
business-repo/packages/
├── go/
│   └── bffkit/
└── java/
    ├── money/
    └── spring-starter/
```

迁移后共享库测试仍在各自 package 目录运行。`fides-bff` 继续通过本地 replace 消费 bffkit，但 replace 路径改为从 `apps/fides-bff` 指向 `../../packages/go/bffkit`。

### D3：tooling 目录

contract dependency scan 迁移为自包含工具：

```text
business-repo/tooling/contract-dependency-scan/
├── contract_dependency_scan.py
├── tests/
└── fixtures/
```

测试入口改为工具目录内的自测命令。CI / Argo 调用不再引用根 `scripts/contract_dependency_scan.py`。

### D4：README 规则

business-repo README 明确三目录规则：

- `apps/`：可部署应用。
- `packages/`：跨应用复用库，按语言分组。
- `tooling/`：仓库工具和工具自测。

旧 `services/README.md` 不再作为 active 目录规则。若旧 `services/` 目录迁移后为空，应删除该目录；历史需求证据中的旧路径不批量改写。

### D5：Harness 与 CI / Argo 路径治理

服务矩阵更新为新路径：

```text
fides.repo_path -> {business-repo}/apps/fides-web
fides-bff.repo_path -> {business-repo}/apps/fides-bff
applicant-api.repo_path -> {business-repo}/apps/applicant-api
money.repo_path -> {business-repo}/packages/java/money
```

CI / Argo path selector 使用新目录触发：

- `apps/fides-web/**` -> TS / frontend gate。
- `apps/fides-bff/**`、`packages/go/bffkit/**` -> Go gate。
- `apps/applicant-api/**`、`packages/java/**` -> Java gate。
- `tooling/contract-dependency-scan/**` 和契约依赖文件 -> contract-scan gate。

Janus delivery verifier 使用同一迁移结果：

- 优先调用 `business-repo/tooling/contract-dependency-scan/contract_dependency_scan.py`。
- 保留旧 `business-repo/scripts/contract_dependency_scan.py` 作为兼容 fallback，避免历史分支 delivery verify 立即失效。

## Data / Config / Permission

- Data model: no schema change.
- Config: path-only changes for Dockerfile, local build commands, service matrix and CI / Argo path selector.
- Permission: no new runtime or cluster permission.

## Observability

- Logs: no log schema change; evidence must not expose secrets, OTP, token or applicantId.
- Metrics: no metric schema change.
- Tracing: no tracing schema change.
- Events: CI / Argo gate events should show new path triggers.

## Testing Strategy

- Tooling baseline: contract dependency scan self-tests before and after migration.
- Go baseline: `go test ./...` in `packages/go/bffkit` and `apps/fides-bff`.
- Java baseline: Maven tests for `packages/java/spring-starter`, `packages/java/money` where applicable, and `apps/applicant-api`.
- Frontend baseline: fides-web package tests / dependency lint / build where existing scripts support them.
- Harness baseline: service matrix validation and Janus delivery readiness after service matrix switch.
- Janus baseline: `go test ./...` in `janus` and `janus delivery verify` against the LEN-99 business-repo worktree.
- Path governance: changed-path scan or CI / Argo evidence proves new paths trigger required gates.
- Runtime smoke: vincent k3s rollout and minimal fides -> fides-bff -> applicant-api smoke, with applicant-api still not publicly exposed.

## Rollout And Rollback

- Gray release: branch / PR level only.
- Kill switch: stop before merge and revert the migration commit stack if any local, CI or k8s validation fails.
- Rollout:
  - Move business-repo paths and update relative references.
  - Update README and tooling test entry.
  - Update service matrix and CI / Argo path governance.
  - Run local validation matrix.
  - Confirm CI / Argo gate trigger paths.
  - Run vincent k3s rollout / smoke.
- Rollback:
  - Revert business-repo move commit.
  - Revert harness service matrix / governance commit.
  - Re-run local tooling and service tests to confirm old layout works again.

## Risks

| Risk | Mitigation | Owner |
|---|---|---|
| Mechanical move leaves stale relative paths | Use targeted search for old paths and run language-specific tests | Codex |
| CI / Argo path selector source is outside harness-repo / business-repo | Locate current truth source before LEN-107; if gitops-repo is required, isolate it before editing | Codex |
| Full-repo historical docs contain old paths | Treat historical requirements/evidence as audit records; only update active docs and gates | Codex |
| Private package credentials block local Java / Go verification | Record raw failure and supplement with focused path/static verification until credentials are available | Codex |
| vincent k3s unavailable | Complete local and CI evidence first; leave LEN-112 evidence pending until cluster access is restored | Forest |
