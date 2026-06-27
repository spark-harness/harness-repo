---
requirement_id: "LEN-135"
evidence_type: "local-verification"
verified_by: "Codex"
verified_at: "2026-06-28T06:56:20+08:00"
status: "pass"
---

# Local Verification

## Scope

本证据覆盖 `gitops-repo` 中 fides-bff lendora-sta runtime 配置的本地渲染验证。LEN-135 不修改业务代码、protobuf IDL、generated contracts 或前端代码。

## Inputs

| Item | Value |
|---|---|
| Branch | `feature/LEN-135-fides-bff-downstream-config` |
| Base | `origin/master` at `9882f96` |
| GitOps commit under review | `ce2013f` plus uncommitted auth Secret reference before final commit |
| Changed manifests | `apps/fides-bff/base/configmap.yaml`, `apps/fides-bff/base/deployment.yaml` |

## Commands And Results

| Command | Result |
|---|---|
| `kubectl kustomize apps/fides-bff/overlays/lendora-sta` | PASS; rendered 151 lines |
| `kubectl kustomize clusters/lendora-sta` | PASS; rendered 229 lines |
| `rg 'service_name: (quote-api|origination-api)|timeout: 3s|base_url: ""|token_mode: hmac|access_token_ttl: 1h|AUTH_TOKEN_SECRET|fides-bff-runtime|token-secret' /tmp/len135-fides-bff-render.yaml` | PASS |

## Render Evidence

Rendered fides-bff overlay contains:

- `quote.consul.service_name: quote-api`
- `quote.consul.address: consul.lendora-sta-consul.svc.cluster.local:8500`
- `quote.http.base_url: ""`
- `quote.http.timeout: 3s`
- `origination.consul.service_name: origination-api`
- `origination.consul.address: consul.lendora-sta-consul.svc.cluster.local:8500`
- `origination.http.base_url: ""`
- `origination.http.timeout: 3s`
- `auth.token_mode: hmac`
- `auth.access_token_ttl: 1h`
- Deployment env `AUTH_TOKEN_SECRET` from Secret `fides-bff-runtime`, key `token-secret`

## Requirement Mapping

| Acceptance Criteria | Evidence |
|---|---|
| AC1 | fides-bff overlay kustomize render PASS and includes quote/origination downstream config |
| AC2 | `clusters/lendora-sta` kustomize render PASS |
| AC3 | Rendered ConfigMap includes quote/origination Consul service names, Consul address, 3s timeout, auth token mode and TTL |
| BR5 | `base_url` remains empty for both quote and origination |
| BR7, BR10 | GitOps stores only Secret reference; no Secret value is committed |

