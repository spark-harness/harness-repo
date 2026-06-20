---
requirement_id: "LEN-40"
owner: "Harness Team"
status: "approved"
updated_at: "2026-06-20"
approved_by: "forest"
approved_at: "2026-06-21T00:48:20+08:00"
decision: "批准 LEN-40 设计方案。"
---

# Design

## Requirement Traceability

| Requirement Item | Design Decision | Notes |
|---|---|---|
| AC1, AC2, AC3 | Requirement front matter 增加 `target_branch`、`release_branch`、`contract_gate_mode`、`affected_repositories` | 不写死 master |
| AC4 | Janus `delivery verify` 用 Git refs / merge-base / merge commit 证据判断 peer 状态 | 后续可接 GitHub PR 查询 |
| AC5, AC6, AC9 | business contract scan 支持 `rc-or-formal` / `formal-only`，Janus 在 business PR 上调用变更范围扫描 | 旧 `rc` / `master` 模式保留兼容 |
| AC7 | release-readiness 验证 business formal dependency、IDL formal tag 和 artifact，不触发发布 | 仅扫描当前 PR 变更到的 contract dependency 文件 |
| AC8, AC10 | 三仓 workflow 调用 Janus，不复制分支判断 bash | workflow 只负责 checkout 和构建 Janus |

## Summary

新增统一交付 verifier：

```bash
janus delivery verify --requirement <REQ-ID> --repo <repo-name>
```

它读取 `harness-repo/requirements/{id}/requirement.md` front matter，判断当前
delivery bound，并输出 `integration-readiness` 或 `release-readiness` gate 语义。

## Affected Services

| Service | Change | Reason |
|---|---|---|
| `harness-repo` | 更新模板和流程文档 | 明确分支声明、epic branch、contract gate 和 readiness gate 规则 |
| `janus` | 新增 `internal/delivery` 和 `delivery verify` CLI | 统一 Git / peer repo 阶段判断 |
| `business-repo` | 扩展 contract dependency scan 模式名 | 支持 integration-bound / release-bound 语义 |
| `idl-repo` | delivery readiness workflow 调用 Janus | 用 Janus 替代同名分支 bash |

## API / Contract Design

- Protobuf IDL required: no schema changes.
- Proto files: none.
- Buf module: unchanged.
- Buf config version: v2.
- Generated outputs: none.
- Breaking check baseline: unchanged.
- Compatibility strategy: contract dependency gate 只改变版本阶段规则，不改业务接口。

## Delivery Verifier Design

输入：

- `--requirement`：需求 ID。
- `--repo`：当前仓库名。
- `--workspace`：多仓 checkout 根目录，默认 `..`。
- `--base`：当前 PR base，CI 传入 `github.base_ref` 或默认分支。
- `--head`：当前 PR head，CI 传入 `github.head_ref` 或 `github.ref_name`。
- `--output-gate`：可选，写入 readiness gate JSON。

核心判断：

```text
target_branch == release_branch => release-bound => release-readiness => formal-only
target_branch != release_branch => integration-bound => integration-readiness => rc-or-formal
```

peer repo 合法状态：

- `related_branch` 存在。
- `related_branch` 是 `target_branch` 的 ancestor。
- `related_branch` 或 `target_branch` 已进入 `release_branch`。
- feature 分支删除后，本地 fallback 可用 merge commit message 证明 related branch。
- `epic/foo -> master` 时，PR head 等于 `target_branch` 且 base 等于
  `release_branch`，按 release-bound / formal-only 处理。
- 当前仓是 `business-repo` 时，Janus 对当前 PR 变更到的 `pom.xml`、`go.mod`、
  `go.sum` 调用 business contract dependency scan。

MVP 不做：

- 不直接调用 GitHub PR API。
- 不自动执行 Formal 发布。

GitHub PR / merge commit 查询作为后续增强接入同一 `delivery verify`，不再散落到
workflow bash。

Release-bound 且当前 PR 变更 `pom.xml`、`go.mod` 或 `go.sum` 时，Janus 解析
business formal dependency，并验证：

- `idl-repo` formal tag 存在。
- tag commit 可从 `release_branch` 追溯。
- Java Maven artifact version 存在，或 Go module tag 存在。
- artifact version 与 business dependency version 匹配。

未变更 contract dependency 文件时，不强扫历史依赖债务。

## Data / Config / Permission

- Data model: none.
- Config: workflow 需要能 checkout `janus`、`harness-repo`、`business-repo`、`idl-repo`。
- Permission: 私有仓读取使用 `JANUS_REPO_TOKEN` 和 `BRANCH_COHERENCE_TOKEN` fallback。
- Artifact permissions: release-bound artifact 只读验证凭据后续接入 Janus。

## Observability

- Logs: `delivery verify` 输出 gate id、bound、contract mode 和 peer 状态。
- Metrics: none.
- Tracing: none.
- Events: none.

## Testing Strategy

- Janus: `go test ./...` 覆盖 bound 判断、peer branch 存在、peer 已合入、base mismatch、gate JSON 输出。
- business-repo: `python3 -m unittest tests/test_contract_dependency_scan.py` 覆盖新旧模式名。
- workflow: 用 `bash -n` 或 YAML 结构检查确认脚本语法。

## Rollout And Rollback

- Rollout: 同一 branch 在 `harness-repo`、`janus`、`business-repo`、`idl-repo` 提交并分别开 PR。
- Rollback: revert workflow 后恢复旧 branch-coherence；revert Janus `delivery` 包不影响现有 `gate` / `requirement` 命令。

## Risks

| Risk | Mitigation | Owner |
|---|---|---|
| workflow checkout 多仓时 token 不足 | 使用专用 token fallback，并在 PR 验证中暴露缺失权限 | Harness Team |
| 本地 Git fallback 无法覆盖所有 feature 删除场景 | 后续把 GitHub PR / merge commit 查询集中接入 Janus | Harness Team |
| artifact 查询凭据缺失 | workflow 传入只读 artifact / generated-contract repo token；缺失时 release-bound formal dependency PR 阻塞 | Harness Team |
