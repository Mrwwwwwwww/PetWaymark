# 0001 — Petra 数据适配，自建公开引擎及缺失走廊

日期：2026-10-08。状态：第 1 周研究决定；适配器与生产规则尚未实现。

**采用“适配”方案：复用带归属的研究记录和官方来源线索，自建可执行规则、联运模型与开源引擎。** 不把 Petra 的 `verified` 标记直接转为本项目已复核，也不把美国出口规则反转或套用于中国。

## 实际读取与样本选择

读取了上游 README、LICENSE、CONTRIBUTING、完整 index 与两条完整走廊 JSON，固定在提交 `eb6496d32e2951c984644a743dfb6d080fd998ce`；数据版本另为 `d7b4411b411758c43b97496e4cbc7d3c3b003483`。逐文件 URL 与 SHA-256 见[清单](../research/week1/petra-manifest.json)，原文在 [Petra 快照目录](../research/week1/petra/README.md)。未读取其私有评估器。

固定版本索引共 56 条；起点或终点为 `CN` 的条目为 **0**。因此无法抽出两条同时覆盖中美欧三地的现成规则：选与目标直接相交的美国→德国、美国→荷兰两个样本，另对中国缺口明确自建。这是版本覆盖限制，不代表未来或其他分支没有中国数据。

| 项目 | 美国→德国 | 美国→荷兰 | 对 PetWaymark 的影响 |
|---|---|---|---|
| 原始文件 | [DE JSON](../research/week1/petra/corridors/united-states-to-germany.json) | [NL JSON](../research/week1/petra/corridors/united-states-to-netherlands.json) | 固定快照可离线比较 |
| scope | `origin_scope=[US]`；`species_scope=null` | 相同 | 不能把空物种解释成犬猫全部支持 |
| 条目 | 8 个 requirements、1 个 manual checklist、6 个 sources | 相同 | 条目均为 `interpretation` |
| 上游审查 | `tier=verified`；2026-09-20 | 相同 | 仅记录上游历史，项目复核仍为空 |
| 内容差别 | 德国标识及链接 | 荷兰标识及链接 | 仅 corridor、destination、url、history_url 四个顶层字段不同 |
| 缺口 | 无路线分段、口岸能力、承运产品、州／地方叠加 | 同；APHIS 来源仍指德国页 | 共同模板不是成员国细则覆盖的证据 |

与六个方向对照：CN→US、US→CN、CN→EU、EU→CN 无中国相关条目；US→EU 有本次两样本；EU→US 的索引中有 IE→US，但无 DE／FR／NL→US，不能拿爱尔兰替代首批三国。国内三地联运也不在两样本内。

## 字段映射（设计，非已实现 schema）

| Petra 路径 | PetWaymark 拟议字段／处置 | 转换条件 |
|---|---|---|
| `schema_version` | `upstream.schema_version` | 与本项目 `schema_version` 分离 |
| `corridor`, `origin.code`, `destination.code` | `upstream.corridor`、`scope.origin/destination` | 保留方向；EU 落到具体成员国 |
| `origin_scope`, `species_scope` | `scope.origin`、待补 `scope.species` | null 进入缺口队列，不默认为全部物种 |
| `ruleset.name/stem` | `upstream.ruleset` | 保留旧命名，不据名字判断现行法规 |
| `requirements[].key` | 候选稳定 ID 的来源键 | ID 加地域与分支；拆条件后保留回指 |
| `requirements[].title/scope_notes` | `draft_summary`、`scope_notes` | 自然语言不能自动变比较运算符 |
| `requirements[].class` | `upstream.record_class=interpretation` | 核原文后另定项目 `record_class`，不提升来源等级 |
| `manual_checklist[].required/detail` | 待核清单与时间轴候选 | `required=false` 不等于法定可选 |
| `sources[].url/authority/page_title` | `source_ids` 与来源目录 | 逐项建立要求→原文定位关系 |
| `sources[].retrieved_at` | `upstream.accessed_at` | 项目实际抓取日单独保存 |
| `sources[].applies_to/supporting_requirements` | 来源适用范围候选 | 不能仅凭文字相似自动匹配 |
| `source_url`, `url`, `history_url` | 主来源、上游页面、版本历史 | 官网优先，历史镜像仅研究线索 |
| `tier/tier_label/last_reviewed` | `upstream.review` | 本项目 `review.status=draft`，`reviewed_by=[]` |
| `recommended_lead_time_days` | 项目准备建议的待核候选 | 不当成法律最短等待期 |
| `caveats/verified_scope_note/related_destination_note` | 解释与缺口 | 空数组不等于无例外 |
| `version` | `upstream.dataset_version` | 与公开仓库 commit 分开保存 |
| `license/license_scope/no_warranty/disclaimer` | 归属、许可、免责声明 | 保留，不覆盖官方文本权利 |
| `corrections` | 上游纠错渠道元数据 | 本周不发消息／issue／PR |
| 上游缺失 | `validity`、结构化 `requirement`、`on_missing`、例外、模式、时区、复核期限 | 必须补证据，未完成不能执行 |

## 核对中发现的阻塞

1. `ruleset` 仍叫 576/2013，但 sources 已引用 2026/131 和 2026/705，不能依据旧标签生成证书逻辑。欧委会当前页与 APHIS 当前德、荷页均已打开；[官方核对记录](../research/week1/official-review.md)区分新证模板与旧证过渡。
2. checklist 把入境时间窗口放在 `required=false` 下；适配器若按该布尔值跳过，会丢失重要条件。证书签发、背书、入境及后续移动需不同时间锚点，不能从标题直接提取一个“10 天”。
3. 荷兰样本重复引用德国 APHIS 页；一条证据来自 Wayback 上的阿联酋页横幅。项目规则需使用当前德国／荷兰官方页、对应法条及附件，历史镜像不作为正式唯一证据。
4. 来源描述提及 `certificate_transition`，实际导出 JSON 没有该字段；`species_scope` 为空，陪同分类简化。不能假设私有引擎中的条件已完整公开。

## 许可、更新与实施取舍

依上游 [LICENSE](../research/week1/petra/LICENSE)，其整理内容与结构为 CC BY 4.0；链接的主管机关原文、第三方引用与商标不在授权内。已保留未修改快照、版本、来源、许可证及[归属与修改说明](../../THIRD_PARTY_NOTICES.md)。复用并不表示上游背书。

上游 README 表明仓库由私有生成器单向发布，含自动生成的 changelog；贡献指南要求每次 PR 只改一个走廊、提供主来源和抓取日、通过来源域名／时效／schema 等门禁，再由人审。受保护版本和审查字段不能由贡献者改写。此处描述的是已读指南，未运行其 CI 或验证其执行效果。

下一步设计：固定 commit 下载→比对哈希／差异→生成候选草稿→官方复核→补全结构化条件和正反例→人工批准后另版发布。不得直接追踪 main 覆盖正式规则；删除或冲突须生成待审事项。若适配成本高于人工整理，仅保留来源索引复用。

| 决定 | 内容 |
|---|---|
| 复用 | 上游研究快照、来源线索、版本与归属机制 |
| 适配 | 两条 US→EU 的解释记录，补类型、日期锚点、来源定位和成员国差异 |
| 自建 | 中国相关四方向、首批 DE／FR／NL→US、国内联运、承运／设施叠加、公开评估引擎 |
| 暂不做 | 自动导入即发布、重写上游私有实现、推送贡献、以两条样本宣称六方向可用 |
