# Hooks

Hook 用于自动化执行前置检查，例如：

- 服务矩阵格式检查。
- 需求目录结构检查。
- 门禁报告状态检查。
- 三仓分支一致性检查。

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

本目录先保留为空骨架。引入真实脚本前，应先在 `context/harness-framework/gate-implementation.md` 中说明检查口径。
