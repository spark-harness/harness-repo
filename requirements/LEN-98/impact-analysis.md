---
requirement_id: "LEN-98"
owner: "Codex"
status: "draft"
updated_at: "2026-06-24"
---

# Impact Analysis

## Summary

LEN-98 影响 IDL 生成配置、BFF HTTP 注册方式、FE adapter 依赖和新增 TS 生成契约仓。它不改变 OTP 业务规则，但会把 FE+BFF HTTP 契约从手写 fetch 和手写 route 推向 generated contract。

## Affected Services And Repos

| Repo | Impact |
|---|---|
| harness-repo | 新增 LEN-98 lifecycle artifacts、证据和门禁输入 |
| idl-repo | 新增 OpenAPI v3 生成配置、Kratos HTTP Go 生成配置、OpenAPI stale check |
| idl-openapi-repo | 新增独立 OpenAPI 生成物仓，目录跟随 `idl-repo` proto 路径 |
| gitops-repo | 发布 workflow 增加 OpenAPI sync、OpenAPI Generator TS 生成和 TS sync 顺序 |
| business-repo | `fides-bff` 改用 generated HTTP registration；`fides` adapter 改用 TS client |
| idl-ts-repo | 新增 TypeScript generated contract 仓与 fides-bff client 包 |

## Service Matrix Facts

- `fides`: `{business-repo}/services/frontend/fides`，不直接需要 protobuf。
- `fides-bff`: `{business-repo}/services/backend/fides-bff`，已有 BFF-facing proto 路径 `{idl-repo}/vesta/lendora/fides-bff/v1`。
- `applicant-api`: 仍是 OTP 业务权威，下游调用链不因 LEN-98 改变。

## Contract Impact

- Protobuf：不新增 RPC，不改变字段语义；生成配置新增 Kratos HTTP binding。
- HTTP / JSON：路径仍为：
  - `POST /api/v1/auth/otp:send`
  - `POST /api/v1/auth/otp:verify`
  - `POST /api/v1/auth/token:refresh`
- OpenAPI：新增 `idl-openapi-repo/vesta/lendora/fides-bff/v1/openapi.yaml`，从 proto HTTP annotation 派生。
- TypeScript：新增 `@spark-harness/idl-ts-client`，由 FE infrastructure adapter 包装。

## Generated Contract Impact

- Go：`idl-go-repo` 需要包含 `auth_http.pb.go`，BFF 才能调用 generated registration。
- OpenAPI：`idl-openapi-repo` 已创建私有远端，发布 workflow 先推送同名分支。
- TS：`idl-ts-repo` 已创建私有远端，`fides` 通过 Git tag `v0.1.0-len98.4` 消费。
- Java：不受影响。

## Runtime, Data, Config

- 不新增数据库、Redis key 或持久化迁移。
- `fides-bff` HTTP middleware、错误信封、trace 和 idempotency 继续复用 `bffkit`。
- `fides` 继续通过 `NEXT_PUBLIC_FIDES_BFF_BASE_URL` 和 adapter mode 选择真实 BFF。

## Observability And Security

- trace header 和 `Idempotency-Key` 由 FE wrapper 传入 TS client headers。
- 不记录 OTP code、完整手机号、access token、refresh token。
- generated client 只在 infrastructure 层使用，避免 UI 层直接接触底层 HTTP DTO。

## Rollout And Rollback

- Rollout 顺序：
  1. 合并/发布 `idl-repo` OpenAPI 与 Go HTTP generation。
  2. 发布 workflow 生成并推送 `idl-openapi-repo` 同名分支。
  3. 发布 workflow clone 已推送的 `idl-openapi-repo`，用固定 OpenAPI Generator 镜像生成并推送 `idl-ts-repo`。
  4. 更新 `fides-bff` 消费 formal `idl-go-repo` tag。
  5. 更新 `fides` 消费 `idl-ts-repo` Git tag。
- Rollback：
  - 可回退 `fides` adapter 到上一版本 generated client tag。
  - BFF route 语义保持同路径，生成注册失败时可回退到上一服务版本。

## Risks

| Risk | Mitigation |
|---|---|
| 私有 Go module 在 CI 中被 sumdb/proxy 拦截 | CI 设置 `GOPRIVATE=github.com/spark-harness/*` |
| `idl-go-repo` formal tag 未进入主发布节奏 | 当前使用 `v0.2.2-len98.1` 验证 tag；合并后按正式发布规则晋级 |
| OpenAPI v3 生成依赖本地插件可用性 | `buf.gen.openapi.yaml` 使用 Buf remote plugin `buf.build/community/google-gnostic-openapi`，避免依赖 runner 本地二进制 |
| TS 生成顺序绕过 OpenAPI 仓 | GitOps workflow 固化 `sync-openapi -> checkout-ts-inputs -> generate-ts -> sync-ts` 顺序 |
| generated client 和 FE 错误语义不一致 | FE infrastructure wrapper 保留裸 401/429、timeout 和 retry-after 映射测试 |

## Context Gaps

- `context/project` 当前没有 Lendora `fides` / `fides-bff` 服务级入口；本需求按服务矩阵和现有 LEN-43 资产定位。
