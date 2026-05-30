# Requirement Commands

## `/requirement:new`

创建 `requirements/{requirement-id}/`，复制需求、影响面、设计、任务和门禁模板。

## `/requirement:continue`

读取需求目录、当前阶段、最近门禁报告和相关上下文，恢复工作状态。

## `/requirement:next`

根据 `context/harness-framework/main-process-numbering.md` 判断是否允许进入下一阶段。

## `/requirement:gate-check`

执行当前阶段对应门禁，并把结果写入 `requirements/{requirement-id}/gates/`。
