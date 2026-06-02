# Service Commands

## `/service:deps`

从 `.service-matrix/dependencies.yaml` 读取服务上下游、仓库路径、protobuf 契约和 buf v2 要求。

## `/service:load-domain`

加载 `context/project/{project}/{domain}/INDEX.md`，再按需读取现状、SOP 和经验文档。

## `/service:onboard`

为新服务补充服务矩阵条目和最小 `context/project/` 知识入口。
