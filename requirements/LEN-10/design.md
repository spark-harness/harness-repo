---
requirement_id: "LEN-10"
owner: "core"
status: "approved"
updated_at: "2026-06-28"
approved_by: "forest"
approved_at: "2026-06-28T01:39:43+08:00"
decision: "用户授权 Agent 批准 LEN-10 design.md，先交付 quote-api HTTP/JDBC 服务，不修改 IDL，不部署。"
---

# Design

## Requirement Traceability

| Requirement Item | Design Decision | Notes |
|---|---|---|
| BR1, BR2, AC1, AC2 | `PricingPolicy` 固化 PIL MVP 金额和期限边界 | 后续 Product Catalog 再替换配置来源 |
| BR3, AC1, AC3 | `CreateQuoteUseCase` 每次成功计算后持久化 Quote | POST pricing/quotes 是创建 Quote |
| BR4, BR7, AC4, AC5 | `QuoteLookupUseCase` 使用 principal applicantId 校验归属和有效期 | 供 LEN-9 使用 |
| BR5 | 金额、APR、总息、总还款额使用 BigDecimal | 禁止 double/float |
| BR6 | Quote 有效期默认 30 分钟，可由配置覆盖 | 返回 validUntil |
| AC6 | 提供 health/ready adapter 和 repository integration test | LEN-131 部署时复用 |
| AC7 | 按 clean architecture 新建 domain/application/adapter/infrastructure | 不复制 applicant/auth 业务代码 |

## Summary

quote-api 是 Pricing 子域独立服务。它负责计算和持久化 Quote，不负责草稿、申请状态或前端路由。

## Affected Services

| Service | Change | Reason |
|---|---|---|
| quote-api | 新建 Java Spring Boot 应用 | 提供试算和 Quote 校验 |
| service matrix | 新增 quote-api 条目 | Janus 和后续 tickets 能定位服务 |
| Java CI gate DAG | 增加 quote-api 项目任务 | 确保 PR Java gate 调度新服务 |

## API / Contract Design

### Create Quote

```text
POST /api/v1/pricing/quotes
```

Request:

```json
{
  "productCode": "PIL",
  "amount": "100000.00",
  "term": 12,
  "purpose": "debt_consolidation"
}
```

Response:

```json
{
  "quoteId": "quote_...",
  "monthly": "8560.75",
  "apr": "0.0520",
  "totalInterest": "2729.00",
  "totalPayable": "102729.00",
  "validUntil": "2026-06-28T02:00:00Z"
}
```

### Internal Quote Read

```text
GET /internal/v1/pricing/quotes/{quoteId}
```

从 `RequestPrincipalContext` 读取 applicantId，返回完整 Quote。缺失 principal 返回 401；归属不一致返回 403；过期返回 410。

## Application Design

### Domain

- `Quote`
- `QuoteId`
- `LoanAmount`
- `LoanTerm`
- `PricingPolicy`
- `QuoteCalculation`

### Application

- `CreateQuoteUseCase`
  1. 读取 principal applicantId。
  2. 校验 productCode、amount、term、purpose。
  3. 使用 BigDecimal 计算 monthly、apr、totalInterest、totalPayable。
  4. 生成 quoteId 和 validUntil。
  5. 保存 Quote。
  6. 返回 Quote result。
- `GetQuoteUseCase`
  1. 按 quoteId 读取 Quote。
  2. 校验 applicantId 归属。
  3. 校验 validUntil。
  4. 返回完整 Quote。

### Infrastructure

- `JdbcQuoteRepository` 实现 quote persistence。
- `JdbcRuntimeDependencyProbe` 检查 DB readiness。
- Flyway migration 创建 quotes 表。

## Data / Config / Permission

- Config:
  - `spark.quote.validity=30m`
  - `spark.quote.jdbc-url`
  - `spark.quote.jdbc-username`
  - `spark.quote.jdbc-password`
- Permission:
  - applicantId 只来自 LEN-22 principal。
  - quoteId 不包含 applicantId 明文。
- Data:
  - 使用 BigDecimal 与 numeric/decimal 对齐。
  - quoteId 使用 `quote_` 前缀 UUID。

## Observability

- health: `/health` 返回服务基本状态。
- ready: `/ready` 检查 DB。
- logs: 失败路径包含 `error_code`，不记录 token。
- tracing: 使用 Spring/OpenTelemetry 默认 instrumentation。

## Testing Strategy

- Domain/unit:
  - PIL amount min/max。
  - allowed terms。
  - monthly/apr/totalInterest/totalPayable。
  - out-of-range 不创建 Quote。
- Application:
  - create quote 保存后返回 quoteId。
  - get quote 校验 applicantId。
  - expired quote 返回 quote_expired。
- Infrastructure:
  - Flyway migration 可执行。
  - JDBC repository save/find。
  - ready 检查 DB 不可用时失败。
- Service:
  - `mvn test`。
- CI support:
  - business-repo Java quality project graph 必须识别 `quote-api`。
  - GitOps Argo Java CI DAG 必须在 `spring-starter` 后调度 `quote-api`。

## Rollout And Rollback

- LEN-10 只交付代码，不部署。
- GitOps 仅交付 PR Java CI gate 调度支撑，不创建 runtime 资源。
- LEN-131 负责 runtime deployment、quote DB 和 service discovery。
- 回滚 LEN-10 只需回滚 `apps/quote-api`、Java CI 支撑和 service matrix 变更。

## Risks

| Risk | Mitigation | Owner |
|---|---|---|
| 计算公式口径后续变更 | 将计算封装在 `PricingPolicy`，测试锁定当前 MVP | core |
| 后续 BFF facade 期望不同字段名 | response 字段按 Jira 固定，LEN-132 适配该结构 | core |
| DB runtime 未就绪 | LEN-131 负责部署验证，LEN-10 ready probe 提供基础能力 | core |
