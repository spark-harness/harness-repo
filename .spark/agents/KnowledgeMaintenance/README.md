# Knowledge Maintenance Agents

知识维护阶段的 Agent 负责把重复问题、人工纠正和服务经验沉淀为可复用资产。

建议角色：

- `experience-extractor`
- `sop-generator`
- `context-index-maintainer`

输出优先写入 `context/project/{project}/{domain}/experience/`，再视情况更新团队级或框架级规范。
