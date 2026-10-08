# Week 1 evidence / 第 1 周证据

研究日期为 2026-10-08。保留中断前实际获取的证据；续做增加分析和核对记录，不改写历史抓取时间。

| 文件 | 用途及限制 |
|---|---|
| [name-check.json](name-check.json) | GitHub、npm、PyPI 与 RDAP 查询元数据；404 不是可注册保证 |
| [whois-check.json](whois-check.json) | `.io`、`.cn`、`.com.cn` WHOIS 超时；状态未知 |
| [iana-rdap-bootstrap.json](iana-rdap-bootstrap.json) | 当次 IANA DNS bootstrap；来源条款保留 |
| [petra-manifest.json](petra-manifest.json) | 固定 commit、数据版本、6 文件哈希与 56 条索引摘要 |
| [petra/README.md](petra/README.md) | 上游原样快照入口，第三方文档链接按原上游语境解释 |
| [official-fetches.json](official-fetches.json) | 官方页面及许可文本的历史 HTTP 状态／哈希；200 不等于完成规则审查 |
| [official-review.md](official-review.md) | 续做时官方正文核对、定位与待核事项 |

Petra 快照未经修改，含 README、LICENSE、CONTRIBUTING、index、US→DE 和 US→NL。没有导入可执行规则；快照不应放进 `data/rules/`。归属与例外见 [THIRD_PARTY_NOTICES](../../../THIRD_PARTY_NOTICES.md)。空 `reviewed_by` 和 `human_reviewed_at=null` 表示未完成人工发布复核。

`python3 scripts/check_scaffold.py`（仓库根目录）离线检查快照哈希、覆盖清单、JSON 与项目本地链接。上游原样文档包含本次未下载的文件链接，校验器会跳过该第三方目录的 Markdown 链接检查；并不伪造这些文件。
