# 金额处理规范

金额是资金安全边界，不是普通数字字段。

## 它不是什么

金额不是 `double`、`float`、裸 `long` 或散落的 `BigDecimal`。

金额单位换算不是业务代码可以随手处理的实现细节。元、分、最小货币单位和渠道字段之间的转换必须有统一入口。

## 它是什么

金额由三部分共同表达：

- 金额数值。
- 币种。
- 舍入策略。

跨服务传递、内部计算、入库和外发渠道时，必须保留这三类语义，避免把金额退化成没有币种和单位上下文的数字。

## 统一类型

团队公共库提供 `Money` 类型作为金额处理入口：

```text
business-repo/packages/java/money
```

Java 服务应依赖公共库：

```xml
<dependency>
  <groupId>com.spark.common</groupId>
  <artifactId>spark-money</artifactId>
  <version>0.1.0-SNAPSHOT</version>
</dependency>
```

服务内部不得新增自己的 Money 类，也不得用工具方法散落实现元分换算。

## 处理原则

- 入口层收到外部金额后，应尽早转换为 `Money`。
- 内部应用之间传输金额时，应同时传递金额和币种。
- 内部计算只允许通过 `Money` 提供的加、减、乘、除和比较方法完成。
- 加、减和比较必须要求币种一致。
- 涉及除不尽、费率、分摊和折扣时，必须显式确认舍入策略。
- 数据库存储使用 `DECIMAL` 保存主单位金额，同时保存 ISO 4217 币种代码。
- 只有外发渠道明确要求最小货币单位时，才允许把金额转换为最小货币单位。

## 禁止事项

- 禁止使用 `double` 或 `float` 表示金额。
- 禁止在业务代码中手动乘以 100 或除以 100 做元分转换。
- 禁止只传金额数字、不传币种。
- 禁止不同币种直接加减或比较。
- 禁止在没有产品、财务或结算规则确认的情况下随意选择舍入模式。
- 禁止把渠道金额单位直接扩散到内部服务契约。

## 存储约定

业务表应拆分存储金额和币种：

| 字段 | 类型 | 示例 | 说明 |
|---|---|---|---|
| `amount` | `DECIMAL(19, 4)` 或按业务精度定义 | `100.00` | 主单位金额 |
| `currency` | `CHAR(3)` | `CNY` | ISO 4217 币种代码 |

不同业务可以提高 `DECIMAL` 精度，但不能降低已发布字段的精度或改变单位语义。

## 接口约定

内部接口优先表达主单位金额和币种：

```json
{
  "amount": "100.00",
  "currency": "CNY"
}
```

对接外部渠道时，适配层负责按渠道文档转换：

| 渠道要求 | 转换位置 | 示例 |
|---|---|---|
| 主单位金额 | 渠道适配层 | `100.00 CNY` |
| 最小货币单位 | 渠道适配层 | `10000 CNY minor units` |

渠道字段格式不得反向污染内部接口。

## 边界规则

金额在不同边界使用不同载体，但语义必须一致。

| 边界 | 推荐载体 | 金额单位 | 规则 |
|---|---|---|---|
| Java 服务内部 | `Money` | 主单位 | 入口转换后，业务逻辑只传 `Money` |
| protobuf / gRPC | 公共 `Money` message | 主单位 decimal string | 不使用 `double`、`float` 或 `int64 cents` |
| 数据库 | `DECIMAL amount` + `currency` | 主单位 | 金额和币种拆字段保存 |
| 前端 JSON | `{ "currency": "...", "amount": "..." }` | 主单位 decimal string | 金额必须是字符串，不返回 number |
| 外部支付渠道 | 渠道适配层字段 | 按渠道文档 | 只在 adapter 层转换主单位或最小货币单位 |

protobuf 公共金额类型建议定义为：

```proto
syntax = "proto3";

package spark.type.v1;

message Money {
  string currency = 1;
  string amount = 2;
}
```

其中：

- `currency` 使用 ISO 4217 三位币种代码，例如 `CNY`、`USD`、`JPY`。
- `amount` 使用主单位十进制字符串，例如 `100.00`。
- 不在 protobuf 中使用 Java `Money` 类名作为契约语义。
- 不用 `minor_units` 作为内部服务默认协议字段。

服务边界处理规则：

- gRPC adapter 收到 protobuf `Money` 后，立即转换成服务内部 `Money`。
- 服务调用下游时，在 adapter 层把内部 `Money` 转回 protobuf `Money`。
- Domain 和 Application 层不得感知 protobuf message。
- Repository 层负责 `Money` 与数据库 `amount`、`currency` 字段之间的转换。
- Channel adapter 层负责按外部渠道要求调用 `amount()` 或 `minorUnits()`。

前端返回规则：

```json
{
  "payableAmount": {
    "currency": "CNY",
    "amount": "100.00"
  }
}
```

如果需要后端统一展示格式，可以额外返回展示字段：

```json
{
  "payableAmount": {
    "currency": "CNY",
    "amount": "100.00",
    "display": "¥100.00"
  }
}
```

`display` 只用于展示，不得作为前端提交、计算或服务间传递的金额来源。

## 设计门禁检查

涉及金额的新需求或改动，设计门禁必须检查：

- 是否使用公共 `Money` 类型承载内部金额语义。
- 是否说明入口转换、内部流转、数据库存储和渠道外发的单位。
- 是否定义舍入策略以及策略来源。
- 是否列出跨币种加减、比较和汇率换算边界。
- 是否有测试覆盖日元、人民币、美元等不同小数位币种。
- 是否避免 `double`、`float` 和手动元分换算。

## 参考来源

- 人人都是产品经理：《资损防控：搞定跨境交易系统中金额处理规范》：https://www.woshipm.com/pd/6166947.html
