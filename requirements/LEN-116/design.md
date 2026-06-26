---
requirement_id: "LEN-116"
owner: "forest"
status: "approved"
updated_at: "2026-06-27"
approved_by: "forest"
approved_at: "2026-06-27T00:11:00+08:00"
decision: "批准 LEN-116 设计，确认 GitOps DAG、fides/fides-bff/Java gate 支撑和 Redis trace 测试稳定性方案，不包含 LEN-117。"
---

# Design

## Requirement Traceability

| Requirement Item | Design Decision | Notes |
|---|---|---|
| R1, AC1, AC2, AC3 | D1: `github-repo-gate` 改为 DAG | checkout 并行，gate task 显式依赖所需 checkout |
| R2, AC4 | D2: fides-ci 扩展为完整非 smoke 前端 gate | 覆盖 dependency lint、lint、Vitest 和 build |
| R3, AC5 | D3: fides-bff-ci 按 Go module 拆分 | bffkit 与 fides-bff 独立任务，复用 skip plan |
| R4, AC6, AC7 | D4: Java quality 项目矩阵配置化 | `projects.yaml` 是项目和依赖声明事实源 |
| R5, AC8 | D5: 测试等待目标事件而不是第一条事件 | 避免 H2/Flyway trace 抢先满足等待条件 |
| BR5, AC9 | D6: LEN-116/LEN-117 分开交付 | PR gate 和 image release 分支、PR、描述均隔离 |

## Summary

LEN-116 的方案是把 repo gate 执行面硬切为 DAG，同时补齐 business-repo 中支撑完整 gate 的测试和配置。GitOps 负责 orchestration，business-repo 负责可执行测试和 project matrix，Harness 负责需求追溯。

## Affected Services

| Service | Change | Reason |
|---|---|---|
| fides | fides-web 非 smoke gate 扩展 | PR 必须覆盖 lint、Vitest 和 build |
| fides-bff | bffkit/fides-bff Go module gate 拆分 | 避免一个模块变更隐藏另一个模块验证结果 |
| applicant-api | Java quality matrix 和 Redis trace test 稳定性 | Java CI 在配置变化时可稳定运行全部项目 |

## API / Contract Design

- Protobuf IDL required: No.
- Proto files: none changed.
- Buf module: unchanged.
- Buf config version: v2.
- Generated outputs: unchanged.
- Breaking check baseline: not applicable.
- Compatibility strategy: no external contract change.

## Application Design

### D1：Repo Gate DAG

`github-repo-gate` 的 `run` 模板使用 DAG。`pending` status 写入后，source checkout 和 peer checkout 可并行执行。各 gate task 只依赖自身需要的 checkout，success fan-in 接受非目标 gate task 的 `Skipped` 或 `Omitted`。

### D2：fides-ci 完整非 smoke gate

fides 前端 gate 使用 package manager 中声明的 pnpm 版本，并执行：

- `pnpm install --frozen-lockfile`
- `pnpm lint:deps`
- `pnpm lint`
- `pnpm exec vitest run --exclude '**/*.smoke.test.*'`
- `pnpm build`

### D3：fides-bff module gate

fides-bff gate 先计算是否涉及 bffkit 或 fides-bff 变更。命中时分别运行 `packages/go/bffkit` 和 `apps/fides-bff` 的 Go quality checks。

### D4：Java quality project matrix

Java quality 工具从 `tooling/java-quality/projects.yaml` 加载项目、pom 和依赖关系。加载阶段拒绝缺失字段、重复项目和未知依赖。

### D5：Redis trace test 稳定性

`RedisTraceExportTest` 等待包含 Redis SET 或 GET 的 OTLP payload，而不是第一条 trace export。这样 H2/Flyway 启动 trace 不会导致 Java CI 偶发失败。

### D6：Ticket 隔离

LEN-116 只包含 PR gate。LEN-117 image release workflow 已在独立分支和独立 PR 中交付。

## Data / Config / Permission

- Data model: no change.
- Config: Java quality project matrix moved to YAML.
- Permission: no new token or cluster permission.

## Observability

- Logs: no runtime log schema change.
- Metrics: no runtime metric schema change.
- Tracing: test-only assertion logic changes; runtime tracing behavior unchanged.
- Events: no event schema change.

## Testing Strategy

- `python3 -m unittest tooling/java-quality/tests/test_java_quality.py`
- `pnpm lint:deps && pnpm lint && pnpm exec vitest run --exclude '**/*.smoke.test.*' && pnpm build`
- `go test ./...` in `packages/go/bffkit`
- `go test ./...` in `apps/fides-bff`
- `mvn -f apps/applicant-api/pom.xml -Dtest=RedisTraceExportTest test`
- `kubectl kustomize workflows/templates`
- `janus delivery verify --workspace /Users/forest/Code/spark/.worktrees/LEN-116 --requirement LEN-116 --repo business-repo --base master --head chore/LEN-116-pr-gate-hard-cut`
- PR Argo statuses for `business-repo#24`

## Rollout And Rollback

- Gray release: branch / PR level only.
- Kill switch: revert the GitOps workflow and business support commits.
- Rollout: merge gitops PR gate change, merge business support PR, merge Harness lifecycle material.
- Rollback: revert corresponding PR merge commits and rerun repo gate validation.

## Risks

| Risk | Mitigation | Owner |
|---|---|---|
| DAG expression typo blocks success fan-in | Render template and verify real PR statuses | Codex |
| Non-smoke Vitest exposes existing flaky tests | Stabilize cooldown test with fake timers | Codex |
| Java CI exports non-Redis trace before Redis spans | Wait for payload containing Redis SET/GET | Codex |
| Scope drift into LEN-117 | Separate branch and PR for image release | Codex |
