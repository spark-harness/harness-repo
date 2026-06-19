---
requirement_id: "LEN-35"
owner: "Codex"
status: "approved"
created_at: "2026-06-20"
related_branch: "feature/LEN-35-contract-versioning"
approved_by: "Forest"
approved_at: "2026-06-20T00:45:53+08:00"
decision: "批准 LEN-35 requirement 与 impact-analysis，允许进入设计阶段。"
---

# 治理 IDL 契约依赖版本发布与消费

## Background

Spark 当前已有 `idl-repo`、`idl-java-repo`、`idl-go-repo` 和 `business-repo` 的多仓形态。随着 Java / Go 服务同时消费 IDL 生成契约，并发开发可能通过共享 `SNAPSHOT`、本地 `replace`、branch dependency、pseudo-version 或未冻结依赖互相污染。

先说不是什么：本需求不是 Git branching 模型调整，不规定团队是否使用 epic 分支；也不是具体业务 proto 改造，不新增或修改业务 RPC、message、field 或业务 API。它是契约依赖版本治理，定义 development、RC、formal 三类版本如何发布、业务仓何时可以消费、master-bound 变更必须满足哪些依赖和证据要求。

现有 `contract-compatibility.md` 覆盖契约兼容性，但尚未明确生成契约的版本发布、消费和门禁规则。本需求需要新增团队级 `contract-versioning.md`，使后续 IDL 变更、生成物发布和业务仓消费有稳定引用。

## Goals

- R1: 定义 IDL 生成契约的 `development`、`rc`、`formal` 三类发布阶段和允许用途。
- R2: 规定 Java 契约开发期使用 ticket scoped `SNAPSHOT`，RC / formal artifact 不可覆盖。
- R3: 规定 Go 契约由 Buf 生成，但通过自有 `idl-go-repo` 的 Go module tag 分发。
- R4: 规定 formal 版本由 `idl-repo` 中人工创建的 SemVer tag 决定，CI 使用该 tag 对应 commit 构建并发布 Java / Go 契约。
- R5: 规定 master-bound business change 只能消费 formal version，不允许 RC、SNAPSHOT、pseudo-version、branch dependency 或 local replacement 进入 master。
- R6: 规定不需要 Traceability Manifest 时的追溯证据：`idl-repo` tag、CI run、Java artifact metadata、Go module tag 和业务测试证据。
- R7: 明确 `idl-java-repo` 和 `idl-go-repo` 默认不因 IDL 变更进入 worktree；只有需要修改发布流水线或生成仓脚本时才加入。
- R8: 新增团队级 `context/team/contract-versioning.md`，并被本需求和后续门禁引用。

## Non-Goals

- 不修改具体业务 `.proto` 内容。
- 不设计或修改业务 API。
- 不规定团队 Git branching 模型。
- 不要求 Java 和 Go 服务同步上线。
- 不把生成代码提交进业务仓。
- 不一次性解决所有 registry 权限治理。
- 不用版本切换掩盖 breaking contract change。
- 不引入 Buf BSR Generated SDK 作为 Go 分发模型。
- 不要求 Traceability Manifest。
- 不在本需求中修改 `idl-java-repo` 或 `idl-go-repo`，除非设计阶段证明必须修改发布流水线或生成仓脚本。

## User / Business Scenarios

### Scenario 1：并发 IDL 开发不会互相污染

Given: 两个 ticket 同时修改或消费 IDL 生成契约。

When: 开发者发布开发期 Java 契约或本地消费 Go 契约。

Then: Java 使用 ticket scoped `SNAPSHOT`，Go 只允许本地开发使用 pseudo-version 或 local `replace`，不同 ticket 不共享同一个开发契约版本。

### Scenario 2：合并候选使用冻结的 RC 契约

Given: 某个 IDL commit 已被冻结用于合并候选验证。

When: 团队发布 RC 契约并让业务仓切换依赖。

Then: Java RC artifact 和 Go RC tag 不可覆盖、不可移动，业务 merge candidate 基于 RC 运行测试并记录证据。

### Scenario 3：正式发布由 IDL tag 驱动

Given: IDL 变更已经合入线上目标分支。

When: 发布人创建 `idl-repo` SemVer tag，例如 `v1.1.0`。

Then: CI 使用该 tag 对应 commit 作为唯一输入，执行 Buf build / generate，并发布正式 Java Maven artifact 与 Go module tag。

### Scenario 4：master-bound 业务变更只能消费正式版本

Given: 业务仓变更准备合入 master。

When: merge-readiness 检查业务依赖。

Then: RC、SNAPSHOT、pseudo-version、branch dependency 和 local replacement 均被拒绝；只有 formal version 可以作为 master-bound 依赖。

## Business Rules

- BR1: 契约发布阶段分为 `development`、`rc`、`formal`。
- BR2: `development` 用于本地开发和 ticket scoped snapshot，不得作为 master-bound 依赖。
- BR3: `rc` 用于冻结 IDL commit 后的业务验证和 merge-readiness，不得进入 master。
- BR4: `formal` 用于 master-bound 业务变更和正式发布。
- BR5: Java 开发期 artifact 必须使用 ticket scoped snapshot：`{base-version}-{ticket-id}-SNAPSHOT`。
- BR6: Java RC artifact 必须使用不可变版本：`{base-version}-rc.{ticket-id}.{yyyymmdd}.{idl-short-sha}`。
- BR7: Java formal artifact 必须使用 SemVer，例如 `1.8.0`、`1.9.0` 或 `2.0.0`。
- BR8: Go 契约代码必须通过 Buf 生成，但 Go 消费版本必须通过自有 `idl-go-repo` 的 Go module tag 发布。
- BR9: Go pseudo-version 或 local `replace` 只允许用于本地开发。
- BR10: Formal 版本事实来源为 `idl-repo` 中人工创建的 SemVer tag。
- BR11: CI 不得从 proto diff、commit message、分支名或业务仓依赖自动推断 formal 版本。
- BR12: RC 和 formal Maven artifact 不得覆盖发布。
- BR13: RC 和 formal Go tag 不得移动、删除或 force-push。
- BR14: 重新发布已存在的 RC / formal 版本必须失败。
- BR15: Master-bound business change 必须消费 formal version。
- BR16: Master 不允许消费 RC、SNAPSHOT、pseudo-version、branch dependency 或 local replacement。
- BR17: 不设置允许 RC 进入 master 的批准例外路径。
- BR18: 不要求 Traceability Manifest；追溯证据来自 `idl-repo` tag、CI run、Java artifact metadata、Go module tag 和业务测试证据。
- BR19: `idl-java-repo` 和 `idl-go-repo` 默认不进入 worktree；只有需要修改生成仓发布流水线、发布脚本或仓库结构时才加入。

## Acceptance Criteria

- AC1: 团队级 `context/team/contract-versioning.md` 定义 development / rc / formal 三类契约发布阶段。
- AC2: Java workflow 规则支持 ticket scoped snapshot、不可变 RC artifact 和 formal SemVer artifact。
- AC3: Go workflow 规则明确通过 Buf 生成代码，并通过自有 `idl-go-repo` 的 RC / formal module tag 分发。
- AC4: Go `v2+` 生成模块规则明确要求 `/vN` module path、require path、import path 和 tag major version 一致，且禁止 `+incompatible`。
- AC5: Formal 发布规则明确由 `idl-repo` SemVer tag 驱动，CI 使用 tag commit 构建 Java / Go 契约。
- AC6: Merge-readiness 规则能拒绝 master-bound 变更消费共享 `SNAPSHOT`、RC、pseudo-version、branch dependency、local `replace` 或缺失线上 artifact/tag 证据。
- AC7: 两个并发 ticket 能发布并消费相互隔离的开发或 RC 契约版本，且不会互相覆盖。
- AC8: 业务 master-bound 变更必须在消费 formal version 后重新运行测试并记录证据。
- AC9: Breaking contract change 必须具备明确的兼容策略、版本决策、迁移计划和回滚计划。
- AC10: Worktree 规则明确 `idl-java-repo` 和 `idl-go-repo` 不因普通 IDL 变更自动进入 worktree。

## Open Questions

| Question | Owner | Deadline | Status |
|---|---|---|---|
| RC workflow 第一版是否只支持手动 GitHub Actions 触发，还是同时支持 label / PR comment 触发 | Codex | 设计阶段 | 默认手动触发 |
| Java artifact group / artifact name 是否需要统一命名表 | Codex | 设计阶段 | 待从发布配置确认 |
| Go module path 是否需要按契约域拆分多个 module | Codex | 设计阶段 | 待从 `idl-go-repo` 初始化方案确认 |

## Notes

- 用户已明确选择自有 `idl-go-repo`，不使用 Buf BSR Generated SDK。
- 用户已明确 master 不允许 RC 进入，且不设置批准例外路径。
- 用户已明确 formal 版本事实来源改为人工创建的 `idl-repo` SemVer tag，而不是 release file。
- 用户已明确不需要 Traceability Manifest。
- 用户已明确 `idl-java-repo` 和 `idl-go-repo` 默认不进入 worktree，因为可以使用线上生成物版本，IDL 先提交。
