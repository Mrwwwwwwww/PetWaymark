# Week 9 coverage audit / 第9周覆盖审计

48/48 executed synthetic cases pass; verified feasible routes 0, actual usage 0.
48/48个合成案例实际执行通过；已验证可行路线0，真实采用0。

Reproduce / 复跑：`python scripts/audit_coverage.py --check`。Generated outputs must match; failures exit nonzero.

Route status differs from draft diagnostic outcomes and final-handover readiness. Unknown never grants permission.
路线状态、草稿诊断与末段交接准备分别展示；未知不表示允许。

- `unsupported`: Scope or evidence incomplete; no permission. / 范围或证据不全，不表示允许。
- `conditional`: Reviewed rule eligibility with unresolved operations; not a confirmed route. / 已复核规则满足但操作条件待确认，非确认路线。
- `ineligible`: Explicit operational contradiction excludes every candidate; draft legal failures alone do not reject. / 明确操作冲突排除全部候选；草稿法律诊断失败本身不裁定拒绝。
- `verified_supported`: Reviewed current rules and evidenced dated whole-route capacity/custody. None exists. / 现行规则已复核且全程日期限定运力与责任有证据；当前无此路线。

| Direction / 方向 | Dog / 犬 | Cat / 猫 | Executed / 执行 | Verified / 已验证 |
|---|---|---|---|---|
| CN→US | unsupported (W9-001) | unsupported (W9-002) | 3 | 0 |
| CN→EU | unsupported (W9-004) | unsupported (W9-005) | 4 | 0 |
| US→CN | unsupported (W9-007) | unsupported (W9-008) | 4 | 0 |
| EU→CN | unsupported (W9-010) | unsupported (W9-011) | 3 | 0 |
| US→EU | unsupported (W9-013) | unsupported (W9-014) | 10 | 0 |
| EU→US | unsupported (W9-016) | unsupported (W9-017) | 14 | 0 |

Full source URLs, access dates, evidence states and pending checks are in [week9-audit.json](week9-audit.json).
完整来源URL、查阅日期、证据状态、缺项及逐案例诊断见同目录JSON。每个方向独立内核输出，未整体宣称成员国覆盖。

| Case / 案例 | Area / 地区方向 | Fixture | Observed status / 观察状态 | Assertion / 断言 |
|---|---|---|---|---|
| W9-001 | CN→US | `tests/fixtures/outbound/cn-us-dog.json` | unsupported | {"classification_resolved": true} |
| W9-002 | CN→US | `tests/fixtures/outbound/cn-us-cat.json` | unsupported | {"classification_resolved": true} |
| W9-003 | CN→US | `tests/fixtures/outbound/cn-us-dog.json` | unsupported | {"classification_resolved": false} |
| W9-004 | CN→EU | `tests/fixtures/outbound/cn-eu-dog.json` | unsupported | {"classification_resolved": true} |
| W9-005 | CN→EU | `tests/fixtures/outbound/cn-eu-cat.json` | unsupported | {"classification_resolved": true} |
| W9-006 | CN→EU | `tests/fixtures/outbound/cn-eu-dog.json` | unsupported | {"classification_resolved": false} |
| W9-007 | US→CN | `tests/fixtures/inbound/us-cn-dog.json` | unsupported | {"classification_resolved": true} |
| W9-008 | US→CN | `tests/fixtures/inbound/us-cn-cat.json` | unsupported | {"classification_resolved": true} |
| W9-009 | US→CN | `tests/fixtures/inbound/us-cn-dog.json` | unsupported | {"classification_resolved": false} |
| W9-010 | EU→CN | `tests/fixtures/inbound/eu-cn-dog.json` | unsupported | {"classification_resolved": true} |
| W9-011 | EU→CN | `tests/fixtures/inbound/eu-cn-cat.json` | unsupported | {"classification_resolved": true} |
| W9-012 | EU→CN | `tests/fixtures/inbound/eu-cn-dog.json` | unsupported | {"classification_resolved": false} |
| W9-013 | US→EU | `tests/fixtures/us-eu/us-eu-dog.json` | unsupported | {"classification_resolved": true} |
| W9-014 | US→EU | `tests/fixtures/us-eu/us-eu-cat.json` | unsupported | {"classification_resolved": true} |
| W9-015 | US→EU | `tests/fixtures/us-eu/us-eu-dog.json` | unsupported | {"classification_resolved": false} |
| W9-016 | EU→US | `tests/fixtures/us-eu/eu-us-dog.json` | unsupported | {"classification_resolved": true} |
| W9-017 | EU→US | `tests/fixtures/us-eu/eu-us-cat.json` | unsupported | {"classification_resolved": true} |
| W9-018 | EU→US | `tests/fixtures/us-eu/eu-us-dog.json` | unsupported | {"classification_resolved": false} |
| W9-019 | CN east | `tests/fixtures/domestic/owner.json` | unsupported | {} |
| W9-020 | CN south | `tests/fixtures/domestic/owner.json` | unsupported | {} |
| W9-021 | US CA→NY | `tests/fixtures/us-domestic/owner.json` | unsupported | {} |
| W9-022 | US NY→TX | `tests/fixtures/us-domestic/owner.json` | unsupported | {} |
| W9-023 | US TX→CA | `tests/fixtures/us-domestic/owner.json` | unsupported | {} |
| W9-024 | EU domestic | `tests/fixtures/eu/domestic.json` | unsupported | {"classification_resolved": true} |
| W9-025 | EU cross-member | `tests/fixtures/eu/cross-member.json` | unsupported | {"classification_resolved": true} |
| W9-026 | US→EU | `tests/fixtures/us-eu/us-eu-dog.json` | unsupported | {"classification_resolved": true, "diagnostic": {"id": "eu.manufacturer-wait", "outcome": "fail"}} |
| W9-027 | US→EU | `tests/fixtures/us-eu/us-eu-dog.json` | unsupported | {"classification_resolved": true, "diagnostic": {"id": "eu.certificate-model", "outcome": "model_issue_cutoff_failed"}} |
| W9-028 | US→EU | `tests/fixtures/us-eu/us-eu-dog.json` | unsupported | {"classification_resolved": true, "diagnostic": {"id": "eu.aphis-old-model-endorsement", "outcome": "fail"}} |
| W9-029 | US→EU | `tests/fixtures/us-eu/us-eu-dog.json` | unsupported | {"classification_resolved": true, "diagnostic": {"id": "eu.issue-to-entry", "outcome": "date_window_conflict"}} |
| W9-030 | US→EU | `tests/fixtures/us-eu/us-eu-dog.json` | unsupported | {"classification_resolved": true, "diagnostic": {"id": "eu.endorsement-to-check", "outcome": "date_window_conflict"}} |
| W9-031 | US→EU | `tests/fixtures/us-eu/us-eu-dog.json` | unsupported | {"classification_resolved": true, "diagnostic": {"id": "eu.passport-us-revaccination", "outcome": "fail"}} |
| W9-032 | US→EU | `tests/fixtures/us-eu/us-eu-dog.json` | unsupported | {"classification_resolved": false} |
| W9-033 | EU→US | `tests/fixtures/us-eu/eu-us-dog.json` | unsupported | {"classification_resolved": true, "diagnostic": {"id": "us.dog-age", "outcome": "fail"}} |
| W9-034 | EU→US | `tests/fixtures/us-eu/eu-us-dog.json` | unsupported | {"classification_resolved": true, "diagnostic": {"id": "us.receipt-country", "outcome": "country_mismatch"}} |
| W9-035 | EU→US | `tests/fixtures/us-eu/eu-us-dog.json` | unsupported | {"classification_resolved": true, "diagnostic": {"id": "us.receipt-not-expired", "outcome": "fail"}} |
| W9-036 | EU→US | `tests/fixtures/us-eu/eu-us-dog.json` | unsupported | {"classification_resolved": true, "diagnostic": {"id": "us.six-month-history", "outcome": "history_conflict"}} |
| W9-037 | EU→US | `tests/fixtures/us-eu/eu-us-dog.json` | unsupported | {"classification_resolved": true, "diagnostic": {"id": "us.six-month-history", "outcome": "missing"}} |
| W9-038 | EU→US | `tests/fixtures/us-eu/eu-us-dog.json` | unsupported | {"classification_resolved": true, "diagnostic": {"id": "us.legacy-export-cutoff", "outcome": "fail"}} |
| W9-039 | EU→US | `tests/fixtures/us-eu/eu-us-dog.json` | unsupported | {"classification_resolved": true, "diagnostic": {"id": "us.return-form-before-exit", "outcome": "fail"}} |
| W9-040 | EU→US | `tests/fixtures/us-eu/eu-us-dog.json` | unsupported | {"classification_resolved": true, "diagnostic": {"id": "us.foreign-titre-to-entry", "outcome": "fail"}} |
| W9-041 | EU→US | `tests/fixtures/us-eu/eu-us-cat.json` | unsupported | {"classification_resolved": true, "diagnostic": {"id": "us.cat-dog-rules", "outcome": "not_applicable"}} |
| W9-042 | CN east | `tests/fixtures/domestic/owner.json` | ineligible | {"reason": "all_paths_excluded"} |
| W9-043 | CN east | `tests/fixtures/domestic/owner.json` | unsupported | {"overnight_outcome": "care_unknown", "pickup_outcome": "window_missed"} |
| W9-044 | US CA→NY | `tests/fixtures/us-domestic/owner.json` | unsupported | {"overnight_outcome": "care_unknown", "pickup_outcome": "within_reported_window"} |
| W9-045 | EU→US | `tests/fixtures/us-eu/eu-us-dog.json` | unsupported | {"overnight_outcome": "care_unavailable", "pickup_outcome": "window_missed"} |
| W9-046 | EU→US | `tests/fixtures/us-eu/eu-us-cat.json` | unsupported | {"overnight_outcome": "care_unavailable", "pickup_outcome": "invalid_time"} |
| W9-047 | US→CN | `tests/fixtures/inbound/us-cn-dog.json` | unsupported | {"diagnostic": {"id": "cn.titre.threshold", "outcome": "threshold_conflict_pending_clarification"}} |
| W9-048 | CN→EU | `tests/fixtures/outbound/cn-eu-dog.json` | unsupported | {"classification_resolved": false} |

Final pickup is evaluated with explicit offset plus IANA timezone; DST folds are distinguished and nonexistent times rejected.
Required overnight care with unknown availability or an unassigned custodian stays unresolved. Self-report cannot confirm custody.
末段使用显式UTC偏移及IANA时区，区分DST重复时刻并拒绝不存在时刻；必需过夜照护未知、保管人未安排不被补齐，自报不能确认责任。

Independent human reviews, full current annexes, EU local export procedures, US state/emergency overlays, actual operating capacity, originals and recovery custody remain pending.
独立人工复核、完整现行附件、欧盟地方出口、美国州／应急叠加、实际运力、原件和异常责任仍待完成。
