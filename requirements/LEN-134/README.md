# LEN-134 origination-api lendora-sta 部署

## Ticket

- ID: `LEN-134`
- Title: `[GitOps] origination-api lendora-sta 部署`
- Branch: `feature/LEN-134-origination-api-deploy`
- Repos: `harness-repo`, `business-repo`, `gitops-repo`

## Scope

部署 LEN-9 已交付的 `origination-api` 到 `lendora-sta`，补齐镜像构建、application DB runtime、Kubernetes Service、Consul 发现、readiness 和 runtime smoke。

本 ticket 不实现 BFF facade，不改前端 Continue 行为，不修改 protobuf IDL。
