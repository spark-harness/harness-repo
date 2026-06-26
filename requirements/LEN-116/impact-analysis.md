---
requirement_id: "LEN-116"
analyst: "forest"
status: "approved"
updated_at: "2026-06-27"
idl_impact: "no"
idl_impact_reason: "本需求只优化 business-repo PR gate、GitOps Argo workflow 和业务仓测试支撑，不修改 .proto、Buf 配置或生成契约。"
approved_by: "forest"
approved_at: "2026-06-27T00:13:00+08:00"
decision: "批准 LEN-116 服务仓库检查，确认涉及 fides、fides-bff、applicant-api，IDL 仅复用既有契约且无 .proto 变更。"
---

# Impact Analysis

## Summary

LEN-116 影响 business-repo 的 PR 验证覆盖面、GitOps repo gate workflow 和 Harness 需求追溯材料。它不改变运行时业务 API、数据模型、部署拓扑或 protobuf 契约。

## Affected Domains

- GitOps CI：`github-repo-gate` 从顺序 steps 硬切为 DAG，减少 checkout 和 gate 串行等待。
- 前端质量门禁：fides 前端 gate 增加 lint、非 smoke Vitest 和 build。
- Go 质量门禁：fides-bff gate 拆分 bffkit 与 fides-bff 模块验证。
- Java quality：项目矩阵迁移到配置文件，并增加配置加载测试。
- Harness 治理：补齐 LEN-116 requirement、设计、任务、证据和门禁。

## Affected Services

| Service | Repo | Reason | Protobuf Required |
|---|---|---|---|
| fides | `business-repo` / `gitops-repo` | PR gate 覆盖 fides-web dependency lint、lint、非 smoke Vitest 和 build | No |
| fides-bff | `business-repo` / `gitops-repo` | PR gate 覆盖 bffkit 与 fides-bff Go module checks | Reuse existing only |
| applicant-api | `business-repo` / `gitops-repo` | Java quality 依赖矩阵包含 applicant-api，并稳定 Redis trace 测试 | Reuse existing only |

## Upstream / Downstream Consumers

- 开发者：PR 反馈更完整，前端、Go 和 Java gate 失败可更早暴露。
- GitHub branch protection：继续消费稳定 `spark/*` status，不新增每项目 required status。
- Argo Workflows：执行面从串行 steps 切换到 DAG。
- 运行时消费者：不受影响。

## API / Contract Impact

- Does this change involve protobuf IDL or external contracts: No.
- Contract repo: `idl-repo` is not edited.
- Proto files: no `.proto` file changed.
- Buf module: unchanged.
- Buf config version: v2.
- Required buf checks: not required for this source change.
- Breaking baseline: not applicable.
- Compatibility risk: none for external API or protobuf contract.

## Generated Contract Impact

- Go generated contracts are reused only by existing fides-bff tests.
- Java generated contracts are not modified.
- `idl-java-repo` and `idl-go-repo` are not part of this requirement.

## Data Impact

- Database schema: none.
- Data migration: none.
- Backfill: none.
- Cache: none.
- Runtime storage: none.

## Config / Permission / Observability Impact

- Config: Java quality project matrix moves to `tooling/java-quality/projects.yaml`.
- Permission: no new GitHub token or registry permission.
- Metrics: no runtime metric schema change.
- Logs: no runtime log output change.
- Tracing: Redis trace test waits for Redis spans instead of first OTLP export.
- Events: no event schema change.

## Rollout And Rollback

- Gray release: PR branch level only.
- Kill switch: revert the LEN-116 gitops and business commits if Argo gate behavior is unacceptable.
- Rollout steps:
  - Merge GitOps PR gate DAG change.
  - Merge business-repo test/tooling support change.
  - Confirm business-repo PR statuses pass.
  - Merge Harness lifecycle material.
- Rollback steps:
  - Revert `github-repo-gate` template change.
  - Revert business-repo Java quality config/test stabilization commits.
  - Re-run repo gate validation.

## Risks

| Risk | Impact | Mitigation | Owner |
|---|---|---|---|
| DAG fan-in 表达式遗漏 Skipped/Omitted | 非目标 gate 被误判失败 | 静态校验 rendered template 包含 Omitted，并由真实 PR gate 验证 | Codex |
| fides 前端 gate 时间增加 | PR 等待变长 | 并行 checkout 和 gate DAG 抵消串行等待，且 smoke 明确不纳入 | Codex |
| Redis trace 测试先收到 H2 span | Java CI 偶发失败 | 测试等待包含 Redis SET/GET 的 OTLP payload | Codex |
| LEN-116 与 LEN-117 scope 混淆 | PR 难以评审和回滚 | 独立分支、独立 PR、独立 Jira correction comments | Codex |
