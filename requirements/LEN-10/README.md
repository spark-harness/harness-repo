# LEN-10 quote-api Java Spring 试算服务

本目录保存 LEN-10 的需求、影响分析、设计、任务、门禁、审查和验证证据。

## 目标

- 新建 `business-repo/apps/quote-api` Java Spring 服务。
- 创建 pricing quote 并持久化到 quote DB。
- 返回 `quoteId`、`monthly`、`apr`、`totalInterest`、`totalPayable`、`validUntil`。
- 提供内部 Quote 读取/校验边界，校验 applicantId 归属和过期时间。

## 验证边界

- 单元测试覆盖金额/期限区间、计算结果、越界不写库。
- 集成测试覆盖 migration、Quote 写入、读取、归属校验和过期校验。
- 本 ticket 不部署服务；部署和 DB runtime 属于 LEN-131。
