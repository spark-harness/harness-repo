# Context Collection Protocol

本文定义 Harness 工作中的上下文收集规范。

它不是要求把所有文档读一遍。它要求按任务类型读取最小必要上下文，并把影响判断的来源记录下来。

## 1. 基本原则

- 先读入口，再读细节。
- 先读团队和框架规则，再读项目和服务知识。
- 先用服务矩阵定位路径，再进入业务仓或 IDL 仓。
- 只收集会影响判断、设计、门禁或实施的上下文。
- 发现上下文缺口时，显式记录缺口，不用猜测替代事实源。

## 2. 固定入口

在 `harness-repo` 内工作时，先读取：

```text
AGENTS.md
context/README.md
context/team/INDEX.md
context/harness-framework/INDEX.md
```

如果任务涉及服务、模块、仓库路径、IDL 或跨服务依赖，继续读取：

```text
.service-matrix/dependencies.yaml
context/project/INDEX.md
```

如果服务级上下文存在，继续读取：

```text
context/project/{project}/{domain}/{service}/INDEX.md
```

如果服务级上下文不存在，应报告为上下文缺口，并给出最小建议文件。

## 3. 按任务收集

| 任务类型 | 必读上下文 |
| --- | --- |
| 创建或推进需求 | `main-process-numbering.md`、`document-template-policy.md`、相关项目上下文 |
| 执行门禁 | `gate-implementation.md`、门禁输入文件、相关团队规范 |
| 修改流程或阶段 | `main-process-numbering.md`、`gate-implementation.md`、`document-template-policy.md`、Skill 和 Agent 入口 |
| 修改模板 | `document-template-policy.md`、受影响阶段、受影响门禁 |
| 修改服务矩阵 | `.service-matrix/dependencies.yaml`、相关项目上下文、相关需求或设计 |
| 修改团队规范 | `context/team/INDEX.md`、受影响门禁、受影响模板 |
| 修改项目知识 | `context/project/INDEX.md`、对应项目或服务入口、相关需求或门禁报告 |

## 4. 证据记录

执行门禁时，必须把影响结论的输入文件记录到门禁报告的 `Source Files`。

编写或修改需求、设计、任务时，应在对应文档中保留可追溯关系：

- 需求条目到设计决策。
- 设计决策到任务。
- 服务影响到服务矩阵条目。
- IDL 影响到 protobuf 文件和 Buf 检查。
- 验收标准到测试、运行日志或人工验收证据。

## 5. 上下文缺口处理

如果缺少必要上下文，按以下方式处理：

1. 明确缺少哪个文件或字段。
2. 说明它影响什么判断。
3. 给出最小补齐位置。
4. 如果缺口阻塞门禁，门禁结果必须为 `BLOCKED`。

缺少上下文时，不允许用聊天记录、目录名或未验证记忆替代事实源。

## 6. 禁止项

- 不把业务实现细节复制进 Harness 框架文档。
- 不把临时聊天结论当作阶段推进依据。
- 不跳过服务矩阵直接猜测服务路径。
- 不在门禁报告中省略实际读取的关键文件。
- 不为了通过门禁而降低模板字段或检查项要求。
