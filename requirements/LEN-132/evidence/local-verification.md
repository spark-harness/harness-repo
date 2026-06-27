# Local Verification

## Scope

验证 `LEN-132` 在 `fides-bff` 中新增的 pricing facade。

## Commands

在 `/Users/forest/Code/spark/.worktrees/LEN-132/business-repo/apps/fides-bff` 执行：

```bash
go test ./internal/server -run 'PricingQuote'
go test ./...
go vet ./...
go build ./cmd/fides-bff
```

## Results

| Command | Result | Evidence |
|---|---|---|
| `go test ./internal/server -run 'PricingQuote'` | PASS | 覆盖无 token、无效 token、成功调用、422 映射、502 映射、principal applicantId 和 trace propagation |
| `go test ./...` | PASS | `cmd/fides-bff`、`internal/biz`、`internal/data`、`internal/observability`、`internal/server` 全部通过 |
| `go vet ./...` | PASS | 无输出 |
| `go build ./cmd/fides-bff` | PASS | 构建成功；验证产物 `apps/fides-bff/fides-bff` 已删除 |

## Test-First Evidence

新增 pricing facade 测试后，生产代码尚未实现时失败：

```text
undefined: service.NewPricingService
undefined: biz.NewPricingUsecase
too many arguments in call to NewHTTPServer
undefined: biz.QuoteResult
undefined: biz.PricingError
```

失败原因符合预期：pricing facade 的 usecase、service、client 和 server wiring 尚未实现。

## Coverage Notes

- `internal/server/http_test.go` 验证 BFF route/filter/error envelope 组合行为。
- `internal/data/quote_client_test.go` 验证真实 HTTP quote client 的 header 传播、422 映射、不可用映射和 Consul service URL 解析。
- `cmd/fides-bff/config_loader_test.go` 验证 `QUOTE_*` 环境变量进入 allowlist。

## Wire Note

`make generate` 未完成，原因是本机 `wire` 二进制使用 Go 1.25 source-processing 包，无法处理当前 Go 1.26 module：

```text
package requires newer Go version go1.26 (application built with go1.25)
```

处理方式：按现有 `wire_gen.go` 结构手工同步 DI 生成文件，并用 `go test ./...`、`go vet ./...`、`go build ./cmd/fides-bff` 验证结果。
