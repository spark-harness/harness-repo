---
requirement_id: "LEN-114"
owner: "forest"
status: "approved"
updated_at: "2026-06-26"
approved_by: "forest"
approved_at: "2026-06-26T08:33:05+08:00"
decision: "用户已授权直接批准；批准 LEN-114 设计，确认路径选择在 business tooling 中完成，GitOps 仅做薄路由，Argo DAG 汇总稳定 spark/java-ci，并使用共享 Maven repo 与 JDK 21 runner 支持 applicant-api。"
---

# Design

## Requirement Traceability

| Requirement Item | Design Decision | Notes |
|---|---|---|
| R1, AC1 | D1: 在 business-repo 增加 `tooling/java-quality` | 工具负责路径选择、项目分层和 Maven gate 入口 |
| R2, AC2 | D2: 每个 Java 项目运行 Maven quality goal | 覆盖 Spotless、Checkstyle、test、SpotBugs |
| R3, R4, R5, AC3-AC5 | D3: 由工具根据路径映射项目并展开依赖项目 | spring-starter 变更会选择 applicant-api |
| R6, AC7-AC9 | D4: GitOps 使用 Argo DAG 汇总为 `spark/java-ci` | Sensor 只做薄路由，复杂判断在 checkout 后执行 |
| BR1, Non-Goals | D5: 不扫描生成契约仓、不修改 IDL | Java CI 仅覆盖手写 Java Maven 项目 |
| BR7 | D6: 输出稳定项目级日志标记 | 便于 Argo UI 定位失败项目 |
| AC7 | D7: Maven local repo 位于共享 workspace | 跨 pod 传递 spring-starter install artifact |
| AC9 | D8: Janus runner 使用 JDK 21 | 支持 applicant-api Java 21 编译 |

## Summary

方案把 Java 项目选择逻辑放在 business-repo 的 Python 工具中，把执行编排放在
GitOps Argo WorkflowTemplate 中。Argo Sensor 只负责识别 business-repo PR 并
触发 `spark/java-ci`，实际变更路径选择、项目依赖展开和跳过逻辑都在 checkout
后的 `tooling/java-quality/java_quality.py` 中执行。

## Affected Services

| Service / Project | Change | Reason |
|---|---|---|
| money | 接入 Java quality gate，补 compiler plugin 版本 | 干净 CI 编译必须识别 `maven.compiler.release` |
| spring-starter | 接入 Java quality gate 并 install 到共享 Maven repo | applicant-api 依赖本分支 artifact |
| applicant-api | 接入 Java quality gate | 验证 Java 21 编译、测试和静态检查 |
| GitOps Argo | 增加 Java CI DAG | 用单一 `spark/java-ci` 汇总多项目结果 |
| Janus runner | 使用 JDK 21/Maven 3.9.11 | 支持 applicant-api release 21 |

## API / Contract Design

- Protobuf IDL required: No.
- Proto files: none changed.
- Buf module: unchanged.
- Generated outputs: unchanged.
- Breaking check baseline: not applicable.
- Compatibility strategy: no external contract change; CI-only behavior change.

## Application Design

### D1：Java quality 工具

`tooling/java-quality/java_quality.py` 定义手写 Java 项目清单、项目路径、POM
路径和项目依赖关系。它提供：

- `plan`：从显式路径生成项目选择和 DAG layer。
- `plan-git`：从 PR base 到 HEAD 的 git diff 生成计划。
- `run-project`：执行单项目 Maven quality gate，支持按 plan 跳过未选项目。

### D2：Maven quality gate

每个项目统一运行格式检查、Checkstyle、单元测试和 SpotBugs。spring-starter
因为被 applicant-api 依赖，在通过 quality gate 后执行 `install`，将 artifact
写入共享 Maven local repo。

### D3：项目依赖展开

money 是独立项目；spring-starter 被 applicant-api 依赖。选择 spring-starter
时，工具会自动展开 applicant-api，保证公共 starter 改动被消费者验证。

### D4：Argo DAG

`github-repo-gate` 中的 Java CI DAG 包含：

- plan
- money
- spring-starter
- applicant-api

money 和 spring-starter 依赖 plan，可并行；applicant-api 依赖 spring-starter。
所有结果汇总到 GitHub status `spark/java-ci`。

### D5：生成契约排除

本需求不扫描 `idl-java-repo` 或生成物仓。applicant-api 对 `spark-idl-java`
的依赖仍按现有 Maven settings 和 GitHub Packages 认证解析。

### D6：日志标记

工具输出 `JAVA_PROJECT_SELECT`、`JAVA_PROJECT_LAYER`、`JAVA_PROJECT_START`、
`JAVA_PROJECT_PASS`、`JAVA_PROJECT_FAIL`、`JAVA_PROJECT_SKIP`。这些标记用于
快速定位项目选择和失败项目。

### D7：共享 Maven local repo

Java quality 命令使用 workspace 级 Maven local repo，确保 spring-starter pod
安装的 snapshot artifact 可被 applicant-api pod 读取。

### D8：JDK 21 runner

Janus runner runtime 使用 Temurin JDK 21，并显式安装 Maven 3.9.11。这样同一
runner 同时支持 Janus、Buf、GitHub CLI 和 Java 21 Maven gate。

## Data / Config / Permission

- Data model: no change.
- Runtime config: no application config change.
- CI config: GitOps WorkflowTemplate/Sensor and runner image changed.
- Permission: use existing GitHub token secret and registry pull secret.

## Observability

- Logs: Java quality output includes project-level markers.
- Metrics: no change.
- Tracing: no change.
- Events: no runtime event schema change.

## Testing Strategy

- Python unit tests for Java project selection, dependency expansion, skip behavior and
  shared Maven repo command construction.
- Local `python3 -m unittest tooling/java-quality/tests/test_java_quality.py`.
- Local project gate for money where feasible.
- Argo `business-repo-java-ci-prwz2` verifies money, spring-starter and applicant-api
  against the live `spark/java-ci` workflow.
- GitOps `kubectl kustomize workflows/templates` and `kubectl kustomize workflows/ci`.
- Janus runner image smoke: `java -version`, `mvn -version`, `janus version`, `buf --version`.

## Rollout And Rollback

- Rollout:
  - Merge Janus no-fallback delivery verify fix.
  - Merge GitOps Java CI DAG and JDK 21 runner.
  - Merge business-repo Java quality tooling.
  - Confirm `spark/java-ci` succeeds on business PR.
- Rollback:
  - Revert GitOps Java CI template and runner image.
  - Revert business Java quality tooling commit.
  - Revert Janus delivery verify scanner requirement if needed.

## Risks

| Risk | Mitigation | Owner |
|---|---|---|
| Project selection misses a dependent project | Unit tests cover spring-starter dependent expansion | Codex |
| applicant-api cannot see spring-starter artifact | Shared `/workspace/.m2/repository` Maven local repo | Codex |
| runner JDK mismatch | JDK 21 runner verified before live template update | Codex |
| CI logs are hard to diagnose | Stable `JAVA_PROJECT_*` markers | Codex |
