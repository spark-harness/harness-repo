# OpenTelemetry Tracing 规范

分布式追踪用于理解一次请求在多个服务、队列、数据库和外部依赖之间的完整路径。

## 它不是什么

Tracing 不是日志的替代品，不是指标系统，也不是业务审计记录。

日志回答“某个点发生了什么”；指标回答“整体趋势如何”；Tracing 回答“一次请求经过了哪里、耗时在哪、失败在哪”。

## 它是什么

本团队统一使用 OpenTelemetry 作为 tracing 标准。

Tracing 规范定义：

- 如何创建 span。
- 如何命名 span。
- 如何跨服务传播 trace context。
- 如何区分同步和异步链路。
- 如何记录错误和关键属性。
- 如何把 trace、log、metric 关联起来。

## 基础要求

- 所有服务应使用 OpenTelemetry API / SDK 或兼容的自动 instrumentation。
- `service.name` 必须与服务矩阵中的服务名一致。
- 入口请求必须创建 server span。
- 外部 HTTP、RPC、数据库、缓存、消息队列调用必须创建对应 client / producer / consumer span。
- 日志必须能关联当前 `trace_id` 和 `span_id`。
- 错误 span 必须携带稳定错误码。
- `trace_id` 不属于业务契约、领域模型或持久化字段；同步链路必须通过 W3C TraceContext 传播。

## 同步与异步链路

Tracing 必须区分同步调用和异步处理。

同步调用表示当前请求必须等待下游返回，例如 HTTP、gRPC、数据库、缓存查询。

异步处理表示当前请求只生产消息、任务或事件，后续消费可能在另一个时间、另一个实例、另一个批次执行，例如 MQ、任务队列、事件总线、延迟任务。

### 同步调用

同步调用使用 parent / child 关系。

规则：

- 入口请求创建 `SERVER` span。
- 出站 HTTP / RPC / DB / Cache 调用创建 `CLIENT` span。
- 下游服务收到请求后，从 `traceparent` 提取上下文，创建自己的 `SERVER` span。
- 下游 `SERVER` span 的 parent 应指向上游 `CLIENT` span。

示意：

```text
order-api SERVER
└── payment-api CLIENT
    └── payment-api SERVER
```

同步链路的 trace 应能表达请求的阻塞路径和耗时组成。

### 异步处理

异步处理使用 span link，不把消费端 span 直接挂成生产端 span 的 child。

原因是异步消费可能延迟、批量、重试或跨批次执行。直接 parent / child 会误导调用关系，让 trace 看起来像同步阻塞。

规则：

- 生产消息、任务或事件时创建 `PRODUCER` span。
- 消费消息、任务或事件时创建新的 `CONSUMER` span。
- `CONSUMER` span 应通过 span link 关联生产端 span context。
- 消息 header 中可以携带 trace context，用于消费端创建 span link。
- 批量消费时，一个 `CONSUMER` span 可以 link 多个生产端 span context；如果每条消息需要独立排障，应拆成每条消息一个消费 span。

示意：

```text
Trace A
order-api SERVER
└── publish order.created PRODUCER

Trace B
consume order.created CONSUMER
  links -> Trace A / publish order.created PRODUCER
```

异步链路的 trace 应表达因果关系，而不是伪造同步调用栈。

## Resource 属性

服务启动时应设置稳定 Resource 属性：

| Attribute | 含义 | 示例 |
|---|---|---|
| `service.name` | 服务名 | `order-api` |
| `service.version` | 服务版本或 commit | `1.4.2` |
| `deployment.environment` | 环境 | `prod`、`staging` |

`service.name` 不得使用本地进程名、临时容器名或机器名。

## Span Kind

| Span Kind | 使用场景 |
|---|---|
| `SERVER` | 处理进入当前服务的 HTTP / RPC 请求 |
| `CLIENT` | 当前服务发起的同步远程调用 |
| `PRODUCER` | 当前服务写入消息、任务或事件 |
| `CONSUMER` | 当前服务消费消息、任务或事件 |
| `INTERNAL` | 服务内部关键步骤 |

不要把所有 span 都标成 `INTERNAL`。跨进程边界必须使用能表达调用方向的 span kind。

异步 `CONSUMER` span 不应因为消息 header 中存在 `traceparent` 就默认创建为生产端 span 的 child。消费端应优先创建新 trace，并用 span link 表达生产和消费之间的因果关系。

## Span 命名

Span 名称必须稳定、低基数、可聚合。

推荐：

```text
POST /orders
OrderService/CreateOrder
publish order.created
consume order.created
db.orders.insert
```

禁止：

```text
POST /orders/123456
CreateOrder user=10001
publish order.created.20260530.abcdef
```

不要把用户 ID、订单 ID、手机号、请求体摘要放进 span name。需要记录业务对象时，使用受控 attribute，并遵守安全规范。

## Context Propagation

跨服务调用必须传播 trace context。

默认使用 W3C TraceContext：

```text
traceparent
tracestate
```

HTTP、RPC、消息队列和任务调度都应支持 context 注入和提取。

同步协议中，提取出的 context 用于建立 parent / child。

异步协议中，提取出的 context 用于建立 span link。

### 外部服务

调用不受信任的外部服务时：

- 不应向外部传播内部敏感 baggage。
- 对外部传入的 trace header 应按网关或服务边界策略处理。
- 不把内部架构、租户、用户敏感信息放入 baggage。

## Attributes

优先使用 OpenTelemetry Semantic Conventions 中已有的 attribute 名称。

团队补充属性应保持低基数：

| Attribute | 含义 | 示例 |
|---|---|---|
| `error_code` | 团队稳定错误码 | `ORDER-STATE-0001` |
| `business.domain` | 业务域 | `order` |
| `feature.flag` | 灰度或功能开关名 | `checkout_v2` |

禁止把以下内容作为高频 span attribute：

- 完整请求体或响应体。
- 明文手机号、身份证、银行卡、令牌。
- 高基数的用户 ID、订单 ID、设备 ID，除非经过安全评估并有采样控制。

## 错误记录

请求失败时必须：

- 设置 span status 为 `Error`。
- 记录稳定 `error_code`。
- 记录异常类型或失败原因。
- 避免把敏感异常上下文写入 attribute。

日志中的 `error_code` 应与 trace 中的 `error_code` 一致。

## Sampling

采样策略必须可解释。

最低要求：

- 线上默认不能全量采集高流量 trace。
- 错误 trace 应优先保留。
- 关键链路可以提高采样率。
- 不用用户 ID、手机号等敏感字段直接作为采样条件。

## Collector 与后端

服务不应直接绑定某个厂商后端。

推荐路径：

```text
service -> OpenTelemetry Collector -> tracing backend
```

这样可以在不改业务代码的情况下调整导出、采样、脱敏和后端路由。

## 设计门禁检查

如果需求新增或修改关键链路，设计门禁必须检查：

- 入口请求是否有 server span。
- 下游调用是否有 client / producer / consumer span。
- 同步调用是否使用 parent / child 传播。
- 异步处理是否使用 span link，而不是伪造 parent / child。
- trace context 是否能跨服务传播，并能在异步消费端恢复为 span link。
- 日志是否包含 `trace_id` 和 `span_id`。
- 错误路径是否同时记录 span status、`error_code` 和日志。
- 是否存在高基数或敏感 attribute。
- 采样策略是否会导致关键错误不可见。
