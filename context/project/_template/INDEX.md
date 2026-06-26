# {Project} Context

本文是项目级知识入口。

它不是团队通用规范，也不是业务代码说明书。团队通用规范放在 `context/team/`；这里只记录本项目的业务语义、架构约束、SOP 和历史经验入口。

## Domains

| Domain | 作用 | 入口 |
|---|---|---|
| `{domain}` | `{说明}` | `{domain}/INDEX.md` |

## Source Of Truth

- 服务矩阵：`.service-matrix/dependencies.yaml`
- 团队规范：`context/team/INDEX.md`
- Harness 流程：`context/harness-framework/INDEX.md`
- 需求目录：`requirements/`

## 维护规则

- 只写项目级约束和入口。
- 不复制团队通用规则。
- 不复制业务代码实现。
- 服务级例外写到 `{domain}/{service}/INDEX.md`。
