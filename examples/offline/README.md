# Pinned offline read-only reuse / 固定版本离线只读复用

From this checkout, with Python 3.11+ and the development dependencies installed:

```sh
python -m examples.offline.read_only
```

No model key, account or network is used at runtime. One existing **synthetic** fixture
is assessed with the production engine. [Lock](lock.json) fixes engine Python files,
validator, data manifest and fixture by SHA-256, engine `0.1.0`, data
`2026.10.08-draft.2`, assessment date `2026-10-08`.
Run from the commit containing this example, or use its immutable commit URL in the
maintenance report; a release tag is unnecessary. Hashes check byte consistency,
not truth or independent review. Drift fails closed; do not auto-update the lock.

运行不需要网络、账号或模型密钥。只读现有合成案例，使用生产引擎；哈希固定
引擎／校验器／清单／输入，并检查全部数据哈希。漂移即失败，不自动更新。
哈希不证明事实正确，不是独立人审或真实采用。

The JSON is a minimal integration contract example: status, reason codes, coverage
gaps, engine/data versions, rule review dates and actual official source locators.
A downstream tool can display these fields without flattening away `draft` or
unknown acceptance. The requirement is also reused with `compare`: its `pass`
is only a synthetic expression diagnostic, while the overall assessment stays
`unsupported`. All curated rules remain draft; no complete journey is covered.
Never pass `coverage_gaps=[]` to suppress missing rule coverage.

输出供下游显示状态、原因、覆盖缺口、复核状态／日期、版本与官方原文定位。
`compare`的`pass`仅说明合成输入满足一项表达式，整体仍未覆盖；
单条条件不证明出行允许。未来Agent可读取此JSON，但没有外部集成或采用证据。
没有托管API、MCP服务、订单、运力查询或规则写入；本轮选择此示例，T41/T84后置。

Code: Apache-2.0. Curated rule summaries: CC BY 4.0, attribution PetWaymark and
linked official source IDs; official website text retains its own rights.
Retain [NOTICE](../../NOTICE), [data license](../../LICENSE-DATA) and
[third-party notices](../../THIRD_PARTY_NOTICES.md) when redistributing data.
