# Contributing / 贡献指南

The public repository accepts focused rule, code and documentation corrections. Use the issue/PR templates; do not submit personal travel records.

1. Read both READMEs, [coverage](docs/zh/corridors.md) and [license boundaries](LICENSE-DATA).
2. Make one coherent change. Describe the problem and affected direction, species, date, transport mode and rule ID, if any.
3. Cite the issuing authority or actual carrier, with canonical URL, original-language heading/article, access date, effective dates (unknown stays unknown) and a short permitted summary or hash. Community reports and Petra interpretations are leads for verification, not official rules.
4. Preserve distinctions between law, official guidance, carrier restrictions and project interpretation. Never promote upstream `verified` into project review approval. Record missing conditions and conflicting sources.
5. Future rule changes need positive, negative and missing-input cases. Use synthetic or expressly authorized anonymized input. No passports, chip numbers, home addresses, phone numbers or bookings in commits or issues.
6. Follow the commands in the [rule contract](docs/en/rule-contract.md): scaffold check, schema/reference validator and `unittest`; also run `git diff --check`. CI repeats validation on Python 3.11/3.13. The checks do not certify legal accuracy; boundary expectations become executable with the Week 3 engine.
7. Update both README languages when their shared content changes. Use the PR template and disclose provider/brand affiliations. No paid rule exceptions or preferential ranking.

High-risk cross-border rules stay `draft` until another qualified human reviewer opens the original source and confirms scope and dates. AI research is not a human signature. Absent that review, a corridor must not be described as verified or eligible. A stale, disputed or missing critical rule blocks a definitive result.

Code and original documentation contributions use Apache-2.0; original curated data uses CC BY 4.0. Only submit material you can license. Preserve upstream attribution and modifications; never relicense evidence texts or third-party assets merely because they are publicly readable.

中文要点：先提供官方依据及定位，再写最小规则和正反例；缺失、过期与冲突必须显式记录。跨境关键条目需要另一位具备语言与领域能力的人工复核者；未到位就保持草稿。不要提交真实身份、订单或未经授权的商业资料。可通过本项目模板提供纠错；勿提交个人材料。
