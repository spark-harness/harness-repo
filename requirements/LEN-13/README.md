# LEN-13

将 Lendora 申请漏斗第 1 步手机验证屏接入 OTP 获取与校验流程。前端消费 `auth/otp:send` 和 `auth/otp:verify`，把静态原型中的假异步与假跳转替换为可演示、可接真实接口的界面行为。

## 当前状态

- 当前阶段：任务拆分。
- 当前结论：`requirement-review` 与 `design-review` 门禁已通过；`LNE-13` 按当前 JIRA 实际 key 解析为 `LEN-13`。
- 父需求：`LEN-2` 手机验证登录（认证身份 + 会话）。
- 前置依赖：`LEN-12` OTP 契约、`LEN-4` FlowController / API 客户端。
- 参考原型：`hk_loan_ui/1._mobile_verification/` 与 `hk_loan_ui/docs/frontend/`。

## 文件

| 类型 | 文件 |
|---|---|
| 需求 | `requirement.md` |
| 影响分析 | `impact-analysis.md` |
| 设计 | `design.md` |
| 任务拆分 | `tasks.json` |
| 需求评审门禁 | `gates/requirement-review.gate.json` |
| 设计评审门禁 | `gates/design-review.gate.json` |

## 下一步

任务拆分草案就绪后，等待人工批准 `tasks.json`；批准后生成 `dev-entry` 门禁。进入实现前，还需要为 `business-repo` 建立 `feature/LEN-13-fe-otp-verification` 隔离工作树并通过 `service-repo-check`。
