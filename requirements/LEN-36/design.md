---
requirement_id: "LEN-36"
owner: "Codex"
status: "approved"
updated_at: "2026-06-20"
approved_by: "Forest"
approved_at: "2026-06-20T11:41:07+08:00"
decision: "批准 LEN-36 design，允许进入任务拆分。"
---

# Design

## Requirement Traceability

| Requirement Item | Design Decision | Notes |
|---|---|---|
| R1, R2, AC1, AC2 | D1: 在 `business-repo` 新增一个本地可执行扫描脚本，GitHub Actions 只调用该脚本 | 本地和 CI 共享规则 |
| R3, AC3 | D2: Maven 扫描解析 `pom.xml` dependencies 和 properties，仅检查集中配置命中的 contract artifact | 默认不扫描所有第三方依赖 |
| R4, AC4 | D3: Go 扫描解析 `go.mod` require / replace，仅检查集中配置命中的 contract module 前缀 | `go.sum` 变化触发扫描，但事实来源是 `go.mod` |
| R5, AC5, AC6, AC7 | D4: GitHub Actions PR 默认运行 `master` 模式并只扫描本 PR 变更的依赖文件，`workflow_dispatch` 支持选择 `rc` 或 `master` 并执行全仓扫描 | 首版不做 label 自动切换 |
| R6, R7, AC6, AC7 | D5: 版本分类器区分 formal、rc、snapshot、pseudo-version、local-replace、branch-or-unclassified | master / rc 模式应用不同允许集 |
| R8, AC9 | D6: 违规输出包含文件、依赖坐标、版本和规则 ID | 便于 CI 失败定位 |
| R9, AC8 | D7: 用 fixture 驱动脚本测试，覆盖 Java / Go pass 与 fail 场景 | 先测试再实现 |
| R10, AC10 | D8: Harness 设计、任务和证据引用 LEN-35 `contract-versioning.md` | 规则来源可追溯 |

## Summary

本设计在 `business-repo` 建立消费侧契约依赖扫描门禁。脚本负责读取集中配置、扫描 Maven 与 Go 依赖、按 `master` / `rc` 模式判断版本阶段，并输出机器和人都能定位的违规信息。PR CI 只扫描本次变更涉及的依赖文件，避免首次接入时被历史 SNAPSHOT 债务阻塞；手动 RC / master 扫描仍可执行全仓检查。

先说不是什么：本设计不实现契约发布流水线，不远程查询 Maven artifact 或 Go tag 是否存在，不修改业务服务逻辑，也不把 RC 依赖放进 master 的批准例外路径。

## Affected Services

| Service | Change | Reason |
|---|---|---|
| user-api | 无业务代码变更；Maven contract dependency 扫描代表 | 服务矩阵中 `idl_required=true` |
| Go contract consumers | 无新增服务；通过 Go module 文件扫描规则覆盖 | 需求要求 Go 规则，不要求新增 Go 服务 |
| business-repo CI | 新增扫描脚本、配置、fixture 测试和 workflow | 落地契约消费门禁 |
| Harness governance | 新增 LEN-36 生命周期产物和 gate | 保持需求、设计、任务和证据可追溯 |

## API / Contract Design

- Protobuf IDL required: 否，不修改 `.proto`。
- Proto files: 不修改。
- Buf module: 不适用。
- Buf config version: v2（既有治理事实，不作为本实现输入）。
- Generated outputs: 不生成。
- Breaking check baseline: 不适用。
- Compatibility strategy: wire contract 兼容性仍由 `contract-compatibility.md` 管理；本需求只检查业务仓消费的生成契约依赖版本阶段。

## Application Design

### 文件布局

`business-repo` 新增：

```text
config/contract-dependencies.json
scripts/contract_dependency_scan.py
tests/contract_dependency_scan/fixtures/
tests/test_contract_dependency_scan.py
.github/workflows/contract-dependency-scan.yml
```

配置文件集中定义要扫描的 contract dependency：

- Maven: `groupId` + `artifactId` 精确匹配。
- Go: module path 前缀匹配。

### 扫描模式

`--mode master`：

- 允许 Java formal SemVer。
- 允许 Go formal SemVer tag。
- 拒绝 Java SNAPSHOT、Java RC、Go pseudo-version、Go local replace、branch dependency、无法归类的 contract dependency。

`--mode rc`：

- 允许 Java formal SemVer。
- 允许 Java RC：`{base-version}-rc.{ticket-id}.{yyyymmdd}.{idl-short-sha}`。
- 允许 Go formal SemVer tag。
- 允许 Go RC tag：`v{base-version}-rc.{ticket-id}.{yyyymmdd}.{idl-short-sha}`，ticket ID 大小写不敏感。
- 拒绝 Java SNAPSHOT、Go pseudo-version、Go local replace、branch dependency、可变或不符合格式的 RC、无法归类的 contract dependency。

### Maven 扫描

脚本解析每个 `pom.xml`：

- 收集当前 POM 的 `<properties>`。
- 遍历 `<dependencies>/<dependency>`。
- 仅检查配置命中的 `groupId:artifactId`。
- 解析直接版本和 `${property}` 版本。
- 无法解析的 contract dependency 版本视为违规。

### Go 扫描

脚本解析每个 `go.mod`：

- 读取 `require` 单行和块语法。
- 读取 `replace` 单行和块语法。
- 仅检查配置中 module 前缀命中的 dependency。
- 本地路径 replace 直接违规。
- 非 formal / 非合规 RC / 非 pseudo-version 的 contract version 归类为 branch-or-unclassified 并失败。

### CI 触发

GitHub Actions：

- `pull_request` 触发，路径包含 `**/pom.xml`、`**/go.mod`、`**/go.sum`、扫描脚本、配置和 workflow。
- PR 默认运行 `master` 模式，并通过 `git diff --name-only` 把变更的 `pom.xml`、`go.mod`、`go.sum` 传给脚本；`go.sum` 映射到同目录 `go.mod`。
- 只修改扫描脚本、配置、测试或 workflow 时，脚本测试会运行，依赖扫描不会扫描历史未变更依赖文件。
- `workflow_dispatch` 触发，输入 `mode` 支持 `master` / `rc`，用于人工执行全仓扫描。
- RC 候选首版通过手动触发 `mode=rc`。

## Data / Config / Permission

- Data model: 无。
- Config: 新增 `config/contract-dependencies.json`。
- Permission: GitHub Actions 使用本仓 checkout 和 Python，不需要跨仓 token。
- Secrets: 不新增。

## Observability

- Logs: 脚本失败输出每条 violation 的 file、dependency、version、rule 和 message。
- Metrics: 无运行时指标。
- Tracing: 无。
- Events: 无。

## Testing Strategy

采用测试优先：

- 先新增 `tests/test_contract_dependency_scan.py` 和 fixture，覆盖 AC8 要求的 pass / fail 场景。
- 先运行测试确认脚本缺失或行为缺失导致失败。
- 实现脚本后运行 `python3 -m unittest tests/test_contract_dependency_scan.py`。
- 运行代表性 CLI 命令验证本地可执行：
  - `python3 scripts/contract_dependency_scan.py --mode master --root tests/contract_dependency_scan/fixtures/java-formal-pass`
  - `python3 scripts/contract_dependency_scan.py --mode rc --root tests/contract_dependency_scan/fixtures/java-rc-pass`
  - `python3 scripts/contract_dependency_scan.py --mode master --path services/backend/user-api/pom.xml`

## Rollout And Rollback

- Gray release: PR path filter 自动运行 master 模式；RC 模式手动触发。
- Kill switch: 不提供 master 接受 RC 的开关；误报通过更新集中配置或脚本规则修复。
- Rollback: 回滚 `business-repo` 新增脚本、配置、测试、workflow 和 `harness-repo/requirements/LEN-36`。

## Risks

| Risk | Mitigation | Owner |
|---|---|---|
| Maven 父 POM 或 profile 中定义版本导致首版无法解析 | 首版解析当前 POM properties；无法解析时 fail closed，并在输出中提示具体 property | Codex |
| Go branch dependency 表达形式多样 | 对 contract module 的非 SemVer / 非合规 RC / 非 pseudo-version 统一 fail closed | Codex |
| 配置漏掉新 contract dependency | 将配置文件纳入评审和 CI 触发路径；新增消费者时更新配置 | Codex |
| workflow_dispatch 的 rc 模式依赖人工选择 | 首版保留 label 自动触发为后续扩展；PR 仍以 changed-file master scan 守住 master-bound 依赖变更 | Codex |
