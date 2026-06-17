---
requirement_id: "LEN-21"
gate_id: "service-repo-check"
gate_name: "服务仓库检查门禁"
stage: "4.3"
checked_by: "service_repo_checker"
checked_at: "2026-06-16T10:30:00+08:00"
result: "PASS"
blocks_next_stage: false
---

<!-- Generated from service-repo-check.gate.json. Do not edit blocking fields here. -->

# 服务仓库检查门禁

## 结论

受影响服务 fides-bff 已登记且仓库路径与分支就绪，idl 影响为 no，满足服务仓库检查门禁；可进入编码循环与后续合并就绪前置。

## 输入快照

| Path | SHA-256 |
| --- | --- |
| `.service-matrix/dependencies.yaml` | `3ab59dbf36b41d9c8be4df35ea5017618aeeee7a4d250001e570feb9f6b1dce5` |
| `requirements/LEN-21/impact-analysis.md` | `9d0b14a065a2ed8c8334c29329477205357cd977a23ab886d2357799d66b17e1` |
| `requirements/LEN-21/design.md` | `607672b4313a739d6e0c1b36c2a9c85ad6f0d38bfc9c6a9ff7f2c6de9593ea4e` |
| `requirements/LEN-21/tasks.json` | `11a3ac07ed8cdd25dca8d3295b5f15ec646c57f35f6c6c7762b7f46e6b2fe027` |

## 检查项

| Item | Result | Evidence |
| --- | --- | --- |
| 受影响服务存在于服务矩阵 | `PASS` | fides-bff 登记于 .service-matrix/dependencies.yaml（module: frontend, idl_required: false）。 |
| repo_path 解析到实际业务仓目录 | `PASS` | repo_path {business-repo}/services/backend/fides-bff 实际存在（T1 已创建 Go/Kratos 工程）。 |
| Harness 仓、业务仓、IDL 仓分支一致 | `PASS` | harness-repo 与 business-repo 均在 feature/fides-bff/LEN-21；idl-repo 不涉及（fides-bff idl_required=false，本需求无 .proto 变更）。 |
| idl_required 服务已准备 IDL 仓/proto_path/buf v2 | `PASS` | N/A：fides-bff idl_required=false，不消费/产出 protobuf 契约；引入的是 HTTP/REST 契约 /api/v1。无需契约仓与 buf 配置。 |
| 人工批准记录存在 | `PASS` | 服务仓库检查批准源 impact-analysis.md front matter status=approved, approved_by=forest。 |

## 阻塞问题

无。

## 警告

| Issue | Follow-up action | Owner |
| --- | --- | --- |
| 首个下游 gRPC 调用任务前需为 idl-go-repo 补 go.mod + replace（设计阶段风险延续） | 在首个业务端点任务（晚于 T1）引入下游客户端时处理；T1 不依赖契约 | `backend` |

## 豁免

- Required: `false`

## 外部证据

无。

