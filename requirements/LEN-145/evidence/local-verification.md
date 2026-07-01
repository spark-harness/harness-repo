# LEN-145 Local Verification

## Scope

- `quote-api` Consul Config and OpenTelemetry configuration model.
- `origination-api` Consul Config and OpenTelemetry configuration model.
- GitOps dev-1 / sta-1 overlay rendering for quote/origination.
- Secret hygiene for Sentry OTLP values.

## Commands

```bash
cd /Users/forest/Code/spark/.worktrees/LEN-145/business-repo/apps/quote-api
mvn -q -Dtest=QuoteConfigurationModelTest test
mvn -q test
```

Result: PASS.

```bash
cd /Users/forest/Code/spark/.worktrees/LEN-145/business-repo/apps/origination-api
mvn -q -Dtest=OriginationConfigurationModelTest test
mvn -q test
```

Result: PASS.

```bash
cd /Users/forest/Code/spark/.worktrees/LEN-145/gitops-repo
kubectl kustomize apps/quote-api/overlays/dev-1 >/tmp/quote-dev.yaml
kubectl kustomize apps/quote-api/overlays/sta-1 >/tmp/quote-sta.yaml
kubectl kustomize apps/origination-api/overlays/dev-1 >/tmp/orig-dev.yaml
kubectl kustomize apps/origination-api/overlays/sta-1 >/tmp/orig-sta.yaml
```

Result: PASS.

```bash
git -C /Users/forest/Code/spark/.worktrees/LEN-145/business-repo diff --check
git -C /Users/forest/Code/spark/.worktrees/LEN-145/gitops-repo diff --check
git -C /Users/forest/Code/spark/.worktrees/LEN-145/harness-repo diff --check
```

Result: PASS.

```bash
rg -n "3e8dfa96|f0380bdb|ingest\\.us\\.sentry\\.io|sentry_key=|4511660414992384|4511660418203648" \
  /Users/forest/Code/spark/.worktrees/LEN-145/harness-repo \
  /Users/forest/Code/spark/.worktrees/LEN-145/business-repo \
  /Users/forest/Code/spark/.worktrees/LEN-145/gitops-repo \
  -g '!**/target/**' -S
```

Result: PASS for LEN-145 changes. The only matches are existing `applicant-api` example/test placeholders using `sentry_key=public`; no real Sentry DSN, public key, project endpoint, or auth header is introduced by this requirement.

## Runtime Evidence Still Needed

After PR merge and Argo sync:

1. Re-run quote/origination Consul seed Jobs in dev-1.
2. Confirm existing Consul endpoint/header lines remain, with values redacted.
3. Restart quote/origination deployments.
4. Trigger quote/origination smoke flow.
5. Query Sentry or the OTLP receiver for `service.name=quote-api`, `service.name=origination-api`, and `deployment.environment=dev-1`.
6. Repeat for sta-1.
