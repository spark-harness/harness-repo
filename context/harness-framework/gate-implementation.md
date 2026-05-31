# Gate Implementation Protocol

本文定义门禁从“检查建议”落到“可执行阻塞”的实施协议。

它回答七个问题：

- 门禁报告模板。
- 字段规范。
- Agent 输出格式。
- Skill 执行流程。
- 阶段推进命令。
- CI / MR 阻塞规则。
- 异常豁免规则。

## 1. 基本原则

门禁不是口头判断。任何门禁结论必须落到固定格式文件中。

阶段推进入口只能读取门禁报告结论，不能读取聊天记录作为放行依据。

```text
没有门禁报告 = 阻塞
门禁报告格式不合法 = 阻塞
Result 为 BLOCKED = 阻塞
Result 为 PASS = 放行
Result 为 WARN = 放行但必须记录风险和后续动作
Result 为 WAIVED = 按豁免规则放行
```

## 2. 门禁报告位置

门禁报告写入：

```text
requirements/{requirement-id}/gates/{gate-id}.md
```

推荐 `gate-id`：

| 阶段 | 门禁 | gate-id |
| --- | --- | --- |
| 2.2 | 需求评审门禁 | `2.2-requirement-review` |
| 3.3 | 设计门禁 | `3.3-design-review` |
| 4.2 | Dev 进入门禁 | `4.2-dev-entry` |
| 4.3 | 服务仓库检查门禁 | `4.3-service-repo-check` |

## 3. 固定字段

门禁报告必须保留下列字段名。字段名使用英文，字段值可以使用中文。

```text
Requirement ID
Gate ID
Gate Name
Stage
Checked By
Checked At
Result
Blocks Next Stage
Source Files
```

字段含义：

| 字段 | 必填 | 含义 |
| --- | --- | --- |
| Requirement ID | 是 | 需求 ID |
| Gate ID | 是 | 机器读取的门禁 ID |
| Gate Name | 是 | 人类可读的门禁名称 |
| Stage | 是 | 当前阶段编号 |
| Checked By | 是 | 执行检查的 Agent、Skill、Command 或人员 |
| Checked At | 是 | 检查时间 |
| Result | 是 | `PASS` / `BLOCKED` / `WARN` / `WAIVED` |
| Blocks Next Stage | 是 | `yes` / `no` |
| Source Files | 是 | 本次检查读取的关键文件 |

`Blocks Next Stage` 必须和 `Result` 保持一致：

| Result | Blocks Next Stage |
| --- | --- |
| PASS | `no` |
| WARN | `no` |
| BLOCKED | `yes` |
| WAIVED | `no` |

## 4. 状态语义

| 状态 | 是否允许进入下一阶段 | 语义 |
| --- | --- | --- |
| PASS | 是 | 所有阻塞条件已满足 |
| WARN | 是 | 存在风险，但不阻塞，必须记录后续动作 |
| BLOCKED | 否 | 存在阻塞问题，不能继续 |
| WAIVED | 是 | 原本会阻塞，但已按豁免规则批准 |

`WARN` 不能用于掩盖阻塞问题。只要存在门禁定义中的阻塞条件，就必须使用 `BLOCKED`，除非有正式豁免记录。

## 5. 门禁检查矩阵

### 2.2 需求评审门禁

输入：

- `requirements/{requirement-id}/requirement.md`
- `requirements/{requirement-id}/impact-analysis.md`

通过条件：

- 背景、目标、非目标明确。
- 场景、业务规则和验收标准可测试。
- 待确认问题显式列出。

阻塞条件：

- 需求文档缺失。
- 关键业务规则缺失。
- 验收标准不可测试。
- 待确认问题未列出。

### 3.3 设计门禁

输入：

- `requirements/{requirement-id}/requirement.md`
- `requirements/{requirement-id}/impact-analysis.md`
- `requirements/{requirement-id}/design.md`

通过条件：

- 设计覆盖服务、接口、数据、配置、权限、可观测性、灰度和回滚。
- 明确 protobuf IDL 或外部契约影响。
- 设计决策能追溯到需求条目。

阻塞条件：

- 设计文档缺失。
- IDL 或外部契约影响未说明。
- 缺少灰度或回滚方案。
- 需求条目无法追溯到设计决策。

### 4.2 Dev 进入门禁

输入：

- `requirements/{requirement-id}/design.md`
- `requirements/{requirement-id}/tasks.json`

通过条件：

- 任务拆分完整。
- 每个任务有范围、验收和追溯来源。

阻塞条件：

- 任务文件缺失或格式不合法。
- 任务没有验收标准。
- 任务无法追溯到需求或设计。

### 4.3 服务仓库检查门禁

输入：

- `requirements/{requirement-id}/impact-analysis.md`
- `requirements/{requirement-id}/design.md`
- `requirements/{requirement-id}/tasks.json`
- `.service-matrix/dependencies.yaml`

通过条件：

- 涉及服务存在于服务矩阵。
- 涉及仓库分支已就位。
- 如涉及 IDL，IDL 契约仓已就位。
- 如涉及 IDL，契约检查证据已记录。

阻塞条件：

- 涉及服务不在服务矩阵中。
- 仓库分支不一致。
- 设计声明涉及 IDL，但契约仓未就位。
- 设计未说明是否涉及 IDL。

无 IDL 变化时，IDL 检查项可以标记为 `N/A`，但必须在报告中说明理由。

## 6. Agent 输出格式

Agent 执行门禁时，必须输出两类内容：

- 写入门禁报告文件。
- 在对话中给出简短结论和文件路径。

Agent 不能只在对话中说“通过”。

Agent 输出报告时必须包含：

- `Metadata` 固定字段。
- `Checklist` 检查项表格。
- `Blocking Issues` 阻塞项表格。
- `Warnings` 风险项表格。
- `Waiver` 豁免信息。
- `Decision` 是否允许进入下一阶段。

对话结论格式：

```text
Gate: 3.3-design-review
Result: BLOCKED
Report: requirements/T12345/gates/3.3-design-review.md
Reason: 缺少回滚方案，不能进入 4.1。
```

## 7. Skill 执行流程

Skill 执行门禁时按以下顺序：

1. 读取流程真相源，确认当前阶段和目标门禁。
2. 读取门禁所需输入文件。
3. 校验输入文件是否存在。
4. 执行门禁检查矩阵中的检查项。
5. 收集证据路径。
6. 生成门禁报告。
7. 根据 `Result` 决定是否允许继续。
8. 如果 `BLOCKED`，停止推进并列出阻塞项。
9. 如果 `WARN`，继续推进但记录后续动作。
10. 如果 `WAIVED`，检查豁免信息是否完整。

Skill 不应在缺少报告时继续推进阶段。

## 8. 阶段推进命令

`/requirement:next` 必须执行以下逻辑：

```text
1. 读取当前需求状态。
2. 计算进入下一阶段所需门禁。
3. 读取对应门禁报告。
4. 如果报告不存在，阻塞。
5. 如果报告固定字段缺失，阻塞。
6. 如果 Result = BLOCKED，阻塞。
7. 如果 Result = PASS，推进阶段。
8. 如果 Result = WARN，推进阶段并输出风险。
9. 如果 Result = WAIVED，校验豁免字段，合法后推进阶段。
```

伪代码：

```text
report = read_gate_report(requirement_id, required_gate)

if report is missing:
  block("missing gate report")

if report has invalid schema:
  block("invalid gate report")

if report.result == "BLOCKED":
  block(report.blocking_issues)

if report.result == "WAIVED" and waiver is invalid:
  block("invalid waiver")

advance()
```

## 9. CI / MR 阻塞规则

CI 或 MR 检查应复用同一套门禁报告，不重新定义第二套口径。

最低检查：

- 需求目录存在。
- 当前阶段所需门禁报告存在。
- 门禁报告固定字段完整。
- `Result` 不是 `BLOCKED`。
- `Blocks Next Stage` 与 `Result` 一致。
- 涉及 IDL 时，有契约检查证据。
- 不涉及 IDL 时，报告中有 `N/A` 和理由。

CI / MR 必须失败的情况：

- 门禁报告缺失。
- 门禁报告格式不合法。
- `Result: BLOCKED`。
- `Result: WAIVED` 但缺少批准人、原因或有效期。
- 代码或 IDL 变更无法追溯到需求、设计或任务。

## 10. 异常豁免规则

豁免不是绕过门禁。豁免是把一次例外写成可审计记录。

只有以下场景可以考虑豁免：

- 线上紧急修复，等待完整门禁会扩大影响。
- 外部依赖临时不可用，但风险已被接受。
- 部分检查无法自动执行，但已有人工证据。

豁免必须写在同一份门禁报告的 `Waiver` 区块中。

必填字段：

```text
Waiver Required: yes
Waiver Reason:
Approved By:
Approved At:
Expires At:
Follow-Up Issue:
```

豁免限制：

- 不能永久有效。
- 不能没有负责人。
- 不能没有后续动作。
- 不能用于掩盖需求、设计或契约影响未说明的问题。

`WAIVED` 只能由有批准记录的门禁报告使用。没有批准记录时，必须保持 `BLOCKED`。

## 11. 最小可用门禁报告示例

```markdown
# Gate Report

## Metadata

- Requirement ID: T12345
- Gate ID: 3.3-design-review
- Gate Name: 设计门禁
- Stage: 3.3
- Checked By: detail-design-quality-reviewer
- Checked At: 2026-05-31T10:00:00+08:00
- Result: BLOCKED
- Blocks Next Stage: yes
- Source Files:
  - requirements/T12345/requirement.md
  - requirements/T12345/impact-analysis.md
  - requirements/T12345/design.md

## Checklist

| Item | Result | Evidence |
| --- | --- | --- |
| 覆盖服务影响 | PASS | design.md#服务影响 |
| 明确 IDL 影响 | PASS | design.md#契约影响 |
| 明确回滚方案 | BLOCKED | design.md 缺少回滚章节 |

## Blocking Issues

| Issue | Required Action | Owner |
| --- | --- | --- |
| 缺少回滚方案 | 补充灰度关闭和代码回滚策略 | backend |

## Warnings

| Warning | Follow-Up | Owner |
| --- | --- | --- |
|  |  |  |

## Waiver

- Waiver Required: no
- Waiver Reason:
- Approved By:
- Approved At:
- Expires At:
- Follow-Up Issue:

## Decision

不允许进入 4.1 任务拆分。补齐回滚方案后重新执行 3.3 设计门禁。
```
