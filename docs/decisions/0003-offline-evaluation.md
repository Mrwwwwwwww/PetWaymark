# 0003: Offline evaluation and civil dates / 离线判定与日历日期

Accepted implementation decision, 2026-10-08. Engine contract version: 0.1.0.

The engine assesses a supplied constraint package, not a route or booking. Callers
must validate schemas, references and source availability first; the repository CLI
runs the existing offline validator. `assessment_at` is mandatory, making replay
independent of the machine clock. Rule explanations preserve ID, revision, bilingual
message, official evidence locator and source IDs. Results never change input records.

内核评估输入规则包；不是路线规划或订舱。调用前须校验 schema、引用与来源状态；CLI 自动调用仓库校验器。
评估日期必填，结果不依赖运行当天；解释保留修订号、双语消息、官方链接、定位和来源 ID。

## Classification and trust / 分类与信任

Classify species, service-animal branch, purpose, ownership transfer, accompaniment,
owner dates and US dog six-month history before comparisons. Missing classification
cannot be a wildcard. Known species/direction/history/mode mismatch skips expressions.
An EU unaccompanied movement leaves legal classification pending rather than silently
reclassifying it as ordinary non-commercial travel. Owner-accompanied travel requires
the same date; authorized travel uses the five-day civil-date boundary only as a
conservative classification check, never proof of authorization or reviewed law.

先分类物种、服务犬、用途、所有权变化、陪同、主人日期及美国犬六个月旅行史。
已知范围不符不计算表达式；缺失不当通配符。欧盟独行留待分类；主人同行须日期一致，授权陪同以五个日历日作保守分类检查，仍需授权证据与法规复核。

Draft comparison outcomes are **diagnostics** only. They cannot block or permit a
journey. Partially known scope can show diagnostic missing fields, but cannot enforce
an expression. Only usable reviewed records with resolved scope can enforce failure.
Possible sourced exceptions send failed comparisons to confirmation, never auto-waive.
Status precedence: known enforceable block → `ineligible`; critical coverage/review
or classification gap → `unsupported`; missing/invalid inputs or soft failure →
`conditional`; otherwise → `eligible` for this supplied constraint package only.

草稿比较仅供诊断，不决定允许或阻塞；范围缺失时亦不执行强制结论。
有效已复核规则且范围明确才能阻塞；失败涉及例外转人工确认。
优先级：确定阻塞、关键覆盖／复核／分类缺口、补件／确认、满足输入规则包。

Review checks use both assessment and travel dates. Review is stale starting on its
due date. Effective start/end dates are inclusive; unknown start is unusable. An
unknown end is not indefinite permission: review freshness still gates it. Two distinct
review identities and valid dates are necessary metadata, not proof of real review.
The engine cannot authenticate a human reviewer.

`coverage_gaps` and `resolved_scope_rule_ids` are trusted maintainer package metadata,
never user form fields. The default leaves coverage and scope exclusions unresolved.
An empty gap list requires a genuinely audited complete package; each resolved scope
exclusion needs its explicit rule ID. No such public package exists today. Synthetic
in-memory tests alone supply these attestations and hypothetical review identities;
those identities are conspicuously labelled, not real people or adoption evidence.

按评估日与适用日核对复核期限；到期当天失效，生效起止日含边界。
未知生效起日不可用；未知终止日仍受复核期限约束。不能靠校验器证明人工复核身份。
覆盖缺口及范围缺口解决记录是维护者可信元数据，不从宠物主人输入获取。
默认覆盖缺失；当前无完整已审核规则包，只有内存合成测试显式声明条件覆盖与假想复核。

## Date policy / 日期策略

- Accept only `YYYY-MM-DD` local civil dates. Invalid dates and ISO timestamps produce
  confirmation, not an inferred timezone. Use the official document's local date.
- Natural months add calendar months and clamp to the target month's last day. Thus
  31 January + one month is 28/29 February; 29 February + twelve months is 28 February.
  This is a documented computational convention requiring authority-specific review.
- Weeks mean seven civil days. Elapsed day counting excludes the event day (day zero);
  event + 21 days reaches the twenty-first-day threshold. Equality is allowed in
  `on_or_before`. Reversed intervals fail.
- This version does not handle hours, IANA timezone conversion, DST, business hours or
  holiday calendars. Hour-based rules must remain uncovered. Never convert a 24-hour
  window to a civil day or interpret a naive datetime as UTC. A later schema must
  specify timezone, ambiguous/nonexistent time handling and each authority's counting
  semantics before implementing those windows.

仅接受官方文档所用当地日历日期；不猜时区，不支持小时窗口。
自然月按月历增加并截到月末；周为七个日历日；事件日为第零日，21 天后达阈值。
月底算法是明确的计算约定，不能代替各机关解释；夏令时、时区、节假日、营业窗口后置，缺口公开。

## External progress / 外部进度

`external_progress.carrier_acceptance` preserves `unknown`, `externally_confirmed`
or `declined` separately from rule status. Even a synthetic `eligible` result leaves
unknown acceptance unknown. A supplied external status is not independently validated,
does not confirm every leg and never sets `booking_confirmed` true. A later route
planner must remove declined legs from candidates. No transaction system is added.

规则结果与外部收运状态独立；输入状态仅原样记录，不独立证明有效、不证明全程。
任何结果均不设已订舱；未来路线生成须剔除拒收段。本周不建交易系统。
