# 后端干净架构规范

干净架构用于让业务规则保持稳定，让框架、数据库、消息、缓存和外部渠道成为可替换的实现细节。

## 它不是什么

干净架构不是为了追求教科书式分层。

如果一个服务很小，强行拆出大量包、接口和转换对象，只会增加评审成本。团队不要求所有代码都做到绝对无框架侵入，也不要求为每个类都创建接口。

干净架构也不是把 MVC 的 `controller`、`service`、`repository` 换一套名字。只改包名但依旧让业务模型依赖数据库表、ORM 注解、HTTP DTO 或消息 payload，不能降低耦合。

## 它是什么

干净架构是一组依赖约束和职责边界。

它要求团队优先设计业务规则，再选择技术实现：

- 领域层回答“能不能做”和“规则怎么算”。
- 应用层回答“什么时候做”和“前后怎么编排”。
- 入站适配层回答“外部请求如何进入应用”。
- 基础设施层回答“数据库、缓存、消息、第三方系统具体怎么做”。

核心目标不是让代码看起来复杂，而是让核心业务在技术栈变化、存储变化、接口变化时少受影响。

## 依赖方向

依赖只能从外向内。

推荐方向：

```text
adapter/inbound -> application -> domain
infrastructure -> application/domain
bootstrap -> adapter/inbound + infrastructure
```

允许外层依赖内层。禁止内层依赖外层。

| Layer | 可以依赖 | 禁止依赖 |
|---|---|---|
| domain | 语言标准库、团队认可的基础值对象 | HTTP、ORM、消息、缓存、DI 框架、外部 SDK |
| application | domain、应用端口接口、事务抽象 | controller、数据库实现类、消息实现类、第三方 SDK |
| adapter/inbound | application、domain、契约 DTO | 数据库表结构、具体 ORM mapper 细节、基础设施实现类 |
| infrastructure | application 端口、domain、技术框架 | 反向污染 domain 的技术模型 |
| bootstrap | 所有装配对象 | 业务规则实现 |

如果语言或框架让完全隔离代价过高，可以接受局部妥协，但必须能解释：

- 这个技术细节是否绕不开。
- 是否有低成本方式把它移到外层。
- 为消除它付出的代码量和可读性代价是否值得。

## 分层职责

### 领域层

领域层保存业务概念、业务状态和业务规则。

适合放在领域层：

- 实体、值对象、领域枚举、领域异常。
- 状态流转、金额计算、库存扣减、资格判断等核心规则。
- 业务不变式，例如终态订单不可修改、余额不能为负。
- 领域需要的端口接口，例如仓储读取、领域策略、外部能力抽象。

不应放在领域层：

- SQL、ORM mapper、HTTP client、消息 producer。
- request、response、protobuf 或 JSON DTO。
- controller 参数校验。
- 数据库分页、排序、字段投影等存储细节。

领域对象应尽量使用充血模型。业务规则不应散落在应用层的脚本式流程中。

### 应用层

应用层也可以命名为 use case 层。它负责组织一次业务用例的执行过程。

适合放在应用层：

- 用例入口，例如 `CreateOrderUseCase`、`CancelOrderUseCase`。
- 事务边界。
- 幂等、重试、权限检查、审计记录的用例级编排。
- 调用领域对象完成业务判断和状态变化。
- 调用端口接口保存数据、发布事件、发送通知。
- 返回面向上层的应用结果对象。

不应放在应用层：

- SQL 或 ORM 查询实现。
- HTTP response 组装细节。
- 第三方 SDK 调用细节。
- 可以放进领域对象的核心业务规则。

判断方法：

- 如果代码在决定“这件事是否符合业务规则”，优先放到领域层。
- 如果代码在决定“先做 A 再做 B，失败后如何处理”，优先放到应用层。

### 入站适配层

入站适配层负责把外部协议转换成应用层能理解的输入，并把应用结果转换成外部响应。

适合放在入站适配层：

- HTTP controller、RPC handler、message consumer、scheduled job handler。
- request 参数校验和协议级错误转换。
- protobuf、JSON、form、header、query 与应用命令对象之间的映射。
- 外部错误码、HTTP status、响应结构转换。

不应放在入站适配层：

- 核心业务规则。
- 数据库查询实现。
- 需要复用的领域计算。
- repository、message producer、third-party client 等出站实现。

入站适配层可以很薄，但不能把所有逻辑透传给一个“大 service”后结束。它必须明确完成协议转换和边界校验。

### 基础设施层

基础设施层实现技术细节。

适合放在基础设施层：

- repository 实现。
- ORM entity、mapper、SQL、数据库事务实现。
- message producer、cache client、third-party client。
- 文件、对象存储、搜索引擎、配置中心等技术集成。

基础设施层必须实现应用层或领域层定义的端口接口。业务层不应直接 new 或 import 基础设施实现类。

### 出站适配器

出站适配器是概念，不是本规范中的单独目录。

应用层访问数据库、消息、缓存、第三方系统时，应先在应用层或领域层定义端口接口，再由基础设施层实现这个端口。也就是说，出站适配器落在 `infrastructure/` 目录下。

推荐对应关系：

| 外部能力 | Port 位置 | 实现位置 |
|---|---|---|
| 订单持久化 | `application/order/port/OrderRepository` | `infrastructure/persistence/JpaOrderRepository` |
| 订单事件发布 | `application/order/port/OrderEventPublisher` | `infrastructure/messaging/KafkaOrderEventPublisher` |
| 支付渠道调用 | `application/payment/port/PaymentGateway` | `infrastructure/external/StripePaymentGateway` |
| 库存缓存 | `application/inventory/port/InventoryCache` | `infrastructure/cache/RedisInventoryCache` |

不要创建 `adapter/outbound/` 作为应用层依赖目标。这样容易让人误解为：

```text
application -> adapter/outbound -> infrastructure
```

正确依赖方向是：

```text
application -> application/domain port
infrastructure -> application/domain port
bootstrap wires infrastructure implementation into application use case
```

存储模型 mapper、第三方请求 mapper、消息 payload mapper 应放在对应基础设施目录内，例如 `infrastructure/persistence/OrderPersistenceMapper` 或 `infrastructure/external/PaymentGatewayMapper`。

## 端口接口

端口接口应由使用方定义，而不是由实现方定义。

示例：

```text
application/order/port/OrderRepository
infrastructure/persistence/OrderRepositoryJpaAdapter
```

`OrderRepository` 应表达业务需要：

```text
findById(orderId)
save(order)
```

不要把技术实现泄漏进端口：

```text
selectByPrimaryKey(id)
insertSelective(record)
updateByExample(example)
```

端口接口数量应受控。只有当业务层需要隔离数据库、消息、外部渠道、时钟、ID 生成、配置或其他不稳定技术细节时，才创建端口接口。

## 数据模型边界

同一个业务对象可能同时存在多种模型，它们不能混用。

| Model | 所属层 | 用途 |
|---|---|---|
| Domain Entity | domain | 表达业务状态和规则 |
| Value Object | domain | 表达不可变业务值 |
| Command / Query | application | 表达用例输入 |
| Use Case Result | application | 表达用例输出 |
| Request / Response DTO | adapter/inbound | 表达外部协议 |
| ORM Entity / Record | infrastructure | 表达存储结构 |

转换规则：

- controller 不直接接收或返回 domain entity。
- repository 实现负责 domain entity 与 ORM entity 的转换。
- 应用层不接触 ORM entity。
- 领域层不接触 request、response、protobuf message。

如果转换对象过多，应先检查边界是否真实存在。没有外部协议、存储结构或复用需求时，不要为了形式创建空壳 DTO。

## 事务边界

事务边界通常放在应用层用例入口。

原因是一次用例往往需要协调多个领域对象、仓储和事件发布。领域对象只表达状态变化和规则，不负责开启、提交或回滚事务。

事务设计必须说明：

- 哪个用例是事务入口。
- 哪些写操作在同一事务内。
- 事件、消息、通知是在事务内、事务后还是通过 outbox 发布。
- 失败后是否需要补偿、重试或人工处理。

不要在领域对象中开启事务。不要让 repository 实现偷偷控制跨用例事务语义。

## 异常和错误码

领域层可以抛出稳定的领域异常，但异常不应绑定 HTTP status、RPC code 或页面文案。

推荐流转：

```text
domain exception
  -> application result or propagated exception
  -> adapter/inbound maps to error code and protocol response
```

错误码必须遵守错误码空间规范。新增或修改用户可见失败语义时，应同步更新错误码文档、契约兼容性说明和设计门禁。

## 目录模板

新服务可以从以下结构起步，再按实际复杂度裁剪：

```text
services/{service-name}/
├── src/main/java/{base-package}/
│   ├── domain/
│   │   └── {domain-name}/
│   │       ├── model/
│   │       ├── value/
│   │       ├── event/
│   │       └── exception/
│   ├── application/
│   │   └── {domain-name}/
│   │       ├── usecase/
│   │       ├── command/
│   │       ├── result/
│   │       └── port/
│   ├── adapter/
│   │   └── inbound/
│   │       ├── http/
│   │       ├── rpc/
│   │       └── message/
│   ├── infrastructure/
│   │   ├── persistence/
│   │   │   └── mapper/
│   │   ├── messaging/
│   │   ├── cache/
│   │   └── external/
│   │       └── mapper/
│   └── bootstrap/
└── src/test/java/{base-package}/
```

裁剪原则：

- 没有消息消费时，不创建 `adapter/inbound/message/`。
- 没有外部调用时，不创建 `infrastructure/external/`。
- 没有复杂模型转换时，不创建 `infrastructure/*/mapper/`。
- 一个服务只有单一简单领域时，可以省略 `{domain-name}` 这一级。
- 包名可以按语言和框架调整，但职责边界必须保留。

## 最小用例模板

设计新后端用例时，至少写清以下内容：

```markdown
## 用例：{use-case-name}

### 业务目标

{这个用例让用户或外部系统完成什么业务结果}

### 领域规则

- {规则 1}
- {规则 2}

### 应用编排

1. {读取或校验}
2. {调用领域对象}
3. {持久化}
4. {发布事件或通知}

### 端口接口

| Port | 使用方 | 实现方 | 说明 |
|---|---|---|---|
| `{PortName}` | application/domain | infrastructure | {为什么需要隔离} |

### 事务和失败处理

- 事务入口：`{UseCase}`
- 事务内操作：{列表}
- 事务后操作：{列表}
- 失败语义：{错误码、重试、补偿或人工处理}

### 契约影响

- API：{无 / 新增 / 修改}
- protobuf：{无 / 新增 / 修改}
- 事件：{无 / 新增 / 修改}
- 错误码：{无 / 新增 / 修改}
```

## 测试要求

测试应围绕业务行为和层边界组织。

| 测试类型 | 优先验证 |
|---|---|
| 领域单元测试 | 状态流转、金额计算、业务不变式、异常路径 |
| 应用层测试 | 编排顺序、事务语义、端口调用后的业务结果 |
| 入站适配层测试 | 参数校验、协议映射、错误码转换 |
| 基础设施集成测试 | ORM 映射、SQL、事务、消息、外部 client 适配 |
| 端到端测试 | 关键业务链路从外部入口到最终状态 |

不要用大量 mock 锁死领域对象内部实现。能用真实领域对象验证的规则，应优先用真实对象。

## 设计门禁检查

新增或重构后端服务时，设计门禁至少检查：

- 是否列出涉及的领域对象、用例和外部契约。
- 核心业务规则是否放在领域层，而不是 controller 或 repository。
- 应用层是否只做用例编排和事务控制。
- 端口接口是否由使用方定义，且没有泄漏 ORM、SQL 或 SDK 语义。
- DTO、domain entity、ORM entity 是否没有跨层混用。
- 事务边界、事件发布和失败处理是否明确。
- 错误码、日志、指标和 tracing 是否与团队规范一致。
- 如果存在框架侵入或分层妥协，是否说明原因和代价。
- 测试计划是否覆盖领域规则、适配映射和基础设施集成风险。

## 合并前检查

合并前必须确认：

- 代码依赖方向没有从内层指向外层。
- 领域层没有直接依赖 HTTP、ORM、消息、缓存或外部 SDK。
- 应用层没有直接依赖基础设施实现类。
- controller、consumer、job handler 中没有堆叠核心业务规则。
- repository 实现完成 domain 与存储模型转换。
- 新增契约、错误码、日志字段、指标和 trace attribute 已同步对应规范或设计证据。
- 测试证据能证明核心业务行为，而不是只证明代码被调用。
