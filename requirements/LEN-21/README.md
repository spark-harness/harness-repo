# LEN-21

为 Lendora MVP 起前端 BFF 服务 `fides-bff`：对前端 `fides` 暴露 REST `/api/v1` 并落地全局 API 约定（错误信封 / 幂等 / 校验 / 可观测 / 健康检查），对内以 gRPC 调用领域服务。

## 状态

- 当前阶段：阶段 1/2 需求定义。
- 当前结论：需求 Brief 已批准（Go/Kratos BFF、前端 `fides`、requirement-id `LEN-21`）；正在产出 `requirement.md` / `impact-analysis.md`。`requirement-review` 门禁待二者就绪并获批后生成。

## 产物

- `requirement.md`
- `impact-analysis.md`
- `design.md`（阶段 3）
- `tasks.json`（阶段 4.1）
- `gates/*.gate.json` / `gates/*.md`
- `evidence/`

## 关联

- JIRA：子任务 `LEN-21`（父 Story `LEN-3` / Epic `LEN-1`）。
- 兄弟需求：`LEN-22`（会话与越权中间件，独立需求，串行在后）。
- 分支：`feature/fides-bff/LEN-21`（harness-repo + business-repo 同名）。
- 服务：`fides-bff`（`business-repo/services/backend/fides-bff`，待登记进 `.service-matrix`）。

## 任务优先级

- 最优先 task = T1：`fides-bff` 可运行骨架（工程初始化 + `/api/v1` + 健康检查 + 本地一键跑 + CI）。它不依赖下游 gRPC/proto，是其余横切 task 的挂载点。
