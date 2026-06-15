---
requirement_id: "LEN-31"
task_id: "T2,T3,T4,T5,T6"
reviewer: "code-review (traceability + security/error checkers, aggregated)"
base_revision: "business-repo@9298274 (master) / harness-repo@b63188d (master)"
diff_scope: "worktree feature-LEN-31-fe-clean-arch-scaffold (harness-repo + business-repo)"
conclusion: "ready-for-gate"
updated_at: "2026-06-14T23:32:06+08:00"
---

# Code Review Report

## Scope

- Repositories: `business-repo`（新建 fides + CI）、`harness-repo`（服务矩阵 + 生命周期）
- Base: `business-repo@9298274`、`harness-repo@b63188d`
- Changed files:
  - business-repo: `services/frontend/fides/**`（应用外壳 + 6 层 README + `.dependency-cruiser.cjs` + scripts/deps + lockfile）、`.github/workflows/fides-ci.yml`
  - harness-repo: `.service-matrix/dependencies.yaml`（新增 fides）、`requirements/LEN-31/**`
- Task IDs: T2（外壳）、T3（骨架）、T4（门禁+脚本）、T5（红线）、T6（CI）

## Findings

| Severity | Dimension | Location | Issue | Impact | Required Fix | Status |
|---|---|---|---|---|---|---|
| P3 | 安全 | `.github/workflows/fides-ci.yml` | actions 固定到主版本 tag（`@v4`）而非完整 commit SHA | 低；`@v4` 可变，上游被攻陷理论上可引入。本工作流仅 `contents: read`、无 secret，爆炸半径极小 | 可选：组织若强制 SHA pin 则改为 `@<40位 sha>`。`@v4` 已满足本票安全门槛，不阻塞 | open（建议） |

无 P0 / P1 / P2。

## Dimension Coverage

| Dimension | Checker | Result | Checked Scope |
|---|---|---|---|
| 追溯与范围 | traceability checker | no findings | fides 全部文件对 R0-R7/AC1-AC5/D0-D9/T1-T7；规则集对 §1-§4；aegis 未改、矩阵仅新增 fides；外壳 build 通过 |
| 契约兼容 | contract checker | skipped | 无 protobuf/HTTP/error-code/event/生成契约；`idl_required=false` |
| 数据与并发 | data/concurrency checker | skipped | 无数据/事务/并发/重试/幂等/运行时存储 |
| 安全与错误处理 | security/error checker | findings（1×P3 建议） | CI 工作流 + `.dependency-cruiser.cjs` + npm 脚本；**实测**门禁失败/通过判别正确、react 命中 pnpm 嵌套、safe-regex 通过 |
| 架构边界 | backend_architecture_reviewer | skipped | 非后端服务；前端边界由 dependency-cruiser 规则承载并经红线验证 |
| 测试价值与复杂度 | aggregation | no findings | build + 绿基线 + 红线证据齐备；config 复杂度低、helper 去重、无构建产物入库 |

skipped 原因均已说明。

## Tests Inspected

- `pnpm build` → exit 0（Next 16.2.6 Turbopack，TS 通过，静态页 3/3）（AC5）。
- `pnpm lint:deps` 绿基线 → `✔ no dependency violations`，exit 0（AC3）。
- `pnpm lint:deps` 红线（domain→infra、core→react）→ 规则名+文件，exit 2（AC1/父票 AC6）；pnpm 嵌套下 react 命中已验证。
- 安全 checker 实测门禁判别正确、safe-regex 通过、CI 最小权限与无注入。
- 证据：`evidence/lint-deps-redline.md`。

## Open Questions

- 指南 `clean-architecture-guide.md` glob 措辞（子域优先）与正则统一，留 self-refinement 对齐（requirement.md 已记录，非阻塞）。
- 前端项目上下文 `context/project/spark/frontend/fides/INDEX.md` 缺失，建议交付后沉淀（非阻塞）。
- 合并前确保 `services/frontend/fides/pnpm-lock.yaml` 一并提交（CI `--frozen-lockfile` 需要）。

## Residual Risk

- 低。构建期静态门禁，无运行时行为。`dep:graph` 依赖 `dot`（graphviz），仅可视化便利、非 CI 路径。
- 空层目录仅含 README（文档化职责），符合团队 SSOT「不为形式建空目录」意图。

## Conclusion

- `ready-for-gate`：无未关闭 P0/P1（唯一 P3 为可选 SHA-pin 加固建议）。

本报告不是门禁结论。阶段推进仍以 Janus 门禁 JSON 和人工审批为准。
