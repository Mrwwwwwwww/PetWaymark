# PetWaymark roadmap / 宠途路标路线图

Updated / 更新：2026-10-08. This is a staged plan, not a claim of implemented services
or a promise of calendar delivery dates. Weeks count from project work starting.

PetWaymark is a free public-benefit open-source project, independent of commercial
brands. All compliant providers may use the same open interfaces and evidence
criteria. The project does not operate transport, sell activities, accept orders,
dispatch, process payments or favor providers. Future connections point to providers'
own channels, where users independently confirm services and responsible entities.

本项目纯公益、免费开放、与商业品牌无关；所有合规服务商适用相同开放接口和证据标准。
项目不经营运输或活动、不收单、不派单、不处理支付、不偏向商家；未来对接由用户自主选择并在外部主体自有渠道确认服务。
周次为工作顺序，不承诺日历交付；后续阶段以验收门槛推进。

## Current evidence / 当前证据

Week 1 delivered the scaffold, licensing, pinned Petra comparison, 15 research
candidates and interview preparation. Actual interviews and verified feasible routes
are zero. Week 2 delivers versioned schemas, four official source reading records,
ten draft constraints (CN 3, US 4, EU 3), nine synthetic boundary contracts, an offline
validator, rejection tests and CI. All rules remain drafts; all 15 candidates remain
unsupported. Week 3 now adds an offline condition/date/explanation kernel and CLI, executing all
nine boundary contracts alongside positive, negative, missing and review-gate tests
(42 total tests). Four official sources were reread; none was promoted to verified.
Rule eligibility preserves unknown external carrier acceptance. Week 4 adds two CN
domestic draft graphs and deterministic road/rail/air-ground research previews with
CN/EN printable handovers. Eight new sources and 28 new tests (70 total) preserve
dated station/flight/facility gaps, pending custody and zero verified feasible routes.
Explicit operational contradictions exclude whole paths; public candidates remain
unsupported and unranked. There is no live inventory, price feed or service connection.
Week 5 adds the CA/NY/TX reading inventory (NY unavailable), three independently
scoped US small-city examples, two partial drafts and a local CN/EN web using the
same kernel. 94 Python tests plus native browser language/export/print/mobile checks
execute in CI; twelve rules remain draft and zero routes are verified. A hosted
static-only build and independent review remain deferred.
Boundary assessments are executed tests, not evidence of supported feasible routes.

第 1 周骨架、许可、Petra 比较、15 条候选与访谈准备已完成；实际访谈和已验证可行路线均为零。
第 2 周完成 schema、4 个官方来源查阅记录、10 条草稿（中3／美4／欧3）、9 个合成边界契约、离线校验和 CI。
所有规则待核、候选仍未覆盖。第 3 周完成离线条件／日期／解释内核与 CLI，执行全部9个边界契约，累计42项测试。
重新查阅4份官方来源，未提升任何规则为正式复核；规则满足仍保留未知承运状态。
第4周交付两组国内草稿图与道路／铁路双模式／陆空研究预览、双语可打印交接清单，新增8来源与28测试（累计70）。
日期限定站对、航段及设施能力保持缺口，责任待安排；操作冲突剔除全路径，正常候选仍未覆盖、不排名，已验证可行路线为零。
无实时仓位、价格或服务对接。第5周新增CA／NY／TX查阅清单（NY不可读）、三组独立限定分段的美国小城图例、
两条部分草稿与复用内核的本机双语网页。累计94项Python测试及真实浏览器语言／导出／打印／手机检查纳入CI；
12规则仍草稿、已验证路线仍零。纯静态托管构建与独立复核顺延。

Week 8 adds independent US/EU→CN carried dog/cat document research, 11 unknown
cost items and three neutral public-policy directory samples with unknown external
confirmation. Four fixtures, bilingual CLI/web and 162 Python tests plus browser
checks preserve cargo/transit/member gaps, titer conflicts and pending originals.
All rules remain draft; zero verified feasible routes. Full export procedures,
current annex lists and independent human review remain incomplete.

第8周新增美／欧→中独立犬猫携带文件链、11未知费用项和3公开政策名录样本。
双语CLI／网页、四合成夹具和累计162测试保留货运／过境／成员国缺口、抗体冲突及原件待确认。
全部规则草稿、已验证路线0；完整出口流程、现行附件和人工复核未完成。

Week 9 adds independent US/EU dog/cat document and return research, bilingual CLI/web,
final pickup and overnight diagnostics, and a reproducible 48-case six-direction audit.
Four new sources bring the catalog to 48; all 15 rules remain draft and every
international dog/cat baseline unsupported. Conditional and verified-supported
route counts, actual usage and qualified reviews remain zero.

第9周新增独立美欧犬猫文件及返程研究、双语CLI／网页、末段及过夜诊断、48案例可复跑六方向审计。
新增4来源累计48；15规则仍草稿，国际方向犬猫基线全部未覆盖；需确认及已验证支持路线、真实采用、合格复核均0。

## Stage A: v0.1 planning tool, weeks 1–12 / A：12 周规划工具

Initial scope: one privately owned dog/cat, CN/US/EU domestic examples plus six
independent international directions. DE/FR/NL are the first EU overlay targets;
other members and states retain visible gaps. Reverse rules are never inferred from
forward rules. Unsupported or ineligible cases are useful test results but do not
count as supported feasible routes.

首版为单只自有犬猫，包含中美欧国内研究案例和三组跨境双向共六方向。
德法荷优先深核，其他成员国／州缺口公开；不反转规则。正确识别未覆盖／不可行不计入已支持可行路线数。

| Week / 周 | Planned deliverable and acceptance / 交付与验收 |
|---|---|
| 1 | Scaffold, names, reuse decision, corridors and interview preparation; actual research outcomes reported honestly. / 骨架、名称、复用、走廊与访谈准备；如实报告实际结果。 |
| 2 | Schema/source/license contract, 10 drafts, ≥5 boundary contracts; stable segment, role, capability evidence and external-reference conventions. / 规则来源许可、10草稿、至少5边界契约及四类扩展约定；本周已交付。 |
| 3 | Offline condition/date/explanation kernel; scope and missing values first; execute boundary fixtures; `eligible` preserves unknown carrier acceptance. Delivered; public drafts remain unsupported. / 离线条件日期解释；先分类与缺失，再比较；执行边界案例，规则通过不改变未知运力。本周已交付，公开草稿保持未覆盖。 |
| 4 | Delivered: two CN draft candidates and an executed infeasible example; road/rail/air-ground preview; printable handover location/window and pending roles. Dated products remain unverified. / 已交付两组国内草稿候选与执行反例、道路铁路陆空预览、可打印交接地点窗口及待安排角色；日期限定能力待核。 |
| 5 | Delivered as research: precise CA/NY/TX inventory, distinct cabin/baggage/cargo scopes, three small-city examples and local bilingual web; parcel first/last legs rejected. Full policies, NY source access and hosted static build remain pending. / 已交付研究清单、客舱行李货运区分、三组小城例子与双语本机网页；配送首末段被拒绝。完整复核、NY来源恢复和纯静态托管待完成。 |
| 6 | Research preview delivered: 27-member inventory, partial DE/FR/NL readings, 2026 model/date diagnostics and domestic/cross-member cases; owner-not-moving gate. Full 2026/131/636 access, incorporated annexes and independent review pending. / 已交付27国研究清单、德法荷部分查阅、2026范本日期诊断、国内／跨成员国案例及主人不移动出口；完整法规附件与独立复核待完成。 |
| 7 | Research preview delivered: independent CN→US/EU dog/cat branches, document dependencies/windows, entry-point diagnostics, appointment conflicts and original-document roles in shared bilingual CLI/web. Current CN local/cargo procedures, full destination packages and two qualified human reviews pending; zero verified feasible routes. / 已交付两方向独立犬猫研究分支、文件依赖窗口、口岸诊断、预约冲突及原件角色，共享双语CLI／网页；现行中国属地货运、完整目的地规则与两位合格人工复核仍待完成，已验证路线零。 |
| 8 | Independent US/EU→CN chains; itemized unknown costs and neutral directory with listing/capability/external-confirmation distinction. / 反向中国文件链、未知费用及中立名录；分清收录、能力证据、实际外部确认。 |
| 9 | Research delivered: independent US/EU dog/cat documents, return cutovers, reproducible six-direction matrix and 48 executed regressions including final pickup/overnight/DST; all directions unsupported and independent reviews pending. / 已交付独立美欧犬猫文件与返程切换、可复跑六方向矩阵及48执行回归，含末段／过夜／DST；各方向仍未覆盖，独立复核待完成。 |
| 10 | P0 gates, bilingual demo, redacted/printed export and separately versioned data; publish v0.1 only after acceptance, with explicit no-booking and coverage gaps. / P0、双语演示、脱敏打印与独立数据版本；验收后发布 v0.1，明确未订舱与服务缺口。 |
| 11 | Prioritize real feedback fixes and integration tutorial; choose optional read-only MCP or a protocol draft within budget. / 真实反馈修复与集成教程；可选只读 MCP 或交接草案择一。 |
| 12 | Maintenance/freshness/cost/adoption report and A→B decision; inventory accurate support application evidence, with no acceptance promise. / 维护、新鲜度、成本、真实采用与 A→B 决定；如实盘点申请材料，不保证支持获批。 |

Public tracking / 公开任务：

| Weeks / 周 | Milestone / 里程碑 | Executable issue / 任务 |
|---|---|---|
| 3 | [Kernel / 内核](https://github.com/Mrwwwwwwww/PetWaymark/milestone/1) | [#1 Offline evaluation / 离线判定](https://github.com/Mrwwwwwwww/PetWaymark/issues/1) |
| 4–5 | [Domestic preview / 国内预览](https://github.com/Mrwwwwwwww/PetWaymark/milestone/2) | [#2 CN/US previews / 中美预览](https://github.com/Mrwwwwwwww/PetWaymark/issues/2) |
| 6–7 | [EU and CN outbound / 欧盟与中国出境](https://github.com/Mrwwwwwwww/PetWaymark/milestone/3) | [#3 Framework and timelines / 框架时间轴](https://github.com/Mrwwwwwwww/PetWaymark/issues/3) |
| 8–9 | [Six directions / 六方向回归](https://github.com/Mrwwwwwwww/PetWaymark/milestone/4) | [#4 Reverse directions and audit / 反向与审计](https://github.com/Mrwwwwwwww/PetWaymark/issues/4) |
| 10 | [v0.1 planning release / 发布](https://github.com/Mrwwwwwwww/PetWaymark/milestone/5) | [#5 P0 acceptance / P0验收](https://github.com/Mrwwwwwwww/PetWaymark/issues/5) |
| 11–12 | [Maintenance / 反馈维护](https://github.com/Mrwwwwwwww/PetWaymark/milestone/6) | [#6 Evidence and integration / 证据集成](https://github.com/Mrwwwwwwww/PetWaymark/issues/6) |

Labels identify engine/rules/web/maintenance, human-review dependencies and Stage A.
The six issues group adjacent weeks to keep tracking manageable; their checklists
preserve each week's deliverables. No release tag is made in Week 2.

六个任务合并相邻周，清单保留逐周验收；标签注明领域、人工复核依赖和阶段。第 2 周不打 release 标签。

Stage A passes when all P0 functions work in the released scope, at least 30 regression
cases execute, unknown never becomes permission, critical published rules have actual
independent human review, and users can identify reasons and confirmation gaps.
Without reviewers, affected directions stay draft. Versioned evidence and disclosures
matter more than counts of routes, commits or directory entries.

A 验收包括范围内 P0、30 执行回归、未知不变允许、关键发布规则真实独立人工复核，使用者能识别理由和待确认项。
复核人不到位则相关方向保留草稿；不为凑数量扩大宣称覆盖。

## Later stages: gates before expansion / 后续阶段：先验收再扩展

B–E have no scheduled dates and do not block v0.1. Each needs a staffing, maintenance,
privacy and compliance estimate before implementation. Service information can be
explored earlier, but actual connections require their stage's evidence and gates.

B–E 不承诺日期、不阻塞 v0.1；实现前单独估算人员、维护、隐私和合规工作。
信息规划可提前研究，服务对接必须满足相应门槛。

| Stage / 阶段 | Output / 产出 | Gate and stop conditions / 验收与暂停条件 |
|---|---|---|
| B: handover protocol / 交接协议 | Open draft, minimal reference implementation/validator; simulations before authorized trials. / 开放草案、参考实现与验证；先模拟再获授权试验。 | Reproduce acceptance/refusal, emergency custody, offline upload, correction, missing evidence and revocation; independent implementations exchange records; custody never unassigned. Requires operator review and private data design; prohibited filming is not required. / 正常拒收、紧急接管、离线、更正、缺证及撤权可复现；独立实现互通，无无人负责状态；需操作人员与隐私能力，不强迫违规拍摄。 |
| C: open capability/quotation information / 开放能力与报价信息 | First evaluate one verified domestic corridor; equal access criteria; authorized manual quotation import before APIs. / 先评估一条已覆盖国内走廊；统一标准，先授权人工报价导入。 | Evidence and complete cost inclusions/exclusions per leg; explicit missing alternatives; expiry, missing fields, provider replacement and absent final leg simulations. Need evidence/interface maintainers; change pilot with recorded rationale if review cost is too high. / 分段能力与费用完整、替代缺口明确；演练到期缺项换商和无末段；需维护人员，核实成本过高可有据换试点。 |
| D: provider-owned channel connections / 自有渠道对接 | Deep links or open adapters on verified limited corridors; users confirm independently externally. / 有限已核实走廊深链或适配，用户在外部自主确认。 | Responsible entity, authorization/data scope, channel validity, per-leg references, duplicate-event and expiry handling; real responsibility/contact for cancellation, missed delivery, overnight delay, emergency, lost contact and dispute. Disable affected connection when qualification, permission or responsibility is missing. / 主体授权数据、渠道、分段确认、重复过期处理明确；取消延误急诊失联争议有责任联系方；资质授权责任缺失停用相关对接。 |
| E1: accompanied tourism planning / 同行旅游规划 | Local/domestic transport, accommodation and activities first; cross-border returns later. / 先本地国内交通住宿活动，后跨境往返。 | Venue restrictions, return paperwork and alternative care evidenced; external package-service responsibilities reviewed. Need destination maintainers; directory size is not verified coverage. / 场所限制、返程和备选照护有据，外部组合服务责任核实；需目的地维护，收录数量不等于覆盖。 |
| E2: institution-led boarding/activity planning / 机构寄游规划 | Familiar local trial, boarding plus fixed-area outings, then evaluate travel; no initial long-distance removal by unfamiliar individuals. / 本地熟悉试托、固定区域寄养活动，再评估外地；初期不对接陌生人长距离带离。 | Review actual carers, local qualifications, authority, privacy and insurance; rehearse stop/return/escape/medical/replacement scenarios and review observation evidence. Serious incidents or broken custody/authority stop affected connections until remediation. / 核实实际照护、地方资质授权隐私保险，演练叫停接回脱逃医疗换人并复盘；严重事件或保管授权断裂后停用整改。 |

E1/E2 can be prioritized by demonstrated need after D. Cross-border boarding, all
species and unfamiliar long-distance escort arrangements remain distant research
questions. Welfare includes a useful option to postpone travel or remain in local
care; the project does not diagnose or prescribe treatment.

E1／E2 在 D 后按实际需求择先。跨境寄游、全物种及陌生人长途陪游留待远期评估。
改期、不出行或原地照护也是有效结果；不由项目诊断或开药。

## Capacity and evidence / 资源与证据

Planning assumes one maintainer at 15–20 hours/week; qualified regional reviewers
are not yet secured. Future protocol/interface additions should stay within roughly
10% of weekly effort (1.5–2 hours); excess moves to B, preserving rule review and
regressions. No private video store, quotation sending, transactions or live inventory
system enters Stage A. Every reference must distinguish rule feasibility from actual
external confirmation, as in the [extension decision](docs/decisions/0002-planning-extension-contract.md).

按一名维护者每周15–20小时规划，合格地区复核人尚未落实；远期增量以约10%（1.5–2小时）为限，超出移到 B，不压缩复核回归。
A 不建私有录像存储、询价发送、交易或实时库存系统；分清规则可行性与外部确认。

Report genuine defects, voluntary feedback and independent adoption with dates,
sample sizes and disclosed affiliations. Synthetic tests and maintainer self-use
stay separate from adoption. No manufactured stars, commits, users or reviews, and
no unsolicited outreach. Application preparation documents real public value and
maintenance; funding is not guaranteed and adds no paid runtime requirement.

反馈、采用与维护须有真实日期、样本量及利益披露；合成测试和维护者自用分别记录。
不刷 star／提交，不造假用户或复核，不擅自外联；申请只整理真实公益价值，不保证资助，不强加付费运行依赖。

## Week 10 authorized research release / 第10周授权研究发布

The user explicitly approved v0.1.0 publication as an early research preview.
[Release scope and P0 audit](docs/releases/v0.1.0.md) distinguish working software
from incomplete independent rule review and real voluntary trial evidence. This
release does not claim Stage A fully passed; no rule or route is promoted to verified.
Engine `0.1.0`; curated dataset `2026.10.08-draft.1`; fixed synthetic Pages demo.

用户明确授权v0.1.0研究预览发布；A阶段人工复核／真实试用门槛尚未通过，相关
方向继续草稿／未覆盖。技术发布不作为规则已核或服务已确认的证明。
