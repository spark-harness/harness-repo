# TypeScript 工程规范

本文适用于 Spark/Lendora TypeScript 前端、BFF 和共享包。

它不是框架教程，也不规定具体页面设计。跨项目规则写在这里；应用级例外写到 `context/project/`。

## 最小规则

| 主题 | 规则 |
|---|---|
| 包管理 | 使用仓库声明的包管理器和 lockfile，不混用 npm、yarn、pnpm |
| 类型 | 新代码不得主动引入 `any`；需要逃逸时必须把边界缩小并说明原因 |
| 分层 | UI、application、domain、infrastructure 边界要清楚 |
| API | 页面和业务逻辑不直接调用生成 client，必须经过 adapter 或 gateway |
| 状态 | 服务端状态、表单状态、UI 状态分开管理 |
| 错误 | 用户可见错误用稳定错误语义，不展示原始异常或后端敏感信息 |
| 环境变量 | 客户端可见变量必须有显式前缀和说明，secret 不得进前端 bundle |
| 格式 | 使用项目既有 lint、format、typecheck 命令 |

## 目录分层

推荐应用内采用：

```text
src/app/ or src/pages/      # 路由和页面入口
src/features/               # 业务功能组合
src/entities/ or src/domain/ # 领域类型和规则
src/shared/                 # 共享 UI、工具、基础设施
src/infrastructure/         # API adapter、生成 client 包装、storage
```

不要让页面组件直接持有请求拼装、错误码映射、重试和鉴权细节。

## API Client 边界

- 生成 OpenAPI client 属于 infrastructure。
- application 或 feature 层只能依赖团队定义的 adapter 接口。
- adapter 负责：请求头、幂等键、错误映射、响应归一化、超时和重试策略。
- 不把生成 client 的类型扩散到 UI 组件。

## UI 和状态

- Loading、empty、error、success 状态必须显式处理。
- 表单校验错误要靠近字段展示；全局失败使用稳定错误文案。
- 异步提交必须防重复点击或重复请求。
- 页面不可依赖 console log 作为用户反馈。

## 测试

| 场景 | 测试方式 |
|---|---|
| 纯函数、状态转换、格式化 | 单元测试 |
| 组件交互、表单校验 | component test |
| API adapter 错误映射 | 单元或集成测试 |
| 关键业务路径 | e2e 或端到端冒烟 |

测试原则遵守 `testing.md`：验证用户可见行为和业务结果，不锁死内部实现。

## 合并前检查

优先运行项目声明的命令，例如：

```bash
pnpm lint
pnpm typecheck
pnpm test
pnpm build
```

实际命令以应用 README、package scripts 或 CI 为准。
