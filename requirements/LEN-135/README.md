# LEN-135 fides-bff quote/origination downstream config

## Scope

本需求交付 `fides-bff` 在 lendora-sta 的 quote/origination 下游运行时配置和 smoke 验证。

## Lifecycle Files

- `requirement.md`
- `impact-analysis.md`
- `design.md`
- `tasks.json`
- `evidence/local-verification.md`
- `evidence/runtime-smoke.md`
- `reviews/T2-T4.md`
- `gates/*.gate.json`

## Boundary

- 包含：fides-bff ConfigMap、服务发现配置、HTTP timeout、运行时 smoke、证据和门禁。
- 不包含：BFF 业务代码、IDL、quote-api/origination-api 业务逻辑、frontend 接入。
