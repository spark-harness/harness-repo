# Service Matrix

服务矩阵是 Harness 判断服务、仓库、语言、IDL 和上下文路由的入口。

它不是业务架构文档，也不是运行时服务发现。它只保存足够让人和 Agent 找到正确仓库、服务、契约和项目知识的结构化事实。

## 文件

| 文件 | 作用 |
|---|---|
| `dependencies.yaml` | 当前真实服务矩阵 |
| `dependencies.example.yaml` | 字段和结构示例 |

## 核心字段

| 字段 | 作用 |
|---|---|
| `workspace` | 多仓工作区根路径，相对 `harness-repo` |
| `business_repo` | 业务代码仓路径 |
| `idl_repo` | protobuf / Buf 契约仓路径 |
| `idl_format` | 契约格式，当前为 `protobuf` |
| `buf_config_version` | Buf 配置版本 |
| `teams` | 团队到仓库的默认映射 |
| `modules` | 业务域或模块分组 |
| `libraries` | 可复用库、语言、artifact 和用途 |
| `services` | 服务名、模块、仓库路径、IDL 需求和 proto 路径 |
| `dependencies` | 上下游服务和库依赖 |

## 服务字段

服务条目至少应能回答：

| 字段 | 用途 |
|---|---|
| `module` | 服务属于哪个业务域或模块 |
| `repo_path` | 服务代码在业务仓中的路径 |
| `language` | 服务主要语言，用于加载 `context/team/{language}.md` |
| `runtime` | 运行时或框架，用于选择本地启动和部署说明 |
| `idl_required` | 是否需要 protobuf / IDL 契约 |
| `idl_repo` | IDL 仓路径 |
| `proto_path` | 服务 proto 目录 |
| `buf_module` | Buf module 名称 |
| `owner` | 服务负责人或团队 |
| `deploy` | 部署目标或运行环境入口 |

当前矩阵如果缺少 `language`、`runtime`、`owner` 或 `deploy`，应在后续服务治理中补齐；本 README 先定义字段语义。

## 路由规则

Agent 或团队成员处理服务任务时：

1. 先从 `services` 找服务名。
2. 用 `repo_path` 定位业务代码。
3. 用 `language` 加载对应团队语言规范。
4. 如果 `idl_required: true`，读取 `idl_repo`、`proto_path` 和契约规范。
5. 用 `module` 找项目/领域上下文。
6. 用 `dependencies` 判断上下游影响。

禁止仅凭目录名猜服务归属。服务矩阵有条目时，以服务矩阵为准。

## 维护规则

- 新增服务必须补 `services` 条目。
- 新增共享库必须补 `libraries` 条目。
- 修改服务路径、IDL 路径或依赖关系时，必须同步更新矩阵。
- 真实服务数据只写在 `dependencies.yaml`。
- 示例只写在 `dependencies.example.yaml`，不得被门禁当作真实拓扑。
- 如果矩阵字段影响门禁，必须同步检查相关 Janus 规则和 Harness gate。
