# Git 规范

## 分支

同一个需求在 Harness 仓、业务仓和 IDL 仓中应使用一致分支名。

推荐格式：

```text
feature/{workstream}/{ticket-id}
```

## 提交

提交信息应说明变更类型和范围，正文说明关键约束或门禁结果。

## 评审

评审时至少确认：

- 变更是否可追溯到需求。
- 是否涉及 protobuf IDL 或外部契约。
- 是否需要更新 `context/project/` 的现状或经验。
