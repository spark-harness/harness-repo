---
requirement_id: "LEN-134"
evidence_type: "local-verification"
verified_by: "Codex"
verified_at: "2026-06-28T05:32:24+08:00"
status: "pass"
---

# Local Verification

## Scope

本证据覆盖 LEN-134 的 business-repo、gitops-repo 本地验证和 live server dry-run。

不是什么：它不证明 Argo CD Application 已 Healthy/Synced，因为当前 vincent-k3s 没有 `argocd` namespace，也没有 `applications.argoproj.io` / `appprojects.argoproj.io` CRD。

它是什么：它证明 origination-api 镜像构建入口、Consul runtime 支撑、application DB 初始化 Job、GitOps overlay、cluster app-of-apps manifest、image release workflow 和运行时依赖修复可构建、可渲染、可验证。

## Revisions

| Repo | Branch | Base Commit |
|---|---|---|
| business-repo | `feature/LEN-134-origination-api-deploy` | `e2ac459` |
| gitops-repo | `feature/LEN-134-origination-api-deploy` | `02b30e6` |
| harness-repo | `feature/LEN-134-origination-api-deploy` | `d7979aa` |

## Commands

| Command | Working Directory | Result |
|---|---|---|
| `mvn test` | `business-repo/apps/origination-api` | PASS, 22 tests, 0 failures, 0 errors |
| `mvn spotless:check` | `business-repo/apps/origination-api` | PASS, 44 Java files clean |
| `python3 tooling/java-quality/java_quality.py run-project spring-starter --skip-unselected` | `business-repo` | PASS, Spotless, Checkstyle, test, SpotBugs |
| `python3 tooling/java-quality/java_quality.py run-project origination-api --skip-unselected` | `business-repo` | PASS, Spotless, Checkstyle, test, SpotBugs |
| `mvn test` | `business-repo/apps/quote-api` | PASS, 14 tests, 0 failures, 0 errors |
| `mvn spotless:check` | `business-repo/apps/quote-api` | PASS, 29 Java files clean |
| `python3 tooling/java-quality/java_quality.py run-project quote-api --skip-unselected` | `business-repo` | PASS, Spotless, Checkstyle, test, SpotBugs |
| `kubectl kustomize apps/origination-api/overlays/lendora-sta` | `gitops-repo` | PASS, image digest `sha256:94ea8d38c46341db044ede4ef6586e7cef96a2745d28fef2f114b5dd3d35880a` |
| `kubectl kustomize apps/quote-api/overlays/lendora-sta` | `gitops-repo` | PASS, image digest `sha256:52373dfe19fdee70bb3ef081b7c64b280804e5e6cc6de962b0d380f71e2b1915` |
| `kubectl kustomize apps/lendora-sta-dependencies/overlays/sta` | `gitops-repo` | PASS, includes `origination-postgres-init` |
| `kubectl kustomize clusters/lendora-sta` | `gitops-repo` | PASS, includes origination-api Application and namespace labels |
| Python YAML parse over `gitops-repo/**/*.yaml` | `gitops-repo` | PASS, `yaml-ok` |
| `kubectl apply --server-side --dry-run=server -f clusters/lendora-sta/namespaces.yaml` | `gitops-repo` | PASS, historical last-applied warnings are non-blocking |
| `kubectl apply --server-side --dry-run=server -f <dependencies render>` | `gitops-repo` | PASS, historical last-applied warnings are non-blocking |

## Behavior Evidence

| Acceptance | Evidence |
|---|---|
| AC1 | origination-api overlay, quote-api overlay, lendora-sta dependencies overlay and cluster app-of-apps kustomize all PASS. |
| AC2 | `apps/origination-api/Dockerfile` built and pushed `ghcr.io/spark-harness/origination-api:len134-amd64-20260628051359`; digest `sha256:94ea8d38c46341db044ede4ef6586e7cef96a2745d28fef2f114b5dd3d35880a`. Image release workflow includes origination-api build, scan, promotion and render validation. |
| AC5 | `HealthHttpAdapter` aggregates `postgresql` and `consul` probes; `ConsulServiceRegistrationTest` verifies Service DNS, port 80 and `/ready` health check registration. |
| AC6, AC7 | Existing origination-api tests cover create/get/patch, idempotency, owner checks and quote validation; runtime evidence proves live draft write/read. |
| AC8 | Consul registration test and runtime evidence verify service DNS registration. |

## Runtime Blocker Fixes

During LEN-134 runtime smoke, origination draft create initially returned `quote_unavailable`. Root cause was proven with live requests:

- `quote-api` internal GET returned `500` because `@PathVariable` had no explicit name and the packaged runtime did not expose parameter names.
- After fixing `@PathVariable("quoteId")`, internal quote GET returned `200`.
- `origination-api` still returned `quote_unavailable` until `lendora-sta-origination-api` namespace received `lendora.io/quote-api-client=true`, which is required by quote-api NetworkPolicy.

These fixes are included in this ticket because LEN-134 AC6/AC7 require live draft create/get through quote ownership validation.

## Test Note

One concurrent `mvn test` run in `business-repo/apps/origination-api` failed with Surefire `Unable to create test class` while Java quality was running in parallel. The same command was rerun alone immediately after and passed with 22 tests. The passing standalone run is the evidence used for this gate.

## Argo CD Environment Check

| Check | Result |
|---|---|
| `kubectl get ns argocd` | `Error from server (NotFound): namespaces "argocd" not found` |
| `kubectl api-resources \| rg "applications.argoproj.io\|appprojects.argoproj.io"` | no matches |

结论：GitOps manifest 已纳入 Argo CD Application 目标状态，但当前 vincent-k3s 没有 live Argo CD 同步能力。AC3 只能记录为环境 WARN，不能伪造 Healthy/Synced 证据。
