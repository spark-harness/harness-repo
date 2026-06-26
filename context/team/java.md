# Java 工程规范

本文适用于 Spark/Lendora Java 服务、库和测试代码。

它不是 Java 教程，也不替代服务级设计。它只定义跨项目最小约定；服务例外写到 `context/project/{project}/{domain}/{service}/`。

## 最小规则

| 主题 | 规则 |
|---|---|
| 版本 | 使用仓库声明的 JDK 和 Maven/Gradle 版本，不在单个模块私自升级 |
| 分层 | Controller / Adapter 不写业务规则，业务规则放在 application/domain 层 |
| 依赖方向 | 内层不依赖外层，domain 不依赖 Spring、HTTP、数据库或生成 client |
| DTO | 外部请求/响应 DTO 不直接进入 domain，必须在边界转换 |
| 事务 | 事务放在 application service 或 use case 边界，不散落到 private helper |
| 时间 | 业务时间通过 `Clock` 或等价注入，不在业务规则里直接 `now()` |
| 金额 | 金额和币种遵守 `money.md`，禁止用浮点数表达金额 |
| 日志 | 遵守 `logging.md`，错误日志必须带稳定错误码或错误类型 |
| 安全 | 不记录敏感字段，不把 token、secret、PII 放进异常消息 |

## 包和目录

推荐服务内采用稳定分层命名：

```text
api/            # HTTP/RPC/controller 和请求响应 DTO
application/    # use case、事务边界、编排
domain/         # 领域模型、业务规则、领域错误
infrastructure/ # 数据库、外部服务、生成契约 client adapter
config/         # 框架配置
```

如果现有服务已有不同但清晰的分层，优先保持现状；新增代码不要再制造第二套结构。

## 错误处理

- 领域错误使用稳定错误类型或错误码，不直接抛框架异常。
- API 层负责把内部错误映射为协议响应。
- 捕获异常必须有处理动作：转换、补偿、重试、降级或记录后继续抛出。
- 禁止吞异常后返回默认成功。

## 外部契约

- 生成 Java 契约只能在边界层使用。
- 业务代码不直接依赖生成 client 的请求/响应对象。
- 消费契约版本遵守 `contract-versioning.md`。
- 兼容性判断遵守 `contract-compatibility.md`。

## 测试

- 领域规则优先写单元测试。
- Repository、事务、序列化、权限和外部 adapter 优先写集成测试。
- 测试命名、分层和覆盖重点遵守 `testing.md`。
- 不为 getter、setter、无分支转发代码补覆盖率型测试。

## 合并前检查

```bash
mvn test
git diff --check
```

如果模块有更窄命令，以模块 README、CI 或服务上下文为准，并在 PR 描述里记录实际命令。
