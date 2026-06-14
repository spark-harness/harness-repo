---
requirement_id: "LEN-31"
owner: "Claude"
status: "approved"
updated_at: "2026-06-14"
approved_by: "Forest"
approved_at: "2026-06-14T23:32:06+08:00"
decision: "设计已在会话中获批准（用户回复「批准，继续实现」），并明确新前端项目为 fides、采用完整 Next.js 应用外壳；可进入任务拆分。"
---

# Design

## Requirement Traceability

| Requirement Item | Design Decision | Notes |
|---|---|---|
| R0, AC5 | D0: 新建 `services/frontend/fides` Next 16 + TS + Tailwind v4 应用外壳，可 dev/build | 系统字体（不依赖 next/font/google），离线/CI build 稳定 |
| R1, AC5 | D1: `fides/src` 建 6 层根 `domain/application/adapters/infrastructure/presentation/api`，各含职责 README；保留 `src/app/` | 层优先布局；子域由后续票在层下创建 |
| R2, AC4 | D2: `.dependency-cruiser.cjs` 落 6 条 forbidden 规则，命名与 `frontend-clean-architecture.md` 一致 | 规则名即违规边界定位 |
| R2 | D3: 路径用「子域优先」正则，`anyDepth()` = `^src/(<层>/\|.+/<层>/)`（星高 1，过 safe-regex），等价指南 glob `src/**/<层>/` | `api` 用 `anyDepthOrApi()` 仅顶层 `src/api/`，不波及层内 `infrastructure/api/` |
| R2 | D4: `options.tsConfig` 指向 `tsconfig.json`，`tsPreCompilationDeps: true` | 解析 `@/` 别名并捕获 `import type` |
| R3, AC2 | D5: `package.json` 加 `lint:deps`（及 `dep:graph`）脚本，devDep `dependency-cruiser` | 一键本地运行 |
| R4, AC3 | D6: 空骨架 `pnpm lint:deps` 绿基线 | README 非 TS 模块，不产生违规 |
| R5, R6, AC1, AC2 | D7: 新增 `.github/workflows/fides-ci.yml`，路径过滤 `services/frontend/fides/**`，pin Node22/pnpm10，`--frozen-lockfile` → `lint:deps`，`permissions: contents: read` | business-repo 首个 CI |
| R5, AC1 | D8: 红线验证——临时注入违规、确认非零退出+规则名、删除，输出证据 | 不提交违规代码 |
| R7 | D9: 服务矩阵新增 fides；requirement/impact/design/tasks/gates/evidence 互引，Janus 校验 | 全链路可追溯 |

## Summary

在新建前端应用 `fides` 中立 Clean Architecture 分层骨架与 `dependency-cruiser` 静态门禁，并接入 CI。它不是业务功能，唯一「行为」是构建期门禁：空骨架绿、跨层违规红、CI 阻断合并；应用外壳可 dev/build。现有 `aegis` 不改。

先说不是什么：本设计不替业务屏决定子域目录，也不实现端口/用例/控制器/基础设施（属 LEN-4 其它子任务）。它交付「fides 应用外壳 + 分层边界 + 可阻断门禁 + 一键/CI 运行」。

## Affected Services

| Service | Change | Reason |
|---|---|---|
| fides（新增） | 新建 Next.js 应用外壳 + 6 层骨架 + `.dependency-cruiser.cjs` + 脚本/依赖 + CI；服务矩阵新增条目 | 建立前端结构与门禁地基 |
| aegis | 无改动 | 仅存在性参照 |

## App Shell Design（D0）

`services/frontend/fides` 采用与 aegis 相同技术栈（Next 16.2.6 / React 19.2.4 / TS strict / Tailwind v4 / pnpm），独立 `pnpm-workspace.yaml`。文件：`package.json`、`tsconfig.json`（别名 `@/* → ./src/*`，`moduleResolution: bundler`）、`next.config.ts`、`eslint.config.mjs`、`postcss.config.mjs`、`.gitignore`、`src/app/{layout.tsx,page.tsx,globals.css}`、`README.md`。

外壳采用系统字体（Tailwind `--font-sans`），**不引入 `next/font/google`**，以保证离线/CI `pnpm build` 稳定。`pnpm build` 本地已通过（Next 16 Turbopack，TS 校验通过，静态页生成）。

## Layer & Dependency Design

依赖方向（外→内）：`app/ + presentation → adapters → application → domain`；`infrastructure → application/domain 端口`；`src/api`（最外）向内编排，内层不得依赖它。

```text
src/
├── app/             # 现有 Next.js 入口（presentation 最外，允许 React）
├── presentation/    # React 屏/组件/hooks/样式（允许 React），只经 adapters
├── adapters/        # controller / presenter / mapper（无 React、无真实 I/O）
├── application/     # use case / command / query / port
├── domain/          # 实体 / 值对象 / 规则 / 错误（no-react）
├── infrastructure/  # HTTP / repository / gateway / storage（实现 port，不依赖 presentation）
└── api/             # Server Actions / 路由处理器（最外代理；内层不可依赖）
```

每层根放职责 `README.md`（文档化允许/禁止依赖），使层目录为文档而非空壳（符合团队 SSOT），无需 `.gitkeep`。

## Dependency-Cruiser Rule Design

`.dependency-cruiser.cjs`（CommonJS），`forbidden` 六条 `severity: error`。路径正则用助手避免嵌套量词以通过 safe-regex：

- `anyDepth(layers)` = `^src/((L)/|.+/(L)/)` —— 层在 src 下任意深度（含零段=裸层根）。
- `anyDepthOrApi(layers)` = `^src/((L)/|.+/(L)/|api/)` —— 额外把**顶层** `src/api/` 纳入禁止目标。

| 规则名 | from | 禁止 to |
|---|---|---|
| `domain-cannot-depend-on-outer` | `anyDepth(domain)` | `anyDepthOrApi(application,adapters,infrastructure,presentation)` |
| `application-cannot-depend-on-outer` | `anyDepth(application)` | `anyDepthOrApi(adapters,infrastructure,presentation)` |
| `adapters-cannot-depend-on-outer` | `anyDepth(adapters)` | `anyDepthOrApi(infrastructure,presentation)` |
| `infrastructure-cannot-depend-on-presentation` | `anyDepth(infrastructure)` | presentation 任意深度 或 `src/app/` |
| `presentation-cannot-depend-on-use-cases-or-repos` | presentation 任意深度 或 `src/app/` | `anyDepth(application,infrastructure)` |
| `no-react-in-core` | `anyDepth(domain,application,adapters,infrastructure)` | 解析到 `node_modules/react(-dom)?/` 的依赖 |

`options`: `tsConfig: { fileName: "tsconfig.json" }`、`tsPreCompilationDeps: true`、`doNotFollow: { path: "node_modules" }`、`enhancedResolveOptions`（解析 exports/别名）。
要点：`app/` 纳入 presentation 规则但豁免 `no-react-in-core`；`src/api` 仅顶层作为内三层禁止 to、自身无 from 限制（composition root）；react 解析正则在 pnpm 嵌套下仍命中。

## CI Design

`business-repo/.github/workflows/fides-ci.yml`：`push`/`pull_request` 且 `paths: services/frontend/fides/**`；`permissions: contents: read`；ubuntu-latest，`working-directory: services/frontend/fides`；checkout → pnpm/action-setup(10) → setup-node(22, cache pnpm) → `pnpm install --frozen-lockfile` → `pnpm lint:deps`。违规即步骤失败、阻断合并。

## Data / Config / Permission

- Data model: 无。
- Config: 新增 fides 整套工程文件、`.dependency-cruiser.cjs`、CI 工作流、服务矩阵 fides 条目。
- Permission: CI `contents: read`。

## Observability

- 无运行时遥测。门禁可观测性体现在 `pnpm lint:deps` 退出码与 CI 步骤状态。

## Testing Strategy

无业务逻辑，不写单元/集成测试。验证以行为为准：
1. 应用外壳：`pnpm build` 成功（AC5）。
2. 绿基线：空骨架 `pnpm lint:deps` 退出 0、无违规（AC3）。
3. 红线（AC1，test-first）：临时注入 `domain→infrastructure`、`core→react` 违规，确认非零退出 + 规则名 + 文件，删除后复绿；输出捕获到 `evidence/lint-deps-redline.md`。
4. CI（AC2）：工作流在 PR 运行 `lint:deps`。

## Rollout And Rollback

- Gray release: 不适用（构建期门禁）。
- Kill switch: 误报时临时禁用 CI 步骤或加显式记录的例外规则。
- Rollback: 删除 `services/frontend/fides/`、CI 工作流、服务矩阵 fides 条目即可完全回退；aegis 不受影响。

## Risks

| Risk | Mitigation | Owner |
|---|---|---|
| tsConfig/别名未解析致 `@/` 漏判 | `options.tsConfig` + `tsPreCompilationDeps`，红线测试确认 | Claude |
| react 解析正则 pnpm 嵌套漏命中 | `node_modules/react(-dom)?/` 段匹配，红线强制验证 | Claude |
| 首个 CI 版本漂移假失败 | pin Node22/pnpm10 + `--frozen-lockfile` | Claude |
| 在线字体致 build 不稳 | 系统字体、不引入 next/font/google；本地 build 已通过 | Claude |
