# 0004: Draft domestic graph / 国内草稿图

Accepted for research preview, 2026-10-08. Graph contract and kernel remain 0.1.0;
the independently identified dataset is `2026-10-08.week4-preview`. This is not a
release tag or an opened feasible transport corridor.

## Classification and evidence / 分类与证据

Only CN→CN, one privately owned ordinary dog/cat, relocation/holiday and a declared
owner/authorized-person/unaccompanied branch build paths. Unknown purpose, ownership,
count, species, accompaniment or travel date returns unsupported before generation.
The Week 3 classifier and condition assessment are reused. CN carried-entry import
rules do not describe CN domestic movements and are deliberately not applied here;
an empty domestic package retains `applicable_rules_uncovered`.

仅CN国内单只自有普通犬猫、搬家／旅游、明确陪同分支和日期才展开候选。
分类缺失先返回未覆盖；复用第3周分类和评估，不把海关携带入境规则套给国内出行。
国内执行规则包仍为空，明确保留必要规则未覆盖。

Graph schema is preview-only: every edge is draft with critical gaps and source
locators. Rail physical limits are sourced draft diagnostics with pass/fail/missing/
invalid outcomes; none enforces a legal prohibition. Historical station entries,
airport service information and highway mentions are evidence leads. Dated rail
station pairs, flights, actual aircraft, animal slots, cargo terminals, opening
hours and complete door-to-door roads are not established. No geographic lead is
promoted to a capacity statement. Current dates do not establish evidence currency.

草稿图每条边均有关键缺口与来源定位，铁路体型限制只诊断，不作正式禁令。
历史站点、机场信息、道路记录不证明特定日期产品、运力、货站或完整门到门路径。
查阅日期不是有效性复核日期；机场坐标库和配送产品没有被用来补充活体段。

## Generation and conflicts / 生成与冲突

The small directed graph enumerates simple paths in deterministic segment-ID order.
No reverse inference, cycles, shortest-distance ranking or unreviewed recommendations.
Owner vehicles, unaccompanied animal carriers, ground transfers, accompanied rail,
unaccompanied rail and passenger checked baggage have distinct product identities.
Unaccompanied inputs cannot use the accompanied rail or passenger baggage branch;
owner vehicles require the owner and declared driving readiness. Ground transfers
retain pending vehicle/provider and responsibility gaps.

小型有向图确定性枚举无环路径，不推导反向，不按缺失距离排序，不推荐未复核候选。
自驾、独行道路承运、接驳、铁路双模式、航空旅客行李分别识别；独行不能套同行产品。
自驾需主人同行和驾驶能力；首末段接驳的车辆主体与责任仍待落实。

Explicit `can_drive=false`, user-reported `declined`, an explicitly missed handover
window or incompatible product branch excludes the whole path, with segment reasons
retained in `excluded`. Those are input/operational contradictions, not AI legal
conclusions. If every enumerated path is excluded, status is ineligible **within this
small graph and input**, not a claim that all transport worldwide is impossible.
Otherwise public candidates remain unsupported. Empty topology stays unsupported.
Unknown does not become a rejection, approval or confirmed booking. Candidates and
excluded examples are separate; `recommendations=[]` and `ranked=false` always.

驾驶不可用、输入报告拒收、窗口已错过或陪同产品不兼容时剔除全路径，并保留分段原因。
全部剔除仅表示此图及此输入不可继续，不是世界范围无出行办法。未知不是拒收也不是允许。
候选仍未覆盖，不排名；空图未覆盖。没有实际确认或订舱。

## Handover and estimates / 交接与估时

Each segment retains its opaque ID, endpoints, arrival handover location, unresolved
window, escort, animal custodian, recipient and original-document custodian. Public
roles are null and print **pending arrangement**. Public facility names are only an
approximate handover place; the exact permitted counter/office remains to be agreed.
No responsibility is implied by a route label or an accompanied-travel declaration.
Time, distance and cost stay null because there is no full route measurement or
schedule. No 800 km preference is applied to missing road distance; no artificial
hourly window is generated from dates. The user can report a missed window, but
this version does not calculate scheduling feasibility.

打印稳定ID、起终点、到达交接地点、待确认窗口以及四类责任角色；未落实均写“待安排”。
设施名仅为交接地理范围，精确柜台／营业部待约定；陪同声明不代表已落实责任。
时间、距离、费用均未知，不猜800公里分档、不用日历日期模拟小时窗口。
可输入已错过窗口，本版不计算时刻衔接。

A local opaque journey ID scopes the segment IDs. Date changes preserve segment
identity; the caller increments `plan_revision`. Splits/replacement require new
maintainer segment IDs and supersession metadata (the data validator rejects missing
references); no interactive graph editing is implemented. Translation and source
array reordering do not alter identity or status. This extends decision 0002 only as
far as the Week 4 printing use case needs, without a custody event protocol.

旅程内稳定ID；改日期保留ID，由调用方升版本；拆分／替换由维护者创建新ID及替代关联。
不实现交互图编辑、签收事件或私有影像协议。翻译与数组顺序不改身份或状态。

## Input and disclosure / 输入与披露

User preview controls permit only opaque journey ID, positive revision, boolean/null
can-drive and existing segment IDs with unknown/declined acceptance and boolean/null
window-met. They cannot override evidence, coverage or roles, assert external
confirmation or fill a leg with parcel delivery. Input-reported acceptance is labelled
as such and is not a carrier receipt. CLI validates graph schema/evidence first.
Both JSON and text emit the same canonical status/reasons; text alone is translated.
No profile object, address, raw document, booking token or contact details is exported.
Use non-personal journey IDs. There is no provider referral, ordering or service API.

用户控制仅含无个人信息的旅程ID、版本、驾驶能力、现有分段的未知／拒收报告及窗口已满足布尔值。
不能覆写证据、规则、角色或宣称外部确认；输入报告不是承运回执。JSON与打印状态原因一致。
不输出原始档案、地址、证书、令牌或联系信息；不建服务推荐、下单或接口系统。
