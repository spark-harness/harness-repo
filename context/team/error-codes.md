# 错误码空间规范

错误码是跨服务、跨端、跨团队定位问题的稳定契约。

## 它不是什么

错误码不是日志文案，不是异常类名，也不是 HTTP status 或 gRPC status 的替代品。

HTTP status 和 gRPC status 描述协议层结果；错误码描述业务或系统语义。

## 它是什么

错误码用于稳定表达：

- 哪个领域出错。
- 错误属于哪一类。
- 错误是否可重试。
- 是否可以暴露给用户。
- 运维和客服如何定位。

## 格式

推荐格式：

```text
{DOMAIN}-{CATEGORY}-{NUMBER}
```

示例：

```text
ORDER-PARAM-0001
ORDER-STATE-0002
PAYMENT-DEPENDENCY-0001
AUTH-PERMISSION-0001
```

## 字段含义

| 字段 | 含义 | 示例 |
|---|---|---|
| `DOMAIN` | 业务域或平台域 | `ORDER`、`PAYMENT`、`AUTH` |
| `CATEGORY` | 错误类别 | `PARAM`、`STATE`、`DEPENDENCY` |
| `NUMBER` | 领域内递增编号 | `0001` |

## 推荐类别

| Category | 含义 | 可重试 |
|---|---|---:|
| `PARAM` | 请求参数不合法 | No |
| `AUTH` | 未登录、认证失败 | No |
| `PERMISSION` | 无权限 | No |
| `STATE` | 业务状态不允许 | No |
| `CONFLICT` | 并发或幂等冲突 | Depends |
| `DEPENDENCY` | 下游服务或外部依赖失败 | Yes |
| `SYSTEM` | 当前服务内部非预期失败 | Yes |

## 分配规则

- 错误码一旦发布，不得复用。
- 删除语义时只能废弃错误码，不能把旧错误码改成新含义。
- 同一个错误码在所有服务中必须含义一致。
- 用户可见文案不得直接等同于错误码说明。
- 日志、指标和追踪中必须保留错误码。
- 对外接口返回错误码时，必须说明兼容性影响。

## 记录模板

团队或项目可以维护错误码表：

| Error Code | HTTP / gRPC Mapping | Meaning | Retryable | User Visible | Owner | Status |
|---|---|---|---:|---:|---|---|
| `ORDER-STATE-0001` | `FAILED_PRECONDITION` | 订单终态不可修改 | No | Yes | order | Active |
| `PAYMENT-DEPENDENCY-0001` | `UNAVAILABLE` | 支付渠道暂不可用 | Yes | No | payment | Active |

## 设计门禁检查

如果需求新增或修改错误码，设计门禁必须检查：

- 错误码是否在正确领域下分配。
- 是否复用了旧错误码。
- 是否定义重试语义。
- 是否定义用户可见文案策略。
- 是否影响前端、客户端、客服或运营排障。
- 日志和指标是否携带该错误码。
