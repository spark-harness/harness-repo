# LEN-77 Runtime Smoke Evidence

## Cluster And Entry

Runtime evidence was collected against `vincent-k3s`:

```bash
GODEBUG=tlsmlkem=0 KUBECONFIG=$HOME/.kube/vincent-k3s.yaml kubectl ...
```

The temporary public STA entry is:

```text
https://api.fuzzytails.fun
```

Routing:

- `/api/v1*` -> `fides-bff.lendora-sta-fides-bff.svc.cluster.local:8000`
- `/` -> `fides.lendora-sta-fides.svc.cluster.local:3000`

`lendora-sta.fuzzytails.fun` and `lendora-api-sta.fuzzytails.fun` remain follow-up DNS / certificate work.

## Dependency Readiness

Readiness was verified from Kubernetes rollout state and service health after applying the STA GitOps resources.

Expected runtime dependencies:

- PostgreSQL in `lendora-sta-postgres`, ClusterIP, PVC backed.
- Redis in `lendora-sta-redis`, ClusterIP, PVC backed.
- Consul in `lendora-sta-consul`, ClusterIP, PVC backed.

Consul applicant-api health:

```bash
GODEBUG=tlsmlkem=0 KUBECONFIG=$HOME/.kube/vincent-k3s.yaml \
  kubectl exec -n lendora-sta-consul deploy/consul -- \
  wget -qO- http://127.0.0.1:8500/v1/health/checks/applicant-api
```

Result: PASS. Observed `Status` was `passing` and the check output included:

```text
HTTP GET http://applicant-api.lendora-sta-applicant-api.svc.cluster.local:80/ready: 200
```

## Service Readiness

```bash
GODEBUG=tlsmlkem=0 KUBECONFIG=$HOME/.kube/vincent-k3s.yaml \
  kubectl get deploy -n lendora-sta-applicant-api -o wide
GODEBUG=tlsmlkem=0 KUBECONFIG=$HOME/.kube/vincent-k3s.yaml \
  kubectl get deploy -n lendora-sta-fides-bff -o wide
GODEBUG=tlsmlkem=0 KUBECONFIG=$HOME/.kube/vincent-k3s.yaml \
  kubectl get deploy -n lendora-sta-fides -o wide
```

Result: PASS.

| Service | Namespace | Ready | Image digest |
|---|---:|---:|---|
| applicant-api | `lendora-sta-applicant-api` | `1/1` | `sha256:8249e6c25693c810c3d59a7ca562823683ea4784bd56a74d907e5a2cefbb1ee4` |
| fides-bff | `lendora-sta-fides-bff` | `1/1` | `sha256:b95914c46980c0c1e3ee433f0230c2322e6a764f43c6c54a9ff37b890811ee45` |
| fides | `lendora-sta-fides` | `1/1` | `sha256:60ff63c63633c385ad7cc1bb56e793de775f53e9c7ccaa61adf1c9e70fd27af2` |

## Public Smoke

Public API health:

```bash
curl -kfsS https://api.fuzzytails.fun/api/v1/health
```

Result: PASS.

Observed response:

```json
{"status":"ok","version":"dev"}
```

Real BFF OTP smoke:

```bash
LEN43_REAL_BFF_SMOKE=1 \
LEN43_FIDES_BFF_BASE_URL=https://api.fuzzytails.fun/api/v1 \
LEN43_SMOKE_PHONE=91990003 \
./node_modules/.bin/vitest run src/api/mobile-verification/mobile-verification-real-bff.smoke.test.tsx
```

Result: PASS. Vitest reported 1 file and 1 test passed.

The smoke verifies:

- fides controller sends OTP through `RestOtpAuthGateway`.
- fides-bff receives the public REST request.
- fides-bff reaches applicant-api.
- test OTP code `123456` verifies and returns a session containing token strings and an `applicant_...` id.

The UI click-through remains covered by focused component / controller tests; the real public smoke intentionally uses controller + gateway to avoid jsdom event flakiness.

## applicant-api Negative Probe

```bash
curl -kfsSI --max-time 20 https://lendora-sta-applicant-api.fuzzytails.fun/health
```

Result: PASS as negative evidence. The request failed with TLS handshake error because applicant-api has no public route.

Observed error:

```text
LibreSSL SSL_connect: SSL_ERROR_SYSCALL in connection to lendora-sta-applicant-api.fuzzytails.fun:443
```

## Sensitive Field Check

Logs checked:

```bash
GODEBUG=tlsmlkem=0 KUBECONFIG=$HOME/.kube/vincent-k3s.yaml \
  kubectl logs -n lendora-sta-applicant-api deploy/applicant-api --since=30m
GODEBUG=tlsmlkem=0 KUBECONFIG=$HOME/.kube/vincent-k3s.yaml \
  kubectl logs -n lendora-sta-fides-bff deploy/fides-bff --since=30m
```

Patterns checked:

```text
91990002|91990001|91989999|123456|accessToken|refreshToken|token-secret|applicant_[0-9a-f-]
```

Result: PASS. No matching sensitive fields were found in applicant-api or fides-bff logs for the smoke window.

## Rollback Exercise

Service exercised: applicant-api.

Current working digest:

```text
sha256:8249e6c25693c810c3d59a7ca562823683ea4784bd56a74d907e5a2cefbb1ee4
```

Older digest tested:

```text
sha256:c09813ac85e215d123252feabfe121bc75625ad3062318ee797b024cec7663c3
```

Result:

- Switching to the older digest produced rollout timeout / `CrashLoopBackOff`.
- The overlay was restored to the current digest.
- STA ConfigMap was updated with `APPLICANT_MIGRATIONS_ENABLED=false` after schema bootstrap to avoid rerunning Flyway against the existing database.
- applicant-api returned to `1/1` Ready.

Rollback conclusion: digest rollback mechanics were exercised and restoration to the known-good digest was proven. The older digest is not a known-good runtime candidate for the current STA data state, so it is not retained as a rollback target.

## Residual Risk

- Final `lendora-*` public DNS / certificate names are unresolved.
- A durable rollback candidate should be captured after the next successful release digest, because the tested older applicant-api digest is incompatible with the current STA state.
- Migration lifecycle for STA should be separated from steady-state pod restarts instead of relying on `APPLICANT_MIGRATIONS_ENABLED=false`.
- OTEL collector / trace evidence is not wired in this closure; readiness, Consul health, smoke, and sensitive log checks provide the current merge evidence.
