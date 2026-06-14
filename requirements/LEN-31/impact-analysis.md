---
requirement_id: "LEN-31"
analyst: "Claude"
status: "approved"
updated_at: "2026-06-14"
approved_by: "Forest"
approved_at: "2026-06-14T23:32:06+08:00"
decision: "影响分析随需求一并进入评审；目标服务为新建 fides，不影响 aegis 与任何契约。"
idl_impact: "no"
idl_impact_reason: "fides 服务 idl_required=false，本票仅前端结构与静态门禁，不涉及任何 protobuf/外部契约。"
---

# Impact Analysis

## Summary

新建前端独立应用 `fides`（Next.js 16 + TS + Tailwind v4 应用外壳）于 `business-repo/services/frontend/fides`，并在其中加入 Clean Architecture 分层骨架、`.dependency-cruiser.cjs` 静态门禁、`pnpm lint:deps` 脚本与 CI；在服务矩阵新增 fides 条目。纯结构与质量门，零业务逻辑、零运行时行为变化、零契约影响；现有 `aegis` 不改。

## Affected Domains

- `frontend`（module）：前端体验地基。本票新建 fides 应用并立结构与门禁，不触碰任何业务子域。

## Affected Services

| Service | Repo | Reason | Protobuf Required |
|---|---|---|---|
| fides（新增） | business-repo (`services/frontend/fides`) | 新建 Next.js 应用外壳 + 分层骨架 + dependency-cruiser 门禁 + lint:deps + CI | No (`idl_required: false`) |
| aegis | business-repo (`services/frontend/aegis`) | 不改（仅作存在性参照） | No |
| —（harness-repo） | harness-repo | 服务矩阵新增 fides + 需求生命周期产物 | No |

## Upstream / Downstream Consumers

- 服务矩阵 `dependencies.user-api.upstream` 含 aegis；本票不改 user-api 及任何 aegis↔user-api 调用/契约/运行时，**对 user-api 与 aegis 零影响**。
- fides 暂不声明对 user-api 的依赖（本票不建立调用）；后续屏票按需补充。
- 下游：fides 的目录骨架与门禁是 LEN-23/24/25 及前端屏票 LEN-11/16/18/20 的前置赋能，属结构性非破坏变更。

## API / Contract Impact

- Does this change involve protobuf IDL or external contracts: **No**。
- Contract repo / Proto files / Buf module: 不适用。
- Buf config version: v2（不涉及）。
- Required buf checks: 不适用。
- Breaking baseline / Compatibility risk: 无契约兼容性风险。

## Data Impact

- Database schema / migration / backfill / cache: 无。
- 运行时存储：无（不引入 localStorage/IndexedDB/cookie 等）。

## Config / Permission / Observability Impact

- Config: 新增 `fides/` 整套工程文件（package.json、tsconfig、next/eslint/postcss 配置、`.dependency-cruiser.cjs`、`pnpm-lock.yaml`、app 外壳、层 README）；新增 CI 工作流 `.github/workflows/fides-ci.yml`；服务矩阵新增 fides 条目。
- Permission: CI 工作流声明 `permissions: contents: read`（最小权限）。
- Metrics / Logs / Tracing / Events: 无运行时遥测；门禁结果体现在 CI 状态与 `pnpm lint:deps` 退出码。

## Rollout And Rollback

- Gray release: 不适用（构建期门禁，无运行时灰度）。
- Kill switch: 误报阻断时可临时在 CI 关闭该步骤或在 `.dependency-cruiser.cjs` 加显式记录的例外规则（附原因与移除计划）。
- Rollback steps: 删除 `services/frontend/fides/`、CI 工作流与服务矩阵 fides 条目即可完全回退；无数据/契约残留，aegis 不受影响。

## Risks

| Risk | Impact | Mitigation | Owner |
|---|---|---|---|
| dependency-cruiser 别名/tsConfig 未解析导致 `@/` import 漏判 | 门禁漏报 | 配置 `options.tsConfig` + `tsPreCompilationDeps`，红线证据确认拦截生效 | Claude |
| `no-react-in-core` react 解析在 pnpm 嵌套下匹配不到 | 漏报 | 用 `node_modules/react(-dom)?/` 段匹配；红线测试强制验证命中 | Claude |
| fides 首个前端 CI 的 pnpm/Node 版本漂移 | CI 假失败 | pin Node 22 + pnpm 10，`--frozen-lockfile`，PR 验证绿基线 | Claude |
| 应用外壳引入 next/font 在线字体导致 build 不稳 | 离线/CI build 失败 | fides 外壳采用系统字体，不依赖 next/font/google；本地 `pnpm build` 已通过 | Claude |
