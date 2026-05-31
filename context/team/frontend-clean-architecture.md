# 前端干净架构规范

前端干净架构用于让业务规则、用例编排、接口适配和 UI 渲染保持清晰边界。

团队使用 Dependency Cruiser 静态检查依赖方向，防止业务核心被 React、HTTP client、生成 API、状态管理或页面结构反向污染。

## 它不是什么

前端干净架构不是把所有页面都拆成大量目录。

如果一个功能只是简单展示数据，强行拆出空的 `domain`、`application`、`adapters` 和 `infrastructure` 目录，只会增加阅读成本。团队要求的是依赖边界清楚，而不是目录数量越多越好。

前端干净架构也不是把业务逻辑藏进 React hook。

如果金额计算、状态流转、权限判断、提交前校验或错误语义都写在组件、hook、store 或 API client 里，即使目录名看起来正确，也没有形成可复用、可测试、可迁移的业务核心。

## 它是什么

前端干净架构是一组依赖规则和职责边界。

它要求团队区分：

- `domain`：表达业务概念、业务状态和业务规则。
- `application`：表达用例、命令、查询、编排和端口接口。
- `adapters`：把 UI 动作转换成应用用例输入，把应用结果转换成 UI 可用数据。
- `infrastructure`：实现 HTTP、生成 API client、存储、浏览器能力、第三方 SDK 等技术细节。
- `presentation`：实现 React 组件、页面、路由、交互和视觉状态。

核心目标不是让前端代码变复杂，而是让业务规则不依赖页面结构、React 生命周期、接口实现或某个状态管理库。

## 静态检查

前端项目必须通过 Dependency Cruiser 检查依赖边界。

推荐命令：

```bash
pnpm lint:deps
```

该命令应扫描 `src/` 目录，并根据 `.dependency-cruiser.cjs` 报告跨层依赖违规。

如果项目使用不同包管理器或目录结构，可以调整命令，但门禁必须保留同等语义：

- 检查对象覆盖前端源码。
- 规则名能定位违规边界。
- CI 中的失败结果能阻止合并。
- 例外必须显式记录原因和到期处理方式。

## 依赖方向

依赖必须从外向内。

推荐方向：

```text
presentation -> adapters -> application -> domain
infrastructure -> application/domain
bootstrap/composition -> presentation + adapters + infrastructure
```

允许外层依赖内层。禁止内层依赖外层。

| Layer | 可以依赖 | 禁止依赖 |
|---|---|---|
| domain | 语言标准库、稳定业务值对象 | application、adapters、infrastructure、presentation、`src/api`、React |
| application | domain、应用层本地类型、端口接口 | adapters、infrastructure、presentation、`src/api`、React |
| adapters | application、domain | infrastructure、presentation、`src/api`、React |
| infrastructure | application/domain 端口、技术 SDK、生成 API client | presentation、React 组件、页面状态 |
| presentation | adapters、UI 组件、React、路由、样式 | use case、repository、基础设施实现类 |

`src/api` 或生成 API client 应视为基础设施细节。业务核心、应用用例和适配层不应直接依赖它。

## 强制规则

Dependency Cruiser 配置必须至少表达以下规则。

### domain-cannot-depend-on-outer

`src/**/domain/` 禁止依赖 `application`、`adapters`、`infrastructure`、`presentation` 和 `src/api`。

原因：领域层保存业务实体、值对象和业务不变式。它不应知道数据如何获取、页面如何渲染、用例如何编排，也不应知道后端接口生成物。

### application-cannot-depend-on-outer

`src/**/application/` 只能依赖 `domain` 和应用层内部类型。

它禁止依赖 `adapters`、`infrastructure`、`presentation` 和 `src/api`。

原因：应用层负责编排用例。它可以定义端口接口，但不能知道端口由 HTTP、localStorage、IndexedDB、浏览器 API 或第三方 SDK 实现。

### adapters-cannot-depend-on-outer

`src/**/adapters/` 只能依赖 `application` 和 `domain`。

它禁止依赖 `infrastructure`、`presentation` 和 `src/api`。

原因：适配层负责控制器、presenter、view model mapper 等边界转换。它不实现真实 I/O，也不依赖 React 组件。

### infrastructure-cannot-depend-on-presentation

`src/**/infrastructure/` 禁止依赖 `src/**/presentation/`。

原因：基础设施实现端口接口，例如 repository、API gateway、storage gateway、feature flag gateway。它不应知道页面、组件、hook 或 UI state。

### presentation-cannot-depend-on-use-cases-or-repos

`src/**/presentation/` 禁止直接依赖 use case、repository、gateway 或基础设施实现类。

UI 应调用 `adapters` 层提供的 controller、presenter 或 view model 接口。

原因：页面和组件应表达交互与渲染，不应直接编排业务流程或绑定数据访问实现。

### no-react-in-core

`domain`、`application`、`adapters` 和 `infrastructure` 禁止 import React。

React 只允许出现在 `presentation` 层。

原因：React 是 UI 框架。业务规则、用例编排、边界转换和基础设施实现不应被 React 生命周期或 hook 规则绑定。

## 分层职责

### 领域层

适合放在领域层：

- 实体、值对象、领域枚举、领域错误。
- 金额、状态、权限、资格、库存、可见性等业务规则。
- 不依赖 UI 和接口的校验逻辑。
- 业务不变式，例如终态不可编辑、金额不能为负。

不应放在领域层：

- React component、hook、context、store。
- HTTP request、generated API type、GraphQL client。
- localStorage、sessionStorage、IndexedDB、cookie。
- 页面路由、文案、toast、modal、form library 细节。

### 应用层

适合放在应用层：

- 用例，例如 `SubmitOrderUseCase`、`LoadDashboardUseCase`。
- command、query、result。
- 调用领域对象完成业务判断。
- 定义 repository、gateway、clock、id generator 等端口接口。
- 处理用例级编排、错误语义和加载结果。

不应放在应用层：

- `fetch`、axios、generated API client 调用。
- React hook、component、context。
- DOM、router、toast、modal。
- 后端 DTO 到 UI 文案的展示细节。

### 适配层

适合放在适配层：

- controller：接收 UI 动作并调用应用用例。
- presenter：把应用结果转换成 UI 可消费的 view model。
- mapper：在应用结果和展示模型之间转换。
- 面向页面的 facade，但不包含 React 代码。

不应放在适配层：

- 真实 HTTP 调用。
- localStorage、browser API、第三方 SDK 调用。
- JSX、React hook、组件状态。
- 可复用的业务规则。

### 基础设施层

适合放在基础设施层：

- API client wrapper。
- repository、gateway、storage、feature flag、analytics 实现。
- generated API type 到 domain/application type 的转换。
- 浏览器能力和第三方 SDK 适配。

基础设施层必须实现 `application` 或 `domain` 定义的端口接口。业务层不应直接 import 基础设施实现类。

### 表现层

适合放在表现层：

- 页面、组件、路由、layout、form、hook、store。
- UI state，例如展开、选中、输入中、loading、toast、modal。
- 调用 adapter controller。
- 根据 view model 渲染内容。

不应放在表现层：

- 直接 new use case。
- 直接 import repository、gateway 或 API client。
- 复制领域规则。
- 拼接后端 payload 或解释底层错误语义。

## 最小目录模板

复杂业务功能可以从以下结构起步：

```text
src/features/{feature-name}/
├── domain/
│   ├── model/
│   ├── value/
│   └── error/
├── application/
│   ├── usecase/
│   ├── command/
│   ├── result/
│   └── port/
├── adapters/
│   ├── controller/
│   ├── presenter/
│   └── mapper/
├── infrastructure/
│   ├── api/
│   ├── storage/
│   └── mapper/
└── presentation/
    ├── pages/
    ├── components/
    ├── hooks/
    └── state/
```

裁剪原则：

- 没有复杂业务规则时，可以不创建 `domain/`。
- 没有外部 I/O 时，可以不创建 `infrastructure/`。
- 只有简单展示时，不要为了形式创建空 use case。
- 一旦 UI 开始直接调用 API、拼接业务 payload 或复制规则，必须重新拆分边界。

## 修复违规

`pnpm lint:deps` 失败时，应先看违规文件和规则名，再移动职责边界。

常见修复：

| 违规 | 处理方式 |
|---|---|
| domain import infrastructure | 在 domain 或 application 定义端口接口，把实现移到 infrastructure |
| application import generated API | 在 application 定义 gateway/repository port，由 infrastructure 包装 generated API |
| adapters import React | 把 hook、component、context 移到 presentation，把纯转换逻辑留在 adapters |
| infrastructure import presentation | 把 UI state、component props、toast、modal 逻辑移到 presentation 或 adapters |
| presentation import use case | 在 adapters 创建 controller，让 presentation 调 controller |
| presentation import repository/API client | 通过 adapter controller 进入应用层，再由 infrastructure 实现端口 |

不要用 Dependency Cruiser ignore 作为默认修复。只有迁移期、第三方限制或历史代码分阶段改造时，才允许临时例外。

## 可视化依赖

需要排查依赖污染时，可以生成依赖图。

```bash
npx depcruise src --include-only "^src/" --output-type dot | dot -T svg > dependency-graph.svg
```

依赖图只作为分析工具。合并门禁以 `pnpm lint:deps` 和 CI 结果为准。

## 设计门禁检查

新增或重构前端功能时，设计门禁至少检查：

- 是否说明该功能是否需要完整分层，还是可以采用裁剪结构。
- 核心业务规则是否没有放在 React component、hook、store 或 API client 中。
- 应用层是否只做用例编排，并通过端口接口访问外部能力。
- 适配层是否只做 controller、presenter 和 mapper，不依赖 React 或真实 I/O。
- 基础设施层是否只实现端口，不反向依赖页面和组件。
- 表现层是否通过 adapter controller 触发业务行为，而不是直接调用 use case 或 repository。
- generated API type、后端 DTO 和 UI view model 是否没有跨层混用。
- Dependency Cruiser 规则是否覆盖新增目录。

## 合并前检查

合并前必须确认：

- `pnpm lint:deps` 通过，或 CI 中等价依赖检查通过。
- `domain` 没有依赖外层、React、`src/api` 或浏览器能力。
- `application` 没有依赖 adapters、infrastructure、presentation 或 generated API。
- `adapters` 没有依赖 infrastructure、presentation 或 React。
- `infrastructure` 没有依赖 presentation。
- `presentation` 没有直接依赖 use case、repository、gateway 或 API client。
- 例外规则有明确原因、影响范围和移除计划。
- 测试证据覆盖核心业务规则、适配转换和关键 UI 行为。
