# LEN-130 Local Verification Evidence

检查时间：2026-06-27T19:26:12+08:00

## 范围

本次验证覆盖：

- `business-repo/apps/fides-web`
- `gitops-repo/apps/fides`
- `harness-repo/requirements/LEN-130`

本次未修改：

- `fides-bff` API
- protobuf / IDL
- generated contract repo
- 后端服务代码

## 已执行检查

| 检查 | 命令 | 结果 |
|---|---|---|
| Test-first 失败确认 | `pnpm test -- src/infrastructure/runtime-config/runtime-config.test.ts src/api/mobile-verification/create-mobile-verification-controller.test.ts src/infrastructure/observability/browser-tracing.test.ts` | FAIL，runtime config 模块不存在、OTP controller 忽略 public config、tracing 未使用 runtime config |
| fides 单元和组件测试 | `pnpm test` | PASS，13 files passed，56 tests passed，1 skipped |
| Clean Architecture 依赖门禁 | `pnpm lint:deps` | PASS，48 modules / 85 dependencies no violations |
| ESLint | `pnpm lint` | PASS with existing warning in `mock-otp-auth-gateway.ts` unused `_command` |
| Next build | `pnpm build` | PASS，`/` 和 `/api/runtime-config` 均为 dynamic route |
| GitOps render | `kustomize build apps/fides/overlays/lendora-sta` or `kubectl kustomize ...` | PASS，输出包含 `FIDES_RUNTIME_*`、`FIDES_OTP_ADAPTER`、`FIDES_BFF_BASE_URL` |
| GitOps legacy variable scan | `rg -n "NEXT_PUBLIC_FIDES|NEXT_PUBLIC_OTEL" apps/fides` | PASS，无旧变量 |
| fides legacy build variable scan | `rg -n "ARG NEXT_PUBLIC|ENV NEXT_PUBLIC|NEXT_PUBLIC_FIDES|NEXT_PUBLIC_OTEL" Dockerfile README.md src` | PASS，Dockerfile 无旧构建变量；源码仅保留旧变量检测和测试 |

## 验收对应

| AC | 证据 |
|---|---|
| AC1 | `MobileVerificationScreen` 从 server-provided public runtime config 创建 OTP controller；GitOps 配置 `FIDES_OTP_ADAPTER=real` 和 `FIDES_BFF_BASE_URL=/api/v1` |
| AC2 | `runtime-config.test.ts` 覆盖 Consul JSON + env override，env 覆盖 Consul |
| AC3 | `runtime-config.test.ts` 覆盖旧 `NEXT_PUBLIC_*` 检测失败；GitOps 已移除旧变量 |
| AC4 | `browser-tracing.test.ts` 和 `rest-otp-auth-gateway.test.ts` 覆盖 tracing 初始化失败或 endpoint 为空时请求继续 |
| AC5 | `browser-tracing.test.ts` 覆盖 endpoint/header 从 runtime public config 初始化 exporter |
| AC6 | `runtime-config.test.ts` 覆盖 public config 白名单，不暴露 `environment` 和 `internal` |
| AC7 | `Dockerfile` 移除 `ARG/ENV NEXT_PUBLIC_*`；`pnpm build` 不需要 OTP/BFF/tracing 环境差异变量 |

## 审查结论

- 实现与 LEN-130 需求、影响分析、设计和任务追溯一致。
- `fides` 镜像构建不再依赖环境差异 public 变量。
- 浏览器只消费 public runtime config，不直接读取运行时环境变量。
- GitOps 部署配置不再注入旧 `NEXT_PUBLIC_*`。
- IDL 影响为 No。
