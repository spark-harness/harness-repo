---
requirement_id: "LEN-115"
owner: "forest"
status: "approved"
created_at: "2026-06-25"
related_branch: "feature/LEN-115-go-lint-depguard"
target_branch: "master"
release_branch: "master"
contract_gate_mode: "auto"
affected_repositories:
  - harness-repo
  - business-repo
approved_by: "forest"
approved_at: "2026-06-25T22:30:46+08:00"
decision: "用户已授权直接批准；批准 LEN-115 需求定义与影响分析，范围限定为 fides-bff golangci-lint 配置、日志 lint 和内部依赖方向约束，不涉及业务行为、前端、applicant-api 或 IDL。"
---

# fides-bff Go lint 与内部依赖方向约束

## Background

fides-bff 已经承担 BFF 编排、HTTP 适配、下游 applicant 契约调用、可观测性初始化等职责。随着 Kratos v3 和 `log/slog` 迁移风险增加，仅依赖默认 Go lint 无法约束结构化日志参数质量，也无法防止内部包依赖方向在后续迭代中反向污染。

它不是什么：本需求不是业务行为变更，不新增接口，不改变用户可见流程，也不修改 protobuf IDL。

它是什么：在 fides-bff 的 Go lint 配置中增强日志质量检查和内部包依赖方向约束，让依赖边界在本地和 CI lint 阶段可执行。

## Goals

- R1：在 `business-repo/apps/fides-bff/.golangci.yml` 启用 `loggercheck`，检查结构化日志 key/value 参数形状。
- R2：启用 `sloglint`，约束未来 `log/slog` 使用风格，降低 Kratos v3 迁移风险。
- R3：启用 `depguard`，覆盖 `internal/biz`、`internal/service`、`internal/data`、`internal/server` 的内部依赖方向。
- R4：保留 `cmd/fides-bff` 作为 composition root，允许依赖内部装配所需包。
- R5：新增 lint 规则不对当前代码产生误报，并能通过本地 lint 验证。

## Non-Goals

- 不修改 fides 前端。
- 不修改 applicant-api。
- 不修改 `idl-repo`、生成契约或 Buf 配置。
- 不改变 fides-bff 运行时业务行为、HTTP API、错误码、日志字段输出或配置语义。
- 不引入第一批高噪声风格规则，例如 `funlen`、`gocognit`、`lll`、`varnamelen`。
- 不通过宽泛 `//nolint` 绕过规则；如未来确需豁免，必须指定具体 linter 并说明原因。

## User / Business Scenarios

### Scenario 1：开发者提交结构化日志变更

Given：开发者在 fides-bff 中新增或修改结构化日志调用。

When：运行 `golangci-lint run ./...` 或 `make lint`。

Then：日志 key/value 参数成对和形状错误应在 lint 阶段暴露。

### Scenario 2：开发者引入 slog 调用

Given：开发者在 Kratos 迁移或新代码中使用 `log/slog`。

When：运行 fides-bff lint。

Then：不符合团队约束的 slog 使用风格应被 lint 阻止。

### Scenario 3：开发者误引入反向依赖

Given：开发者在 `internal/biz`、`internal/service`、`internal/data` 或 `internal/server` 中新增 import。

When：该 import 违反本需求列出的依赖方向。

Then：`depguard` 应在 lint 阶段报告违反的边界和原因。

## Business Rules

- BR1：`internal/biz` 不依赖 `data`、`service`、`server`、`observability`、`conf`、protobuf DTO、Kratos、gRPC、OTel。
- BR2：`internal/service` 不依赖 `data`、`server`、`observability`，且不直接依赖 applicant 下游契约。
- BR3：`internal/data` 不依赖 `service`、`server`。
- BR4：`internal/server` 不直接依赖 `data`。
- BR5：`cmd/fides-bff` 是 composition root，可依赖内部装配所需包。
- BR6：新增规则必须避免对当前代码产生误报。

## Acceptance Criteria

- AC1：`business-repo/apps/fides-bff/.golangci.yml` 启用 `loggercheck` 和 `sloglint`。
- AC2：`depguard` 规则覆盖 BR1-BR4 的内部依赖方向。
- AC3：未启用 `funlen`、`gocognit`、`lll`、`varnamelen`。
- AC4：未新增 `//nolint`；如未来需要豁免，必须指定具体 linter 并说明原因。
- AC5：`golangci-lint config verify` 通过。
- AC6：`golangci-lint run ./...` 通过。
- AC7：`make lint` 通过。
- AC8：变更只影响 `business-repo/apps/fides-bff/.golangci.yml` 和本需求 Harness 产物。

## Open Questions

| Question | Owner | Deadline | Status |
|---|---|---|---|
| 是否需要为 depguard 规则单独增加负向 fixture 测试 | Forest | 合并前 | 不需要；本任务按 Jira DoD 使用 golangci-lint 配置与 lint 命令验证 |

## Notes

- 用户已在 2026-06-25 明确授权补齐流程并直接批准 LEN-115。
