# 本地开发规范

本文定义本地启动、调试和验证的第一版团队约定。

它不是每个服务的 README。服务自己的启动细节、端口和依赖写到服务目录或 `context/project/`。

## 最小规则

| 主题 | 规则 |
|---|---|
| 命令来源 | 优先使用仓库 README、Makefile、package scripts 或服务上下文 |
| 配置 | 本地配置不得提交真实 secret |
| 依赖 | 数据库、缓存、消息队列等依赖必须有本地或测试替代说明 |
| 验证 | 修改前后记录实际运行的最小验证命令 |
| 环境差异 | 本地 mock、stub、fake 和真实环境差异必须写清 |
| 清理 | 不提交本地缓存、生成临时文件、IDE 配置和日志 |

## 开始修改前

```bash
git status --short --branch
```

确认：

- 当前仓库和分支正确。
- 没有无关脏改动混入。
- 当前 ticket 的 worktree 已隔离。
- 需要的服务上下文和语言规范已读取。

## 本地配置

- 使用 `.env.example`、README 或服务上下文说明变量。
- `.env`、token、证书、Cookie、私钥不得提交。
- 需要共享的配置只提交名称、用途和示例值，不提交真实值。

## 本地验证

按变更类型选择最小命令：

| 变更 | 常用验证 |
|---|---|
| Java | `mvn test` 或模块测试 |
| TypeScript | `pnpm lint`、`pnpm typecheck`、`pnpm test`、`pnpm build` |
| Go | `go test ./...`、`go vet ./...` |
| IDL | `buf lint`、`buf generate`、`buf breaking` |
| Harness 文档 | `janus gate validate`、`janus requirement status` 或 diff 检查 |

实际命令以项目配置为准，不要编造未运行结果。

## 调试记录

复杂问题应记录：

- 复现步骤。
- 实际错误。
- 已排除原因。
- 最小修复点。
- 后续需要沉淀到项目经验的位置。
