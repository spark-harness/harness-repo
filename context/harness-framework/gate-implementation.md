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

Agent 不能代表人工评审人批准门禁。Agent 自检通过只能说明门禁材料 `ready for approval`；在人工评审人明确批准前，门禁总结果必须保持 `BLOCKED`，阻塞项写明“等待人工批准”。

这条由机器执行，不只靠自觉：`janus hook guard-edit` 拦截任何把产物 `status` 改为
`approved` 的 Write/Edit；人工批准只能由人执行 `janus requirement approve ... --yes`
写入。见 `.spark/hooks/README.md`。

```text
没有门禁报告 = 阻塞
门禁报告格式不合法 = 阻塞
Result 为 BLOCKED = 阻塞
Result 为 PASS = 机器检查通过且人工批准完成后放行
Result 为 WARN = 放行但必须记录风险和后续动作
Result 为 WAIVED = 按豁免规则放行
```

## 2. 门禁报告位置

门禁机器事实源写入：

```text
requirements/{requirement-id}/gates/{gate-id}.gate.json
```

历史 `requirements/{requirement-id}/gates/{gate-id}.md` 只视为旧审计快照，不再由 Janus 生成、刷新、校验或作为阶段推进事实源。新需求不得新增 gate Markdown。

推荐 `gate-id` 使用语义名称，不把阶段编号写进身份字段：

| 阶段 | 门禁 | gate-id |
| --- | --- | --- |
| 2.2 | 需求评审门禁 | `requirement-review` |
| 3.3 | 设计门禁 | `design-review` |
| 4.2 | Dev 进入门禁 | `dev-entry` |
| 4.3 | 服务仓库检查门禁 | `service-repo-check` |
| 5.1 | 合并就绪门禁 | `merge-readiness` |

`stage` 字段保留阶段编号，用来表达流程位置。

## 3. JSON 固定字段

门禁 JSON 必须保留下列字段名。字段名使用 snake_case，字段值可以使用中文。

```text
schema_version
requirement_id
gate_id
gate_name
stage
checked_by
checked_at
result
blocks_next_stage
inputs
checklist
blocking_issues
warnings
waiver
repos
evidence
idl_impact
decision
```

字段含义：

| 字段 | 必填 | 含义 |
| --- | --- | --- |
| schema_version | 是 | 门禁 JSON schema 版本 |
| requirement_id | 是 | 需求 ID |
| gate_id | 是 | 机器读取的门禁 ID |
| gate_name | 是 | 人类可读的门禁名称 |
| stage | 是 | 当前阶段编号 |
| checked_by | 是 | 执行检查的 Agent、Skill、Command 或人员 |
| checked_at | 是 | RFC3339 检查时间 |
| result | 是 | `PASS` / `BLOCKED` / `WARN` / `WAIVED` |
| blocks_next_stage | 是 | 是否阻塞下一阶段 |
| inputs | 是 | 本次检查读取的关键文件及 sha256 |
| checklist | 是 | 检查项、结果和证据 |
| blocking_issues | 是 | 阻塞项；无阻塞时为空数组 |
| warnings | 是 | 非阻塞风险；无风险时为空数组 |
| waiver | 是 | 豁免信息 |
| repos | 否 | 需要校验分支策略的仓库快照 |
| evidence | 否 | 测试、Buf、验收等外部证据 |
| idl_impact | 否 | IDL 影响声明 |
| decision | 是 | 是否允许继续及原因 |

`blocks_next_stage` 必须和 `result` 保持一致：

| result | blocks_next_stage |
| --- | --- |
| PASS | `false` |
| WARN | `false` |
| BLOCKED | `true` |
| WAIVED | `false` |

## 4. 状态语义

| 状态 | 是否允许进入下一阶段 | 语义 |
| --- | --- | --- |
| PASS | 是 | 机器检查通过，且人工批准完成 |
| WARN | 是 | 存在风险，但不阻塞，必须记录后续动作 |
| BLOCKED | 否 | 存在阻塞问题，不能继续 |
| WAIVED | 是 | 原本会阻塞，但已按豁免规则批准 |

`WARN` 不能用于掩盖阻塞问题。只要存在门禁定义中的阻塞条件，就必须使用 `BLOCKED`，除非有正式豁免记录。

如果所有机器检查项都满足，但缺少人工批准记录，也必须使用 `BLOCKED`。这类阻塞项的 `required_action` 应指向对应人工评审人，而不是要求 Agent 自行继续推进。

人工批准字段保留在被评审的原始产物中，gate JSON 只保存本次检查快照：

| gate-id | 批准源 |
| --- | --- |
| `requirement-review` | `requirements/{requirement-id}/requirement.md` front matter |
| `design-review` | `requirements/{requirement-id}/design.md` front matter |
| `dev-entry` | `requirements/{requirement-id}/tasks.json` 顶层字段 |
| `service-repo-check` | `requirements/{requirement-id}/impact-analysis.md` front matter |
| `merge-readiness` | `requirements/{requirement-id}/tasks.json` 顶层字段和 evidence 文件 |

批准源使用统一字段：`status`、`approved_by`、`approved_at`、`decision`。`status` 为 `approved` 表示该产物对应的门禁已批准；`tasks.json` 中单个任务的执行状态使用 `state`，不能再使用 `status`。

状态值必须使用中心化枚举：

| 字段 | 允许值 | 说明 |
| --- | --- | --- |
| lifecycle artifact `status` | `draft`、`approved`、`blocked`、`waived` | 用于 `README.md`、`requirement.md`、`impact-analysis.md`、`design.md` front matter，以及 `tasks.json` 顶层字段 |
| task `state` | `todo`、`in_progress`、`done`、`blocked`、`waived` | 用于 `tasks.json` 中单个任务的执行状态 |
| gate `result` | `PASS`、`BLOCKED`、`WARN`、`WAIVED` | 用于 gate JSON 和 checklist item |

不要使用 `Reviewed`、`reviewed` 或其他大小写变体表达批准状态。人工批准只能使用 `status: "approved"`，并同时补齐 `approved_by`、`approved_at`、`decision`。

`impact-analysis.md` 必须在 front matter 中声明 IDL 影响：

```yaml
idl_impact: "no"
idl_impact_reason: "只复用现有 protobuf IDL，不修改契约。"
```

Janus 优先读取结构化字段 `idl_impact` 和 `idl_impact_reason`。正文中的 `IDL`、`protobuf`、`Proto files` 只作为兼容旧文档的辅助检查，不能覆盖 front matter 的结构化结论。

## 5. 门禁检查矩阵

### 2.2 需求评审门禁

输入：

- `requirements/{requirement-id}/requirement.md`
- `requirements/{requirement-id}/impact-analysis.md`

通过条件：

- 背景、目标、非目标明确。
- 场景、业务规则和验收标准可测试。
- 待确认问题显式列出。
- 影响分析覆盖服务、契约、数据、配置、权限、可观测性和回滚。

阻塞条件：

- 需求文档缺失。
- 关键业务规则缺失。
- 验收标准不可测试。
- 待确认问题未列出。
- 影响分析缺失或关键影响面未覆盖。

生成时机：

- `requirement.md` 和 `impact-analysis.md` 都存在后才生成正式门禁。
- 两者之一尚未创建时，阶段仍在进行中，不生成预期失败的 `BLOCKED` 门禁。

`janus requirement status` 可以展示未来阶段 gate 的存在状态，但正常未到阶段的 gate 缺失不应计入当前阶段阻塞。阶段推进由 `janus requirement next` 只验证当前阶段所需 gate；合并前完整性由 `janus requirement verify --target merge` 验证。

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
- 每个任务有状态、范围、验收和追溯来源。

阻塞条件：

- 任务文件缺失或格式不合法。
- 任务缺少 `state`。
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
- 如涉及 IDL，契约仓存在 `buf.yaml` v2 和 `buf.gen.yaml` v2。

阻塞条件：

- 涉及服务不在服务矩阵中。
- 仓库分支不一致。
- 设计声明涉及 IDL，但契约仓未就位。
- 设计未说明是否涉及 IDL。

无 IDL 变化时，IDL 检查项可以标记为 `N/A`，但必须在报告中说明理由。

### 5.1 合并就绪门禁

输入：

- `requirements/{requirement-id}/requirement.md`
- `requirements/{requirement-id}/impact-analysis.md`
- `requirements/{requirement-id}/design.md`
- `requirements/{requirement-id}/tasks.json`
- `requirements/{requirement-id}/evidence/*`
- `.service-matrix/dependencies.yaml`

通过条件：

- `requirement-review`、`design-review`、`dev-entry` 和 `service-repo-check` 都是 `PASS`、`WARN` 或 `WAIVED`。
- 涉及 IDL 时，合并就绪门禁包含 Buf 检查证据。
- 涉及服务实现时，合并就绪门禁包含服务测试证据。
- 证据文件 hash 与当前文件内容一致。
- 仓库分支和 ticket id 策略满足合并目标。

阻塞条件：

- 必需阶段门禁缺失或未通过。
- 任务标记完成但缺少对应证据。
- `idl_impact.impact = "yes"` 但缺少 Buf 或契约检查证据。
- 测试证据缺失或 hash 过期。

说明：

- 早期阶段门禁只负责阶段推进，不承载实现完成后的证据。
- `merge-readiness` 是合并前唯一强制检查实现证据的门禁。

## 6. Agent 输出格式

Agent 执行门禁时，必须输出两类内容：

- 写入 `*.gate.json`。
- 运行 `janus gate validate <gate.json>`。
- 在对话中给出简短结论和文件路径。

Agent 不能只在对话中说“通过”。

Agent 也不能在没有人工批准记录时把门禁总结果写成 `PASS`。这种情况下 checklist 可以记录机器检查项为 `PASS`，但报告顶层 `result` 必须是 `BLOCKED`。

Agent 输出 JSON 时必须包含：

- `inputs` 固定读取文件及 sha256。
- `checklist` 检查项。
- `blocking_issues` 阻塞项。
- `warnings` 风险项。
- `waiver` 豁免信息。
- `decision` 是否允许进入下一阶段。

对话结论格式：

```text
Gate: design-review
Result: BLOCKED
Source: requirements/T12345/gates/design-review.gate.json
Reason: 缺少回滚方案，不能进入 4.1。
```

## 7. Skill 执行流程

Skill 执行阶段门禁时按以下顺序：

1. 读取流程真相源，确认当前阶段和目标门禁。
2. 读取门禁所需输入文件。
3. 校验输入文件是否存在。
4. 执行门禁检查矩阵中的检查项。
5. 只在当前门禁职责需要时收集证据路径。
6. 生成门禁 JSON。
7. 运行 `janus gate validate`。
8. 根据 `result` 决定是否允许继续。
9. 如果 `BLOCKED`，停止推进并列出阻塞项。
10. 如果 `WARN`，继续推进但记录后续动作。
11. 如果 `WAIVED`，检查豁免信息是否完整。

Skill 不应在缺少报告时继续推进阶段。正常流程尚未完成时，不应为了表达“还没做到下一步”而生成预期失败的正式门禁。

## 8. 阶段推进命令

`/requirement:next` 必须执行以下逻辑：

```text
1. 读取当前需求状态。
2. 计算进入下一阶段所需门禁。
3. 读取对应门禁 JSON。
4. 如果 JSON 不存在，阻塞。
5. 如果 JSON 固定字段缺失或 Janus 校验失败，阻塞。
6. 如果 result = BLOCKED，阻塞。
7. 如果 result = PASS，推进阶段。
8. 如果 result = WARN，推进阶段并输出风险。
9. 如果 result = WAIVED，校验豁免字段，合法后推进阶段。
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
- 合并前 `merge-readiness` 门禁存在。
- 门禁报告固定字段完整。
- `Result` 不是 `BLOCKED`。
- `Blocks Next Stage` 与 `Result` 一致。
- 涉及 IDL 时，`merge-readiness` 有契约检查证据。
- 不涉及 IDL 时，报告中有 `N/A` 和理由。

CI / MR 必须失败的情况：

- 门禁报告缺失。
- 门禁报告格式不合法。
- `Result: BLOCKED`。
- `Result: WAIVED` 但缺少批准人、原因或有效期。
- 代码或 IDL 变更无法追溯到需求、设计或任务。

### 落地

`harness-repo` 的 `.github/workflows/harness-gates.yml` 已落地这套口径：对本次改动
涉及的 `requirements/<id>` 跑 `janus requirement status`（按阶段判定）、对涉及的 gate
JSON 跑 `janus gate validate`；向默认分支发起的 PR 额外跑
`janus requirement verify --target merge`（合并就绪）。

`business-repo` 与 `idl-repo` 的 MR 流水线应复用同一个 `janus`：按改动关联的
ticket id 跑 `janus requirement verify --requirement <id> --target merge`，不另写第二套
判定。（跨仓接入待后续补齐。）

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

## 11. 最小可用门禁 JSON 示例

```json
{
  "schema_version": "1",
  "requirement_id": "T12345",
  "gate_id": "design-review",
  "gate_name": "设计门禁",
  "stage": "3.3",
  "checked_by": "design_reviewer",
  "checked_at": "2026-05-31T10:00:00+08:00",
  "result": "BLOCKED",
  "blocks_next_stage": true,
  "inputs": [
    {
      "path": "requirements/T12345/requirement.md",
      "sha256": "..."
    },
    {
      "path": "requirements/T12345/impact-analysis.md",
      "sha256": "..."
    },
    {
      "path": "requirements/T12345/design.md",
      "sha256": "..."
    }
  ],
  "checklist": [
    {
      "item": "覆盖服务影响",
      "result": "PASS",
      "evidence": "design.md#服务影响"
    },
    {
      "item": "明确 IDL 影响",
      "result": "PASS",
      "evidence": "design.md#契约影响"
    },
    {
      "item": "明确回滚方案",
      "result": "BLOCKED",
      "evidence": "design.md 缺少回滚章节"
    }
  ],
  "blocking_issues": [
    {
      "issue": "缺少回滚方案",
      "required_action": "补充灰度关闭和代码回滚策略",
      "owner": "backend"
    }
  ],
  "warnings": [],
  "waiver": {
    "required": false
  },
  "decision": "不允许进入 4.1 任务拆分。补齐回滚方案后重新执行 3.3 设计门禁。"
}
```
