# Templates

本目录保存 Harness 需求生命周期模板。

它不是示例需求库。真实需求写到 `requirements/{requirement-id}/`，模板只保存结构、字段和最小提示。

## 模板

| 模板 | 生成位置 | 使用阶段 |
|---|---|---|
| `requirement.md` | `requirements/{id}/requirement.md` | 初始化、需求定义 |
| `impact-analysis.md` | `requirements/{id}/impact-analysis.md` | 需求定义 |
| `design.md` | `requirements/{id}/design.md` | 设计 |
| `tasks.json` | `requirements/{id}/tasks.json` | 任务拆分 |
| `gate-report.gate.json` | `requirements/{id}/gates/{gate}.gate.json` | 各阶段门禁 |
| `review-report.md` | `requirements/{id}/reviews/{task}.md` | 编码审查 |

## 使用规则

1. 创建需求目录时，先复制 `requirement.md`。
2. 需求进入评审前，补齐 `impact-analysis.md`。
3. 设计阶段复制 `design.md`。
4. 开发前复制 `tasks.json`。
5. 门禁文件由工具或流程生成，不手写聊天结论。

## 维护规则

- 模板只写结构和最小提示。
- 不写真实业务需求、服务实现、密钥或生产数据。
- 修改模板字段时，同步检查 `document-template-policy.md`。
- 如果字段影响 Janus 或 gate，必须同步检查 gate 实现和相关 skill。
