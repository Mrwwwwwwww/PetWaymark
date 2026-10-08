# Draft inventory / 草稿清单

All fifteen records are `draft`, not usable production permissions. Sources were read
on 2026-10-08; no human reviewer has approved them. Format and references pass the
[contract checks](../../docs/en/rule-contract.md). No supported route is added.

十五条均为草稿，2026-10-08 实际查阅，人工复核零；结构通过不表示允许运输，不增加已支持路线。

| Region / 地区 | IDs / 标识 | Scope / 范围 |
|---|---|---|
| CN (3) | `cn.gacc.carried.maximum-count`, `cn.gacc.carried.microchip`, `cn.gacc.carried.health-certificate` | Carried entry only / 仅携带入境 |
| US (4) | `us.cdc.dog.low-risk.minimum-age`, `us.cdc.dog.low-risk.microchip`, `us.cdc.dog.low-risk.receipt`, `us.cdc.cat.arrival-health` | CDC, low-risk-history dogs or cat health / CDC 低风险旅行史犬或猫健康 |
| US domestic (1) | `us.ca.domestic.health` | Partial CA health draft; no full state package / CA健康部分草稿，非完整州包 |
| Carrier (1) | `us.as.cargo.health-certificate` | Source-identified US domestic cargo certificate presence only / 来源标识美国国内货运证书存在检查 |
| EU (3) | `eu.ec.rabies.minimum-vaccination-age`, `eu.ec.rabies.identification-order`, `eu.ec.rabies.primary-wait` | Standard non-commercial third-country entry / 普通第三国非商业入境 |
| EU intra-member (3) | `eu.ec.intra.rabies.minimum-vaccination-age`, `eu.ec.intra.rabies.identification-order`, `eu.ec.intra.rabies.primary-wait` | Cross-member only; wholly domestic excluded / 仅跨成员国，排除单一成员国内 |

Each record includes scope exclusions, official source URL, exact heading locator,
reading date, bilingual original summary and pending checks. See the
[actual reading record](../../docs/research/week2/README.md). These are deliberately
partial constraints: CN rabies certificate/quarantine, CDC dog health, USDA/local
requirements, EU identification alternatives/certificates/titration and actual
carrier requirements need further rules and independent review.

每条含范围缺口、官方链接、原文标题定位、查阅日、双语原创整理及待核事项。
中国接种／隔离、CDC 犬健康、USDA／属地、欧盟其他证件／抗体／识别方式、实际承运要求仍需补规则与独立复核。

[Week 5 reading and unavailable sources](../../docs/research/week5/README.md) and
[CA/NY/TX inventory](../coverage/us-state-overlays.json) distinguish reading from
independent review. NY has no extracted executable constraint; TX age/initial-dose
branches remain inventory-only. / 第5周区分查阅与独立复核；NY未提取执行规则，TX年龄与首针分支仅列清单。

See [Week 6 reading](../../docs/research/week6/README.md) and [EU inventory](../coverage/eu-members.json).
Model/date and tattoo helpers are unenforced diagnostics, not additional reviewed rules.
第6周文件范本与纹身辅助诊断不计为新增复核规则；旧三条欧盟第三国草稿仍独立、revision 2。
