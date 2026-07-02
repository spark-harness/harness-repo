---
requirement_id: "LEN-157"
evidence_type: "implementation"
updated_at: "2026-07-02T18:57:58Z"
repos:
  - gitops-repo
  - harness-repo
---

# LEN-157 Implementation Evidence

## Implementation

- fides dev-1 / sta-1 public runtime config now writes `bffBaseUrl: "/api/v1"`。
- fides dev-1 / sta-1 Deployment now injects internal fides-bff Service URL into `FIDES_BFF_BASE_URL`。
- fides runtime-config Consul Job preserves existing `browserTracing` private runtime values while replacing `bffBaseUrl`。
- fides-bff dev-1 / sta-1 ConfigMap enables OTEL。
- fides-bff dev-1 / sta-1 Deployment enables Consul config source at `spark/lendora/{env}/fides-bff/config.yaml`。
- fides-bff runtime-config Consul Job writes non-secret OTEL defaults and preserves existing endpoint / headers.
- applicant-api Deployment now injects `OTEL_EXPORTER_OTLP_TRACES_ENDPOINT` from `applicant-api-runtime/otlp-traces-endpoint` so explicit env overrides the empty ConfigMap default when OTLP export is enabled.

## Test-First Exception

This is a config-only GitOps change. No production code behavior test was added.

Replacement verification:

```text
kubectl kustomize apps/fides/overlays/dev-1
kubectl kustomize apps/fides/overlays/sta-1
kubectl kustomize apps/fides-bff/overlays/dev-1
kubectl kustomize apps/fides-bff/overlays/sta-1
kubectl kustomize apps/applicant-api/overlays/dev-1
kubectl kustomize apps/applicant-api/overlays/sta-1
Result: PASS
```

## Static Verification

```text
fides_dev_internal_url=1
fides_sta_internal_url=1
fides_dev_public_api_v1=2
fides_sta_public_api_v1=2
old_public_bff_url_count=0
bff_dev_otel_true=3
bff_sta_otel_true=3
bff_dev_config_path=2
bff_sta_config_path=2
committed_secret_pattern_count=0
```

```text
merge-preserves-fides-browserTracing
merge-preserves-fides-bff-otel
```

## Live Baseline Before Merge

- dev-1 and sta-1 live fides Deployments still used old public BFF URLs before this change.
- dev-1 and sta-1 live fides Consul runtime config still used old public BFF URLs before this change.
- live fides browser tracing private values existed in Consul and were not copied into Git evidence.
- live `fides-bff-runtime` Secret only exposed `token-secret`; fides-bff tracing private values must be provided through Consul runtime config.

## GitOps Merge Evidence

- gitops-repo PR #34 merged at `7c84e1818bedaad4377bd8b2612ce3658328ff38`: configured fides public `/api/v1`, server-only internal BFF URLs, fides-bff OTEL, and fides-bff Consul runtime config.
- gitops-repo PR #35 merged at `d2145f02426eb91fcc062e91721cb1d8bb988705`: promoted sta fides/fides-bff image digests to include LEN-156 runtime hardening.
- gitops-repo PR #36 merged at `12f2cbde5db5ea33bd25ec5018fd0ade822f394f`: injected applicant-api OTLP endpoint from Secret.

## Post-Merge Verification

Argo CD:

```text
lendora-dev-1-applicant-api  Synced  Healthy  12f2cbde5db5ea33bd25ec5018fd0ade822f394f
lendora-sta-1-applicant-api  Synced  Healthy  12f2cbde5db5ea33bd25ec5018fd0ade822f394f
lendora-dev-1-fides          Synced  Healthy  12f2cbde5db5ea33bd25ec5018fd0ade822f394f
lendora-sta-1-fides          Synced  Healthy  12f2cbde5db5ea33bd25ec5018fd0ade822f394f
lendora-dev-1-fides-bff      Synced  Healthy
lendora-sta-1-fides-bff      Synced  Healthy
```

Runtime config and BFF health:

```text
dev-1 runtime-config: bffBaseUrl=/api/v1, browserTracing endpoint present, header key x-sentry-auth present
sta-1 runtime-config: bffBaseUrl=/api/v1, browserTracing endpoint present, header key x-sentry-auth present
dev-1 /api/v1/health: {"status":"ok","version":"dev"}
sta-1 /api/v1/health: {"status":"ok","version":"dev"}
```

Consul health:

```text
dev-1 applicant-api passing count: 1
sta-1 applicant-api passing count: 1
```

Cross-service smoke:

```text
dev-1 POST /api/v1/auth/otp:send trace_id=15715715715715715715715715715701 result=200 challengeId=true
sta-1 POST /api/v1/auth/otp:send trace_id=15715715715715715715715715715702 result=200 challengeId=true
```

Trace/log correlation:

```text
dev-1 fides-bff: operation=POST /api/v1/auth/otp:send trace_id=15715715715715715715715715715701 status_code=200
dev-1 applicant-api: service=applicant-api operation=send_otp result=success trace_id=15715715715715715715715715715701
sta-1 fides-bff: operation=POST /api/v1/auth/otp:send trace_id=15715715715715715715715715715702 status_code=200
sta-1 applicant-api: service=applicant-api operation=send_otp result=success trace_id=15715715715715715715715715715702
```

Secret handling:

```text
dev-1 applicant-api-runtime: otlp-traces-endpoint key present
sta-1 applicant-api-runtime: otlp-traces-endpoint key present
secret values: not printed and not committed
```
