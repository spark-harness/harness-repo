---
requirement_id: "LEN-116"
owner: "forest"
status: "approved"
created_at: "2026-06-26"
related_branch: "chore/LEN-116-pr-gate-hard-cut"
target_branch: "master"
release_branch: "master"
contract_gate_mode: "auto"
affected_repositories:
  - harness-repo
  - business-repo
  - gitops-repo
approved_by: "forest"
approved_at: "2026-06-27T00:10:00+08:00"
decision: "用户已授权硬切优化；批准 LEN-116 需求定义与影响分析，范围限定为 business-repo PR gate DAG、非 smoke gate 覆盖和测试支撑，不包含 LEN-117 镜像发布。"
---

# business-repo PR 门禁硬切优化

## Background

LEN-114 已经补齐一部分 Java CI 和 GitOps runner 能力，但 business-repo PR 门禁
仍存在两类问题：一是多个 checkout 和 gate 任务按顺序串行等待，二是 fides
前端、fides-bff、bffkit 和 Java quality 项目矩阵没有形成完整、稳定、可追溯
的非 smoke PR 验证入口。

它不是什么：本需求不是镜像发布 workflow 改造，也不是 smoke 验证治理。

它是什么：把 business-repo PR gate 硬切为更完整的 Argo DAG 门禁，并把必要的
业务仓测试支撑改为可维护的配置和稳定测试。

## Goals

- R1：`github-repo-gate` 使用 DAG 表达 checkout、gate 执行和成功回写，减少无谓串行等待。
- R2：fides 前端 PR gate 执行 dependency lint、lint、非 smoke Vitest 和 build。
- R3：fides-bff PR gate 分别验证 `packages/go/bffkit` 和 `apps/fides-bff`。
- R4：Java quality 项目矩阵从 Python 常量移到配置文件，便于后续维护。
- R5：修复 fides-web cooldown resend 测试对真实时间的依赖，保证非 smoke Vitest 在 gate 中稳定运行。

## Non-Goals

- 不处理 smoke 测试。
- 不修改 LEN-117 镜像发布 workflow。
- 不保留旧 PR gate 串行路径的兼容行为。
- 不修改 protobuf IDL、生成契约或运行时业务 API。

## User / Business Scenarios

### Scenario 1：业务 PR 触发完整前端门禁

Given：PR 修改 `apps/fides-web/**`。

When：Argo repo gate 收到 business-repo PR 事件。

Then：`spark/fides-ci` 执行 dependency lint、lint、非 smoke Vitest 和 build。

### Scenario 2：业务 PR 触发 Go 模块门禁

Given：PR 修改 `packages/go/bffkit/**` 或 `apps/fides-bff/**`。

When：Argo repo gate 执行 fides-bff gate。

Then：bffkit 和 fides-bff 按模块分别执行 Go quality checks。

### Scenario 3：业务 PR 触发 Java quality 选择

Given：PR 修改 Java 项目或 Java quality 配置。

When：`spark/java-ci` 执行。

Then：Java quality 从 `projects.yaml` 读取项目矩阵并选择受影响项目。

## Business Rules

- BR1：GitOps Sensor 仍保持薄路由，复杂判断放在 workflow 或业务仓 tooling 中。
- BR2：PR gate 成功回写必须接受未命中的 gate task 为 `Skipped` 或 `Omitted`。
- BR3：fides 前端 gate 不运行 smoke 测试。
- BR4：Java 项目依赖关系必须由配置声明，并拒绝未知依赖。
- BR5：LEN-116 与 LEN-117 必须分开分支、PR 和交付记录。

## Acceptance Criteria

- AC1：`github-repo-gate` 模板使用 DAG 表达 checkout、gate 和 success fan-in。
- AC2：peer checkout 可并行执行，gate task 只依赖所需 checkout。
- AC3：success fan-in 接受非目标 gate task 的 `Skipped` 或 `Omitted` 状态。
- AC4：`fides-ci` 执行 `pnpm lint:deps`、`pnpm lint`、非 smoke Vitest 和 `pnpm build`。
- AC5：`fides-bff-ci` 分别执行 bffkit 和 fides-bff 的 Go checks。
- AC6：Java quality 项目矩阵来自 `tooling/java-quality/projects.yaml`。
- AC7：Java quality 配置加载测试覆盖正常配置和未知依赖失败。
- AC8：fides-web cooldown resend 测试不依赖真实时间等待。
- AC9：LEN-116 PR 不包含 LEN-117 镜像发布 workflow 变更。

## Open Questions

| Question | Owner | Deadline | Status |
|---|---|---|---|
| 是否需要把 smoke 重新纳入 PR gate | Forest | 后续 ticket | 不处理 |

## Notes

- 用户明确要求 smoke 不处理。
- 用户明确要求 LEN-116 和 LEN-117 分开处理，通过独立 PR 合并 master。
