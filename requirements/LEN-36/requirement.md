---
requirement_id: "LEN-36"
owner: "Codex"
status: "approved"
created_at: "2026-06-20"
related_branch: "feature/LEN-36-contract-dependency-ci-gates"
approved_by: "Forest"
approved_at: "2026-06-20T11:40:19+08:00"
decision: "批准 LEN-36 requirement 与 impact-analysis，允许进入设计阶段。"
---

# 实现 business-repo 契约依赖 CI 门禁

## Background

LEN-35 已经定义 IDL 生成契约的 `development`、`rc`、`formal` 三类版本，以及 master-bound business change 只能消费 formal version 的团队规则。当前还缺少 `business-repo` 侧自动检查：PR 或 RC 候选仍可能通过 Maven、Go module、pseudo-version、local `replace` 或 branch dependency 消费错误阶段的契约。

先说不是什么：本需求不是 Java / Go 契约发布流水线，不修改 `.proto`，不修改 `idl-java-repo` / `idl-go-repo` 发布逻辑，也不修改业务服务代码。

它是什么：本需求是在 `business-repo` 中新增消费侧契约依赖扫描门禁。门禁必须本地可运行，GitHub Actions 复用同一个脚本，并按 `master` / `rc` 两种模式执行不同阶段的版本规则。

## Goals

- R1: 新增本地可执行的 contract dependency scan 脚本。
- R2: 扫描脚本支持 `--mode master` 和 `--mode rc`。
- R3: 扫描 Maven `pom.xml` 中的 IDL contract dependency，并识别 formal、RC、SNAPSHOT。
- R4: 扫描 Go `go.mod` 中的 contract module，并拒绝 pseudo-version、local `replace`、branch dependency。
- R5: 在 GitHub Actions 中按 PR 变更范围运行扫描脚本。
- R6: `master` 模式只允许 formal version，不允许人工批准 RC 依赖进入 master。
- R7: `rc` 模式允许符合 LEN-35 格式的 RC version，拒绝 development 依赖和不可归类依赖。
- R8: 失败输出必须定位到文件、依赖坐标、发现的版本和违反规则。
- R9: contract dependency 识别规则集中定义，默认不扫描所有第三方依赖。
- R10: Harness 需求、设计、任务、门禁和证据引用 LEN-35 `contract-versioning.md` 作为规则来源。

## Non-Goals

- 不实现 `idl-repo` tag 触发的 Java / Go 契约发布流水线。
- 不修改 `.proto`。
- 不修改 `idl-java-repo` / `idl-go-repo` 发布逻辑。
- 不修改业务服务代码。
- 不允许通过人工批准让 RC 依赖进入 master。
- 不新增 Go 服务；Go 规则通过 `go.mod` fixture 和扫描逻辑覆盖。
- 不验证线上 Maven artifact 或 Go module tag 是否真实存在；本需求先阻断错误阶段依赖，线上可解析性证据仍由后续发布和 merge-readiness 证据承担。

## User / Business Scenarios

### Scenario 1: master-bound PR 消费 formal 契约

Given: `business-repo` PR 准备合入 `master`。

When: PR 修改了 `pom.xml`、`go.mod`、`go.sum`、扫描脚本或 workflow。

Then: CI 以 `master` 模式运行扫描，只有 formal Java / Go 契约版本通过，RC、SNAPSHOT、pseudo-version、local `replace`、branch dependency 和不可归类依赖失败。

### Scenario 2: RC 候选验证消费合规 RC

Given: 某个业务变更需要基于冻结 IDL commit 做 RC 候选验证。

When: 工程师手动触发 RC 门禁。

Then: CI 以 `rc` 模式运行扫描，符合 LEN-35 格式的 Java RC artifact 或 Go RC module tag 可以通过；development 依赖、不可变性不足或格式不合规的 RC 失败。

### Scenario 3: 本地开发者提前发现错误依赖

Given: 开发者在本地修改契约依赖。

When: 开发者运行同一个扫描脚本。

Then: 脚本输出违规文件、依赖坐标、版本和违反规则，开发者无需等 GitHub Actions 才能定位问题。

## Business Rules

- BR1: CI 必须区分 `master` 和 `rc` 两种模式。
- BR2: `master` 模式用于 PR 合入 `master`，只允许 formal version。
- BR3: `rc` 模式用于 RC 候选验证，允许符合 LEN-35 规则的 RC version，但拒绝 development 依赖。
- BR4: `master` 模式必须拒绝 Java `SNAPSHOT`、Java RC、Go pseudo-version、Go local `replace`、branch dependency 和无法归类的 contract dependency。
- BR5: `rc` 模式必须拒绝 Java `SNAPSHOT`、Go pseudo-version、Go local `replace`、branch dependency，以及可变或不符合格式的 RC。
- BR6: `rc` 模式允许 Java RC artifact：`{base-version}-rc.{ticket-id}.{yyyymmdd}.{idl-short-sha}`。
- BR7: `rc` 模式允许 Go RC module tag，格式必须与 LEN-35 团队规范一致。
- BR8: PR 中 `**/pom.xml` 变化时扫描 Maven 依赖。
- BR9: PR 中 `**/go.mod` 或 `**/go.sum` 变化时扫描 Go 依赖。
- BR10: workflow 或扫描脚本自身变化时也运行扫描。
- BR11: CI 输出必须列出违规文件、依赖坐标、发现的版本和违反规则。
- BR12: GitHub Actions 只调用同一个本地扫描脚本。
- BR13: 默认只扫描 contract dependency，不扫描所有第三方依赖。
- BR14: contract dependency 的识别规则必须配置化或集中定义。
- BR15: 不允许通过人工批准让 RC 依赖进入 master。

## Acceptance Criteria

- AC1: `business-repo` 新增本地可执行的 contract dependency scan 脚本。
- AC2: 脚本支持 `--mode rc` 和 `--mode master`。
- AC3: 脚本能扫描 Maven `pom.xml` 中的 IDL contract dependency，并识别 formal / RC / SNAPSHOT。
- AC4: 脚本能扫描 Go `go.mod` 中的 contract module，拒绝 pseudo-version、local `replace`、branch dependency。
- AC5: GitHub Actions 在 PR 变更 `pom.xml` / `go.mod` / `go.sum` / 扫描脚本 / workflow 时运行。
- AC6: PR 合入 `master` 时运行 `master` 模式，RC 依赖会失败。
- AC7: RC 候选路径运行 `rc` 模式，合法 RC 通过，不合法 RC / SNAPSHOT / pseudo-version / replace 失败。
- AC8: 测试 fixture 覆盖 Java formal pass、Java RC pass/fail、Java SNAPSHOT fail、Go formal pass、Go RC pass/fail、Go pseudo-version fail、Go replace fail。
- AC9: CI 失败信息可定位到具体文件和依赖。
- AC10: LEN-35 的 `contract-versioning.md` 规范被引用为规则来源。

## Open Questions

| Question | Owner | Deadline | Status |
|---|---|---|---|
| RC gate 是否后续支持 PR label 如 `contract-rc` 自动触发 | Codex | 设计阶段 | 首版使用 `workflow_dispatch` + `mode=rc` |
| Go contract module 是否已有固定 module path | Codex | 设计阶段 | 若没有，首版用集中配置维护 module 前缀 |
| Java contract artifact 坐标是否固定 | Codex | 设计阶段 | 若没有，首版用集中配置维护 group/artifact 白名单 |

## Notes

- 规则来源为 LEN-35 `context/team/contract-versioning.md`。
- `user-api` 是 Java / IDL 生成契约消费者代表。
- Go 服务不作为本需求新增对象；Go 规则通过 module 文件扫描和 fixture 验证。
