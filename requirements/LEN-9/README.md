# LEN-9 origination-api 申请草稿创建与静默保存

本目录保存 `LEN-9` 的需求、影响分析、设计、任务、门禁、审查和验证证据。

## Ticket

- Jira: `LEN-9`
- Title: `[BE] origination-api 申请草稿创建与静默保存`
- Branch: `feature/LEN-9-origination-api-drafts`

## Scope

新建 `origination-api` Java Spring 服务，支持 LoanApplication draft 创建、读取回填、PATCH 静默保存、幂等和 Quote 校验。

本 ticket 不部署服务、不创建 Kubernetes/GitOps runtime 清单；`LEN-134` 负责 `lendora-sta` 部署和 application DB runtime 验证。
