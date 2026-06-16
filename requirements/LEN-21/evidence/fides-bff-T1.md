# LEN-21 T1 — fides-bff 骨架与健康检查证据

## Context

- Requirement: `LEN-21`
- Task: `T1`（fides-bff 可运行 Kratos 骨架 + 健康检查 + CI + 服务矩阵登记）
- Service: `fides-bff`
- Working directory: `business-repo/services/backend/fides-bff`
- Branch: `feature/fides-bff/LEN-21`（harness-repo 与 business-repo 一致）
- Checked at: `2026-06-16T10:30:00+08:00`
- Toolchain: Go 1.26.2（go.mod 声明 go 1.24）、Kratos v2.9.2、wire v0.7.0、golangci-lint v2.11.4

## Commands & Results

```bash
gofmt -l .                 # 输出为空 → 格式干净
go vet ./...               # ok
go test ./... -count=1     # 见下
golangci-lint run ./...    # 0 issues
make build                 # go build -ldflags "-X main.Version=$(git describe ...)" -o bin/fides-bff ./cmd/fides-bff
```

测试结果：

```text
ok   github.com/spark/fides-bff/internal/biz      (PASS)
ok   github.com/spark/fides-bff/internal/server   (PASS)
?    github.com/spark/fides-bff/internal/conf      [no test files]
?    github.com/spark/fides-bff/internal/service   [no test files]
?    github.com/spark/fides-bff/cmd/fides-bff       [no test files]
```

- gofmt：clean
- go vet：PASS
- go test：2 个测试包 PASS，0 失败
- golangci-lint：0 issues
- go mod tidy：no drift
- 内层包 wire 隔离校验：`grep -rl google/wire internal/` 无匹配（biz/service/server 不依赖 DI 框架）

## 运行时冒烟（AC1 / AC5）

```bash
make run            # go run -ldflags "-X main.Version=..." ./cmd/fides-bff -conf configs/config.yaml
curl -s localhost:8000/api/v1/health
```

输出：

```text
INFO service.name=fides-bff service.version=v0-t1-test msg=[HTTP] server listening on: [::]:8000
{"status":"ok","version":"v0-t1-test"}      # HTTP 200
INFO service.name=fides-bff service.version=v0-t1-test msg=[HTTP] server stopping
```

- 未知路由 `GET /api/v1/nope` → HTTP 404（路由仅挂载已声明端点）。
- 优雅停机：收到信号后 Kratos `server stopping` 正常退出。

## 验收标准覆盖

| AC | 说明 | 证据 |
|---|---|---|
| AC1 | `GET /api/v1/health` 返回成功 + 健康/版本信息 | `curl` 返回 `{"status":"ok","version":...}` HTTP 200；`internal/server/http_test.go` 断言 200 + JSON + 注入版本 |
| AC5 | 本地一键启动 + 健康检查 + CI 跑通 lint+test | `make run` 一键启动并 curl 通过；`make test`/`make lint` 全绿；`.github/workflows/fides-bff-ci.yml` 配置 gofmt/vet/build/test + golangci-lint |

> AC2/AC3/AC4/AC6（错误信封 / 幂等 / 可观测 / gRPC 映射）属 T2–T4，不在本切片。

## 测试清单

- `internal/biz/health_test.go::TestHealthUsecase_Check_reportsOkWithInjectedVersion` — 注入 version 透传、status=ok（单元，AAA）。
- `internal/server/http_test.go::TestHTTPServer_Health_returnsStatusAndVersion` — GET /api/v1/health → 200 + JSON，验证 /api/v1 前缀挂载（适配层集成）。

测试先行记录：先写上述测试，server 未挂载路由时 `http_test` 以 404 失败（红），挂载路由后转绿。

## 关联

- 代码审查报告：`requirements/LEN-21/reviews/T1.md`（结论 ready-for-gate，无未关闭 P0/P1）。
- 服务矩阵登记：`.service-matrix/dependencies.yaml` 新增 `fides-bff`。
- CI：`business-repo/.github/workflows/fides-bff-ci.yml`（GitHub Actions 实际执行待首个 PR 触发确认）。
