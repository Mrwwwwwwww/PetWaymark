# Week 3 official-source reading / 第 3 周官方来源查阅

Read on 2026-10-08 using the browser. This is an AI-assisted reading record, not
independent human verification. Ten rules remain `draft`; reviewers and complete
jurisdiction/transport coverage are still missing. No new official rule is promoted.
Linked original texts retain their own rights; only brief original summaries follow.

2026-10-08 浏览器重新查阅；属于辅助查阅，不是独立人工复核，不填人工签名。
10 条规则保留草稿，全部候选仍未覆盖。下列为原创摘要，官方原文保留自身权利。

| Source / 来源 | Locator / 原文定位 | Reading result / 查阅结果 | Unresolved / 待核 |
|---|---|---|---|
| [cn.gacc.2019-5 — MOFCOM republication](https://www.mofcom.gov.cn/zcfb/zgdwjjmywg/art/2019/art_71739ec848d14deca4ec330fad835774.html) | 第一项、第二项、附件说明 | 携带入境犬猫数量、芯片与证书三项草稿与该转载正文一致；不是独行货运规则。 | 海关现行替代关系、附件、指定地区／实验室、实际口岸设施及服务犬分支仍需独立复核。 |
| [us.cdc.low-risk — CDC](https://www.cdc.gov/importation/dogs/rabies-free-low-risk-countries.html) | At a glance; What else is required; How do I show the form's receipt | 低风险犬分支仍按过去六个月旅行史区分，页面支持年龄、通用扫描器可识读芯片及回执三个必要条件。 | 健康条件尚无犬专属规则记录；USDA、州、领地、实际承运及高风险分支未覆盖。 |
| [us.cdc.animals — CDC](https://www.cdc.gov/importation/bringing-an-animal-into-the-us/index.html) | Cats; Certificates of health for pets | 猫的到达健康要求与草稿一致，不能套用犬的年龄或回执规则。 | 目的州／领地与承运要求需另核，不能据 CDC 单项得出完整入境允许。 |
| [eu.ec.non-eu — European Commission](https://food.ec.europa.eu/animals/live-animal-movements/dogs-cats-and-ferrets/bringing-pet-eu-non-eu-country_en) | Rabies vaccination; Animal Health Certificate and declaration; Owner travelling with the pet animal | 三条狂犬病条件草稿与页面相符。页面另列2026证书过渡及授权陪同主人前后五日条件。 | 生效链、2026证书模型、签发与入境时间、抗体检测、成员国叠加及非主人移动分类需独立复核。 |

## Impact on the engine / 对内核的影响

The existing official summaries do not establish complete coverage. The kernel
therefore preserves unresolved scope exclusions and package gaps. The old-certificate
fixture remains `unsupported` with `certificate_transition_unreviewed`; no certificate
cutoff is silently implemented from an unreviewed reading. Owner timing is a
conservative classification check; full document and authorization requirements
remain outside this Week 3 package. High-risk dog history cannot match low-risk rules.

查阅不补齐整个规则包。证书过渡继续输出未覆盖；主人日期检查只作保守分类，不证明授权与证件完整。
高风险犬旅行史不匹配低风险规则。正式复核规则数、已验证可行路线数和实际外部确认仍为零。

The [date/trust decision](../../decisions/0003-offline-evaluation.md) records civil-day
counting, calendar month conventions and unsupported hourly/timezone windows.
The [offline guide](../../en/offline-engine.md) reproduces boundary assessments
without fetching official pages or using a model key.
