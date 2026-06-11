# Document Template Policy

本文定义 Harness 文档模板的框架级口径。

可复制的需求生命周期文档模板保存在本文档同级的 `templates/` 子目录。

它负责说明哪些模板属于需求生命周期、何时使用、如何维护。

## 1. 模板真相源

| 模板 | 文件 | 使用阶段 | 生成位置 |
| --- | --- | --- | --- |
| 需求说明 | `context/harness-framework/templates/requirement.md` | 阶段 1、阶段 2 | `requirements/{requirement-id}/requirement.md` |
| 影响面分析 | `context/harness-framework/templates/impact-analysis.md` | 阶段 2 | `requirements/{requirement-id}/impact-analysis.md` |
| 设计说明 | `context/harness-framework/templates/design.md` | 阶段 3 | `requirements/{requirement-id}/design.md` |
| 任务拆分 | `context/harness-framework/templates/tasks.json` | 阶段 4.1 | `requirements/{requirement-id}/tasks.json` |
| 门禁 JSON | `context/harness-framework/templates/gate-report.gate.json` | 阶段 2.2、3.3、4.2、4.3、5.1 | `requirements/{requirement-id}/gates/{gate-id}.gate.json` |
| 门禁审计视图 | Janus 渲染生成 | 阶段 2.2、3.3、4.2、4.3、5.1 | `requirements/{requirement-id}/gates/{gate-id}.md` |
| 代码审查报告 | `context/harness-framework/templates/review-report.md` | 阶段 4.4 | `requirements/{requirement-id}/reviews/{task-id}.md` |

门禁 JSON 必须使用固定字段。阶段推进只能读取 JSON 结论，不能读取聊天记录或手写 Markdown 作为放行依据。

Markdown 文档的轻量元数据使用文件顶部 YAML front matter。正文不再保留 `## Metadata` 列表，避免同一份文档出现两套元数据口径。

## 2. 使用规则

创建需求目录时，至少复制：

- `context/harness-framework/templates/requirement.md`
- `context/harness-framework/templates/impact-analysis.md`

进入设计阶段前，应补齐：

- `context/harness-framework/templates/design.md`

进入任务拆分前，应补齐：

- `context/harness-framework/templates/tasks.json`

执行门禁时，应生成或更新固定格式门禁 JSON，并用 Janus 渲染审计 Markdown。

阶段 4.4 每个任务完成审查时，应从 `review-report.md` 模板生成 `requirements/{requirement-id}/reviews/{task-id}.md`。

## 3. 模板内容边界

模板只保留结构、字段和最小示例。

模板不保存：

- 真实业务需求。
- 具体服务实现代码。
- 私密配置、密钥或生产数据。
- 只适用于单次需求的临时判断。

如果模板字段会影响门禁判断，必须同步更新：

- `context/harness-framework/main-process-numbering.md`
- `context/harness-framework/gate-implementation.md`
- `.spark/skills/`
- `.spark/agents/`
- `.spark/rules/`
- Janus 校验逻辑或规则文件。

## 4. 新增模板规则

新增模板前必须回答：

| 问题 | 要求 |
| --- | --- |
| 属于哪个阶段 | 必须能映射到五阶段流程 |
| 生成到哪里 | 必须有稳定路径 |
| 谁读取它 | 必须说明人、Agent、Skill 或 Janus |
| 是否影响门禁 | 如果影响，必须同步门禁协议 |
| 是否可复用 | 不能只服务一次性需求 |

新增模板文件后，必须同步更新本文档的模板真相源表。
