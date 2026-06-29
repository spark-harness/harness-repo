# LEN-137 Local Browser E2E Evidence

## Scope

- Requirement: `LEN-137`
- Task: `T7 / LEN-143 local 身份信息链路网页真实验证`
- Checked at: `2026-06-29T10:56:32+08:00`

## Local Runtime

Local services were healthy before browser validation:

| Service | URL | Result |
|---|---|---|
| `fides-web` | `http://127.0.0.1:3001/` | PASS |
| `fides-bff` | `http://127.0.0.1:8000/api/v1/health` | PASS |
| `applicant-api` | `http://127.0.0.1:8080/ready` | PASS |
| `origination-api` | `http://127.0.0.1:8081/ready` | PASS |
| `quote-api` | `http://127.0.0.1:8082/ready` | PASS |

The final browser run used a temporary `next dev` instance on `127.0.0.1:3001` and a temporary headless Chrome profile. The temporary server and browser profile were removed after verification.

## Browser Flow

Executed flow:

```text
OTP -> Step 2 loan draft save -> Step 3 identity information save -> browser reload -> Step 3 prefill
```

Result: PASS.

Sanitized browser evidence:

```json
{
  "browser_e2e": "ok",
  "url": "http://127.0.0.1:3001/",
  "beforeReload": {
    "heading": "Identity information",
    "currentStep": "identity_information",
    "hasTokenPointer": true
  },
  "afterReload": {
    "heading": "Identity information",
    "currentStep": "identity_information",
    "hkidBodyPresent": true,
    "firstNamePresent": true,
    "hasTokenPointer": true
  }
}
```

No token, phone number, Authorization header, or HKID value is recorded in this evidence file.

## API Cross-Check

Sanitized API chain result:

```text
send_otp_status=200
verify_otp_status=200
quote_status=200
draft_status=200
identity_put_status=200
identity_get_status=200
api_e2e=ok applicant_id_present=yes token_present=yes draft_step=loan_request identity_step=identity_information nationality=hong_kong load_empty=false first_name_present=yes
```

This verifies BFF compatibility with generated TS SDK numeric enum payloads for nationality and BFF response mapping to domain string values.

## Scope Boundary

LEN-143 is treated as local validation only.

Not performed:

- dev-1 deployment
- public URL validation
- GitOps digest update

## Stale Draft Owner Regression Recheck

After the original browser run, local testing reproduced a stale
`fides.loanRequest.draftPointer` case where a new verified applicant attempted
to PATCH an old draft application and received `403 Forbidden`.

Fix verification:

- `fides-web` unit/application tests prove owner mismatch clears the old draft
  pointer and creates a new draft instead of PATCHing the stale application.
- Local BFF HTTP cross-owner check proves the backend ownership guard still
  returns `403` when applicant B PATCHes applicant A's draft.

Sanitized HTTP result:

```text
create_status=200
cross_patch_status=403
same_applicant_distinct=true
application_created=true
```

The local page was also restarted with the current runtime config model:

```text
env -u NEXT_PUBLIC_FIDES_OTP_ADAPTER \
    -u NEXT_PUBLIC_FIDES_BFF_BASE_URL \
    -u NEXT_PUBLIC_OTEL_EXPORTER_OTLP_TRACES_ENDPOINT \
    -u NEXT_PUBLIC_OTEL_EXPORTER_OTLP_TRACES_HEADERS \
    FIDES_OTP_ADAPTER=real \
    FIDES_BFF_BASE_URL=http://localhost:8000 \
    pnpm dev
```

`/api/runtime-config` returned:

```json
{
  "otpAdapter": "real",
  "bffBaseUrl": "http://localhost:8000",
  "browserTracing": {
    "headers": {}
  }
}
```

No token, phone number, Authorization header, or HKID value is recorded in this
evidence file.
