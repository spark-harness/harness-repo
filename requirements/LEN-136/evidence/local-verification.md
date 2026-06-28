# LEN-136 Local Verification Evidence

## Scope

- Requirement: LEN-136
- Verified at: `2026-06-28T17:32:54+08:00`
- Branch: `feature/LEN-136-argocd-dev1-sta1`
- Harness HEAD: `1284146`
- GitOps HEAD: `4f13f72`

## Result

PASS for local GitOps rendering, YAML parsing, static isolation guards, PostgreSQL database declaration consistency, and fides-bff Consul service-name override tests.

Live cluster rollout evidence is recorded separately in `runtime-smoke.md`.

## Kustomize Rendering

Ran in `gitops-repo`:

```bash
rm -f /tmp/len136-*.yaml
for path in clusters/lendora-shared clusters/lendora-dev-1 clusters/lendora-sta-1 apps/lendora-shared-dependencies/overlays/shared; do
  /usr/local/bin/kubectl kustomize "$path" >/tmp/len136-$(printf '%s' "$path" | /usr/bin/tr / -).yaml
done
for env in dev-1 sta-1; do
  for app in applicant-api quote-api origination-api fides-bff fides; do
    /usr/local/bin/kubectl kustomize "apps/$app/overlays/$env" >/tmp/len136-$app-$env.yaml
  done
done
```

Result: PASS.

Rendered targets:

| Path | Result |
|---|---|
| `clusters/lendora-shared` | PASS |
| `clusters/lendora-dev-1` | PASS |
| `clusters/lendora-sta-1` | PASS |
| `apps/lendora-shared-dependencies/overlays/shared` | PASS |
| `apps/applicant-api/overlays/dev-1` | PASS |
| `apps/applicant-api/overlays/sta-1` | PASS |
| `apps/quote-api/overlays/dev-1` | PASS |
| `apps/quote-api/overlays/sta-1` | PASS |
| `apps/origination-api/overlays/dev-1` | PASS |
| `apps/origination-api/overlays/sta-1` | PASS |
| `apps/fides-bff/overlays/dev-1` | PASS |
| `apps/fides-bff/overlays/sta-1` | PASS |
| `apps/fides/overlays/dev-1` | PASS |
| `apps/fides/overlays/sta-1` | PASS |

## YAML Parsing

Ran in `gitops-repo`:

```bash
/usr/bin/python3 - <<'PY'
from pathlib import Path
import yaml
paths = []
for root in ['clusters/lendora-shared','clusters/lendora-dev-1','clusters/lendora-sta-1','apps/lendora-shared-dependencies','apps/applicant-api/overlays/dev-1','apps/applicant-api/overlays/sta-1','apps/quote-api/overlays/dev-1','apps/quote-api/overlays/sta-1','apps/origination-api/overlays/dev-1','apps/origination-api/overlays/sta-1','apps/fides-bff/overlays/dev-1','apps/fides-bff/overlays/sta-1','apps/fides/overlays/dev-1','apps/fides/overlays/sta-1']:
    paths.extend(Path(root).rglob('*.yaml'))
for path in sorted(set(paths)):
    with path.open() as f:
        list(yaml.safe_load_all(f))
print(f'PASS yaml parse: {len(set(paths))} files')
PY
```

Result: PASS, 45 YAML files parsed.

## Static Isolation Guard

Ran in `gitops-repo`:

```bash
rg -n "overlays/lendora-sta|clusters/lendora-sta|apps/.*/overlays/sta1|apps/.*/overlays/sta2|config/(applicant-api|quote-api|origination-api|fides-bff|fides)/data|service_name: (applicant-api|quote-api|origination-api|fides-bff)|service-name: (applicant-api|quote-api|origination-api|fides-bff)|lendora-sta-(postgres|redis|consul|applicant-api|quote-api|origination-api|fides-bff|fides)" workflows/templates/github-image-release-workflow-template.yaml clusters/lendora-dev-1 clusters/lendora-sta-1 apps/*/overlays/dev-1 apps/*/overlays/sta-1 /tmp/len136-*.yaml
```

Result: PASS, no matches.

Guard coverage:

- no old `overlays/lendora-sta`, `clusters/lendora-sta`, or `apps/lendora-sta-dependencies` target in the active GitOps state.
- no `sta1` / `sta2` overlay names in the new Lendora targets.
- no old Consul KV path `config/<service>/data`.
- no bare Consul service discovery names for new environment services, including `fides-bff`.
- no old per-service `lendora-sta-*` namespace references in new target paths or rendered output.

## PostgreSQL Database Consistency

Ran in `gitops-repo`:

```bash
for db in dev_1_applicant sta_1_applicant dev_1_quote sta_1_quote dev_1_origination sta_1_origination; do
  rg -q "CREATE DATABASE ${db} OWNER ${db}" apps/lendora-shared-dependencies/base
  rg -q ":5432/${db}" apps/*/overlays/dev-1 apps/*/overlays/sta-1
done
```

Result: PASS.

Verified database / role pairs:

| Environment | Service | Database / Role |
|---|---|---|
| dev-1 | applicant-api | `dev_1_applicant` |
| sta-1 | applicant-api | `sta_1_applicant` |
| dev-1 | quote-api | `dev_1_quote` |
| sta-1 | quote-api | `sta_1_quote` |
| dev-1 | origination-api | `dev_1_origination` |
| sta-1 | origination-api | `sta_1_origination` |

## Runtime Behavior Covered By Static Evidence

- Business namespaces are `lendora-dev-1` and `lendora-sta-1`.
- Shared infrastructure namespaces are `lendora-shared-postgres`, `lendora-shared-redis`, and `lendora-shared-consul`.
- Consul KV keys use `spark/lendora/{env}/{component}/{kind}`.
- Consul service names use `{env}-{service}`.
- `dev-1` service Applications include `syncPolicy.automated`.
- `sta-1` service Applications omit automated sync.
- Image release workflow updates only `apps/*/overlays/dev-1/kustomization.yaml`.
- `sta-1` overlays carry fixed digest values for manual promotion.
- Caddy contains the four target hostnames with `fides` spelling.
- `api.fuzzytails.fun` no longer routes Lendora Web / API traffic.
- GitHub webhook paths use `github.fuzzytails.fun`.
- `fides-bff` supports `registry.consul.service_name`, and dev / sta overlays set `dev-1-fides-bff` / `sta-1-fides-bff`.

## fides-bff Registry Test

Ran in `business-repo/apps/fides-bff`:

```bash
go test ./cmd/fides-bff -run TestNewConsulRegistrar -count=1
```

Result: PASS.

## Runtime Work Still Required

- Install / restore Argo CD CRDs before Argo CD Application sync can be verified.
- Run browser-level login, quote, and draft save checks through the public hostnames.
