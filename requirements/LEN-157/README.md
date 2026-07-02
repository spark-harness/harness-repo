---
current_stage: "4.4"
---

# LEN-157

[GitOps] dev/sta 配置内网 BFF 地址并验证跨服务 trace。

本需求承接 LEN-156。fides-web 浏览器侧只访问同源 `/api/v1`，服务端代理通过
`FIDES_BFF_BASE_URL` 访问集群内 fides-bff。

