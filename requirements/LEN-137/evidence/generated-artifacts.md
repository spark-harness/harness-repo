# LEN-137 Generated Contract Artifacts

## Scope

- Requirement: `LEN-137`
- Tasks: `T2`, `T3`, `T4`, `T5`, `T6`
- Checked at: `2026-06-29T01:08:01+08:00`

## IDL Release

- `idl-repo` branch: `feature/LEN-137-identity-information`
- Published commit: `2519ad9`
- Published tag: `v0.2.4`

## Consumed Artifacts

| Consumer | Artifact | Version | Result |
|---|---|---:|---|
| `applicant-api` | `com.spark.contract:spark-idl-java` | `0.2.4` | consumed locally |
| `origination-api` | `com.spark.contract:spark-idl-java` | `0.2.4` | consumed locally |
| `fides-bff` | `github.com/spark-harness/idl-go-repo` | `v0.2.4` | consumed locally |
| `fides-web` | `@spark-harness/idl-ts-client` | `v0.2.4` | consumed locally |

## Frontend Generated SDK Boundary

Command:

```text
rg -n "@spark-harness/idl-ts-client" apps/fides-web/src
```

Result: PASS.

Observed imports:

- `apps/fides-web/src/infrastructure/identity-profile/rest-identity-profile-gateway.ts`
- `apps/fides-web/src/infrastructure/mobile-verification/rest-otp-auth-gateway.ts`

Conclusion: generated OpenAPI TypeScript SDK is used by FE infrastructure adapters only. Generated types do not leak into `domain`, `application`, `adapters`, or `presentation`.
