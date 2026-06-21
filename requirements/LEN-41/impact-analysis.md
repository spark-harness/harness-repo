---
requirement_id: "LEN-41"
analyst: "Codex"
status: "approved"
updated_at: "2026-06-21"
approved_by: "Forest"
approved_at: "2026-06-21T01:08:50+08:00"
decision: "批准 LEN-41 impact-analysis 和 service-repo-check，允许继续后续交付验证。"
idl_impact: "yes"
idl_impact_reason: "本需求迁移 Lendora applicant protobuf namespace，并在既有 Java / Go generated contract 仓库和发布坐标下同步生成路径。"
---

# Impact Analysis

## Summary

将 Lendora applicant 身份契约从 Spark applicant namespace 迁移到 Lendora applicant namespace；同步更新 `applicant-api` generated Java imports、服务矩阵和契约发布证据。生成仓库和发布坐标保持既有 `idl-java-repo` / `idl-go-repo`。

交付验证发现 release-bound `janus delivery verify` 需要识别已 squash merge 的 IDL peer PR、优先使用远端 release ref 判定 formal tag reachability，并优先使用 Java generated contract token 查询 Maven package。因此本需求同时纳入 Janus delivery verifier 的聚焦修复。

## Affected Domains

- `applicant`：Lendora 申请人身份、手机号 OTP 和短期会话契约。
- `contract publishing`：Java Maven artifact 和 Go module 发布仍使用既有坐标，生成内容新增 Lendora applicant package path。
- `frontend`：未来 BFF 或前端职责方会消费 applicant 契约；本需求不修改 `fides-bff`。
- `user`：明确不在本需求范围内；`vesta/spark/user/*` 后续移除任务单独处理。

## Affected Services

| Service | Repo | Reason | Protobuf Required |
|---|---|---|---|
| applicant-api | business-repo (`services/backend/applicant-api`) | 切换 generated Java imports，Maven dependency 坐标保持不变 | Yes |
| applicant proto | idl-repo (`vesta/lendora/applicant/v1`) | 迁移 applicant auth.proto 路径、package、java_package 和 go_package | Yes |
| Java generated contract | idl-java-repo | 保持 `com.spark.contract:spark-idl-java`，生成 `com.vesta.lendora.applicant.v1` | Yes |
| Go generated contract | idl-go-repo | 保持 `github.com/spark-harness/idl-go-repo`，生成 `vesta/lendora/applicant/v1` package path | Yes |
| harness lifecycle | harness-repo (`requirements/LEN-41`) | 记录需求、影响、设计、任务、证据和门禁 | No |
| delivery verifier | janus (`internal/delivery`) | release-bound delivery-readiness 需要接受已 merge peer PR、远端 release ref 和正式 Maven package 查询 | No |

## Upstream / Downstream Consumers

- 当前已知直接消费者：`business-repo/services/backend/applicant-api`。
- 未来消费者：`fides-bff` 或前端职责方可能消费 applicant 契约，但本需求不修改 BFF。
- 不处理消费者：`user-api` 不属于本需求范围。
- Generated contract consumers: Java consumer in `applicant-api`；Go consumers 暂未在当前业务仓中确认。

## API / Contract Impact

- Does this change involve protobuf IDL or external contracts: **Yes**。
- Contract repo: `idl-repo`。
- Current proto files: `{idl-repo}/vesta/spark/applicant/v1/auth.proto`。
- Target proto files: `{idl-repo}/vesta/lendora/applicant/v1/auth.proto`。
- Current proto package: `vesta.spark.applicant.v1`。
- Target proto package: `vesta.lendora.applicant.v1`。
- Current Java package: `com.vesta.spark.applicant.v1`。
- Target Java package: `com.vesta.lendora.applicant.v1`。
- Maven artifact: 保持 `com.spark.contract:spark-idl-java`。
- Go module: 保持 `github.com/spark-harness/idl-go-repo`。
- Target Go package path: `github.com/spark-harness/idl-go-repo/vesta/lendora/applicant/v1`。
- Buf module: 当前 `idl-repo/buf.yaml` 为 v2 单模块；`buf.gen.yaml` 和 `buf.gen.go.yaml` 当前使用 Spark Go package prefix。
- Buf config version: v2。
- Required buf checks:
  - `buf lint`
  - `buf generate`
  - `buf breaking --against .git#branch=master`
- Breaking baseline: `master` 上已发布的 `vesta.spark.applicant.v1`。
- Compatibility risk: 中。RPC 字段和业务语义保持不变，但 protobuf service full name、Java package 和 Go import path 会改变。Maven coordinate 和 Go module coordinate 不变。若删除旧 namespace，`buf breaking` 可能失败；必须在设计中明确是双轨迁移还是受控 breaking。

## Generated Contract Impact

- Java generated contracts:
  - 生成路径从 `com/vesta/spark/applicant/v1` 迁移到 `com/vesta/lendora/applicant/v1`。
  - `idl-java-repo/pom.xml`、README、发布 workflow 继续使用 `com.spark.contract:spark-idl-java`。
  - `applicant-api` 只需要切换 imports，dependency 坐标不变。
- Go generated contracts:
  - Go package 输出路径迁移到 `vesta/lendora/applicant/v1`。
  - `buf.gen.yaml` / `buf.gen.go.yaml` 的 Go package prefix 继续使用 `github.com/spark-harness/idl-go-repo`。
  - 生成物进入既有 `idl-go-repo` 的 `vesta/lendora/applicant/v1` 路径。
  - `vesta/spark/user/v1` Go 生成物保留，user 后续移除任务单独处理。
- Package publication:
  - Formal version 必须来自 `idl-repo` SemVer tag。
  - Master-bound `applicant-api` 不能消费 RC、SNAPSHOT、branch dependency 或 local replacement。
- Delivery verification:
  - `janus delivery verify` 必须接受同名 `idl-repo` PR 已合入 `master` 的 release-bound peer 证据。
  - Formal tag reachability 应优先使用 `origin/master` 等远端 release ref，避免 stale local branch 阻塞。
  - Maven package 查询应优先使用 `IDL_JAVA_REPO_TOKEN`，再回退到通用 GitHub token。

## Data Impact

- Database schema: 无。
- Data migration: 无。
- Backfill: 无。
- Cache: 无 Redis key 或 token 状态迁移；契约 namespace 变更不改变运行时数据。
- Runtime storage: 无。

## Config / Permission / Observability Impact

- Config:
  - Maven repository / artifact 坐标不变。
  - Go module path / tag 发布配置不变。
  - GitHub Actions secret 继续使用既有 generated repo 权限。
  - `business-repo` delivery-readiness workflow 继续从同名 Janus 分支构建 `janus`。
- Permission:
  - Java publish token 继续对 `spark-harness/idl-java-repo` / `com.spark.contract:spark-idl-java` 有写权限。
  - Go publish token 继续对 `spark-harness/idl-go-repo` 有写权限。
  - Java package 查询优先使用 workflow 中的 `IDL_JAVA_REPO_TOKEN`，避免低权限通用 token 造成 false negative。
- Metrics: 无运行时指标变更。
- Logs: 无运行时日志字段变更。
- Tracing: 无运行时 tracing 变更。
- Events: 无业务事件变更。

## Rollout And Rollback

- Gray release:
  - 先在 IDL 和生成契约链路发布包含 Lendora applicant namespace 的 RC / formal version。
  - 再切换 `applicant-api` imports 并消费既有 artifact 的对应版本。
  - 最后在后续任务清理旧 Spark applicant namespace。
- Kill switch:
  - 无运行时开关；回滚通过恢复 `applicant-api` contract dependency 和 imports 到旧 formal version。
- Rollback steps:
  - 回滚 `applicant-api` import 变更，必要时回到上一版 `spark-idl-java`。
  - 回滚服务矩阵 `proto_path` 到旧 applicant proto path。
  - 回滚 IDL 迁移提交或保留旧 namespace 作为兼容路径。
  - 如已发布错误 artifact/tag，不移动 formal tag；改发后续修正版本。

## Risks

| Risk | Impact | Mitigation | Owner |
|---|---|---|---|
| 删除旧 `vesta.spark.applicant.v1` 导致 breaking check 失败 | IDL 门禁阻塞或旧消费者无法编译 | 设计阶段选择双轨迁移或显式受控 breaking；列出已知消费者 | Backend / Platform |
| `applicant-api` 同时依赖 starter snapshot 和新 contract formal | master-bound 扫描可能仍因其他依赖失败 | 明确本需求只修正 contract dependency；其他 snapshot 风险单独记录 | Backend |
| Go 生成物仍带 Spark applicant path | Go 消费者继续看到错误 namespace | 通过 proto `go_package` 和生成物路径验证 `vesta/lendora/applicant/v1` | Platform |
| 历史 LEN-12 文档仍引用 Spark path | 审计时出现新旧路径并存 | LEN-41 记录 supersede 关系；不回写篡改已批准历史门禁 | Codex |
| user proto 不迁移 | `vesta/spark/user/*` 仍存在短期噪声 | 明确作为 Non-Goal，后续 user 移除任务处理 | Product / Backend |
| delivery-readiness 不识别 squash merge peer 状态 | business PR 被错误阻塞 | 在 Janus 中增加 `release_pr_merged` peer 状态、远端 release ref 优先级和 Java token fallback，并用 LEN-41 现场命令验证 | Harness |

## Context Gaps

- `harness-repo/context/project/` 当前没有 `lendora/applicant/INDEX.md`；缺少 Lendora applicant 领域上下文入口。建议在本需求设计或交付阶段补齐最小项目上下文。
