---
requirement_id: "LEN-36"
analyst: "Codex"
status: "approved"
updated_at: "2026-06-20"
approved_by: "Forest"
approved_at: "2026-06-20T11:46:53+08:00"
decision: "批准 LEN-36 服务仓库检查；harness-repo 与 business-repo 同名分支已就位，不修改 IDL。"
idl_impact: "yes"
idl_impact_reason: "本需求不修改 .proto 或 wire contract，但新增业务仓消费 IDL 生成契约的 CI 门禁，影响契约依赖治理和 merge-readiness 证据。"
---

# Impact Analysis

## Summary

本需求影响 `business-repo` 的 CI、扫描脚本和测试 fixture，也影响 `harness-repo` 的 LEN-36 生命周期产物；不修改 protobuf IDL、生成契约仓或业务服务代码。

## Affected Domains

- user：`user-api` 是当前服务矩阵中 `idl_required=true` 的 Java 服务，作为 Maven contract dependency 消费代表。
- team governance：扫描规则来源于团队级 `contract-versioning.md`，并会成为后续业务仓消费契约的通用门禁。
- CI / delivery：`business-repo` PR 和 RC 候选验证会增加 contract dependency scan。

## Affected Services

| Service | Repo | Reason | Protobuf Required |
|---|---|---|---|
| user-api | business-repo (services/backend/user-api) | Java Maven 依赖扫描代表；本需求不改业务代码 | Yes（既有服务属性）；本需求不改 IDL |
| Go contract consumers | business-repo | 通过 go.mod / go.sum 扫描规则和 fixture 覆盖，不新增 Go 服务 | No（本需求不新增服务） |
| Harness governance | harness-repo | 新增 LEN-36 requirement / impact / design / tasks / gates / evidence | No |

## API / Contract Impact

- Does this change involve protobuf IDL or external contracts: **Yes, governance / consumption gate only**。
- Wire contract impact: **No**。
- Contract repo: `idl-repo` 不进入本需求 worktree。
- Proto files: 不修改。
- Buf module: 不运行生成或 breaking 检查作为本需求实现证据。
- Buf config version: v2。
- Required buf checks: 不适用；本需求不修改 `.proto`。
- Breaking baseline: 不适用。
- Compatibility risk: wire compatibility 风险低；消费侧门禁误报 / 漏报风险中等。

## Generated Contract Impact

- `idl-java-repo`: 不修改。
- `idl-go-repo`: 不修改。
- 本需求只识别业务仓依赖的版本阶段，不发布 Java / Go 生成契约。
- 线上 artifact / tag 可解析性不在本需求脚本中做远程校验，避免 CI 权限和网络可用性成为消费侧基础门禁的误报来源。

## Data Impact

- Database schema: 无。
- Data migration: 无。
- Backfill: 无。
- Cache: 无。
- Runtime storage: 无。

## Config / Permission / Observability Impact

- Config: `business-repo` 需要集中定义 contract dependency 识别规则，例如 Maven group/artifact 白名单和 Go module 前缀。
- Permission: 不新增跨仓写权限。GitHub Actions 只读取本仓文件并运行本仓脚本。
- Metrics: 不新增运行时指标。
- Logs: CI 输出必须包含违规文件、依赖坐标、版本和规则 ID，作为失败定位证据。
- Tracing: 无运行时 tracing 影响。
- Events: 无。

## Rollout And Rollback

- Gray release: `master` 模式通过 PR path filter 自动运行；`rc` 模式首版通过 `workflow_dispatch` 手动触发。
- Kill switch: 不提供让 RC 进入 master 的人工批准开关。若扫描脚本误报，应修复集中配置或规则实现。
- Rollback steps: 回滚 `business-repo` 扫描脚本、fixture、workflow，以及 `harness-repo/requirements/LEN-36` 产物即可；无数据残留。

## Risks

| Risk | Impact | Mitigation | Owner |
|---|---|---|---|
| Java artifact 坐标或 Go module 前缀未集中维护 | 漏扫 contract dependency | 首版使用集中配置文件，后续新增契约消费者必须更新配置 | Codex |
| 变量化 Maven 版本解析不完整 | 误判或漏判 `${...}` 形式的版本 | 扫描脚本解析当前 pom 的 properties，并对无法解析的 contract version 报错 | Codex |
| Go branch dependency 没有统一语法 | 漏掉非 SemVer 的可变版本 | 将非 formal / 非合规 RC / 非 pseudo-version 的 contract version 归类为 branch_or_unclassified 并失败 | Codex |
| path filter 未覆盖脚本配置变化 | 修改规则后 CI 不运行 | workflow 将扫描脚本、配置和 workflow 自身纳入触发路径 | Codex |
| 只做本仓静态扫描，无法证明 artifact/tag 已发布 | merge-readiness 证据不完整 | 本需求只阻断错误阶段依赖；线上发布可解析性继续由 LEN-35 定义的发布证据和后续 merge-readiness 负责 | Codex |
