# Harness 门禁

本文是 Harness gate 的简明入口。

它不是 gate JSON 协议。字段、状态和执行细节以 `gate-implementation.md` 为准。

## 门禁列表

| Gate | 阶段 | 主要检查 |
|---|---|---|
| `requirement-review` | 2.2 | `requirement.md` 和 `impact-analysis.md` 是否可评审 |
| `design-review` | 3.3 | `design.md` 是否覆盖需求、影响面、测试、回滚和风险 |
| `dev-entry` | 4.2 | `tasks.json` 是否可执行、可追溯 |
| `service-repo-check` | 4.3 | 服务矩阵、分支、IDL 仓和 Buf 配置是否就绪 |
| `merge-readiness` | 5.1 | 验收、测试、证据、仓库状态和交付风险是否满足合并 |

## Gate JSON

新需求只使用 JSON gate：

```text
requirements/{requirement-id}/gates/{gate-id}.gate.json
```

历史 Markdown gate 只作为旧审计快照，不作为新阶段放行依据。

## 结果语义

| 结果 | 含义 |
|---|---|
| `PASS` | 当前输入满足该门禁 |
| `WARN` | 可继续，但必须记录风险、owner 和后续动作 |
| `BLOCKED` | 不允许进入下一阶段 |

门禁结论必须能追溯到源文件、命令结果或人工审批记录。聊天记录不能替代 gate 输入。

## 常用命令

```bash
janus gate validate requirements/{requirement-id}/gates/{gate-id}.gate.json
janus requirement status {requirement-id}
janus requirement verify --requirement {requirement-id} --target merge --ticket-id {ticket-id}
```

实际命令以当前 Janus 版本和仓库脚本为准。

## 常见失败

| 失败 | 处理 |
|---|---|
| 输入 hash 过期 | 重新生成或刷新 gate JSON |
| lifecycle 文件缺失 | 补齐对应阶段源文件 |
| 审批缺失 | 等待人工审批，不写假审批字段 |
| 服务矩阵缺失服务 | 先补服务矩阵或修正 affected services |
| IDL 影响不清 | 回到 impact/design 阶段澄清 |
