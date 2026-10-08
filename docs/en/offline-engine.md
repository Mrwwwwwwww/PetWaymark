# Offline constraint evaluation

[中文](../zh/offline-engine.md) · [Date/trust decision](../decisions/0003-offline-evaluation.md)

Week 3 implements five expression shapes and executes all nine Week 2 boundary
fixtures. All ten public rules remain drafts and produce `unsupported` assessments.
There are still zero verified feasible routes. No network or model key is used at
runtime; install the existing development requirements once for CLI package validation.

From the repository root:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m packages.cli tests/fixtures/boundaries/boundary.unknown-carrier.json --assessment-at 2026-10-08
.venv/bin/python -m unittest discover -s tests -v
```

CLI exit 0 means a valid assessment was produced, including `unsupported` or
`ineligible`. Invalid input/package/date returns exit 2. Flat Week 2 fixtures select
only their listed rules for regression replay. Ordinary JSON profiles use nested
`pet`, `journey`, `documents`, `events` objects and assess all public rules. Input
`coverage_gaps` cannot override the CLI's unresolved coverage default.

Profiles use the dotted field names from the [rule contract](rule-contract.md).
Journey classification fields are `origin`, `destination`, `purpose`,
`ownership_transfer`, `accompaniment`, `transport_mode`, `entry_at`, `owner_entry_at`,
`travel_history_branch`, `vaccination_branch`, optional `subdivision`, and
`carrier_acceptance`. Pet classification includes `species` and `service_animal`.
Missing fields stay unknown. Dates are local civil dates, not timestamps. Unknown
history does not become low risk; origin alone cannot establish six-month history.

The standard-library API is `packages.engine.evaluate(profile, validated_rules,
assessment_at=...)`. Schema/reference validation is the caller's responsibility;
`packages.engine.io.load_repository()` performs it for repository packages. API
coverage attestations are trusted maintenance inputs described in the decision;
never pass them from a user form. Synthetic reviewed records exist only in tests,
with fictional review identities and explicit scope resolution. They are not
published official rules, human reviews or feasible route evidence.

Outputs include status, coverage gaps, deterministic reason codes, matched/excluded
rule IDs, revisions, evidence and bilingual explanations. Failed draft comparisons
are diagnostic only. Rule satisfaction never confirms carrier acceptance. Even an
externally supplied confirmed status does not establish booking validity.
