---
requirement_id: "LEN-12"
analyst: "Codex"
status: "approved"
updated_at: "2026-06-19"
approved_by: "Forest"
approved_at: "2026-06-20T18:10:45+08:00"
decision: "批准 LEN-12 impact-analysis 与服务仓库检查，允许进入交付验证。"
idl_impact: "yes"
idl_impact_reason: "本需求新增 applicant-api 后端服务及 OTP/session protobuf 契约，属于 additive new service/RPC/message。"
---

# Impact Analysis

## Summary

新建 Java + Spring Boot 后端服务 `applicant-api`，通过新增 protobuf 契约提供 OTP 发送、OTP 校验和 token 刷新能力；使用 Redis 保存 OTP challenge、冷却、错误次数、锁定和 token 状态；不修改 `fides-bff` 或前端代码。

## Affected Domains

- `applicant`（新增 domain/module）：Lendora 申请人身份、手机号验证和短期会话。
- `frontend`（间接受影响）：未来 BFF 或前端侧服务会消费 `applicant-api` 契约；本需求不修改 `fides-bff`。
- `user`（不直接修改）：`user-api` 不承接 Applicant 身份，本需求避免把 Lendora applicant 与用户域混在一起。

## Affected Services

| Service | Repo | Reason | Protobuf Required |
|---|---|---|---|
| applicant-api（新增） | business-repo (`services/backend/applicant-api`) | 新建 Java + Spring Boot 服务，承载 OTP、Applicant 身份、token/session 和 Redis 状态 | Yes |
| applicant proto（新增） | idl-repo (`vesta/spark/applicant/v1`) | 新增 protobuf package、service、rpc 和 message | Yes |
| generated contracts | idl-java-repo（至少 Java 生成物）；idl-go-repo 是否需要待设计确认 | `applicant-api` 需要 Java 契约；BFF 后续消费语言生成物需确认 | Yes |
| harness lifecycle | harness-repo (`requirements/LEN-12`) | 新增需求、影响分析、后续设计、任务、门禁和证据 | No |

## Upstream / Downstream Consumers

- 上游消费者：后续 BFF / 前端职责方会调用 `applicant-api`；本需求只承诺后端契约和服务可用性。
- 下游依赖：Redis 作为运行时状态存储；未来真实 SMS provider 不在本需求内。
- 横向依赖：`packages/spring-starter` 可复用 Java/Spring clean architecture 基线；如能力不足，设计阶段决定是否补最小扩展。
- 现有服务：`user-api`、`fides-bff` 不在本需求实现范围内。

## API / Contract Impact

- Does this change involve protobuf IDL or external contracts: **Yes**。
- Contract repo: `idl-repo`。
- Proto files: 新增 `{idl-repo}/vesta/spark/applicant/v1/*.proto`，具体文件名设计阶段确定，建议独立 `applicant_auth.proto` 或 `auth.proto`。
- Buf module: 当前 `idl-repo/buf.yaml` 为 v2，模块 path 为 `.`；可能需要沿用单模块配置。
- Buf config version: v2。
- Required buf checks:
  - `buf lint`
  - `buf generate`
  - `buf breaking --against '.git#branch=master'` 或团队当前主干等价基线
- Breaking baseline: `origin/master` / `master` 上已发布 IDL。
- Compatibility risk: 低。新增 package/service/rpc/message 属 additive change，不改变现有 `vesta.spark.user.v1` 契约。风险主要来自未来消费者对 token、错误语义和字段必填性的理解，需在设计中列出请求/响应样例和错误语义。

## Generated Contract Impact

- Java generated contracts: 需要更新 `idl-java-repo/src/main/java` 与 `src/main/grpc-java`，供 `applicant-api` 编译和测试。
- Go generated contracts: 当前 `buf.gen.yaml` 会输出到 `../idl-go-repo/`；是否纳入本需求交付取决于后续 BFF 是否由本阶段消费。用户已明确本需求不管 `fides-bff`，因此 Go 生成物可在设计中标为非必需或另行确认。
- Package publication: 如果 `business-repo` 通过 GitHub Packages 消费 `spark-idl-java`，实现阶段需确认本地和 CI 的包解析策略。

## Data Impact

- Database schema: 设计阶段需决定 applicant 是否需要持久化数据库表。需求要求“新建或查找 Lendora applicant”，如果只存在 Redis 会话状态则无法长期稳定查找；建议设计明确 applicant 持久化模型。
- Data migration: 新服务初建默认无历史数据迁移。
- Backfill: 无。
- Cache: Redis 保存 OTP challenge、重发冷却、错误次数、临时锁定、token 状态和幂等记录。
- Runtime storage: Redis 是本需求的强依赖；TTL、key 命名、命名空间、最大记录数和过期策略需在设计中明确。

## Config / Permission / Observability Impact

- Config: `applicant-api` 需要服务端口、Redis 连接、token 签名/密钥配置、OTP TTL、重发冷却、错误阈值、锁定时长、验证码替身策略和幂等 TTL。
- Permission: 本需求不实现资源越权中间件；token 只表达“手机号已验证的 applicant 身份”。密钥和 token 配置不得写入需求、设计或门禁报告。
- Metrics: 建议设计覆盖 OTP 发送成功/失败、限流、校验成功/失败、锁定、token 刷新成功/失败等低基数指标。
- Logs: 日志不得记录手机号明文、OTP 明文、token、refreshToken 或 Redis key 全量；可记录脱敏手机号、applicantId、challengeId 哈希和错误码。
- Tracing: applicant-api 应贯穿 traceId/correlationId；后续 BFF 消费时可透传。
- Events: 本需求不发布业务事件。

## Rollout And Rollback

- Gray release: 先发布新增 IDL 和 `applicant-api` 服务；未接 BFF 前不会产生用户流量。可通过环境配置限制调用方。
- Kill switch: 可通过关闭 OTP 发送能力或只允许测试验证码替身策略来阻断外部调用；真实短信未接入，无第三方发送风险。
- Rollback steps:
  - 回滚 `applicant-api` 服务代码和配置。
  - 回滚新增 protobuf 和生成契约提交。
  - 删除服务矩阵中的 `applicant-api` 条目。
  - 清理 Redis 中 `applicant-api` 命名空间 key。
  - 因本需求不改现有服务契约，回滚不影响 `user-api` 或 `fides-bff` 已有行为。

## Risks

| Risk | Impact | Mitigation | Owner |
|---|---|---|---|
| `applicant-api` 是新服务，服务矩阵当前没有 module/service 条目 | service-repo-check 无法通过 | 设计或任务阶段新增 applicant module/service、repo_path、proto_path 和依赖关系 | Codex |
| Applicant 是否持久化未定 | “新建或查找 applicant”语义可能只在 Redis TTL 内成立 | 设计阶段明确 applicant 持久化模型；如需要数据库，补迁移和回滚方案 | Backend |
| 验证码替身策略不清 | 联调方可能误以为真实短信已发送 | 设计阶段明确固定测试码、日志输出或环境配置策略，并在响应/文档中避免误导 | Backend |
| Token 签名和密钥管理未定 | 安全风险或环境不可复现 | 设计阶段定义密钥来源、轮换预留和测试替身，文档中不保存真实密钥 | Backend |
| Redis 成为强依赖 | Redis 不可用会导致 OTP 和 token 能力不可用 | 设计阶段定义健康检查、超时、错误码、降级策略和告警指标 | Backend |
| 生成契约发布链路依赖私有包权限 | CI 或本地实现无法解析新契约 | 在 IDL 协议阶段记录 buf generate 结果和 package 消费方式；必要时使用本地模块或明确凭据前置 | Codex |
| 本需求不修改 `fides-bff` | 端到端用户流程不会在本需求完成 | Non-Goals 明确 BFF/前端接入属于后续或前端职责；验收只覆盖后端契约与服务行为 | Product / Backend |

## Context Gaps

- `harness-repo/context/project/` 当前只有 `spark/user/`，缺少 `spark/applicant/` 或 Lendora applicant 域上下文；建议在设计或实现后沉淀 `context/project/spark/applicant/INDEX.md`。
- `.service-matrix/dependencies.yaml` 当前没有 `applicant-api`；设计和 service-repo-check 前必须补齐。
