# Definition Agents

需求定义阶段的 Agent 负责检查业务意图是否足够清晰。

建议角色：

- `requirement-input-normalizer`：把自然语言输入整理为需求模板。
- `requirement-quality-reviewer`：执行需求评审门禁。

输出应写入 `requirements/{requirement-id}/gates/`。
