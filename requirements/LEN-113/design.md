---
requirement_id: "LEN-113"
owner: "Forest"
status: "approved"
updated_at: "2026-06-25T21:27:23+08:00"
approved_by: "Forest"
approved_at: "2026-06-25T21:31:31+08:00"
decision: "批准 LEN-113 设计，允许进入任务拆分阶段。"
---

# Design

## Requirement Traceability

| Requirement Item | Design Decision | Notes |
|---|---|---|
| AC1, BR1 | D1: Harness 文档和工作区 AGENTS 指令统一指向 `context/harness-framework/templates/` | 不保留不存在的根 `templates/` 目录说明 |
| AC2, BR2 | D2: business-repo 只做目录和服务矩阵扫描验证，不创建业务仓代码 diff | `services/*` 不存在是当前正确状态 |
| AC3, BR3 | D3: Janus 交付仓库推断补齐治理相关仓库名称 | 保持现有文本名称扫描模型，不在本票改成结构化解析 |
| AC4, BR4 | D4: runtime mirror 验证使用 `harness-repo/scripts/install.sh --check` | mirror 输出不作为业务代码改动 |

## Summary

本设计把 LEN-113 限定为治理漂移修复。

它不是什么：它不是业务功能设计，不定义新 API，不改变服务运行时配置，也不发布契约。

它是什么：它统一文档事实源、验证 business-repo 目录事实、修正 Janus 治理仓推断覆盖，并用 install 检查证明 runtime mirror 无漂移。

## Affected Services

| Service | Change | Reason |
|---|---|---|
| N/A | `harness-repo` 文档和 lifecycle 产物 | 治理入口需要与模板事实源一致 |
| N/A | `business-repo` 扫描验证 | 证明 `apps/*` 是当前服务路径事实源 |
| N/A | `janus` delivery inference | 避免治理相关仓库被旧 allowlist 漏掉 |

## API / Contract Design

- Protobuf IDL required: No.
- Proto files: N/A.
- Buf module: N/A.
- Buf config version: v2, unchanged.
- Generated outputs: N/A.
- Breaking check baseline: N/A.
- Compatibility strategy: no contract surface is changed.

## Application Design

### D1: Harness 模板路径口径

修改 Harness README 和工作区 AGENTS 指令中仍暗示根 `templates/` 的内容，统一指向 `context/harness-framework/templates/`。

验收方式：

- 搜索旧路径表达，确认没有 `harness-repo/templates` 或根 `templates/` 目录口径残留。

### D2: business-repo 目录事实验证

重新扫描 business-repo 主 checkout 和 LEN-113 worktree。

验收方式：

- `git status --short --branch` 显示主 checkout 干净。
- `find business-repo ... services` 不返回旧 `services/*`。
- `.service-matrix/dependencies.yaml` 中服务路径仍解析到 `apps/fides-web`、`apps/fides-bff` 和 `apps/applicant-api`。

### D3: Janus 仓库推断覆盖

在 Janus delivery inference 的已知仓库集合中补齐当前治理和交付相关仓库。

验收方式：

- 增加回归测试，证明需求文本包含 `learning-docs-repo` 和 `janus` 时可以推断出来。
- 运行 `go test ./...`。

### D4: Runtime mirror 校验

在 Harness worktree 内运行 install check。

验收方式：

- `./scripts/install.sh --check` 返回 `install --check: in sync`。

## Data / Config / Permission

- Data model: no change.
- Config: no service runtime config change.
- Permission: no permission model change.

## Observability

- Logs: no application log change.
- Metrics: no metric change.
- Tracing: no tracing change.
- Events: no event change.

## Testing Strategy

- Harness:
  - old template path grep check.
  - `./scripts/install.sh --check`.
  - `janus gate validate` for lifecycle gates.
- business-repo:
  - directory scan for `services/*`.
  - service matrix path verification.
- Janus:
  - focused regression test for governance repository inference.
  - full `go test ./...`.

## Rollout And Rollback

- Rollout:
  - Keep existing PRs as Draft until lifecycle gates are backfilled.
  - Push Harness lifecycle/docs change and Janus inference change through their own PRs.
  - Restore PRs to Ready only after dev-entry and service-repo-check are valid.
- Rollback:
  - Revert Harness README / lifecycle PR if template path governance is wrong.
  - Revert Janus PR if delivery inference regresses.
  - No business-repo rollback expected because no business code change is planned.

## Risks

| Risk | Mitigation | Owner |
|---|---|---|
| Draft PRs already exist before lifecycle artifacts | Keep them Draft until gates are restored | Forest |
| Janus text inference remains simple string matching | Limit this ticket to allowlist coverage; open separate ticket for structured repository metadata if needed | Platform |
| business-repo directory layout changes again | Treat service matrix and README as source of truth and record scan commands in evidence | Platform |
