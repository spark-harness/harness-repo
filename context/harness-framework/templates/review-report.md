---
requirement_id: ""
task_id: ""
reviewer: ""
base_revision: ""
diff_scope: ""
conclusion: "not-ready" # not-ready | ready-for-gate
updated_at: ""
---

# Code Review Report

## Scope

- Repository:
- Base revision:
- Changed files:
- Task ID:

## Findings

| Severity | Dimension | Location | Issue | Impact | Required Fix | Status |
|---|---|---|---|---|---|---|
| P0 |  |  |  |  |  | open |

Severity 口径：

- `P0`：正确性、数据丢失、安全或契约破坏。
- `P1`：大概率生产 Bug、缺少必需证据或门禁阻塞项。
- `P2`：可维护性、测试、可观测性或灰度风险。
- `P3`：不应阻塞的小问题。

## Dimension Coverage

| Dimension | Checker | Result | Checked Scope |
|---|---|---|---|
| 追溯与范围 | code_review_traceability_checker | findings / no findings / skipped |  |
| 契约兼容 | code_review_contract_checker | findings / no findings / skipped |  |
| 数据与并发 | code_review_data_concurrency_checker | findings / no findings / skipped |  |
| 安全与错误处理 | code_review_security_error_checker | findings / no findings / skipped |  |
| 架构边界 | backend_architecture_reviewer | findings / no findings / skipped |  |
| 测试价值与复杂度 | code_review_reporter | findings / no findings |  |

`skipped` 必须附原因。

## Tests Inspected

列出审查过或执行过的测试及结果。

## Open Questions

## Residual Risk

## Conclusion

- `ready-for-gate`：无未关闭的 P0/P1。
- `not-ready`：存在未关闭的 P0/P1。

本报告不是门禁结论。阶段推进仍以 Janus 门禁 JSON 和人工审批为准。
