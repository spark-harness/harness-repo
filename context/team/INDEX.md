# Team Context Index

团队级知识适用于所有项目和需求。

## 当前入口

- `git.md`：分支、提交和评审要求。
- `git-workflow.md`：从需求到合并的 Git 工作流。
- `backend-clean-architecture.md`：后端干净架构分层、依赖方向、端口接口和评审要求。
- `frontend-clean-architecture.md`：前端干净架构分层、Dependency Cruiser 依赖规则和评审要求。
- `testing.md`：单元测试、集成测试、端到端测试和测试门禁要求。
- `contract-compatibility.md`：protobuf、HTTP、事件和错误码的契约兼容性要求。
- `error-codes.md`：错误码空间、分配规则和兼容性要求。
- `logging.md`：日志与可观测性要求。
- `metrics.md`：指标命名、标签、业务指标、告警和 SLO 要求。
- `money.md`：金额、币种、舍入和单位换算规范。
- `tracing.md`：OpenTelemetry 分布式追踪规范。
- `security.md`：安全与敏感信息要求。

## 维护原则

- 只写跨项目通用约束。
- 不复制某个服务的业务实现细节。
- 规则变化必须能被需求、设计或门禁引用。
- 如果规则影响服务契约、错误码或日志字段，必须同步更新对应需求或设计门禁。
