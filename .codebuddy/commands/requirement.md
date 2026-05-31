# Requirement Commands

## `/requirement:new`

创建 `requirements/{requirement-id}/`，复制需求、影响面、设计、任务和门禁模板。

## `/requirement:continue`

读取需求目录、当前阶段、最近门禁报告和相关上下文，恢复工作状态。

## `/requirement:next`

根据 `context/harness-framework/main-process-numbering.md` 判断是否允许进入下一阶段。

执行要求：

1. 读取当前需求阶段。
2. 根据阶段找到必须通过的门禁。
3. 读取 `requirements/{requirement-id}/gates/{gate-id}.md`。
4. 如果报告缺失、字段不完整或 `Result: BLOCKED`，停止推进。
5. 如果 `Result: PASS`，推进到下一阶段。
6. 如果 `Result: WARN`，推进到下一阶段，并输出风险和后续动作。
7. 如果 `Result: WAIVED`，校验豁免字段完整后推进。

详细协议见 `context/harness-framework/gate-implementation.md`。

## `/requirement:gate-check`

执行当前阶段对应门禁，并把结果写入 `requirements/{requirement-id}/gates/`。

执行要求：

1. 读取门禁检查矩阵。
2. 读取当前门禁所需输入文件。
3. 生成固定格式门禁报告。
4. 不允许只在对话中给出“通过”或“阻塞”。

## `/requirement:gate-waive`

按豁免规则为指定门禁补充 `Waiver` 区块。

执行要求：

1. 只能针对已有 `BLOCKED` 门禁报告。
2. 必须填写原因、批准人、批准时间、失效时间和后续动作。
3. 豁免后 `Result` 可改为 `WAIVED`。
4. 豁免不能永久有效。
