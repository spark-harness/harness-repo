# LEN-77：Lendora STA 三服务生产化部署

## 状态

- 当前阶段：开发准备
- 需求来源：Jira Epic `LEN-77`
- 子票：`LEN-78` 至 `LEN-84`
- 分支：`feature/LEN-77-lendora-sta-runtime`
- 目标分支：`master`
- 受影响仓库：`harness-repo`、`gitops-repo`、`business-repo`

## 文件

- `requirement.md`：需求定义。
- `impact-analysis.md`：影响面分析。
- `design.md`：生产化部署设计。
- `tasks.json`：实现任务拆分。
- `gates/`：阶段门禁结果。
- `evidence/`：测试、GitOps 渲染、smoke、回滚和观测证据。

## 交付原则

本需求优先完成 Lendora STA 公网访问、验证码链路、内网服务隔离、不可变镜像部署和回滚证据。技术债、加固和优化另开后续 ticket，不阻塞当前 CI/CD 到 runtime 的闭环。
