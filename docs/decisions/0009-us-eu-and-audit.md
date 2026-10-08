# 0009: independent US/EU research and reproducible coverage audit

Status: accepted for draft implementation, 2026-10-08. No independent reviewers.

US→EU and EU→US have independent branches in `packages/engine/us_eu.py`.
Only pure date, field comparison and existing model-date helpers are shared;
CN export steps, CN entry conditions and inverse directions are never applied.
All diagnostic rows are unenforceable and public route status remains unsupported.
A failed draft diagnostic does not become an enforceable legal rejection.

Only one ordinary privately owned dog/cat, accompanied cabin/baggage, no transit is
compiled. Non-commercial EU owner-movement and written authority gates run first.
EU→US cargo/export classification is not inferred from CDC's import allowance.
US→EU APHIS accredited-vet guidance was read for France; other first-entry members
have an explicit destination guidance gap. DE/FR/NL export authority details remain
unreviewed. Passport returns and health certificates remain distinct.

US import dog history is explicit anonymous self-report, never inferred from the
last departure country. A six-civil-month estimate detects contradictions in the
last high-risk exit; complete chronological location evidence is not established.
Cats never receive dog age, chip or CDC forms. High-risk foreign vaccination needs
its own form/ACF/titer/quarantine chain. Missing US-vaccinated return proof points to
that separate fallback, but does not automatically assert the fallback is satisfied.
The specific US form must be endorsed before original US departure. A legacy export
issue cutoff is only one condition, not proof of database/content/vaccine compliance.

`assess_round_trip` requires opposite directions and matching species, reevaluates
both on current trusted data and flags dataset changes. It does not establish pet
identity, continuity of ownership or that two anonymous profiles describe one animal.
It is an engine API, not a hosted round-trip product. Rule-change regression uses the
actual old/new certificate and legacy US proof cutoffs, not a fictitious law.

The audit runner dispatches numbered fixtures to production engines, asserts explicit
expectations, and emits deterministic JSON/Markdown. Route status and individual
draft diagnostic outcomes are separate. `conditional` would require reviewed rules
with unresolved operational conditions; `verified_supported` additionally requires
dated external capacity and custody evidence. Current counts for both remain zero.
Only explicit operational contradictions in domestic graphs can be `ineligible`.
Synthetic tests with fake reviewers never enter the public matrix or adopted-route
counts. No count is presented as usage, quotes, reviews or transport availability.

中文：美欧两方向独立分支，只共享纯日期及范本辅助函数；未反转中国规则。
公开结果未覆盖，草稿失败不构成法律拒绝。仅单只普通自有犬猫、陪同客舱／行李、无过境；
法国美国出口指引可读，其他首入境国明确缺口；欧盟当地出口签发／认证仍待核。
犬六个月历史仅自报，最后起运国不证明全程低风险；猫不套犬条件。
返程API用当前可信数据独立重评两腿并标注版本变化，不证明动物身份和责任连续。
编号审计调用真实内核并断言；未覆盖／需确认／明确操作不可行／已验证支持分别统计，
需确认和已验证支持均为零。合成复核和测试不进入真实采用统计。
