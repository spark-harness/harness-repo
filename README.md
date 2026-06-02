# Harness Repo

这个仓库是团队 AI 协作治理仓。

它负责保存：

- 需求生命周期产物。
- 阶段和门禁规则。
- 服务矩阵。
- 团队级、框架级、项目级上下文。
- Skill、Agent、Command 和 Hook 源文件。
- 可复用模板。

## 目录

```text
harness-repo/
├── .service-matrix/
├── .spark/
├── context/
├── requirements/
└── templates/
```

## 关联仓库

- 业务仓：`../business-repo`
- protobuf 契约仓：`../idl-repo`
- 学习文档仓：`../learning-docs-repo`

服务路径和 protobuf 路径以 `.service-matrix/dependencies.yaml` 为准。
