---
requirement_id: "LEN-130"
owner: "core"
current_stage: "1"
status: "draft"
created_at: "2026-06-27"
---

# [FE] fides 支持运行时配置中心和 .env 覆盖

本需求用于把 `fides` 前端从构建期 public 环境变量切换到服务端运行时配置。

它不是新增业务页面，也不是修改 `fides-bff` 或后端契约；它只约束前端镜像、运行时配置、GitOps 部署配置和验收证据。

## 文件

- `requirement.md`：需求范围、业务规则和验收标准。
- `impact-analysis.md`：影响面分析。
- `design.md`：运行时配置方案。
- `tasks.json`：可验证任务拆分。
- `gates/`：Janus 门禁 JSON。
- `reviews/`：任务审查报告。
- `evidence/`：测试、构建、GitOps 和验收证据。
