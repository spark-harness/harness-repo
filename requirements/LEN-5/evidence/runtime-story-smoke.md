---
requirement_id: "LEN-5"
evidence_type: "runtime-story-smoke"
verified_by: "Codex"
verified_at: "2026-06-28T13:13:00+08:00"
status: "pass-with-warnings"
environment: "vincent-k3s / lendora-sta / https://api.fuzzytails.fun"
---

# Runtime Story Smoke

## Scope

验证 LEN-5 AC1-AC5：

- AC1: 服务端试算展示月供、年化和总额。
- AC2: 越界输入不产生可继续 quote。
- AC3: loan terms 变化后旧 quote 失效。
- AC4: Continue 静默保存 draft，并停留贷款请求步骤。
- AC5: 同一 draft 可读取回填金额、期限和用途。

## Runtime Inputs

| Item | Value |
|---|---|
| Public domain | `https://api.fuzzytails.fun` |
| Cluster | `vincent-k3s` |
| Kubeconfig | `~/.kube/vincent-k3s.yaml` with `GODEBUG=tlsmlkem=0` |
| Namespaces | `lendora-sta-fides`, `lendora-sta-fides-bff`, `lendora-sta-quote-api`, `lendora-sta-origination-api`, `lendora-sta-postgres`, `lendora-sta-consul`, `caddy` |
| API trace base | `len520260628051111` |
| Session probe trace | `len5probe20260628051843` |
| Browser evidence traces | pricing `1398d363f9d299967057a6010bcb3d12`, draft save `e9c9f39bf880af236f780db159f81629` |
| fides image | `ghcr.io/spark-harness/fides@sha256:37212ca4e5a028dbc41c707aa214f2fd8955f77ecf0e8de98cc98a2e2fb98c8f` |
| fides-bff image | `ghcr.io/spark-harness/fides-bff@sha256:dad7a58f4305b2f41f0577602315c747487c8d0e2220a5b08d88c08167397f3a` |
| quote-api image | `ghcr.io/spark-harness/quote-api@sha256:52373dfe19fdee70bb3ef081b7c64b280804e5e6cc6de962b0d380f71e2b1915` |
| origination-api image | `ghcr.io/spark-harness/origination-api@sha256:94ea8d38c46341db044ede4ef6586e7cef96a2745d28fef2f114b5dd3d35880a` |

No access token, refresh token, token secret, OTP secret or database password is written in this evidence.

## Public Access

| Check | Result |
|---|---|
| `GET https://api.fuzzytails.fun/api/runtime-config` | PASS; `{"otpAdapter":"real","bffBaseUrl":"/api/v1","browserTracing":{"headers":{}}}` |
| `GET https://api.fuzzytails.fun/api/v1/health` | PASS; `{"status":"ok","version":"dev"}` |
| `deployment/fides` rollout | PASS; `1/1`, image digest `sha256:37212ca4e5a028dbc41c707aa214f2fd8955f77ecf0e8de98cc98a2e2fb98c8f` |
| `deployment/fides-bff` rollout | PASS; `1/1` |
| `deployment/quote-api` rollout | PASS; `1/1` |
| `deployment/origination-api` rollout | PASS; `1/1` |
| `deployment/applicant-api` rollout | PASS; `1/1` |

Live `fides` runtime environment contains runtime config keys only:

```text
FIDES_RUNTIME_ENV=sta
FIDES_RUNTIME_CONFIG_CONSUL_URL=http://consul.lendora-sta-consul.svc.cluster.local:8500
FIDES_RUNTIME_CONFIG_CONSUL_KEY=spark/lendora/sta/fides-web/runtime-config
FIDES_OTP_ADAPTER=real
FIDES_BFF_BASE_URL=/api/v1
```

The stale `NEXT_PUBLIC_*` runtime env drift was removed from the live deployment.

## Deployment And Discovery

| Check | Result |
|---|---|
| `quote-api /ready` from pod | PASS; `{"service":"quote-api","dependencies":{"consul":"UP","postgresql":"UP"},"status":"READY"}` |
| `origination-api /ready` from pod | PASS; `{"dependencies":{"consul":"UP","postgresql":"UP"},"status":"READY","service":"origination-api"}` |
| Consul health service discovery | PASS; `fides-bff`, `quote-api`, `origination-api` all returned passing entries |
| `kubectl kustomize apps/fides/overlays/lendora-sta` | PASS; rendered 77 lines and the expected fides digest |

Consul passing entries:

| Service | Address | Port |
|---|---|---:|
| fides-bff | `fides-bff.lendora-sta-fides-bff.svc.cluster.local` | 8000 |
| quote-api | `quote-api.lendora-sta-quote-api.svc.cluster.local` | 80 |
| origination-api | `origination-api.lendora-sta-origination-api.svc.cluster.local` | 80 |

Quote DB count after smoke: `20`, latest `2026-06-28 05:11:13.946937`.

Application DB count after smoke: `8`, latest `2026-06-28 05:11:13.833013`.

## Public API Evidence

The public API smoke used real OTP login through `https://api.fuzzytails.fun/api/v1/auth/otp:send` and `https://api.fuzzytails.fun/api/v1/auth/otp:verify` with the fixed test OTP code. Tokens were kept in process memory only and were not written to this evidence.

### Authentication Boundary

```text
POST /api/v1/auth/otp:send
HTTP 200
challengeId=otp_d351df80-9c46-4fd0-9540-359f4360342f

POST /api/v1/auth/otp:verify
HTTP 200
applicantId=applicant_6d862fba-eff1-48a2-90ba-841e66feedce

POST /api/v1/protected/session:probe
HTTP 200
applicantId=applicant_05f5b1ec-ea45-4a36-a9aa-29b5d1038d51
```

The protected business endpoints below returned 200 with the real bearer access token issued by OTP verify, proving the session token and applicant principal boundary for the Story flow.

### AC1: 服务端试算

Request:

```text
POST /api/v1/pricing/quotes
amount=50000.00, term=9, purpose=debt_consolidation
```

Result:

```text
HTTP 200
quoteId=quote_4e0cb029-fc3e-4a57-8e55-70afe7cfb1d9
monthly=5669.26
apr=0.0520
totalInterest=1023.38
totalPayable=51023.38
```

Quote DB row:

```text
quote_4e0cb029-fc3e-4a57-8e55-70afe7cfb1d9|applicant_6d862fba-eff1-48a2-90ba-841e66feedce|50000.00|9|debt_consolidation
```

Conclusion: PASS.

### AC2: 越界输入

Request:

```text
POST /api/v1/pricing/quotes
amount=999999.00, term=9, purpose=debt_consolidation
```

Result:

```text
HTTP 422
error.code=amount_out_of_range
error.message=amount out of range
```

Conclusion: PASS. No quoteId was returned, so no continueable quote was produced.

### AC3: 旧报价失效

Request:

```text
POST /api/v1/loan-applications
loan.amount=60000.00, loan.term=9, purpose=debt_consolidation
quoteId=quote_4e0cb029-fc3e-4a57-8e55-70afe7cfb1d9
```

The quote was created for amount `50000.00`, so this simulates changed loan terms with an old quote.

Result:

```text
HTTP 422
error.code=amount_out_of_range
error.message=amount_out_of_range
```

Conclusion: PASS. Continue with stale/mismatched quote was rejected by the backend boundary.

### AC4: Continue 静默保存

Create draft:

```text
POST /api/v1/loan-applications
loan.amount=50000.00, loan.term=9, purpose=debt_consolidation
quoteId=quote_4e0cb029-fc3e-4a57-8e55-70afe7cfb1d9
```

Result:

```text
HTTP 200
applicationId=app_b6fe3da0-a3cc-4065-86df-32fc33aeaf0f
status=draft
currentStep=loan_request
```

Patch same draft after a new quote:

```text
PATCH /api/v1/loan-applications/app_b6fe3da0-a3cc-4065-86df-32fc33aeaf0f
loan.amount=75000.00, loan.term=12, purpose=home_improvement
quoteId=quote_f3e5c5e6-ac61-4d1f-9124-6b4f76f65941
```

Result:

```text
HTTP 200
applicationId=app_b6fe3da0-a3cc-4065-86df-32fc33aeaf0f
status=draft
currentStep=loan_request
```

Browser check:

```text
Page: https://api.fuzzytails.fun/
Screen heading: How much do you need?
Monthly Repayment: HKD $5,669.26
Representative APR: 5.20%
Total Interest: HKD $1,023.38
Click Continue: navigationOccurred=false
BFF log: PATCH /api/v1/loan-applications/app_b46ca200-5c7b-4fc4-981f-fb49cc05eb63 status_code=200 latency_ms=11
```

Conclusion: PASS. Continue saved the draft and the browser stayed on the loan request screen with no navigation.

### AC5: 同一草稿回填

Request:

```text
GET /api/v1/loan-applications/app_b6fe3da0-a3cc-4065-86df-32fc33aeaf0f
```

Result:

```text
HTTP 200
loan.amount=75000.00
loan.term=12
loan.purpose=home_improvement
acceptedQuote.quoteId=quote_f3e5c5e6-ac61-4d1f-9124-6b4f76f65941
status=draft
currentStep=loan_request
```

Application DB row:

```text
app_b6fe3da0-a3cc-4065-86df-32fc33aeaf0f|applicant_6d862fba-eff1-48a2-90ba-841e66feedce|draft|loan_request|75000.00|12|home_improvement|quote_f3e5c5e6-ac61-4d1f-9124-6b4f76f65941
```

Conclusion: PASS.

## Trace Evidence

`fides-bff` access logs for trace base `len520260628051111`:

```text
POST /api/v1/auth/otp:send status_code=200
POST /api/v1/auth/otp:verify status_code=200
POST /api/v1/pricing/quotes status_code=200
POST /api/v1/pricing/quotes status_code=422 error_code=amount_out_of_range
POST /api/v1/loan-applications status_code=422 error_code=amount_out_of_range
POST /api/v1/loan-applications status_code=200
POST /api/v1/pricing/quotes status_code=200
PATCH /api/v1/loan-applications/app_b6fe3da0-a3cc-4065-86df-32fc33aeaf0f status_code=200
GET /api/v1/loan-applications/app_b6fe3da0-a3cc-4065-86df-32fc33aeaf0f status_code=200
```

## Warnings

- `kubectl port-forward pod/fides-847ffb6bcf-cdqnt 13000:3000` still fails because the Next.js process does not listen on `127.0.0.1:3000` inside the pod. Public Caddy access and Kubernetes Service access are working, so deployed reachability is PASS, but local pod port-forward remains a runtime caveat.
- Argo CD is not installed in the current `vincent-k3s` cluster, so Healthy/Synced is not claimed here. Runtime functional smoke and live `kubectl` rollout status are used as current deployment evidence.

## Result

PASS with WARN. LEN-5 AC1-AC5 are satisfied through the public domain `https://api.fuzzytails.fun` and the live `vincent-k3s / lendora-sta` services. The remaining warnings are outside the public user flow.
