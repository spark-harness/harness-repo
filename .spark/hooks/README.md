# Hooks

Hook 用于把流程顺序和审批完整性从「散文约束」变成「机器阻断」。

判定逻辑全部在 `janus` 里，hook 只是薄分发：hook 不重新定义门禁规则（与
`context/harness-framework/gate-implementation.md` 一致）。`.spark/hooks.json`
是 Claude 形态的事实源，`scripts/install.sh` 按 host 安装到 `.claude` / `.codex`
/ `.gemini`。

## 当前 hook

| 事件 | matcher | 命令 | 作用 |
| --- | --- | --- | --- |
| PreToolUse | `Write\|Edit\|MultiEdit` | `janus hook guard-edit` | 编辑生命周期产物前阻断违规写入 |
| Stop | （全部） | `janus hook gate-drift-check` | 收尾时检查 gate JSON 是否有效 |

## guard-edit 判定（事前阻断）

`janus hook guard-edit` 从 stdin 读取 PreToolUse 事件，按 `tool_name` 自动识别
host（Claude `Write/Edit/MultiEdit`、Gemini `write_file/replace`、Codex
`apply_patch`），算出「这次写入后的文件内容」，只对
`requirements/<id>/{requirement.md,impact-analysis.md,design.md,tasks.json}` 和
`requirements/<id>/gates/<gate>.gate.json` 生效，其余一律放行。

规则与 `gate-implementation.md` 的对应关系：

- R3 防伪造审批：写入把 `status` 从非 `approved` 翻成 `approved` 时阻断。对应
  §1「Agent 不能代表人工评审人批准门禁」。批准只能由人执行
  `janus requirement approve ... --yes`。
- R1 worktree 隔离：在仓库主 checkout 写 `requirements/**` 时阻断。对应
  `spark-worktree-isolation`：需求文件必须写在 `.worktrees/` 隔离 worktree。
- R2 阶段顺序：`design.md` 需 `requirement.md`+`impact-analysis.md` 已存在；
  `tasks.json` 需 `design.md` 存在且 `design-review` 已批准；
  `requirement-review.gate.json` 需 `impact-analysis.md` 存在。对应 §5 门禁矩阵
  与 main-process-numbering 的阶段产物。

未覆盖：`.proto` 阶段规则。idl-repo 的 `.proto` 与具体需求没有确定性关联，留给
`merge-readiness` 门禁与 CI，不由 hook 猜测。

## 三端 deny 口径

三端（Claude / Codex / Gemini）的 PreToolUse 都把「退出码 2 + stderr 写原因」当作
deny；allow 为退出码 0 静默。所以 `guard-edit` 无需 per-host 输出 JSON，只需
per-host 输入适配器（已内置）。

## CI / MR 阻塞口径

Hook 或 CI 不应重新定义门禁规则，应读取 `context/harness-framework/gate-implementation.md`。

最低检查：

- 需求目录存在。
- 当前阶段所需门禁报告存在。
- 门禁报告固定字段完整。
- `Result` 不是 `BLOCKED`。
- `Blocks Next Stage` 与 `Result` 一致。
- `WAIVED` 门禁必须有完整豁免信息。
- 涉及 IDL 时，有契约检查证据。
- 不涉及 IDL 时，有 `N/A` 说明和理由。
