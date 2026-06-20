---
requirement_id: "LEN-12"
owner: "Codex"
current_stage: "5"
status: "draft"
created_at: "2026-06-19"
related_branch: "feature/applicant-api/LEN-12"
---

# [BE] OTP 发送 / 校验 / 会话与限流

## Summary

LEN-12 新建 `applicant-api` 后端身份服务，为 Lendora 申请漏斗提供手机号 OTP、Applicant 身份和短期会话能力。服务通过 protobuf 契约对上游开放；BFF 和前端接入不在本需求范围。

先说不是什么：它不是 `fides-bff` 需求，不实现前端验证屏，不接真实短信供应商，不采集 KYC，也不创建贷款申请。

## Links

- JIRA: LEN-12（Subtask）← LEN-2（手机验证登录）← LEN-1。
- Parent business story: LEN-2。
- Branch: `feature/applicant-api/LEN-12`
- Worktree: `.worktrees/LEN-12/{harness-repo,business-repo,idl-repo,idl-java-repo}`

## Lifecycle Artifacts

- requirement.md
- impact-analysis.md
- design.md
- tasks.json
- gates/
- reviews/
- evidence/
