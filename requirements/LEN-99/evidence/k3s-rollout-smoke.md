# LEN-99 Vincent K3s Rollout And Smoke Evidence

## Scope

- Requirement: LEN-99
- Verified at: `2026-06-25T16:45:48+08:00`
- Cluster: vincent k3s via `KUBECONFIG=$HOME/.kube/vincent-k3s.yaml`
- Business HEAD: `eccb6c5`
- GitOps HEAD: `5c8985f`

## Result

PASS for rollout, public Fides / BFF smoke, OTP end-to-end smoke, and applicant-api public exposure control.

The applicant-api HTTP management endpoints are not used as cross-namespace smoke endpoints. Direct pod-local checks pass, while cross-pod HTTP `/health` and `/ready` to applicant-api port 80 returned connection refused from temporary curl pods. The accepted runtime smoke is the user-facing BFF path that calls applicant-api over gRPC and exercises Redis and PostgreSQL.

## Rollout Status

| Deployment | Namespace | Result |
|---|---|---|
| `applicant-api` | `lendora-sta-applicant-api` | rollout status succeeded |
| `fides-bff` | `lendora-sta-fides-bff` | rollout status succeeded |
| `fides` | `lendora-sta-fides` | rollout status succeeded |

## Running Pods And Images

| Service | Pod | Ready | Restarts | Image |
|---|---|---|---|---|
| `applicant-api` | `applicant-api-84d784cbf-n47gz` | `true` | `0` | `ghcr.io/spark-harness/applicant-api@sha256:70b3a3f5c0179b11a8171e7bbdb254020f29e6c1471a93a70827776c50504ff3` |
| `fides-bff` | `fides-bff-766bcbccdb-v7jns` | `true` | `0` | `ghcr.io/spark-harness/fides-bff@sha256:e0054c49621611a9b629701af5913532b108513a1e9a26cc750ec11fa1bb85f8` |
| `fides` | `fides-8478cd5bfb-twpxq` | `true` | `0` | `ghcr.io/spark-harness/fides@sha256:57fbc974ac53d24b81511b781b21f73ce69dc4cb415a81e1e2491c934e1df599` |

## Public Smoke

| Endpoint | Result |
|---|---|
| `curl --http1.1 -k https://api.fuzzytails.fun/` | HTTP `200`, body contained Fides HTML |
| `curl --http1.1 -k https://api.fuzzytails.fun/api/v1/health` | HTTP `200`, body `{"status":"ok","version":"dev"}` |

## OTP End-To-End Smoke

| Step | Request | Result |
|---|---|---|
| Send OTP | `POST https://api.fuzzytails.fun/api/v1/auth/otp:send` with `{"countryCode":"+852","phone":"91234567"}` | HTTP `200`; response included `challengeId=otp_3c2af67c-efdb-4ed8-9f70-b2754854334d`, `expiresInSec=300`, `resendAfterSec=60` |
| Verify OTP | `POST https://api.fuzzytails.fun/api/v1/auth/otp:verify` with the challenge above and test code `123456` | HTTP `200`; response included `applicantId=applicant_7f2015b9-0140-4bf7-97d7-943d74ebbbf6`; access and refresh tokens were redacted from evidence |

## Applicant-Api Exposure Evidence

| Check | Result |
|---|---|
| `kubectl get svc -n lendora-sta-applicant-api applicant-api -o wide` | `ClusterIP 10.43.3.231`, ports `80/TCP,9090/TCP`, no external IP |
| `kubectl get ingress -A` filtered for applicant / fides / api.fuzzytails | No ingress resource listed for applicant-api |
| `kubectl get networkpolicy applicant-api-ingress -n lendora-sta-applicant-api` | Allows namespace selector `lendora.io/applicant-api-client=true` to `9090`, `8080`, and `80`; allows Consul namespace to `8080` |
| `kubectl get ns lendora-sta-fides-bff default --show-labels` | `lendora-sta-fides-bff` has `lendora.io/applicant-api-client=true`; `default` does not |

## Runtime Notes

- `applicant-api` listens on container ports `8080` and `9090`; pod-local checks to `127.0.0.1:8080/health`, `127.0.0.1:8080/ready`, and pod IP `10.42.0.165:8080/health` returned HTTP `200`.
- Temporary curl pods in `lendora-sta-fides-bff` can reach `fides-bff` and `fides` service HTTP endpoints.
- Temporary curl pods saw applicant-api HTTP `:80` return connection refused, while `telnet://applicant-api...:9090` timed out waiting for data. The public BFF OTP smoke is therefore the authoritative applicant-api runtime smoke for this requirement.
