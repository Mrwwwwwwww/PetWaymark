# 0002: Minimal planning extensions / 最小规划扩展

Status: accepted design, 2026-10-08. No transport or integration implementation yet.

## Stable segments / 稳定分段

Future plans use opaque `journey_id`, `plan_revision` and `segment_id`. IDs are scoped
to a journey, are not array positions or hashes of personal details, and survive
reordering or translation. Editing a time preserves the segment ID and increments
plan revision. Splitting, merging or replacing a physical leg creates new IDs with
`supersedes_segment_ids`; removed IDs are not reused. Export must preserve identity.
Public fixtures use synthetic IDs only.

未来计划采用旅程内稳定的分段 ID，不用数组位置、个人信息哈希或翻译文本作 ID。
改时间保留 ID 并升计划版本；拆分、合并、替换实际段生成新 ID，显式关联被替代段；删除 ID 不复用。导出保留关联，公开样例仅用合成标识。

## Accompaniment and responsibility / 陪同与责任

Rule scope already distinguishes `owner`, `authorized_person`, `unaccompanied`.
Future segment assignments separately record escort role, custodian role, handover
recipient role, authority scope, document custodian and owner/pet dates. Unknown
assignment remains `needs_confirmation`. A role is not a provider qualification or
proof that the owner is travelling. No personally identifying assignment enters
public data. Week 4 prints a role as pending arrangement when nobody is confirmed.

现有规则范围复用主人、授权陪同、独行。未来分段另记陪同、保管、接收、授权范围、原件保管及主人／宠物日期；角色未落实标待确认。
角色不证明资质，也不证明主人移动；个人分配信息不入公共数据。第 4 周打印清单在无人落实时写待安排。

## Capability evidence / 服务能力证据

Reuse source IDs and evidence locator/access/review semantics. A future capability
record binds provider reference, modes, species, geography, facility, product, hours,
authority/permission basis, valid dates, evidence and reviewer status. Each asserted
capability needs its own scope; directory inclusion, membership or registration
does not prove acceptance of a specific animal/leg. Unavailable or disputed critical
evidence leaves a gap. All compliant providers face the same published criteria;
there is no paid inclusion, brand preference or affiliation implied by a source.

服务能力复用来源、定位、查阅和审查字段；后续限定主体、模式、物种、地域、设施、产品、营业窗口、授权依据与有效时间。
名录收录、会员或登记不等于具体段收运。关键证据缺失／争议保留缺口，所有合规主体适用同一标准，不付费优先、不暗示商业关联。

## External confirmation references / 外部确认引用

Future private references bind `segment_id`, external responsible entity/channel,
opaque confirmation reference, source/evidence, received time, expiry, applicable
plan revision and status (`unknown`, `pending`, `externally_confirmed`, `declined`,
`expired`). Any material leg change invalidates the old reference until reconfirmed.
A link click, public listing or one confirmed leg cannot confirm the whole journey.
Public exports omit tokens, booking numbers, personal records and exact private
locations; a synthetic status can illustrate semantics without fabricated inventory.

外部确认引用绑定分段、外部责任主体／渠道、私有引用、证据、取得／过期时间、适用计划版本与状态。
实际段重要变化后须重新确认；跳转、收录、单段确认不证明全程落实。公开导出不含密钥、真实预订号、个人档案或私有精确地点。

`eligible` is a future rule evaluation result and is independent of confirmation
progress. The Week 3 regression must keep carrier acceptance unknown even when
verified rules are satisfied. No project order, dispatch, contract, payment or refund
schema is introduced. These are design conventions until a v0.1 use case requires
fields. Full handover protocol, private evidence storage and interfaces belong to
later stages B–D; they are not v0.1 dependencies.

`eligible` 与外部确认进度独立；第 3 周须测试规则满足也不改变未知承运确认。
本周不建项目订单、派单、合同、支付、退款 schema。v0.1 有实际用例再实现字段；完整交接协议、私有证据存储和接口归后续 B–D，不阻塞 v0.1。
