# Project Context Index

项目级知识按项目、领域、服务逐层组织。

它不是团队规范目录。团队通用 Java、TypeScript、Go、测试、契约、Git、CI/CD、安全等规则放在 `context/team/`。

## 推荐结构

```text
context/project/{project-name}/
├── INDEX.md
└── {domain-name}/
    ├── INDEX.md
    └── {service-name}/
        ├── INDEX.md
        ├── sop/
        └── experience/
```

## 使用顺序

1. 先通过 `.service-matrix/dependencies.yaml` 确认项目、模块、服务、代码路径和语言。
2. 再读取 `context/team/INDEX.md` 中对应团队规范。
3. 最后读取项目、领域或服务级 `INDEX.md`。

不要跳过服务矩阵直接根据目录名猜服务归属。

## 写入规则

| 内容 | 放置位置 |
|---|---|
| 跨项目通用规则 | `context/team/` |
| Harness 流程、门禁、模板 | `context/harness-framework/` |
| 项目业务语义和边界 | `context/project/{project}/INDEX.md` |
| 领域共享规则 | `context/project/{project}/{domain}/INDEX.md` |
| 服务特例、SOP、经验 | `context/project/{project}/{domain}/{service}/` |

## 不写什么

- 不复制业务代码实现。
- 不保存真实 secret、生产数据或个人信息。
- 不把临时聊天结论当作项目事实。
- 不重复定义团队通用规范。

## 模板

- `_template/INDEX.md`：项目级入口模板。
- `_template/domain/INDEX.md`：领域级入口模板。
- `_template/domain/service/INDEX.md`：服务级入口模板。

## 当前项目

当前没有已沉淀的真实项目级上下文入口。新增真实项目上下文前，应先确认服务矩阵中已有对应服务或模块。
