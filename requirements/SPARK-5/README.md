# SPARK-5

## Title

User Disable And Restore Login Control

## Status

- Requirement: approved
- Impact analysis: approved
- Design: approved
- Tasks: approved

## Scope

`user-api` 新增禁用和恢复用户的 gRPC API。被禁用用户再次通过手机号验证码注册/登录时必须被拒绝，恢复后可以重新登录。
