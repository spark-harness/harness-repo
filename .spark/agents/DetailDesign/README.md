# Detail Design Agents

设计阶段的 Agent 负责检查方案是否覆盖关键约束。

建议角色：

- `detail-design-quality-reviewer`：检查服务、接口、数据、配置、灰度、回滚和契约影响。
- `traceability-gate-checker`：检查需求、设计和任务之间的追溯关系。

输出应写入 `requirements/{requirement-id}/reviews/` 或 `requirements/{requirement-id}/gates/`。
