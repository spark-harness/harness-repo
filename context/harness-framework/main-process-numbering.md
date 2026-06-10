# Main Process Numbering

本文档是 Harness 需求生命周期的阶段真相源。

## 阶段 1：初始化

目标：创建需求目录，记录需求来源、负责人和初始状态。

最小产物：

- `requirements/{requirement-id}/README.md`
- `requirements/{requirement-id}/requirement.md`

## 阶段 2：需求定义

目标：把自然语言需求整理成可评审规格。

最小产物：

- `requirement.md`
- `impact-analysis.md`

### 阶段 2.2：需求评审门禁

通过条件：

- 背景、目标、非目标明确。
- 场景、业务规则和验收标准可测试。
- 待确认问题显式列出。
- 影响分析覆盖服务、契约、数据、配置、权限、可观测性、灰度和回滚。

说明：`requirement.md` 和 `impact-analysis.md` 属于同一个需求定义阶段。两者都进入可评审状态前，不生成正式 `requirement-review` 门禁。

## 阶段 3：设计

目标：形成能追溯到需求的工程方案。

最小产物：

- `design.md`
- 需求条目到设计决策的追溯关系。

### 阶段 3.3：设计门禁

通过条件：

- 覆盖服务、接口、数据、配置、权限、可观测性、灰度和回滚。
- 明确 protobuf IDL 或外部契约影响。
- 设计决策能追溯到需求条目。

## 阶段 4：开发

目标：把设计拆成可执行任务，并在正确仓库和分支上实施。

### 阶段 4.1：任务拆分

最小产物：

- `tasks.json`

### 阶段 4.2：Dev 进入门禁

通过条件：

- 任务拆分完整。
- 每个任务有范围、验收和追溯来源。

### 阶段 4.3：服务仓库检查门禁

通过条件：

- `.service-matrix/dependencies.yaml` 中涉及服务存在。
- Harness 仓、业务仓、IDL 仓分支一致。
- `idl_required` 服务已准备 protobuf 契约仓。
- 契约仓存在 `buf.yaml` v2 和 `buf.gen.yaml` v2。

### 阶段 4.4：编码循环

执行代码修改、测试、审查和修复。

## 阶段 5：交付

目标：确认验收、门禁、文档和经验沉淀完成。

最小检查：

- 验收标准有证据。
- 必要测试已执行。
- 项目知识和经验沉淀已处理。

### 阶段 5.1：合并就绪门禁

通过条件：

- `requirement-review`、`design-review`、`dev-entry` 和 `service-repo-check` 都已通过。
- 涉及 IDL 时，Buf lint、generate 和 breaking 证据已记录。
- 涉及服务实现时，服务测试证据已记录。
- 合并目标所需仓库和分支状态已记录。

说明：实现后才产生的证据只进入 `merge-readiness` 门禁，不回写早期阶段门禁。
