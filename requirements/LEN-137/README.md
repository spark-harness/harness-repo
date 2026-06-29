# LEN-137 填写并保存身份信息

本目录保存 `LEN-137` Story 的需求、影响分析、设计、任务、门禁、审查和本地网页真实链路证据。

## Scope

- Jira: `LEN-137`
- Branch: `feature/LEN-137-identity-information`
- Target: `master`
- Runtime: local

## Acceptance Boundary

LEN-137 是申请漏斗第 3 步身份信息能力。

- 已登录且已有 Step 2 `applicationId` 的申请人可以填写身份信息。
- 身份信息保存到申请人档案。
- 保存成功后当前草稿推进到 `identity_information`。
- 已保存资料可刷新或重新打开后完整回填。
- 完成标准以 local 网页真实链路验证为准。

不包含 dev-1 发布、公网验证或 GitOps digest 更新。
