# 名称与域名重查

2026-10-08（Asia/Shanghai）。用户已批准 PetWaymark / 宠途路标；本次保留该名称。以下采用中断前同日实际查询的证据，续做时未把旧请求伪记为新请求。

| 查询 | 实际结果 | 可得出的结论 |
|---|---|---|
| [GitHub 仓库名搜索](https://api.github.com/search/repositories?q=petwaymark+in:name&per_page=100) | HTTP 200，0 项，`incomplete_results=false` | 本次未找到仓库名匹配；未查用户名 |
| [npm](https://registry.npmjs.org/petwaymark) | HTTP 404 | 未找到该精确包名 |
| [PyPI](https://pypi.org/pypi/petwaymark/json) | HTTP 404 | 未找到该精确包名 |
| [petwaymark.com RDAP](https://rdap.verisign.com/com/v1/domain/petwaymark.com) | HTTP 404，空正文 | 未返回注册对象；空正文不足以保证可注册 |
| [petwaymark.net RDAP](https://rdap.verisign.com/net/v1/domain/petwaymark.net) | HTTP 404，空正文 | 同上 |
| [petwaymark.org RDAP](https://rdap.publicinterestregistry.org/rdap/domain/petwaymark.org) | HTTP 404，Object not found | 查询时未找到注册对象 |
| [petwaymark.dev RDAP](https://pubapi.registry.google/rdap/domain/petwaymark.dev) | HTTP 404，Not Found | 查询时未找到注册对象 |
| [petwaymark.app RDAP](https://pubapi.registry.google/rdap/domain/petwaymark.app) | HTTP 404，Not Found | 查询时未找到注册对象 |
| petwaymark.io | IANA 快照无 RDAP 端点；`whois.nic.io:43` 超时 | **注册状态待核** |
| petwaymark.cn | IANA 快照无 RDAP 端点；`whois.cnnic.cn:43` 超时 | **注册状态待核** |
| petwaymark.com.cn | 同上，WHOIS 超时 | **注册状态待核** |

原始元数据：[HTTP 查询](../research/week1/name-check.json)、[WHOIS 尝试](../research/week1/whois-check.json)、[IANA bootstrap 快照](../research/week1/iana-rdap-bootstrap.json)。请求时间约 01:35 UTC／09:35 北京时间，精确时间、URL、响应摘要和哈希在 JSON 内。RDAP 端点由 IANA DNS bootstrap 选取，没有用搜索结果或 DNS 无解析来推断未注册。

本次只覆盖上述 8 个域名。注册局保留名、溢价、平台保留政策、商标及近似名称未核实；404 不构成可注册保证。发布前再查，尤其补齐 3 个 WHOIS 超时项。没有注册、占名、创建外部仓库或发布包。
