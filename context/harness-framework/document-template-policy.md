# Document Template Policy

本文定义 Harness 文档模板的框架级口径。

它不负责保存每一份可复制模板文件。模板文件仍放在仓库根目录 `templates/`，便于命令、Skill 和人工复制。

它负责说明哪些模板属于需求生命周期、何时使用、如何维护。

## 1. 模板真相源

| 模板 | 文件 | 使用阶段 | 生成位置 |
| --- | --- | --- | --- |
| 需求说明 | `templates/requirement.md` | 阶段 1、阶段 2 | `requirements/{requirement-id}/requirement.md` |
| 影响面分析 | `templates/impact-analysis.md` | 阶段 2 | `requirements/{requirement-id}/impact-analysis.md` |
| 设计说明 | `templates/design.md` | 阶段 3 | `requirements/{requirement-id}/design.md` |
| 任务拆分 | `templates/tasks.json` | 阶段 4.1 | `requirements/{requirement-id}/tasks.json` |
| 门禁审计视图 | `templates/gate-report.md` | 阶段 2.2、3.3、4.2、4.3 | `requirements/{requirement-id}/gates/{gate-id}.md` |
| 项目现状 | `templates/current-state.md` | 阶段 5 或知识维护 | `context/project/{project}/{domain}/current-state.md` |

门禁机器事实源不使用 Markdown 模板。门禁机器事实源是：

```text
requirements/{requirement-id}/gates/{gate-id}.gate.json
```

Markdown 门禁报告只作为审计视图，由 Janus 从 gate JSON 渲染。

## 2. 使用规则

创建需求目录时，至少复制：

- `templates/requirement.md`
- `templates/impact-analysis.md`

进入设计阶段前，应补齐：

- `templates/design.md`

进入任务拆分前，应补齐：

- `templates/tasks.json`

执行门禁时，应先生成或更新 gate JSON，再按需渲染 Markdown 审计视图。

维护项目现状知识时，应优先使用 `templates/current-state.md`，并放到对应项目上下文目录。

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
- `.agents/skills/`
- `.codebuddy/skills/`
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
