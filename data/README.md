# Data scope / 数据许可与状态

Original curated records under this directory use [CC BY 4.0](../LICENSE-DATA). Credit PetWaymark contributors, link the license and identify modifications and the dataset version. Third-party materials retain their own terms; see [notices](../THIRD_PARTY_NOTICES.md).

`coverage/week1-candidates.json` is an original **research plan**, not a route service catalogue or legal rule package. All candidates are `unsupported`, carrier acceptance is unknown, and there are zero verified production rules. The ten Week 2 records remain drafts, with no approved human review. Week 2 rule records are governed by the [rule/source contract](../docs/en/rule-contract.md). `sources/catalog.json` is the current rule source registry; Week 1 research and Petra snapshots remain historical leads. A structurally valid record is not legal approval.

`null` means unknown, never “no restriction.” Source access dates are separate from human review and effective dates. Do not store raw personal documents or invent provider, schedule, distance or price data.

`corridors/cn-preview.json` is the Week 4 draft-only directed research graph, dataset
version `2026-10-08.week4-preview`. It adds two domestic examples and per-segment
evidence from eight additional catalog readings. Its schema cannot claim verified
capacity. The [offline preview](../docs/en/domestic-preview.md) retains unsupported
status, unknown estimates and pending responsibilities. Original curation is CC BY
4.0; linked texts retain their own rights. No original source page is redistributed.

本目录的走廊是待研究候选；不能用于断言可以运输。正式规则需独立来源、日期、适用范围与人工复核记录。
第4周图仅为国内草稿研究预览；增加来源不等于完成独立复核或开放实际能力。

## v0.1 package / 独立数据包

Curated package version `2026.10.08-draft.1` is independent of engine `0.1.0`.
`VERSION.json` records SHA-256 hashes; `scripts/package_data.py --check` detects drift,
and `scripts/package_data.py` builds a deterministic archive. All 15 rule records
remain drafts; no verified route. Component historical versions are preserved.

数据包版本独立于引擎，哈希仅证明文件一致，不证明规则已核。全部15条规则仍为
草稿、零已验证路线；发布边界见[发布说明](../docs/releases/v0.1.0.md)。
