# 规则与来源契约 0.1.0

[English](../en/rule-contract.md)

[四份 JSON Schema](../../packages/schema/) 使用 Draft 2020-12：公共定义、规则、来源目录和合成边界案例。
`https://petwaymark.org/schemas/` 是逻辑标识，不代表已注册域名或线上服务；校验器从本地解析，不下载 schema。
代码、schema 与原创说明采用 Apache-2.0；原创整理数据采用 CC BY 4.0，官方原文保留自身权利。

## 规则记录

必填版本、稳定 ID、递增修订号、记录类别、主管机关、适用范围、有效期、条件表达式、失败／缺失处理、例外、来源与证据、审查、替代关系、双语消息、待核清单和许可。
未知属性和含混表达式被拒绝。schema 版本表示格式；revision 表示规则内容版本。语义改变需升修订号并补回归，替代另一条规则用 `supersedes`。

`law`、`official_guidance`、`carrier_policy`、`project_interpretation` 分开保存。
政府说明页即使引用法规，仍按指引记录。起运、中转、首入境、目的地、州／成员国及实际承运政策叠加；空属地列表不代表已核实地方要求。
单条规则只表达必要约束，不能证明整条路线允许。

scope 区分来源／目的地、犬猫、运输模式、移动类别、陪同、旅行史、接种分支。
分类缺失应转待确认，不能当通配符。`any_non_eu` 排除欧盟起点；`any` 显式不限制起点。
`exclusions` 记录不可自动消除的缺口。主人、授权陪同、独行分别记录；授权不自动证明满足非商业移动分类。

第 3 周最小表达式契约：布尔 `equals`、数值 `at_most`、自然月／周年龄 `calendar_age_at_least`、日期先后 `on_or_before`、天数间隔 `elapsed_at_least`。
必须先处理日期缺失，再比较；自然月不能换成 30 天，周按七个日历日。天数窗口需适用机关的计日规则；当地时间与 IANA 时区支持在第 3 周确定。
本周校验器不执行任何表达式。`on_missing` 固定 `needs_confirmation`；失败为 `block` 或 `needs_confirmation`。
每个例外有独立 ID、范围说明和带证据的来源；此版本只转人工确认，不自动覆盖规则。

`effective_from/to` 由原文支持，不用查阅日期代替；`null` 是未记录，包括未知终止日，并非无限有效。
`applies_at` 区分入境与接种。`accessed_at` 是查阅；`last_verified_at`、复核人和 `review_due_at` 是人工审查。
ISO 日期校验真实日历；发布还需检查新鲜度与旅行日期，结构通过不等于规则可用。

状态为 `draft → verified → stale/disputed/retired`。
verified 要有已知生效起日、两名不同人工复核人、复核日期、晚于复核的期限、证据且无待核项。
自动校验无法证明署名人真的复核，维护者须核实；AI 不得填人工签名。草稿不能声称完成人工复核。
历史已核实记录即使到期仍可保存并通过结构校验，但内核不得当作当前已核实约束。
关键数据缺失、过期、争议、退役均不能支撑确定结论。

## 来源与校验

[catalog.json](../../data/sources/catalog.json) 是本周来源登记；第 1 周索引保留为历史研究队列。
来源含稳定 ID、签发机关、实际刊载单位、类型、HTTPS 原始链接、双语标题、语言、实际查阅日期／方式、状态、许可边界和待核项。
官方转载分别记录刊载单位与签发机关。证据记录相同的 URL／日期／语言、标题或条款定位、简短原创摘要及可选哈希，不整页复制。
查阅不等于规则复核；访问失败应保留 unavailable，不编造引文或查阅日期。

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python scripts/check_scaffold.py
.venv/bin/python scripts/validate_data.py
.venv/bin/python -m unittest discover -s tests -v
```

安装依赖后可全部离线运行，无需模型密钥。CI 使用 Python 3.11／3.13。
`validate_data.py --root PATH` 支持隔离副本，校验 schema、严格 JSON、重复 ID／键、引用、来源与证据一致性、机关、例外和审查日期约束。
不验证法规真实性、实时链接、复核人身份、实际运力或路线可行性。
边界案例固定 `phase=week3_engine_target`：本周只校验输入和预期结构，第 3 周须接入内核执行断言；结构通过不是内核回归通过。
规则发布前须有正例、反例与缺失输入测试。

另见[规划扩展决定](../decisions/0002-planning-extension-contract.md)。
