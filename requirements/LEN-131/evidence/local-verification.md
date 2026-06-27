---
requirement_id: "LEN-131"
evidence_type: "local-verification"
verified_by: "Codex"
verified_at: "2026-06-28T02:54:35+08:00"
status: "pass"
---

# Local Verification

## Scope

本证据覆盖 LEN-131 的 business-repo、gitops-repo 本地验证和 live server dry-run。

不是什么：它不证明 Argo CD Application 已 Healthy/Synced，因为当前 vincent-k3s 没有 `argocd` namespace，也没有 `applications.argoproj.io` / `appprojects.argoproj.io` CRD。

它是什么：它证明 quote-api 镜像构建入口、Consul runtime 支撑、quote DB 初始化 Job、GitOps overlay、cluster app-of-apps manifest 和 image release workflow 更新可构建、可渲染、可 dry-run。

## Commands

| Command | Working Directory | Result |
|---|---|---|
| `mvn test` | `business-repo/apps/quote-api` | PASS，13 tests，0 failures，0 errors |
| `mvn spotless:check` | `business-repo/apps/quote-api` | PASS，29 Java files clean |
| `python3 tooling/java-quality/java_quality.py run-project spring-starter --skip-unselected` | `business-repo` | PASS，Spotless、Checkstyle、test、SpotBugs |
| `python3 tooling/java-quality/java_quality.py run-project quote-api --skip-unselected` | `business-repo` | PASS，Spotless、Checkstyle、test、SpotBugs |
| `kubectl kustomize apps/quote-api/overlays/lendora-sta` | `gitops-repo` | PASS，214 lines |
| `kubectl kustomize apps/lendora-sta-dependencies/overlays/sta` | `gitops-repo` | PASS，309 lines |
| `kubectl kustomize clusters/lendora-sta` | `gitops-repo` | PASS，198 lines |
| `GODEBUG=tlsmlkem=0 kubectl --kubeconfig ~/.kube/vincent-k3s.yaml --context vincent-k3s apply --server-side --dry-run=server -f clusters/lendora-sta/namespaces.yaml` | `gitops-repo` | PASS；已有资源出现 last-applied migration warning，非阻塞 |
| `kubectl kustomize apps/lendora-sta-dependencies/overlays/sta \| GODEBUG=tlsmlkem=0 kubectl --kubeconfig ~/.kube/vincent-k3s.yaml --context vincent-k3s apply --server-side --dry-run=server -f -` | `gitops-repo` | PASS；已有资源出现 last-applied migration warning，非阻塞 |

## Behavior Evidence

| Acceptance | Evidence |
|---|---|
| AC1 | quote-api overlay、lendora-sta dependencies overlay 和 cluster app-of-apps kustomize 均 PASS。 |
| AC2 | `apps/quote-api/Dockerfile` 已构建并推送 `ghcr.io/spark-harness/quote-api:len131-final-20260628025928`；digest 为 `sha256:551b29fdf5f31be37ed962890e5d61b89163d27d2810087a041cd7074124df63`。image release workflow 已加入 quote-api build、scan、digest promotion 和 render validation。 |
| AC5 | `HealthHttpAdapterTest.ready_whenDependencyIsDown_returnsServiceUnavailable` 验证 dependency DOWN 时 `/ready` 返回 503 和 `NOT_READY`；`QuoteHttpAdapterTest.ready_withDatabaseAvailable_returnsReady` 验证 DB 可用时 READY。 |
| AC7 | `ConsulServiceRegistrationTest` 验证注册 request 使用 `quote-api.lendora-sta-quote-api.svc.cluster.local`、port 80 和 `/ready` health check。 |

## Argo CD Environment Check

| Check | Result |
|---|---|
| `kubectl api-resources \| rg "applications.argoproj.io|appprojects.argoproj.io"` | no matches |
| `kubectl get ns argocd` | `Error from server (NotFound): namespaces "argocd" not found` |

结论：GitOps manifest 已纳入 Argo CD Application 目标状态，但当前 vincent-k3s 只有 Argo Workflows，不具备 live Argo CD 同步能力。AC3 只能记录为环境缺口，不能伪造 Healthy/Synced 证据。

