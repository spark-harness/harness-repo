# {Service} Context

本文是服务级知识入口。

它记录服务特例、业务语义、上下游约束和运行注意事项。团队通用规则仍以 `context/team/` 为准。

## Service Facts

| 字段 | 内容 |
|---|---|
| 服务名 | `{service}` |
| 所属领域 | `{domain}` |
| 代码路径 | `{business-repo}/...` |
| 主要语言 | `{java/typescript/go}` |
| Runtime | `{spring-boot/node/go}` |
| IDL | `{proto_path 或 N/A}` |
| Owner | `{team/person}` |

## What Is Special Here

- `{本服务与团队通用规范不同的地方，必须说明原因}`

## Upstream / Downstream

| 类型 | 对象 | 说明 |
|---|---|---|
| upstream | `{service}` | `{说明}` |
| downstream | `{service}` | `{说明}` |

## SOP

- `sop/`：稳定操作流程，例如本地启动、排障、数据修复。

## Experience

- `experience/`：历史问题、根因、修复方式和后续防线。

## 不写什么

- 不复制 controller、repository、proto 的实现细节。
- 不记录真实 secret 或生产数据。
- 不把临时 workaround 当作稳定规范。
