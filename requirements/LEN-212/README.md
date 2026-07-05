---
requirement_id: "LEN-212"
owner: "forest"
current_stage: "4.2"
status: "draft"
created_at: "2026-07-06"
---

# fides-bff 升级到 Kratos v3

LEN-212 将 `fides-bff`、共享 BFF 横切包和 BFF Go 契约生成链路升级到 Kratos v3。

它不是什么：这不是新增贷款、报价、身份资料或 OTP 业务能力，也不是重写 BFF。

它是什么：这是一次框架运行时升级，目标是在外部可见行为不变的前提下移除旧 Kratos v2 运行时依赖，并完成本地、dev、sta 验证。

## Lifecycle Artifacts

- requirement.md
- impact-analysis.md
- design.md
- tasks.json
- gates/
- reviews/
- evidence/
