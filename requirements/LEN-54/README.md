---
current_stage: "5"
---

# LEN-54 Argo 仓库门禁硬切

## 状态

- 需求：draft，等待 `janus requirement approve` 记录人工批准
- 分支：`chore/LEN-54-argo-repo-gates`
- 目标分支：`master`
- 发布分支：`master`
- 影响仓库：`gitops-repo`、`harness-repo`、`business-repo`、`idl-repo`

## 文件

| 文件 | 用途 |
|---|---|
| `requirement.md` | 定义 GitHub Actions 到 Argo 的硬切需求和验收标准 |
| `impact-analysis.md` | 分析 GitOps、Webhook、runner、门禁和分支保护影响 |
| `design.md` | 描述 Argo Events / Workflows / GitHub status 的实现边界 |
| `tasks.json` | 拆分可验证实现任务 |

## 交付说明

本需求不是在 GitHub Actions 与 Argo 之间长期双轨运行。它是一次仓库门禁硬切：
GitHub 只保留 PR、Webhook、commit status 和 branch protection，门禁执行面迁移到
Argo。
