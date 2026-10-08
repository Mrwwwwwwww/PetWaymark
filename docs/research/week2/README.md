# Week 2 source reading / 第 2 周来源查阅

2026-10-08, Asia/Shanghai. All four sources were opened and read in this execution
using the browser tool. Access dates describe that reading, not an independent human
review. No raw page snapshots or fabricated content hashes are stored. This record
is original documentation under Apache-2.0; summaries in the curated rules are
CC BY 4.0. Source texts retain their own rights.

本次实际打开并读取四个官方页面；日期仅代表查阅，人工复核为零。
不保存整页原文、不编造内容哈希；整理数据不改变官方原文许可。

| Source / 来源 | Locator / 定位 | Used for / 用途 | Pending / 待核 |
|---|---|---|---|
| [GACC 2019 No. 5, official MOFCOM republication](https://www.mofcom.gov.cn/zcfb/zgdwjjmywg/art/2019/art_71739ec848d14deca4ec330fad835774.html) | 第一条；实施日期 | Three carried-entry draft constraints / 三条携带入境草稿 | Current annex lists, supersession, cargo classification, vaccine/quarantine branches / 现行附件、替代、货运分类、接种与隔离分支 |
| [CDC low-risk dogs](https://www.cdc.gov/importation/dogs/rabies-free-low-risk-countries.html) | CDC Dog Import Form; What else is required… | Three dog-only drafts / 三条仅犬草稿 | Current risk list, complete history, other federal/state/carrier layers / 风险名单、完整旅行史、其他联邦／州／承运叠加 |
| [CDC animal entry](https://www.cdc.gov/importation/bringing-an-animal-into-the-us/index.html) | Cats | Cat arrival-health draft / 猫到达健康草稿 | Inspection procedure, local overlays, effective start not established / 检查流程、属地叠加、生效起日未知 |
| [European Commission non-EU entry](https://food.ec.europa.eu/animals/live-animal-movements/dogs-cats-and-ferrets/bringing-pet-eu-non-eu-country_en) | Conditions / Rabies vaccination; Exceptions | Three rabies drafts and classification/transition fixtures / 三条接种草稿及分类／过渡案例 | 2026 legislation and annexes, exceptions, member-country practice, exact effective dates / 2026 法规附件、例外、成员国执行及生效日 |

The EC explanation links 2026/131 and 2026/705 and describes an old-certificate
issuance cutoff before 1 October 2026. We have not completed article/annex review;
the cutoff fixture requests review rather than implementing certificate permission.
No reverse corridor is inferred from these entry rules. Sources remain
`read_pending_review`, all ten rules remain `draft` with pending checks and empty
human reviewer lists. Unknown dates remain null. No carrier product has been
verified; carrier policy records and airport capacity stay unpopulated.

欧委会页面引用 2026/131、2026/705，并说明旧证书在 2026 年 10 月 1 日前签发的过渡条件。
本次未完成条款／附件复核，案例要求继续核查，不实现证书允许判定。
不反转入境规则推导出境；所有规则保持草稿，未知日期为 null，承运产品与机场能力未验证。

## Boundary contracts / 边界契约

Nine [synthetic fixtures](../../../tests/fixtures/boundaries/) cover missing birth date,
cat/dog mismatch, six-day owner gap, old certificate cutoff, unknown carrier,
high-risk history, calendar month age, owner not travelling and unknown microchip.
They all pass schema/reference checks. Expected route statuses remain unsupported
because critical data/classification is unreviewed. Their notes also specify isolated
condition behavior once reviewed data becomes available. These are Week 3 engine
targets, not executed legal or route regressions.

九个合成案例涵盖缺生日、犬猫误套、主人差六天、旧证书截止日、未知承运、高风险史、自然月年龄、主人不移动和未知芯片。
结构和引用通过；关键数据未核，路线预期保持未覆盖。备注另说明未来已核实条件的独立行为；第 3 周接入内核，不能当作已经执行的路线回归。
