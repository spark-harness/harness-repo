---
requirement_id: "LEN-40"
owner: "Harness Team"
status: "approved"
created_at: "2026-06-20"
related_branch: "feature/LEN-40-delivery-flow"
target_branch: "master"
release_branch: "master"
contract_gate_mode: "auto"
affected_repositories:
  - harness-repo
  - janus
  - business-repo
  - idl-repo
approved_by: "forest"
approved_at: "2026-06-21T00:48:09+08:00"
decision: "批准 LEN-40 需求定义和影响分析。"
---

# Harness 多仓需求交付流程优化

## Background

当前多仓 CI 把“同名 feature 分支必须存在”当作跨仓一致性的主要判断。它不适合
两类真实交付路径：

- `feature -> master`
- `feature -> epic/foo -> master`

这个需求不是什么：它不绑定 LEN-12，不负责补救历史需求，也不处理任何业务
API、服务逻辑、数据库、缓存、BFF 或前端实现。

它是什么：它定义 Harness 多仓需求交付流程优化，让需求显式声明 source /
target / release 分支，并让 Janus / CI 按当前交付阶段验证 peer repo、contract
dependency 和人工 Formal 发布证据。

## Goals

- 支持多仓需求声明 `related_branch`、`target_branch`、`release_branch` 和
  `contract_gate_mode`。
- 支持 `feature -> master` 和 `feature -> epic/foo -> master` 两种路径。
- 让 peer repo 校验从“同名分支必须存在”升级为“满足当前阶段状态”。
- 区分 integration-bound 的 `rc-or-formal` 与 release-bound 的 `formal-only`。
- Formal 发布由人完成，Janus / CI 只验证可追溯证据。
- 各仓 workflow 调用 Janus，不复制分支判断 bash。

## Non-Goals

- 不实现任何具体业务 API、服务逻辑、数据库、缓存、BFF 或前端代码。
- 不自动执行 Formal 发布。
- 不手写或维护 `delivery-manifest.json`。
- 不为某个历史需求补救流程。

## User / Business Scenarios

### Scenario 1: 直接发布

Given: 需求声明 `target_branch: "master"` 且 `release_branch: "master"`

When: CI 运行 `janus delivery verify`

Then: Janus 判定为 release-bound，并使用 `formal-only` contract 规则。

### Scenario 2: 先集成后发布

Given: 需求声明 `target_branch: "epic/foo"` 且 `release_branch: "master"`

When: feature PR 合入 `epic/foo`

Then: Janus 判定为 integration-bound，并允许 immutable RC 或 formal，禁止 SNAPSHOT。

### Scenario 3: feature 分支已清理

Given: peer repo 的 feature 分支已合并并删除

When: Janus 验证 peer repo 状态

Then: 只要能证明 related 已合入 target 或 release，gate 不因同名 feature 分支缺失失败。

### Scenario 4: Formal 发布人工完成

Given: 人工已创建 Formal tag 并触发发布

When: release-bound gate 运行

Then: Janus / CI 验证 tag、commit 可追溯性、artifact 和 business dependency，不自动发布。

## Business Rules

- BR1 `target_branch == release_branch` 表示 release-bound，contract gate mode 为
  `formal-only`。
- BR2 `target_branch != release_branch` 表示 integration-bound，contract gate mode 为
  `rc-or-formal`。
- BR3 integration-bound peer repo 合法状态包括同名 `related_branch` 存在、
  `related_branch` 已合入 `target_branch`、或 `target_branch` 已合入
  `release_branch`。
- BR4 release-bound peer repo 合法状态要求 `related_branch` 或 `target_branch` 已合入
  `release_branch`；在 PR gate 阶段，允许用同一 requirement 的 open release PR
  作为待合并 peer 证据。
- BR5 integration-bound 禁止 SNAPSHOT，但允许 immutable RC 或 formal。
- BR6 release-bound 只允许 formal。
- BR7 Formal 发布由人完成；Janus / CI 只验证证据。
- BR8 各仓 workflow 不复制复杂 bash 逻辑，只调用 Janus。

## Acceptance Criteria

- AC1 不写死 `master`，所有判断来自 requirement front matter 或 PR base。
- AC2 支持 `feature -> master`。
- AC3 支持 `feature -> epic/foo -> master`。
- AC4 peer feature branch 删除后，只要已合入 target/release，gate 不失败。
- AC5 integration-bound 禁止 SNAPSHOT，但允许 immutable RC。
- AC6 release-bound 只允许 formal。
- AC7 Formal 发布不自动化，但 gate 能验证人工发布结果。
- AC8 方案不依赖具体业务需求或业务实现。
- AC9 business contract scan 支持 `rc-or-formal` 和 `formal-only`。
- AC10 Harness、business、IDL 的 branch coherence workflow 改为调用
  `janus delivery verify`。
- AC11 多仓 release-bound PR 同步打开时，peer repo 可用 open release PR 证据通过
  PR 阶段 readiness；最终发布仍必须验证 merge / formal 证据。

## Open Questions

| Question | Owner | Deadline | Status |
|---|---|---|---|
| GitHub token 是否能跨私有仓读取 peer repo branch / tag / PR 证据？ | Harness Team | 2026-06-24 | open |
| Maven / Go artifact registry 的只读验证凭据在 CI 中如何配置？ | Harness Team | 2026-06-24 | open |

## Notes

- 现有 IDL workflow 已支持 RC 与 Formal 发布入口；本需求先验证和接入证据口径，不改发布自动化。
- `delivery-manifest.json` 不作为事实源；需求 front matter 与 Git / CI 证据是事实源。
