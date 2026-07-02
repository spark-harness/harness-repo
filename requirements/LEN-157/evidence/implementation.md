---
requirement_id: "LEN-157"
evidence_type: "implementation"
updated_at: "2026-07-02T18:20:00Z"
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

## Test-First Exception

This is a config-only GitOps change. No production code behavior test was added.

Replacement verification:

```text
kubectl kustomize apps/fides/overlays/dev-1
kubectl kustomize apps/fides/overlays/sta-1
kubectl kustomize apps/fides-bff/overlays/dev-1
kubectl kustomize apps/fides-bff/overlays/sta-1
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

## Post-Merge Verification

Pending until GitOps PR is merged and Argo sync completes.

