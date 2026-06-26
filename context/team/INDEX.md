# Team Context Index

团队级知识适用于所有项目和需求。

它不是服务实现手册。跨项目通用规则放在这里；项目、领域、服务特例放到 `context/project/`。

## 语言规范

| 文档 | 作用 |
|---|---|
| `java.md` | Java / Spring Boot 服务和库的最小工程约定 |
| `typescript.md` | TypeScript 前端、BFF 和共享包的最小工程约定 |
| `go.md` | Go 服务、BFF、worker 和库的最小工程约定 |

## 架构和代码

| 文档 | 作用 |
|---|---|
| `backend-clean-architecture.md` | 后端干净架构分层、依赖方向、端口接口和评审要求 |
| `frontend-clean-architecture.md` | 前端干净架构分层、Dependency Cruiser 依赖规则和评审要求 |
| `money.md` | 金额、币种、舍入和单位换算规范 |
| `error-codes.md` | 错误码空间、分配规则和兼容性要求 |

## 测试、契约和交付

| 文档 | 作用 |
|---|---|
| `testing.md` | 单元测试、集成测试、端到端测试和测试门禁要求 |
| `contract-compatibility.md` | protobuf、HTTP、事件和错误码的契约兼容性要求 |
| `contract-versioning.md` | IDL 生成契约的 development / RC / formal 版本发布、消费和门禁要求 |
| `git.md` | 分支、提交、PR 标题和评审要求 |
| `git-workflow.md` | 从需求到合并的 Git 工作流 |
| `ci-cd.md` | CI/CD、PR 描述、门禁失败和合并前检查的第一版口径 |

## 运行质量

| 文档 | 作用 |
|---|---|
| `observability.md` | 日志、指标、Tracing 和告警的入口规范 |
| `logging.md` | 日志字段、级别和敏感信息边界 |
| `metrics.md` | 指标命名、标签、业务指标、告警和 SLO 要求 |
| `tracing.md` | OpenTelemetry 分布式追踪规范 |
| `security.md` | 安全、权限、Secret 和敏感信息要求 |
| `database.md` | migration、索引、事务、查询和数据修复规则 |
| `local-development.md` | 本地启动、配置、依赖和验证的最小约定 |

## 维护原则

- 只写跨项目通用约束。
- 不复制某个服务的业务实现细节。
- 一条规则只定义在一个源文件，其他文档只引用。
- 规则变化必须能被需求、设计或门禁引用。
- 如果规则影响服务契约、错误码、日志字段、指标或权限，必须同步更新对应需求、设计或门禁。
