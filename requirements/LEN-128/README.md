# LEN-128 applicant-api 多配置来源与覆盖优先级

本需求定义 `applicant-api` 运行时配置来源、覆盖优先级和验证边界。

它不新增业务接口，不修改 OTP、会话或申请人身份规则。

## Lifecycle Artifacts

| Artifact | Purpose |
|---|---|
| `requirement.md` | 需求目标、业务规则、场景和验收标准 |
| `impact-analysis.md` | 服务、仓库、配置、部署和回滚影响 |
| `design.md` | 工程设计和需求追溯 |
| `tasks.json` | 可验证任务拆分 |

## Scope

- `harness-repo/requirements/LEN-128`
- `business-repo/apps/applicant-api`
- `gitops-repo/apps/applicant-api`

## Branch

```text
feature/LEN-128-applicant-api-config-precedence
```
