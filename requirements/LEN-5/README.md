# LEN-5 发起贷款请求并试算

本目录保存 `LEN-5` Story 验收收口的需求、影响分析、设计、任务、门禁、审查和端到端证据。

## Scope

- Jira: `LEN-5`
- Branch: `feature/LEN-5-story-acceptance`
- Target: `master`
- Runtime: `vincent-k3s / lendora-sta`

## Acceptance Boundary

LEN-5 不再新增业务实现。它验证前序票组合后的用户故事是否成立：

- 贷款请求页能调用服务端试算并显示估算结果。
- 越界输入不会产生可继续报价。
- loan terms 变化后旧 quote 失效。
- Continue 静默保存草稿并停留当前页。
- 同一草稿重新打开时能回填金额、期限和用途。
