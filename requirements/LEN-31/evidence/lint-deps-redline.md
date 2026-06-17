# LEN-31 fides 构建 + lint:deps 绿基线/红线证据

## Context

- Requirement: `LEN-31`
- Checked at: `2026-06-14T23:32:06+08:00`
- Service: `fides`（新建）
- Working directory: `business-repo/services/frontend/fides`（worktree `.worktrees/feature-LEN-31-fe-clean-arch-scaffold/`）
- Branch: `feature/LEN-31-fe-clean-arch-scaffold`
- Tool: `dependency-cruiser 17.4.3`，命令 `pnpm lint:deps`（= `depcruise src`）

## 1. 应用外壳构建（AC5）

```bash
pnpm build
```

```text
▲ Next.js 16.2.6 (Turbopack)
✓ Compiled successfully in 1169ms
  Running TypeScript ... Finished
✓ Generating static pages (3/3)
Route (app):  ○ /   ○ /_not-found
exit code 0
```

结论：fides 应用外壳可生产构建（系统字体，无 next/font/google 在线依赖）。

## 2. 绿基线（AC3）

空骨架（6 层根仅含 README + app 外壳）运行：

```text
✔ no dependency violations found (4 modules, 2 dependencies cruised)
exit code 0
```

## 3. 红线（AC1 / 父票 AC6）

临时注入违规文件（验证后已删除，未提交）：

- `src/infrastructure/__redline_target__.ts`：干净目标。
- `src/domain/__redline_outer__.ts`：`import "@/infrastructure/__redline_target__"` —— domain 依赖 infrastructure。
- `src/domain/__redline_react__.ts`：`import { useMemo } from "react"` —— core 层 import react。

```text
  error no-react-in-core: src/domain/__redline_react__.ts → node_modules/.pnpm/react@19.2.4/node_modules/react/index.js
  error domain-cannot-depend-on-outer: src/domain/__redline_outer__.ts → src/infrastructure/__redline_target__.ts
x 2 dependency violations (2 errors, 0 warnings). 8 modules, 4 dependencies cruised.
exit code 2
```

结论：

- 门禁以非零退出码失败，逐条打印**规则名 + 违规文件路径 + 目标**，满足 AC1 / 父票 AC6。
- `@/` 路径别名经 `tsConfig` 正确解析。
- `no-react-in-core` 在 pnpm 嵌套 `node_modules/.pnpm/react@.../node_modules/react/` 下仍正确命中。

## 4. 复位

删除临时文件并清理 `.next` 构建产物后重新运行 `pnpm lint:deps` → 绿；`git status` 确认无红线/`.next`/`node_modules` 残留入库（均 gitignore）。
