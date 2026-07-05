# LEN-211 Buf Checks

检查时间：2026-07-05T18:09:34+08:00

## Summary

`quote.proto` 已删除 `CreateQuoteRequest.trace_id`，并保留字段号和字段名：

```proto
reserved 5;
reserved "trace_id";
```

该删除是 LEN-211 明确要求的硬切：trace/log 关联只能来自 OpenTelemetry Context，不再通过业务契约、command、domain 或数据库字段表达。

## Commands

| Repo | Command | Result |
|---|---|---|
| idl-repo | `buf lint` | PASS |
| idl-repo | `buf breaking --against .git#branch=master` | FAIL，expected hard-cut breaking |
| idl-repo | `find . -maxdepth 3 \( -name 'buf.gen.yaml' -o -name 'buf.gen.yml' \) -print` | `./buf.gen.yaml` |

## Breaking Output

```text
vesta/lendora/quote/v1/quote.proto:15:1:Previously present field "5" with name "trace_id" on message "CreateQuoteRequest" was deleted.
```

## Decision

- 该 breaking change 不复用字段号或字段名，降低未来误用风险。
- 业务仓同步移除 fides-bff `CreateQuoteRequest.trace_id` 写入，以及 quote-api command、domain、repository、migration 中的 `trace_id` 字段。
- 风险接受依据：LEN-211 BR6、BR7 和 AC7 要求硬切，不保留 fallback 或双轨兼容。
