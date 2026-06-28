---
requirement_id: "LEN-5"
evidence_type: "predecessor-matrix"
verified_by: "Codex"
verified_at: "2026-06-28T13:13:00+08:00"
status: "pass-with-warnings"
---

# Predecessor Matrix

LEN-5 Story 验收依赖前序 ticket 的已交付边界。本证据只汇总 gate 结论和 Story 影响，不重复复制实现细节。

## Gate Summary

| Ticket | Scope | Merge Gate | Story Impact |
|---|---|---|---|
| LEN-22 | BFF token 校验、principal context、`x-applicant-id`、traceparent | PASS | 受保护 pricing/draft API 的身份与 tracing 前置已满足；公网 OTP 登录后业务接口以真实 bearer token 成功 |
| LEN-10 | `quote-api` 试算、quote DB、内部 Quote 校验边界 | PASS | AC1、AC2、AC3 的服务端 quote 能力已实现 |
| LEN-131 | quote-api lendora-sta 部署、quote DB、readiness、service discovery | WARN | quote-api runtime 可用；Argo CD 不存在作为环境 WARN |
| LEN-132 | BFF pricing facade | PASS | 前端通过 BFF 调 pricing，不直连 Java 服务 |
| LEN-9 | origination-api 草稿创建、PATCH、GET、幂等、quote 校验 | PASS | AC4、AC5 的 draft 能力已实现 |
| LEN-134 | origination-api lendora-sta 部署、application DB、readiness、service discovery | WARN | origination-api runtime 可用；Argo CD 不存在作为环境 WARN |
| LEN-133 | BFF origination facade | PASS | 前端通过 BFF 调 draft create/get/patch |
| LEN-135 | fides-bff quote/origination 下游配置和 protected smoke | WARN | BFF 下游 discovery、timeout 和受保护 smoke 可用；Argo CD/环境 drift 为 WARN |
| LEN-11 | 前端第二页接真实 pricing/draft API，UI 参照 code.html，Continue 不跳转 | PASS | 当前公网浏览器验证已覆盖 OTP 登录、真实 pricing 展示、Continue 静默保存、不跳转 |

## Source Gate Decisions

已读取：

- `requirements/LEN-22/gates/merge-readiness.gate.json`
- `requirements/LEN-10/gates/merge-readiness.gate.json`
- `requirements/LEN-131/gates/merge-readiness.gate.json`
- `requirements/LEN-132/gates/merge-readiness.gate.json`
- `requirements/LEN-9/gates/merge-readiness.gate.json`
- `requirements/LEN-134/gates/merge-readiness.gate.json`
- `requirements/LEN-133/gates/merge-readiness.gate.json`
- `requirements/LEN-135/gates/merge-readiness.gate.json`
- `requirements/LEN-11/gates/merge-readiness.gate.json`

## Current Runtime Closure

- Public OTP send/verify now returns HTTP 200. The earlier `applicant_unavailable` warning is resolved in the current live runtime.
- `fides` runtime config is served by `/api/runtime-config`, and the live deployment no longer carries stale `NEXT_PUBLIC_*` env vars.
- Public browser flow reaches the loan request screen, displays real pricing values, and Continue saves via BFF without navigation.

## Warnings

- 当前 `vincent-k3s` 没有 Argo CD，LEN-131、LEN-134、LEN-135 均以 runtime functional smoke 证明服务可用，不声称 Argo CD Healthy/Synced。
- `fides` pod port-forward 仍因容器监听地址限制失败；公网 Caddy 入口和 Kubernetes Service 可访问，不影响用户访问域名。

## Result

前序交付边界足以执行 LEN-5 Story 验收；当前公网与集群 runtime 证据证明 AC1-AC5 已通过。剩余 WARN 均为环境/运维观测 caveat，不阻塞用户通过 `https://api.fuzzytails.fun` 访问和完成贷款请求主链路。
