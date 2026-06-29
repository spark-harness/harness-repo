---
requirement_id: "LEN-137"
owner: "core"
status: "approved"
created_at: "2026-06-28"
related_branch: "feature/LEN-137-identity-information"
target_branch: "master"
release_branch: "master"
contract_gate_mode: "auto"
affected_repositories:
  - harness-repo
  - idl-repo
  - business-repo
approved_by: "forest"
approved_at: "2026-06-28T22:22:59+08:00"
decision: "批准 LEN-137 requirement 和 impact-analysis；范围为 Step 3 身份信息填写、保存、回填、校验、currentStep 推进和 local 网页真实链路验证，不包含 dev-1 发布、公网验证或 GitOps digest 更新。"
---

# 填写并保存身份信息

## Background

LEN-137 是申请漏斗第 3 步。用户已通过手机验证，并已在 Step 2 保存贷款请求草稿。

这条需求不是什么：它不是文件上传、OCR、活体检测、地址、工作收入、银行账户、最终提交，也不是第 2 步贷款请求改造。

它是什么：它在已有登录态和 Step 2 `applicationId` 的前提下，采集身份信息，保存到申请人档案，并把当前申请草稿推进到身份信息步骤。

## Goals

- 提供身份信息表单，采集 HKID 主体、HKID 校验位、First Name、Last Name、Chinese Name、Nationality 和 Date of Birth。
- 保存身份信息前完成前端基础校验，后端再次执行权威校验。
- 通过 BFF HTTP facade 保存和回填身份信息。
- BFF 保存成功后推进当前 loan application draft 的 `currentStep` 为 `identity_information`。
- 已保存身份信息后刷新或重新打开 Step 3 可以完整回填。
- 通过 local 网页真实链路验证 OTP、Step 2、Step 3 保存和回填。

## Non-Goals

- 不做文件上传、OCR、活体检测、地址、工作收入、银行账户或最终提交。
- 不做第 4 步跳转；保存成功后停留在 Step 3。
- 不改造 Step 2 贷款请求业务语义。
- 不做 HKID 加密、脱敏或 PII 特殊日志处理；本需求按父 Story 要求明文保存。
- 不做 dev-1 发布、公网验证或 GitOps digest 更新。
- 不把真实 token、手机号、HKID 或其他个人信息写入证据文件。

## User / Business Scenarios

### Scenario 1: 打开身份信息表单

Given: 用户已登录，且已有 Step 2 产生的 `applicationId`。

When: 用户进入申请漏斗第 3 步。

Then: 页面显示身份信息表单，HKID 主体与校验位在同一行分段输入，Nationality 选项与后端契约一致。

### Scenario 2: 缺少前置条件

Given: 用户未登录，或没有 Step 2 产生的 `applicationId`。

When: 用户尝试进入或保存 Step 3。

Then: 用户不能保存身份信息，并回到可恢复的前置流程。

### Scenario 3: 保存合法身份信息

Given: 用户已登录、已有 `applicationId`，并填写合法身份信息。

When: 用户点击 Continue。

Then: 身份信息被保存，当前申请草稿推进到 `identity_information`，页面停留在 Step 3，不 toast，不跳转第 4 步。

### Scenario 4: 身份信息字段非法

Given: 用户在 Step 3 表单输入非法 HKID、非法年龄、或 First Name / Last Name 包含非英文字母。

When: 用户点击 Continue。

Then: 字段旁显示对应错误，身份信息不保存。

### Scenario 5: 回填已保存身份信息

Given: 用户此前已保存身份信息。

When: 用户刷新或重新打开 Step 3。

Then: 页面完整回填 HKID、姓名、Nationality 和 DOB。

### Scenario 6: 未保存过身份信息

Given: 用户已登录且已有 `applicationId`，但此前没有保存身份信息。

When: 用户进入 Step 3 并触发回填。

Then: 页面显示空表单，不报错。

## Business Rules

- BR1: 用户必须已登录，且必须已有 Step 2 产生的 `applicationId`；否则不应进入或保存 Step 3。
- BR2: 身份信息字段包含 HKID 主体、HKID 校验位、First Name、Last Name、Chinese Name、Nationality、Date of Birth。
- BR3: HKID 只支持单字母前缀、6 位数字和单独校验位，并按香港身份证 check digit 校验。
- BR4: First Name 和 Last Name 必填，且只允许英文字母。
- BR5: Chinese Name 必填。
- BR6: Nationality 必须来自后端契约枚举：Chinese、HongKong、British、Indian、Filipino、Indonesian、Pakistani、American、Australian、Canadian、Other。
- BR7: Date of Birth 按 Asia/Hong_Kong 自然日期计算，年龄必须在 18 到 60 周岁之间；前端限制可选范围，后端再次校验。
- BR8: 保存成功后停留在 Step 3，不 toast，不跳转第 4 步。
- BR9: GET 回填返回完整明文字段；未保存过资料时返回空对象。
- BR10: HKID 不做 PII 加密、脱敏或特殊日志处理，数据库明文保存。
- BR11: 保存身份信息成功后，当前 loan application draft 的 `currentStep` 推进为 `identity_information`。
- BR12: 所有新增对外和内部 API 必须先有 IDL；前端调用 BFF HTTP，BFF 调内部服务使用 gRPC。
- BR13: 是否完成以 local 网页真实链路验证为准；只通过单元测试、mock 或接口直调不能视为完成。

## Acceptance Criteria

- AC1: 已登录且已有 Step 2 `applicationId` 时，打开第 3 步能看到身份信息表单，HKID 主体与校验位在同一行分段输入，Nationality 选项与后端枚举一致。
- AC2: 用户未登录或没有 `applicationId` 时，尝试进入或保存第 3 步不能保存身份信息，并回到可恢复的前置流程。
- AC3: 用户填写合法身份信息并点击 Continue 后，身份信息被保存，页面停留 Step 3，不 toast，不跳转第 4 步。
- AC4: HKID 校验位不合法时，点击 Continue 后字段旁提示 HKID 不合法，身份信息不保存。
- AC5: DOB 未满 18 或超过 60 周岁时，前端限制或字段旁提示年龄不符合要求，后端也拒绝非法值。
- AC6: First Name 或 Last Name 含非英文字母时，提交表单后字段旁提示只能输入英文字母。
- AC7: 已保存身份信息后，刷新或重新打开 Step 3 能完整回填 HKID、姓名、Nationality 和 DOB。
- AC8: 用户此前没有保存身份信息时，进入 Step 3 并触发回填显示空表单，不报错。
- AC9: 身份信息保存成功后，查询当前申请草稿可看到 `currentStep` 为 `identity_information`。
- AC10: 本地前端、BFF、applicant-api、origination-api 及依赖服务均已启动后，在 local 网页执行 OTP、Step 2 保存、Step 3 保存、刷新回填，完整链路通过；证据包含 local 网页 URL、请求结果和 `currentStep` 验证范围。

## Open Questions

| Question | Owner | Deadline | Status |
|---|---|---|---|
| LEN-143 Jira 描述是否需要同步从 dev-1 改为 local？ | product/core | 2026-06-28 | open: 父 Story 和 Summary 已明确 local，本需求实现按父 Story local 范围执行 |

## Notes

- 依赖：LEN-2 手机验证、LEN-5 贷款请求草稿、LEN-22 会话与身份传播、本地运行依赖服务。
- 父 Story 明确不做 dev-1 发布、公网验证或 GitOps digest 更新。
- 本 Requirement Brief 已在 2026-06-28 对话中由用户确认，文档 front matter 的正式审批字段仍需通过 Harness/Janus 审批流程记录。
