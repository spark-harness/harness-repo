---
requirement_id: "LEN-11"
evidence_type: "runtime-smoke"
created_at: "2026-06-28T07:34:59+08:00"
status: "partial-pass"
environment: "vincent-k3s / lendora-sta"
---

# LEN-11 Runtime Smoke

## Scope

验证目标：

- 本地 `fides-web` 可访问并进入第二页 UI。
- 第二页不再本地假试算，缺少 BFF proxy 时 pricing 失败可见。
- lendora-sta `fides-bff` 的第二页所需 API 可用：pricing、draft create、draft patch。
- 完整 OTP -> token -> pricing -> draft E2E 是否可走通。

## Local Browser Smoke

命令：

```bash
pnpm dev --port 3000
```

访问：

```text
http://localhost:3000
```

结果：

- 页面 HTTP 200。
- 首屏显示 mobile verification。
- 使用 mock OTP 后进入贷款请求屏。
- 贷款请求屏显示：
  - `How much do you need?`
  - Step 2 progress
  - `Loan Amount (HKD)`
  - `Loan Term (Months)`
  - `Loan Purpose`
  - `Estimated Summary`
  - fixed bottom `Continue`
- 在本地未配置 BFF proxy 时选择 purpose 后，页面显示 `Request failed`，未使用本地假 quote 伪装成功。

Chrome MCP 截图 readback 失败，改用 accessibility tree 验证上述结构。

## BFF Runtime Health

命令：

```bash
curl -sS -i http://127.0.0.1:18080/api/v1/health
```

结果：

```text
HTTP/1.1 200 OK
{"status":"ok","version":"dev"}
```

## BFF Pricing / Draft API Smoke

使用 `fides-bff-runtime` secret 生成临时 HMAC access token，只用于验证受保护第二页 API，不打印 secret。

命令覆盖：

```bash
POST http://127.0.0.1:18080/api/v1/pricing/quotes
POST http://127.0.0.1:18080/api/v1/loan-applications
PATCH http://127.0.0.1:18080/api/v1/loan-applications/{applicationId}
```

结果：

```text
pricing response:
{"quoteId":"quote_53d67c49-b543-4924-ab24-7f9c9663c42d","monthly":"5669.26","apr":"0.0520","totalInterest":"1023.38","totalPayable":"51023.38","validUntil":"2026-06-28T00:01:17.712287417Z"}

draft create response:
{"applicationId":"app_7713440f-7528-497e-938a-061960f721b1","status":"draft","currentStep":"loan_request"}

draft patch response:
{"applicationId":"app_7713440f-7528-497e-938a-061960f721b1","status":"draft","currentStep":"loan_request"}
```

结论：LEN-11 第二页依赖的真实 BFF pricing/create/patch API 在 lendora-sta 可用。

## Full E2E Blocker

完整 OTP verify 链路执行：

```bash
POST http://127.0.0.1:18080/api/v1/auth/otp:verify
```

结果：

```json
{"error":{"code":"applicant_unavailable","message":"applicant-api is unavailable","traceId":"e83ff3752b845a8b5151fd7b56e7cd77"}}
```

BFF 日志对应：

```text
operation=POST /api/v1/auth/otp:verify status_code=503 error_code=applicant_unavailable
```

只读诊断：

```bash
GODEBUG=tlsmlkem=0 kubectl --kubeconfig ~/.kube/vincent-k3s.yaml get pods,svc -n lendora-sta-applicant-api -o wide
GODEBUG=tlsmlkem=0 kubectl --kubeconfig ~/.kube/vincent-k3s.yaml exec -n lendora-sta-applicant-api deploy/applicant-api -- wget -qO- http://127.0.0.1:8080/ready
```

结果：

```text
pod/applicant-api-84d784cbf-n47gz   1/1 Running
service/applicant-api               ClusterIP 80/TCP,9090/TCP
{"status":"READY","service":"applicant-api","dependencies":{"consul":"UP","postgresql":"UP","redis":"UP"}}
```

结论：

- `applicant-api` pod/service/readiness 正常。
- `fides-bff` 在 OTP verify 下游调用时仍返回 `applicant_unavailable`。
- 该阻塞属于既有 BFF/applicant 下游发现或调用链路，不是 LEN-11 前端实现缺陷。

## Result

Runtime smoke 为 `partial-pass`：

- PASS：前端页面可访问、第二页 UI 可见、第二页真实 BFF pricing/create/patch API 可用。
- BLOCKED OUTSIDE LEN-11：完整 OTP 登录到第二页的部署 E2E 被 `fides-bff -> applicant-api` verify 链路阻塞。
