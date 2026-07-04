# Buf And Contract Checks

验证时间：2026-07-05T02:26:13+08:00

工作目录：`/Users/forest/Code/spark/.worktrees/LEN-180/idl-repo`

## Commands

```bash
buf lint
buf generate --template buf.gen.java.yaml
buf breaking --against '.git#branch=master'
```

## Result

全部通过。

## Generated Outputs

- `../idl-java-repo/src/main/java/com/vesta/lendora/origination/v1/*LoanApplication*`
- `../idl-java-repo/src/main/grpc-java/com/vesta/lendora/origination/v1/OriginationLoanApplicationServiceGrpc.java`

## Compatibility

`loan_application.proto` 位于 `vesta.lendora.origination.v1`。`buf breaking --against '.git#branch=master'` 通过，未删除或复用 master 上已有字段、RPC 或 service。
