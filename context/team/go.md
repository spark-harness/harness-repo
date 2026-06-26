# Go 工程规范

本文适用于 Spark/Lendora Go 服务、BFF、worker 和库。

它不是 Go 教程，也不替代服务级架构说明。跨项目规则写在这里；服务例外写到 `context/project/`。

## 最小规则

| 主题 | 规则 |
|---|---|
| 版本 | 使用 `go.mod` 声明的 Go 版本，不在局部脚本私自升级 |
| package | package 名称表达职责，不使用 `common`、`utils` 承载业务语义 |
| context | 所有 IO、RPC、DB、cache 调用必须接收并传递 `context.Context` |
| error | 错误必须保留原因和稳定分类，禁止只返回字符串拼接错误 |
| logging | 日志遵守 `logging.md`，使用结构化字段 |
| concurrency | goroutine 必须有退出条件，channel 必须明确关闭责任 |
| timeout | 外部调用必须有 timeout、deadline 或上游 context 约束 |
| contracts | 生成契约只在 adapter 边界使用，不扩散到核心业务规则 |

## 目录分层

推荐服务内采用：

```text
cmd/             # 进程入口
internal/api/    # HTTP/gRPC handler
internal/app/    # use case、编排、事务边界
internal/domain/ # 领域模型和业务规则
internal/infra/  # DB、RPC、生成契约 adapter
pkg/             # 确认要给仓内外复用的库
```

不要为了复用过早放进 `pkg/`。默认先放 `internal/`，有明确复用者再提升。

## 错误处理

- 使用 `%w` 或等价方式保留错误链。
- API 层负责把内部错误映射为协议响应和稳定错误码。
- 不用 panic 表达可预期业务失败。
- 重试必须区分可重试和不可重试错误。

## 并发和资源

- 启动 goroutine 的地方负责取消、等待或说明生命周期。
- ticker、timer、response body、文件、连接必须关闭。
- 后台任务必须处理 context cancel。
- 禁止无界 goroutine、无界 channel 和无限重试。

## 测试

- domain 和 app 层优先写单元测试。
- handler、repository、外部 adapter 优先写集成测试。
- 涉及 contract 的 adapter 测试要覆盖错误映射和兼容字段。
- 测试不依赖执行顺序，不依赖真实外部网络。

## 合并前检查

```bash
go test ./...
go vet ./...
gofmt -w <changed-go-files>
```

如果仓库使用 `golangci-lint` 或自定义 Makefile，以仓库命令为准，并在 PR 描述记录实际命令。
