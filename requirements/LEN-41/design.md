---
requirement_id: "LEN-41"
owner: "Codex"
status: "approved"
updated_at: "2026-06-21"
approved_by: "Forest"
approved_at: "2026-06-21T00:48:26+08:00"
decision: "批准 LEN-41 design，允许进入任务拆分。"
---

# Design

## Requirement Traceability

| Requirement Item | Design Decision | Notes |
|---|---|---|
| R1, R2, R8, AC1, AC6 | D1: 将 applicant auth proto 从 `vesta/spark/applicant/v1/auth.proto` 移动到 `vesta/lendora/applicant/v1/auth.proto`，并改 package 为 `vesta.lendora.applicant.v1` | RPC、字段编号、字段名和业务语义不变 |
| R3, R6, AC2, AC4, AC7 | D2: Java generated package 改为 `com.vesta.lendora.applicant.v1`，`applicant-api` 同步切换 imports | 只修改 applicant-api；不修改 user-api |
| R4, BR2, BR6, AC2, AC4 | D3: Java 发布坐标保持 `com.spark.contract:spark-idl-java`，只迁移 applicant generated Java package | 继续使用 `spark-harness/idl-java-repo` |
| R5, BR2, AC3 | D4: Go module 保持 `github.com/spark-harness/idl-go-repo`，只迁移 applicant Go package path | 继续使用 `spark-harness/idl-go-repo` |
| R7, AC5, AC9 | D5: 更新服务矩阵和 Harness 产物，使 applicant proto path 统一指向 `vesta/lendora/applicant/v1` | 历史 LEN-12 产物不回写，只由 LEN-41 supersede |
| BR4, AC6, AC9 | D6: 迁移按受控 breaking 处理；`buf breaking` 预期可能因删除旧 package/service 失败，证据必须记录失败项和已知消费者清单 | 已知直接消费者为 `applicant-api` |
| BR5, AC8 | D7: `vesta/spark/user/*` 完全不纳入本需求 diff | user 后续移除任务处理 |

## Summary

本设计修正 Lendora applicant 契约归属。目标不是新增身份能力，而是把已经存在的 `ApplicantAuthService` 从 Spark applicant namespace 迁移到 Lendora applicant namespace。

设计采用受控 breaking 迁移，而不是长期双轨保留。Maven artifact 和 Go module 继续使用既有团队级生成契约仓库与发布坐标；继续保留旧 Spark applicant namespace 才是需要清理的混淆点。受控 breaking 的风险通过消费者清单、发布顺序和可回滚依赖版本控制。

## Affected Services

| Service | Change | Reason |
|---|---|---|
| applicant-api | generated Java imports 从 Spark package 切到 Lendora package；Maven dependency 坐标不变 | 当前唯一已知直接消费者 |
| idl-repo | 移动 applicant auth proto；保留 Buf Go generation prefix 与发布 workflow 目标 | 契约事实源 |
| idl-java-repo | 继续发布 `com.spark.contract:spark-idl-java`，新增 Lendora applicant generated Java package | Java generated contract 发布目标 |
| idl-go-repo | 继续发布 `github.com/spark-harness/idl-go-repo`，新增 Lendora applicant Go package path | Go generated contract 发布目标 |
| harness-repo | 更新服务矩阵、LEN-41 需求生命周期产物和证据 | 追溯与门禁 |

`user-api`、`vesta/spark/user/*`、`fides-bff` 和前端不在本设计修改范围内。

## API / Contract Design

- Protobuf IDL required: Yes。
- Proto files:
  - Remove or move from `idl-repo/vesta/spark/applicant/v1/auth.proto`。
  - Add `idl-repo/vesta/lendora/applicant/v1/auth.proto`。
- Buf module: 仍沿用 `idl-repo/buf.yaml` v2 单模块配置。
- Buf config version: v2。
- Generated outputs:
  - Java message + Java gRPC stub under `com/vesta/lendora/applicant/v1`。
  - Go message + Go gRPC stub under `vesta/lendora/applicant/v1` in the existing `idl-go-repo` module。
- Breaking check baseline: `buf breaking --against .git#branch=master`。
- Compatibility strategy: 受控 breaking replacement；字段和 RPC 行为保持不变，但 package/service full name、Java package 和 Go import path 改变。Maven coordinate 和 Go module coordinate 不改变。

目标 proto 形状：

```proto
syntax = "proto3";

package vesta.lendora.applicant.v1;

option go_package = "github.com/spark-harness/idl-go-repo/vesta/lendora/applicant/v1;applicantv1pb";
option java_multiple_files = true;
option java_outer_classname = "ApplicantAuthProto";
option java_package = "com.vesta.lendora.applicant.v1";

service ApplicantAuthService {
  rpc SendOtp(SendOtpRequest) returns (SendOtpResponse);
  rpc VerifyOtp(VerifyOtpRequest) returns (VerifyOtpResponse);
  rpc RefreshToken(RefreshTokenRequest) returns (RefreshTokenResponse);
}
```

RPC 和 message 字段保持 LEN-12 已发布形状：

| RPC | Request | Response |
|---|---|---|
| `SendOtp` | `country_code`, `phone`, `idempotency_key` | `challenge_id`, `expires_in_sec`, `resend_after_sec` |
| `VerifyOtp` | `challenge_id`, `code`, `idempotency_key` | `access_token`, `refresh_token`, `applicant_id`, `expires_in_sec`, `refresh_expires_in_sec` |
| `RefreshToken` | `refresh_token`, `idempotency_key` | `access_token`, `expires_in_sec` |

## Generated Contract Publishing

### Java

Java artifact target:

```text
com.spark.contract:spark-idl-java
```

Required changes:

- `idl-java-repo/pom.xml`
  - keep `groupId`: `com.spark.contract`
  - keep `artifactId`: `spark-idl-java`
  - keep `name`: `spark-idl-java`
  - keep publishing all generated Java classes under the existing artifact.
- `idl-java-repo/README.md`
  - continue documenting `spark-idl-java`.
- `idl-repo/.github/workflows/publish-java-idl.yml`
  - keep `MAVEN_PACKAGE_NAME=com.spark.contract.spark-idl-java`.
  - keep Maven version preparation targeting `<artifactId>spark-idl-java</artifactId>`.
- `idl-repo/.github/workflows/sync-java-idl.yml`
  - continue pushing generated Java code to `spark-harness/idl-java-repo`.

Master-bound `applicant-api` must depend on a formal version of `spark-idl-java`; RC or snapshot can be used only before merge-readiness.

### Go

Go module target:

```text
github.com/spark-harness/idl-go-repo
```

Required changes:

- `idl-repo/buf.gen.yaml` and `buf.gen.go.yaml` keep `go_package_prefix` as `github.com/spark-harness/idl-go-repo`.
- `idl-repo/.github/workflows/sync-go-idl.yml` keeps `GO_IDL_REPOSITORY=spark-harness/idl-go-repo`.
- `idl-repo/.github/workflows/publish-go-idl.yml` keeps `GO_IDL_REPOSITORY=spark-harness/idl-go-repo`.
- `auth.proto` sets `go_package` to `github.com/spark-harness/idl-go-repo/vesta/lendora/applicant/v1;applicantv1pb`.

## Application Design

`applicant-api` changes are intentionally narrow:

- `pom.xml`
  - keep dependency `com.spark.contract:spark-idl-java`.
  - keep `spark.contract.version` and repository URL.
  - update only if the formal generated contract version changes as part of normal release promotion.
- Java source and tests:
  - replace `com.vesta.spark.applicant.v1.*` imports with `com.vesta.lendora.applicant.v1.*`.
  - keep adapter behavior and tests unchanged except package imports.
- README:
  - continue mentioning `spark-idl-java` as the applicant contract dependency.

No application, domain, Redis, token, telemetry, or endpoint behavior changes are allowed in this ticket.

## Service Matrix And Harness Docs

`harness-repo/.service-matrix/dependencies.yaml` changes:

```yaml
applicant-api:
  proto_path: "{idl-repo}/vesta/lendora/applicant/v1"
  buf_module: "local/lendora-applicant"
```

Do not alter `user-api` proto settings in this ticket.

Historical LEN-12 files remain immutable audit history. LEN-41 documents that its new path supersedes LEN-12’s `vesta/spark/applicant/v1` path.

## Data / Config / Permission

- Data model: no database, Redis, token, or applicant data migration.
- Config:
  - Maven contract coordinate stays unchanged in `applicant-api`.
  - Go module target stays unchanged in IDL publish workflows.
  - CI token scopes stay on the existing generated repos/packages.
- Permission:
  - `IDL_JAVA_REPO_TOKEN` must continue to read/write `spark-harness/idl-java-repo` and publish `com.spark.contract:spark-idl-java`.
  - `IDL_GO_REPO_TOKEN` must continue to read/write `spark-harness/idl-go-repo` and create immutable tags.

## Observability

- Logs: no runtime log field changes.
- Metrics: no runtime metric changes.
- Tracing: no runtime tracing changes.
- Events: no business event changes.
- CI evidence must log resolved IDL commit, Java artifact coordinate/version, Go module tag, and consumer commit.

## Testing Strategy

IDL and generated contract checks:

- `buf lint`
- `buf generate`
- `buf breaking --against .git#branch=master`
- Java generated repo: `mvn -B test`
- Go generated repo: `go mod tidy` and `go test ./...`

Business consumer checks:

- `mvn test` in `business-repo/services/backend/applicant-api`
- Contract dependency scanner in `business-repo` for master mode using the existing artifact/module policy

Expected breaking behavior:

- If old `vesta/spark/applicant/v1/auth.proto` is removed, `buf breaking` may report deleted package/service/message paths.
- This is acceptable only if the gate evidence records:
  - old package deleted,
  - new Lendora package added,
  - known direct consumer migrated in the same ticket,
  - no BFF / external consumer found in current repo scan,
  - rollback path via previous formal artifact version.

## Rollout And Rollback

Rollout order:

1. Land IDL path/package and generation workflow changes on LEN-41 branch.
2. Generate Java and Go contracts into existing generated repos/branches.
3. Publish immutable RC versions for Java and Go.
4. Switch `applicant-api` imports and contract version to the RC during branch validation.
5. Create formal IDL tag and publish formal Java artifact / Go module tag on the existing coordinates.
6. Switch `applicant-api` to the formal `spark-idl-java` version before master-bound merge.
7. Record evidence in LEN-41 merge-readiness.

Rollback:

- Before merge: revert LEN-41 branch changes.
- After publishing RC: do not delete or overwrite RC; publish a corrected RC.
- After formal publication: do not move formal tags; publish a subsequent formal version and roll `applicant-api` dependency forward or back to the prior formal artifact version if emergency rollback is required.
- Runtime rollback is dependency-level only; no data rollback is needed.

## Risks

| Risk | Mitigation | Owner |
|---|---|---|
| `buf breaking` fails because old package is removed | Treat as controlled breaking with explicit evidence and consumer migration | Backend / Platform |
| Existing `idl-java-repo` still contains user generated code | Accept as existing generated contract repo scope; do not change user proto in this ticket | Platform |
| Business scanner behavior drifts after namespace migration | Verify existing scanner still accepts `spark-idl-java` and `idl-go-repo` policies | Backend |
| Historical LEN-12 docs still mention Spark path | Record supersede relation in LEN-41 and avoid rewriting old approved gates | Codex |

## Open Decisions Before Implementation

| Decision | Default | Blocking If Different |
|---|---|---|
| Old Spark applicant proto | delete in this ticket as controlled breaking | If retained, design must become dual-track migration |
