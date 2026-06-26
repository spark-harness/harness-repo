---
requirement_id: "LEN-114"
owner: "forest"
status: "approved"
created_at: "2026-06-25"
related_branch: "feature/LEN-114-java-ci"
target_branch: "master"
release_branch: "master"
contract_gate_mode: "auto"
affected_repositories:
  - harness-repo
  - business-repo
  - gitops-repo
approved_by: "forest"
approved_at: "2026-06-26T08:33:05+08:00"
decision: "用户已授权直接批准；批准 LEN-114 需求定义与影响分析，确认范围限定为 business-repo 手写 Java 项目质量门禁、GitOps Argo Java CI DAG 和 Janus runner 工具链，不涉及 IDL、生成契约或运行时业务行为。"
---

# business-repo Java 项目按变更范围并行执行质量门禁

## Background

business-repo 已经包含多个手写 Java Maven 项目，包括 `packages/java/money`、
`packages/java/spring-starter` 和 `apps/applicant-api`。旧的 Java CI 以
applicant-api 为中心，无法准确表达共享 Java 包和应用之间的依赖关系，也不利于
按变更范围减少 PR 等待时间。

它不是什么：本需求不是拆分多个 GitHub required status，也不是让 Argo Sensor
承担复杂路径判断。

它是什么：将 Java 仓库门禁演进为统一的 `spark/java-ci`，由 Argo Workflow 在
checkout 后计算变更路径，选择受影响 Java Maven 项目，并按项目依赖关系并行或
串行执行质量门禁。

## Goals

- R1：新增 `business-repo/tooling/java-quality`，集中维护 Java 变更选择和项目
  质量门禁入口。
- R2：为 `money`、`spring-starter`、`applicant-api` 接入统一的 Maven 格式、
  Checkstyle、单元测试和 SpotBugs 验证。
- R3：修改 `packages/java/money/**` 时只验证 money。
- R4：修改 `packages/java/spring-starter/**` 时验证 spring-starter，并在通过后
  验证依赖它的 applicant-api。
- R5：修改 Java quality 工具或公共配置时验证全部 Java 项目。
- R6：将 Argo Java gate 演进为稳定的 `spark/java-ci` status，并用 DAG 表达可
  并行项目和依赖顺序。

## Non-Goals

- 不修改 protobuf IDL、Buf 配置或生成契约仓。
- 不扫描 `idl-java-repo` 生成物。
- 不改变 applicant-api、money 或 spring-starter 的运行时业务行为。
- 不把 Java 项目拆成多个 GitHub required status。
- 不把复杂路径判断放到 Argo Sensor。
- 不重构 Maven 多模块结构。

## User / Business Scenarios

### Scenario 1：PR 只修改 money

Given：PR 只修改 `packages/java/money/**`。

When：Argo 触发 Java CI。

Then：只运行 money 的格式、Checkstyle、单元测试和 SpotBugs，`spark/java-ci`
反映该项目结果。

### Scenario 2：PR 修改 spring-starter

Given：PR 修改 `packages/java/spring-starter/**`。

When：Argo 触发 Java CI。

Then：spring-starter 与 applicant-api 被选中，money 不运行，且 applicant-api
在 spring-starter 验证通过后执行。

### Scenario 3：PR 同时修改多个可并行项目

Given：PR 同时修改 `packages/java/money/**` 和 `packages/java/spring-starter/**`。

When：Argo 触发 Java CI。

Then：money 与 spring-starter 可并行执行，applicant-api 在 spring-starter
验证通过后执行。

### Scenario 4：PR 未修改 Java 相关路径

Given：PR 只修改 fides 前端、Go 服务或非 Java 文档。

When：Argo 触发 Java CI。

Then：`spark/java-ci` 成功跳过，并输出无 Java 项目变更。

## Business Rules

- BR1：Java CI 只覆盖 business-repo 中手写 Java 项目，不覆盖生成物仓。
- BR2：未修改 Java 相关路径时，`spark/java-ci` 必须成功跳过。
- BR3：修改独立 Java 项目时，只运行该项目的 Maven quality gate。
- BR4：修改 `packages/java/spring-starter/**` 时，必须同时验证依赖它的
  `apps/applicant-api`。
- BR5：可并行的项目应并行执行；存在依赖关系的项目必须按依赖顺序执行。
- BR6：GitHub branch protection 只依赖稳定 status `spark/java-ci`，不按 Java
  项目拆 required status。
- BR7：失败日志必须明确标识失败项目，便于从 Argo UI 定位。

## Acceptance Criteria

- AC1：`business-repo/tooling/java-quality` 能根据 PR 相对 base 的变更路径输出
  需要验证的 Java 项目。
- AC2：money、spring-starter 和 applicant-api 都接入格式、Checkstyle、单元测试
  和 SpotBugs。
- AC3：修改 `packages/java/money/**` 时只选择 money。
- AC4：修改 `packages/java/spring-starter/**` 时选择 spring-starter 和
  applicant-api。
- AC5：修改 Java quality 工具或公共 Java 配置时选择全部 Java 项目。
- AC6：无 Java 相关变更时 `spark/java-ci` 成功跳过。
- AC7：Argo Workflow 使用 DAG 表达 money 与 spring-starter 可并行执行、
  applicant-api 依赖 spring-starter。
- AC8：GitOps Sensor 保持薄路由，复杂路径选择在 checkout 后的 workflow/tooling
  中完成。
- AC9：business-repo PR 中 Java 相关检查通过后由稳定 status `spark/java-ci`
  汇总结果。

## Open Questions

| Question | Owner | Deadline | Status |
|---|---|---|---|
| GitHub branch protection 何时从旧 Java status 迁移到 `spark/java-ci` | Forest | 合并前 | 需要在 GitOps 变更合入并生效后确认 |

## Notes

- Jira LEN-114 描述要求保持 GitHub status 为 `spark/java-ci`，并确认 branch
  protection 从旧 Java status 迁移到新 status。
- 当前文件仅记录需求事实源，不记录人工 approval 或门禁通过结论。
