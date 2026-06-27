# Runtime Smoke

## Scope

验证 `fides-bff` pricing facade 在真实 BFF 进程中可访问，并能调用 quote-api HTTP 下游。

由于 LEN-135 才交付 Kubernetes/GitOps 下游地址、端口、服务发现和超时配置，本 smoke 使用本地 `QUOTE_HTTP_BASE_URL` 指向临时 quote-api stub。该验证覆盖 BFF runtime wiring、auth filter、config、HTTP client、身份传播、trace propagation 和响应契约。

## Setup

启动本地 quote-api stub：

```bash
python3 /tmp/len132_quote_stub.py
```

启动 BFF：

```bash
QUOTE_HTTP_BASE_URL=http://127.0.0.1:18080 \
SERVER_HTTP_ADDR=127.0.0.1:18081 \
REGISTRY_CONSUL_ENABLED=false \
AUTH_TOKEN_SECRET=local-dev-token-secret \
go run ./cmd/fides-bff -conf configs/config.yaml
```

## Request

```bash
curl -i -X POST http://127.0.0.1:18081/api/v1/pricing/quotes \
  -H "Authorization: Bearer <local-hmac-token>" \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: len132-smoke-1" \
  -H "X-Applicant-Id: attacker" \
  -H "traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01" \
  -H "tracestate: vendor=state" \
  --data '{"productCode":"PIL","amount":"100000.00","term":12,"purpose":"debt_consolidation"}'
```

## Response

```http
HTTP/1.1 200 OK
Content-Type: application/json
X-Correlation-Id: 4bf92f3577b34da6a3ce929d0e0e4736
X-Trace-Id: 4bf92f3577b34da6a3ce929d0e0e4736
```

```json
{"quoteId":"quote_smoke","monthly":"8560.75","apr":"0.0520","totalInterest":"2729.00","totalPayable":"102729.00","validUntil":"2026-06-28T03:00:00Z"}
```

## Downstream Stub Record

```json
{
  "path": "/api/v1/pricing/quotes",
  "x_applicant_id": "applicant_001",
  "traceparent": "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01",
  "tracestate": "vendor=state",
  "body": "{\"productCode\":\"PIL\",\"amount\":\"100000.00\",\"term\":12,\"purpose\":\"debt_consolidation\"}"
}
```

## Result

PASS.

- BFF endpoint 可访问。
- 响应字段符合前端契约。
- 外部伪造 `X-Applicant-Id: attacker` 未被信任。
- 下游收到 principal 派生的 `x_applicant_id=applicant_001`。
- 下游收到 `traceparent` 和 `tracestate`。

## Runtime Boundary

LEN-132 未修改 GitOps runtime 配置。`lendora-sta` 中 BFF 指向真实 quote-api 的运行时 smoke 由 LEN-135 完成。
