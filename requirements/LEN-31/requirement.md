---
requirement_id: "LEN-31"
owner: "Claude"
status: "approved"
created_at: "2026-06-14"
related_branch: "feature/LEN-31-fe-clean-arch-scaffold"
approved_by: "Forest"
approved_at: "2026-06-14T23:32:06+08:00"
decision: "Requirement Brief 已在会话中批准；用户进一步明确新前端项目为 fides（非修改 aegis）、采用完整 Next.js 应用外壳，可创建需求文档并实现。"
---

# [FE] Clean Architecture 脚手架 + dependency-cruiser 门禁 Requirement

## Background

Spark 申请漏斗各前端屏（LEN-2/5/6/7/8 等）需要一套遵循 Clean Architecture、由静态门禁守护的前端工程地基。本票新建前端独立应用 **fides**（Next.js App Router），在其中立「所有屏共享的分层边界与依赖纪律」，并用 `dependency-cruiser` 把边界变成可在 CI 阻断合并的红线。

先说不是什么：本票不是实现某个业务屏，也不是修改现有 `aegis` 应用（aegis 保持不动）。它是一张地基票（enabler）：建 fides 应用外壳 + 分层结构 + 静态门禁，后续屏票在此红线之上填充各自子域代码。

## Goals

- R0: 新建 fides 应用外壳（`business-repo/services/frontend/fides`，Next.js 16 + TS + Tailwind v4），可 `pnpm dev` / `pnpm build`。
- R1: 在 `fides/src` 建立 Clean Architecture 分层骨架：`domain / application / adapters / infrastructure / presentation` 五层 + 最外 `src/api`，保留 `src/app/`。
- R2: 落地 `.dependency-cruiser.cjs`，表达团队 `frontend-clean-architecture.md` 与 `clean-architecture-guide.md` §1–§4 的六条强制规则，并能解析 `@/` 路径别名。
- R3: 提供 `pnpm lint:deps` 脚本（扫描 `src/`），可一键本地运行。
- R4: 空骨架运行 `pnpm lint:deps` 通过（绿）。
- R5: 任意层违反依赖方向时，`pnpm lint:deps` 失败并指出违规规则名与文件（红）。
- R6: 将 `pnpm lint:deps` 接入 CI，违规即 CI 失败、阻断合并。
- R7: 在服务矩阵新增 fides；需求、影响分析、设计、任务、门禁与证据可互相追溯。

## Non-Goals

- 不实现任何业务屏或业务逻辑（→ LEN-11/16/18/20 等屏票）。
- 不修改现有 `aegis` 应用。
- 不实现令牌 SSOT、端口/基础设施实现、用例、草稿续填、PII 脱敏（属 LEN-4 其它子任务）。
- 不发明业务子域名（如 kyc / origination）；子域目录由后续屏票按需创建。
- 不涉及 protobuf IDL、生成契约、后端代码或代码生成。

## User / Business Scenarios

### Scenario 1：应用外壳可构建 + 空骨架跑通门禁

Given: fides 应用外壳与五层 + `src/api` 骨架（各层仅 README/占位）、`.dependency-cruiser.cjs`、`lint:deps` 就位。

When: 开发者运行 `pnpm build` 与 `pnpm lint:deps`。

Then: 构建成功；`lint:deps` 退出码 0、无依赖违规，作为后续票绿基线。

### Scenario 2：违规被门禁拦截（红线）

Given: 某文件违反依赖方向，例如 `src/domain/**` import `src/infrastructure/**`，或核心层 `import ... from "react"`。

When: 开发者运行 `pnpm lint:deps`。

Then: 命令以非零退出码失败，输出命中的规则名（如 `domain-cannot-depend-on-outer` / `no-react-in-core`）与违规文件路径。

### Scenario 3：CI 阻断合并

Given: 一个含跨层违规的改动被推送触发 CI。

When: CI 运行 `pnpm lint:deps`。

Then: CI 步骤失败、阻断合并；修复违规后 CI 通过。

## Business Rules

- 依赖只向内：`domain → application → adapters` 不依赖更外层；`infrastructure` 不依赖 `presentation`；`presentation` 不直接依赖 use case / repository（只经 `adapters` 控制器）。
- `no-react-in-core`：`domain / application / adapters / infrastructure` 禁止 `import react`；React 只允许出现在 `presentation/` 与 `app/`。
- `src/api` 与生成 API client 视为基础设施/最外细节，业务核心、应用层、适配层不得直接依赖（顶层 `src/api`）。
- 规则路径采用「子域优先」glob 语义（`src/**/<层>/`），既治理裸层根目录、又向后兼容子域嵌套。
- 例外（dependency-cruiser ignore）不作为默认修复手段；如需例外必须记录原因与移除计划。

## Acceptance Criteria

- AC1（承接 LEN-4 AC6）：任意层违反依赖方向，运行 `pnpm lint:deps` 门禁失败并指出违规规则名与文件范围。
- AC2（承接 LEN-4 AC5）：CI 包含 `lint:deps` 步骤，且本地可一键 `pnpm lint:deps` 运行。
- AC3：空骨架运行 `pnpm lint:deps` 通过（绿基线）。
- AC4：`.dependency-cruiser.cjs` 规则集覆盖 §1–§4 / `frontend-clean-architecture.md` 的六条强制规则，规则名可定位违规边界。
- AC5：fides 应用外壳可 `pnpm build`；分层骨架含 `domain / application / adapters / infrastructure / presentation / api`，各层有职责 README，保留 `src/app/`。

## Open Questions

| Question | Owner | Deadline | Status |
|---|---|---|---|
| 根 `clean-architecture-guide.md` 示例 glob（子域优先）与票/父票正文（层优先）措辞不一致，已用正则统一，是否在 self-refinement 对齐指南文字 | Claude | 交付阶段 | 待定（非阻塞） |
| 前端项目上下文 `context/project/spark/frontend/fides/INDEX.md` 缺失，是否在交付时沉淀 | Claude | 交付阶段 | 待定（非阻塞） |

## Notes

- 包管理器 pnpm 10.25；fides 别名 `@/* → ./src/*`，`moduleResolution: bundler`，dependency-cruiser 接 `tsConfig` 解析别名。
- 团队 SSOT 反对「为形式强行拆空层目录」；本票用「层根 + 职责 README」使其为文档而非空壳，且其门禁红线对后续票有实际价值。
- 在工作区级 git worktree 内开发，避免污染主检出。business-repo 首个前端 CI 工作流随本票新建。
