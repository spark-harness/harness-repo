# Buf And Contract Checks

验证时间：2026-07-05T00:32:32+08:00

工作目录：`/Users/forest/Code/spark/.worktrees/LEN-176/idl-repo`

## Commands

```bash
buf lint
buf generate --template buf.gen.java.yaml
buf generate --template buf.gen.go.yaml
buf breaking --against '.git#branch=master'
```

## Result

全部通过。

## Generated Outputs

- `../idl-java-repo/src/main/java/com/vesta/lendora/quote/v1/*`
- `../idl-java-repo/src/main/grpc-java/com/vesta/lendora/quote/v1/QuoteServiceGrpc.java`
- `../.generated/idl-go/vesta/lendora/quote/v1/quote.pb.go`
- `../.generated/idl-go/vesta/lendora/quote/v1/quote_grpc.pb.go`

## Compatibility

`quote.proto` 是新增 protobuf package 和新增 service。`buf breaking --against '.git#branch=master'` 通过，未修改或删除 master 上已有字段、RPC 或 service。
