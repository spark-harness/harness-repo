---
requirement_id: "LEN-114"
analyst: "forest"
status: "approved"
updated_at: "2026-06-26"
idl_impact: "no"
idl_impact_reason: "本需求只改 business-repo 手写 Java 项目质量门禁、GitOps Argo 工作流和 Janus runner 工具链，不修改 .proto、Buf 配置或生成契约。"
approved_by: "forest"
approved_at: "2026-06-26T08:49:52+08:00"
decision: "用户已授权直接批准；批准 LEN-114 服务仓库检查，确认涉及 harness-repo、business-repo、gitops-repo 和 janus，服务矩阵服务为 applicant-api，IDL 影响为 no。"
---

# Impact Analysis

## Summary

LEN-114 将 business-repo 中手写 Java Maven 项目的 PR 质量门禁统一为
`spark/java-ci`。变更影响业务仓 Java 项目质量检查入口、GitOps 中 Argo
WorkflowTemplate/Sensor 路由，以及 Janus runner 镜像的 Java 工具链；不改变
运行时业务逻辑、数据模型或外部契约。

## Affected Domains

- Java CI 治理：新增 `tooling/java-quality`，根据 PR 变更范围选择项目。
- Java 项目质量门禁：money、spring-starter、applicant-api 统一运行格式、
  Checkstyle、单元测试和 SpotBugs。
- Argo CI 编排：`spark/java-ci` 使用 DAG 表达 money 与 spring-starter 可并行，
  applicant-api 依赖 spring-starter。
- CI runner 工具链：Janus runner 需要 JDK 21 和 Maven 3.9.11，以支持
  applicant-api 的 Java 21 编译。
- Harness 治理：补齐 LEN-114 生命周期、门禁和证据材料。

## Affected Services

| Service / Tool | Repo | Reason | Protobuf Required |
|---|---|---|---|
| money | `business-repo` | 接入统一 Java quality gate；修正干净 CI 编译插件版本 | No |
| spring-starter | `business-repo` | 接入统一 Java quality gate，并为 applicant-api 提供本地 Maven artifact | No |
| applicant-api | `business-repo` | 接入统一 Java quality gate；验证 Java 21 编译、测试和静态检查 | No |
| github-repo-gate | `gitops-repo` | 增加 Java CI DAG 和 JDK 21 runner 默认镜像 | No |
| Janus delivery verify | `janus` | 要求使用 business tooling contract scanner，避免旧 fallback | No |

## Upstream / Downstream Consumers

- GitHub PR checks：继续使用稳定 status `spark/java-ci`，不拆分项目级 required
  status。
- Spark 开发者和 Agent：通过 `tooling/java-quality/java_quality.py` 获得一致的
  Java 项目选择与门禁入口。
- Argo Workflows：在 checkout 后执行路径选择，并按项目依赖关系调度。
- branch protection：应依赖 `spark/java-ci` 的汇总结果。

## API / Contract Impact

- Does this change involve protobuf IDL or external contracts: No.
- Contract repo: `idl-repo` is not edited.
- Proto files: none changed.
- Buf module: unchanged.
- Buf config version: unchanged.
- Required buf checks: not required for this CI-only source change.
- Breaking baseline: not applicable.
- Compatibility risk: none for external API or protobuf contract.

## Generated Contract Impact

- `idl-java-repo` 不在本需求范围内。
- `spark-idl-java` 仅作为 applicant-api 既有依赖被 Maven 解析，不修改生成物版本。

## Data Impact

- Database schema: none.
- Data migration: none.
- Backfill: none.
- Cache: none.
- Runtime storage: none.

## Config / Permission / Observability Impact

- Config: GitOps WorkflowTemplate/Sensor 和 Janus runner image tag 变更。
- Permission: 继续使用现有 GitHub source token 和 registry pull secret。
- Metrics: no metric schema change.
- Logs: Java CI 日志需要明确输出 `JAVA_PROJECT_START/PASS/FAIL/SKIP`。
- Tracing: no tracing schema change.
- Events: Argo Sensor 继续薄路由，不承载复杂路径判断。

## Rollout And Rollback

- Gray release: branch / PR level by Argo status checks.
- Rollout steps:
  - 合入 Janus no-fallback delivery verify 修复。
  - 合入 GitOps Java CI DAG 与 JDK 21 runner 默认镜像。
  - 合入 business-repo Java quality tooling 和 Maven 项目配置。
  - 手动应用 live `WorkflowTemplate/github-repo-gate`，并运行 Java CI workflow 验证。
- Rollback steps:
  - 回退 GitOps `github-repo-gate` 默认 runner image 和 Java CI DAG。
  - 回退 business-repo Java quality tooling commit。
  - 回退 Janus delivery verify contract scanner 要求。

## Risks

| Risk | Impact | Mitigation | Owner |
|---|---|---|---|
| Argo project pod 之间 Maven local repo 不共享 | applicant-api 无法解析本分支安装的 spring-starter artifact | Java quality 命令固定使用 `/workspace/.m2/repository` | Codex |
| runner JDK 版本低于 applicant-api release | applicant-api 编译失败 | Janus runner 切换为 Temurin JDK 21 并显式安装 Maven 3.9.11 | Codex |
| Docker Hub base 拉取不稳定 | runner image 构建失败 | 使用已验证可拉取的 `eclipse-temurin:21-jdk-jammy` runtime base | Codex |
| Java 项目选择逻辑误选或漏选 | PR 等待时间或覆盖率异常 | 单测覆盖 money、spring-starter、质量工具、无 Java 变更和未知项目路径 | Codex |
