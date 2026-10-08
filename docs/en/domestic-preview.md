# Domestic research preview

Week 4 provides a first offline data/engine preview, free and without model keys,
accounts or runtime network access. It has two CN research corridors, not verified
feasible transport routes. The web interface and US work remain Week 5.

After the installation in [README](../../README.md), run:

```sh
python -m packages.cli tests/fixtures/domestic/owner.json --corridor dom.cn.east --assessment-at 2026-10-08
python -m packages.cli tests/fixtures/domestic/owner.json --corridor dom.cn.south --assessment-at 2026-10-08 --format checklist --language en
python -m packages.cli tests/fixtures/domestic/unaccompanied.json --corridor dom.cn.east --assessment-at 2026-10-08
python -m packages.cli tests/fixtures/domestic/infeasible.json --corridor dom.cn.east --assessment-at 2026-10-08 --format checklist --language en
```

Redirect a checklist to a local `.txt` file for printing. Use `--language zh-CN` for
Chinese. Both languages retain the same IDs, statuses, reason codes and evidence.
Default JSON is suitable for offline integrations. Exit 0 includes valid unsupported
or ineligible results; malformed JSON, dates, controls or data return 2 on stderr.

| Corridor | Road | Rail research hubs | Air-ground research hubs |
|---|---|---|---|
| `dom.cn.east` | Huzhou → Qingyuan | Huzhou → Shanghai Hongqiao → Guangzhou South → Qingyuan | Huzhou → PVG → CAN → Qingyuan |
| `dom.cn.south` | Qingyuan → Langfang | Qingyuan → Guangzhou South → Beijing West → Langfang | Qingyuan → CAN → PEK → Langfang |

An owner profile yields up to three distinct research candidates: self-drive,
accompanied rail with first/last transfers, and passenger checked baggage with
first/last transfers. An unaccompanied profile uses separate animal-carrier/rail
branches and cannot borrow passenger baggage. Road-carrier and ground-transfer
providers are unverified and unassigned. Rail station history is separate from the
2026 two-mode product; no particular station pair, date or train is claimed available.
Passenger baggage is separate from manifest cargo, whose terminals/products remain
uncovered. These products are evidence scopes, not brand recommendations.

All public candidates are **unsupported**, unranked, without duration, cost, slots or
booking. Rail weight/size comparisons are draft diagnostics even when they fail.
Actual CN domestic requirements and complete roads still need human review.
No CN import rule is used domestically. `infeasible.json` explicitly disables driving,
reports an air refusal and a missed rail handover window, excluding all graph paths.
This is a synthetic operational counterexample, not a real refusal or a statement
that no other trip could work. Declining a final transfer also excludes the whole path.

`preview` controls support `journey_id`, `plan_revision`, `can_drive`, and `segments`
keyed by stable segment ID. Per-segment fields are `reported_acceptance` (unknown or
declined) and `handover_window_met` (boolean or null). Missing is unknown; no automatic
clock-window calculation exists. Evidence/coverage/roles cannot be overridden by
these controls. IDs must be opaque and free of personal information; increment
revision when changing dates. Input declarations are not carrier confirmations.

Each printed segment includes the destination facility as an approximate handover
location, a needs-confirmation window, pending escort/custodian/recipient/document
custodian, and evidence URLs/locators/access dates. Nobody is assigned custody by the
project. Exact counter/office, receiving hours, documents, care, delay handling and
backup arrangements must be confirmed outside the project. No booking or order is
created. Postponing travel or arranging local care remains a useful alternative.

[Decision and contract](../decisions/0004-domestic-preview.md) ·
[Source reading and unresolved work](../research/week4/README.md) ·
[Graph data](../../data/corridors/cn-preview.json) · [中文](../zh/domestic-preview.md)
