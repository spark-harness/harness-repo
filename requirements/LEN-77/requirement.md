---
requirement_id: "LEN-77"
owner: "forest"
status: "approved"
created_at: "2026-06-23"
related_branch: "feature/LEN-77-lendora-sta-runtime"
target_branch: "master"
release_branch: "master"
contract_gate_mode: "auto"
affected_repositories:
  - harness-repo
  - gitops-repo
  - business-repo
approved_by: "forest"
approved_at: "2026-06-23T19:56:08+08:00"
decision: "批准 LEN-77 需求定义和影响分析，优先实现所有子票；技术债和优化后续处理。"
---

# Lendora STA 三服务生产化部署

## Background

Lendora 已完成部分本地验证码链路和 Argo 门禁基础，但 applicant-api、fides-bff 和 fides 前端还没有以生产化方式部署到 STA 环境。当前用户无法通过公网 Lendora 入口访问前端并完成手机验证码链路。

它不是什么：本需求不是贷款申请完整链路，不是真实短信供应商切换，也不是生产流量切换。

它是什么：把 Lendora STA runtime、依赖、三服务、入口、smoke 和回滚证据纳入 GitOps 与可审计发布流程。

## Goals

- R1：维护者能通过 GitOps 入口查看 Lendora STA app-of-apps、namespace 和每个服务 / 依赖的独立入口。对应 `LEN-78`。
- R2：applicant-api、fides-bff 和 fides 都有可发布、可扫描、可追溯、可回滚的不可变镜像。对应 `LEN-79`。
- R3：PostgreSQL、Redis 和 Consul 作为 STA 内网依赖运行在独立 namespace，并具备 Secret 引用、健康检查、资源限制和持久化策略。对应 `LEN-80`。
- R4：applicant-api 作为内网身份服务运行，不暴露公网，只允许 fides-bff 访问业务端口。对应 `LEN-81`。
- R5：fides-bff 作为公网 API 边界，对内调用 applicant-api，对外限制前端来源并返回统一错误体验。对应 `LEN-82`。
- R6：fides 前端通过 Lendora 公网 HTTPS 入口访问真实 STA BFF，并能完成手机验证码流程。对应 `LEN-83`。
- R7：端到端 smoke、日志 / 指标 / trace 检查、applicant-api 公网不可达检查和任一服务回滚演练有证据。对应 `LEN-84`。

## Non-Goals

- 不实现贷款申请完整业务链路、KYC、授信或放款能力。
- 不切换真实短信供应商，不产生真实短信费用路径。
- 不做生产流量切换、多区域容灾、压测或数据库高可用。
- 不把真实密钥、token、kubeconfig 或 registry 凭据写入 Git。
- 不处理非阻塞技术债、长期加固和体验优化；这些后续单独建 ticket。

## User / Business Scenarios

### Scenario 1：维护者查看 STA runtime GitOps

Given：维护者需要确认 Lendora STA runtime 目标状态。

When：打开 GitOps 配置入口。

Then：能看到 Lendora STA app-of-apps、独立 namespace、依赖和三服务入口。

### Scenario 2：用户通过公网前端完成手机验证

Given：Lendora STA 部署完成。

When：用户打开公网 HTTPS 域名，输入手机号，请求并提交测试验证码。

Then：前端调用 fides-bff，fides-bff 调用 applicant-api，用户进入已验证状态或看到可理解错误。

### Scenario 3：公网不可直接访问 applicant-api

Given：applicant-api 已部署。

When：外部用户尝试通过公网访问 applicant-api。

Then：请求不可达；applicant-api 只能通过集群内服务和 NetworkPolicy 访问。

### Scenario 4：维护者回滚服务

Given：任一 Lendora 服务的新 digest 不可用。

When：维护者把 GitOps overlay 切回上一 digest。

Then：服务通过 GitOps 回滚，验证码链路恢复可用。

### Scenario 5：维护者审查生产化证据

Given：STA 部署和 smoke 已运行。

When：维护者查看 evidence、日志、指标和 trace。

Then：能证明 smoke 通过、回滚路径可用、applicant-api 不暴露公网，且手机号、OTP、token、applicantId 等敏感字段未泄漏。

## Business Rules

- BR1：Runtime 品牌命名使用 Lendora，不再使用 Spark 作为 runtime 品牌。
- BR2：STA 环境使用独立 namespace，不与 CI namespace 混合。
- BR3：每个服务和关键依赖使用独立 namespace。
- BR4：GitOps 是 runtime 配置事实源；手工 apply 只能作为临时 bootstrap，并必须回填。
- BR5：部署配置只能引用 immutable image digest，不能引用浮动 tag。
- BR6：镜像不得打入密钥或本地配置。
- BR7：Secret 值不写入 Git；Git 只保存 Secret 引用、ExternalSecret 或 bootstrap 说明。
- BR8：PostgreSQL、Redis、Consul 只暴露 ClusterIP。
- BR9：applicant-api 不创建公网 Ingress。
- BR10：只有 fides-bff 可以访问 applicant-api 的业务端口。
- BR11：fides-bff 对 applicant-api 使用内网地址，面向公网只暴露前端需要的 API。
- BR12：fides 前端 OTP adapter 指向真实 STA BFF，不使用 mock。
- BR13：用户可见错误必须友好，不暴露内部服务名、堆栈、手机号、OTP、token 或 applicantId。
- BR14：Smoke 不使用真实敏感手机号或真实短信费用路径。

## Acceptance Criteria

- AC1：GitOps 仓包含 Lendora STA app-of-apps、namespace 清单、基础 labels、同步边界和回滚入口。
- AC2：集群中 Lendora STA 关键 runtime 资源都能对应到 GitOps 配置。
- AC3：三服务镜像发布流程能产生 digest，并能由集群拉取。
- AC4：三服务部署配置均引用 digest，不引用浮动 tag。
- AC5：PostgreSQL、Redis、Consul 分别运行在独立 namespace，Ready，且只暴露 ClusterIP。
- AC6：依赖资源具备 Secret 引用、PVC、健康检查和资源限制。
- AC7：applicant-api Deployment、Service、配置、Secret 引用、迁移、健康检查和 NetworkPolicy 存在，并且公网不可达。
- AC8：fides-bff Deployment、Service、公网 API 路由、内网 applicant 配置、CORS、健康检查和 smoke 存在。
- AC9：fides Deployment、Service、公网 HTTPS 路由和真实 BFF 配置存在。
- AC10：公网前端验证码发送和验证 smoke 通过。
- AC11：applicant-api 公网探测不可达证据存在。
- AC12：至少一个服务完成切换上一 digest 的回滚演练并有证据。
- AC13：smoke 期间日志、指标或 trace 检查未发现手机号、OTP、token、applicantId 泄漏。
- AC14：Kustomize 渲染、服务测试和前端 / BFF / applicant-api 相关测试结果记录到 evidence。

## Open Questions

| Question | Owner | Deadline | Status |
|---|---|---|---|
| STA 公网域名最终使用哪个 Lendora 域名 | Forest | 部署验证前 | Open |
| 当前 kubeconfig `~/.kube/wsl.yaml` 的 API server 连接不可用，何时恢复集群访问 | Forest | smoke 前 | Open |
| Secret 采用 ExternalSecret、SealedSecret 还是手工 bootstrap 后记录引用 | Forest | 依赖部署前 | Open |
| 是否保留 Consul 服务发现，还是 fides-bff 直接使用 Kubernetes Service DNS | Forest | fides-bff 部署前 | Open |

## Notes

- Jira Epic：`LEN-77`。
- 子票：`LEN-78`、`LEN-79`、`LEN-80`、`LEN-81`、`LEN-82`、`LEN-83`、`LEN-84`。
- 用户已明确允许通过所有 ticket 的批准，当前优先级最高是实现；技术债和优化后续处理。
