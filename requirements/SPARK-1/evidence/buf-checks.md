# SPARK-1 Buf Evidence

## Commands

```text
buf lint
buf generate
buf breaking --against '.git#branch=master'
```

## Current Evidence

- `idl-repo/buf.yaml` uses `version: v2`.
- `idl-repo/buf.gen.yaml` uses `version: v2`.
- `idl-repo/vesta/spark/user/v1/ping.proto` is the protobuf source for `PingService`.

## Status

This evidence file records the expected contract checks for the Harness lifecycle sample. A CI run or local Buf run should replace this section with raw command output before merge.
