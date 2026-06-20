---
requirement_id: "LEN-41"
owner: "Codex"
status: "approved"
created_at: "2026-06-21"
related_branch: "feature/LEN-41-lendora-applicant-idl"
target_branch: "master"
release_branch: "master"
contract_gate_mode: "auto"
affected_repositories:
  - harness-repo
  - idl-repo
  - business-repo
approved_by: "Forest"
approved_at: "2026-06-21T00:43:30+08:00"
decision: "批准 LEN-41 requirement 与 impact-analysis，允许进入设计阶段。"
---

# [BE] Lendora applicant IDL namespace 迁移

## Background

LEN-12 已经为 Lendora 申请漏斗建立 `applicant-api` 和 `ApplicantAuthService`，但当前 applicant protobuf 路径、protobuf package 和 Java generated package 仍带有 Spark namespace：`vesta/spark/applicant/v1`、`vesta.spark.applicant.v1`、`com.vesta.spark.applicant.v1`。

这会让 Lendora applicant 契约在治理、发布、消费和审计时继续被归入 Spark namespace。随着 `user` 后续会移除，继续沿用 Spark namespace 会扩大后续清理范围，也会让 `applicant-api` 的契约来源与业务域不一致。

先说不是什么：`idl-java-repo` 和 `idl-go-repo` 是团队现有生成契约仓，不等同于 Spark 业务域。本需求不新建 `lendora-idl-java` 或 `lendora-idl-go-repo`，也不修改 Maven artifact 坐标 `com.spark.contract:spark-idl-java` 或 Go module `github.com/spark-harness/idl-go-repo`。

本需求不是新增 OTP 能力，不改变 `SendOtp`、`VerifyOtp`、`RefreshToken` 的字段或业务语义；也不迁移 `vesta/spark/user/*`，user 清理由后续独立任务处理。

## Goals

- R1：将 applicant protobuf 源文件从 `vesta/spark/applicant/v1/auth.proto` 迁移到 `vesta/lendora/applicant/v1/auth.proto`。
- R2：将 protobuf package 从 `vesta.spark.applicant.v1` 改为 `vesta.lendora.applicant.v1`。
- R3：将 Java generated package 从 `com.vesta.spark.applicant.v1` 改为 `com.vesta.lendora.applicant.v1`。
- R4：保留 Java 生成契约仓与 Maven artifact：`spark-harness/idl-java-repo`、`com.spark.contract:spark-idl-java`；只让 applicant generated Java package 改为 `com.vesta.lendora.applicant.v1`。
- R5：保留 Go 生成契约仓与 Go module：`spark-harness/idl-go-repo`、`github.com/spark-harness/idl-go-repo`；只让 applicant Go package path 改为 `github.com/spark-harness/idl-go-repo/vesta/lendora/applicant/v1`。
- R6：更新 `applicant-api` 的 generated Java imports，使其消费 Lendora applicant Java package；Maven dependency 坐标保持 `com.spark.contract:spark-idl-java`。
- R7：更新服务矩阵、需求、影响分析、设计、任务、证据和门禁，使 applicant 契约路径统一指向 `vesta/lendora/applicant/v1`。
- R8：保留 `ApplicantAuthService` 的 RPC、字段编号、字段名和业务语义，确保迁移是命名和发布坐标修正，不夹带行为变更。
- R9：记录 breaking 风险、发布顺序、回滚方式和生成契约发布证据。

## Non-Goals

- 不迁移、重命名或修复 `vesta/spark/user/*`。
- 不实现 user 移除；user 后续清理由独立需求承接。
- 不新增或修改 OTP 发送、OTP 校验、token 刷新的业务行为。
- 不修改 `fides-bff` 或前端代码。
- 不接真实短信供应商，不修改 Redis、token、幂等或 applicant 持久化规则。
- 不新建或切换到 `lendora-idl-java`、`lendora-idl-go-repo`、`com.vesta.lendora.contract:lendora-idl-java` 或 `github.com/spark-harness/lendora-idl-go-repo`。
- 不修改 `idl-java-repo` 的 Maven groupId/artifactId，也不修改 `idl-go-repo` 的 module path。

## User / Business Scenarios

### Scenario 1：Lendora applicant 契约使用 Lendora namespace

Given：工程师查看 applicant 身份契约来源。

When：打开 IDL 仓和生成契约仓。

Then：applicant 契约位于 `vesta/lendora/applicant/v1`，package 与生成物 package 均体现 Lendora 归属。

### Scenario 2：applicant-api 消费 Lendora Java package

Given：`applicant-api` 构建并运行 OTP 相关测试。

When：解析 generated Java contract dependency。

Then：服务仍消费 `com.spark.contract:spark-idl-java`，业务代码 import `com.vesta.lendora.applicant.v1.*`。

### Scenario 3：Go 契约在既有 module 下使用 Lendora path

Given：IDL 发布流程生成 Go applicant 契约。

When：发布或验证 Go module。

Then：Go package 进入 `github.com/spark-harness/idl-go-repo/vesta/lendora/applicant/v1`，module 仍是 `github.com/spark-harness/idl-go-repo`。

### Scenario 4：不处理 user proto

Given：仓库中仍存在 `vesta/spark/user/*`。

When：执行 LEN-41。

Then：本需求不迁移 user proto，不要求 `user-api` 同步改动；user 清理由后续任务处理。

## Business Rules

- BR1：Lendora applicant 契约不得继续以 Spark applicant namespace 作为事实来源。
- BR2：生成契约仓库和发布坐标保持既有团队级基础设施：Java 使用 `idl-java-repo` / `com.spark.contract:spark-idl-java`，Go 使用 `idl-go-repo` / `github.com/spark-harness/idl-go-repo`。
- BR3：`ApplicantAuthService` 的 RPC 名、字段编号、字段名和业务语义必须保持不变。
- BR4：如果删除旧 `vesta.spark.applicant.v1` 导致 protobuf breaking 检查失败，必须在设计和证据中明确分类为受控 breaking，并列出已知消费者。
- BR5：`vesta/spark/user/*` 不属于本需求范围，不能为了“顺手清理”迁移或删除。
- BR6：master-bound business change 只能消费 formal contract version，不能把 RC、SNAPSHOT、branch dependency 或 local replacement 合入 master。
- BR7：发布证据必须能追溯到 IDL commit、既有 Java artifact、既有 Go module tag、业务仓 consumer commit 和测试结果。

## Acceptance Criteria

- AC1：`idl-repo` 中存在 `vesta/lendora/applicant/v1/auth.proto`，package 为 `vesta.lendora.applicant.v1`。
- AC2：generated Java package 为 `com.vesta.lendora.applicant.v1`，并继续由 `com.spark.contract:spark-idl-java` 发布。
- AC3：generated Go package path 为 `github.com/spark-harness/idl-go-repo/vesta/lendora/applicant/v1`，且 Go module tag 可追溯到 IDL commit。
- AC4：`applicant-api` 不再引用 `com.vesta.spark.applicant.v1.*`，Maven dependency 仍可保持 `com.spark.contract:spark-idl-java`。
- AC5：服务矩阵中 `applicant-api.proto_path` 指向 `{idl-repo}/vesta/lendora/applicant/v1`。
- AC6：`buf lint`、`buf generate` 和 `buf breaking --against .git#branch=master` 有结果记录；若 breaking 失败，设计和证据必须说明批准路径与风险。
- AC7：`applicant-api` 测试通过，并覆盖现有 `ApplicantAuthService` gRPC adapter 行为。
- AC8：`vesta/spark/user/*` 未被本需求迁移或删除。
- AC9：Harness 生命周期产物和门禁证据记录既有 Maven artifact、既有 Go module、发布顺序和回滚方案。

## Open Questions

| Question | Owner | Deadline | Status |
|---|---|---|---|
| 是否需要保留旧 `vesta.spark.applicant.v1` 一段迁移窗口，还是允许本票删除旧 namespace 并作为受控 breaking | Backend / Platform | 设计阶段 | Open |

## Notes

- 关联 JIRA 子任务 `LEN-41`（父 Story `LEN-2` / Epic `LEN-1`）。
- 用户已明确：`user` 后续会移除，本需求不需要考虑 user proto；Maven artifact 和 Go module 要纳入检查，但结论是继续使用现有 `idl-java-repo` / `idl-go-repo`，只改变 namespace。
- 当前项目上下文缺少 `lendora/applicant` 的 `context/project` 入口；本需求需要在影响分析中记录该上下文缺口。
