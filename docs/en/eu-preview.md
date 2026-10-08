# EU evidence preview

The local bilingual web and CLI share an offline research assessment for one privately
owned dog or cat. Install the development dependencies as in the repository README.
There are no model calls, accounts, stored profiles or paid runtime services.

```sh
python -m packages.cli tests/fixtures/eu/cross-member.json --eu-preview --assessment-at 2026-10-08
python -m packages.cli tests/fixtures/eu/domestic.json --eu-preview --assessment-at 2026-10-08 --format checklist --language en
python -m packages.cli tests/fixtures/eu/owner-not-moving.json --eu-preview --assessment-at 2026-10-08
python -m apps.web.server --port 8766
```

Open `http://127.0.0.1:8766/?example=eu-owner` or `/?example=eu-boarding`.
Choose a domestic DE/FR/NL example, DE→FR, FR→NL, NL→DE, or DE→IE local-gap example.
Expand “EU evidence inputs” to enter owner movement/dates, written authorisation and
anonymous document/event dates. Do not enter chip numbers, contacts or private addresses.
Language switching preserves inputs; JSON and printable output omit raw profiles.

Classification precedes document diagnostics. Owner-stays-home boarding, missing
purpose/ownership or owner movement, unsupported member and unresolved accompaniment
stop the ordinary cross-member branch. Written authorisation and owner movement within
five civil days are checked separately from cargo transport mode. This preview uses
civil dates; zoned schedules and responsibility evidence are not yet supported.
A valid classification means only that research diagnostics can run.

Entirely domestic journeys do not execute the cross-member rabies/passport drafts.
Cross-member cases expose three partial, unenforced constraints and identification /
passport model-date diagnostics. A consistent model/date does not establish document
validity, residence eligibility, recognised issuer, uninterrupted rabies cover, booking
or confirmed custody. Tattoo exceptions remain for confirmation. Health-certificate
and titre helpers are research-only, not an international timeline or entry decision.

The [27-member inventory](../../data/coverage/eu-members.json) contains partial readings
for DE/FR/NL and explicit local gaps for the other 24. A common framework is not complete
country coverage. All results remain `unsupported`; transport paths, estimates, ranking
and verified feasible route counts are absent or zero. Original-document responsibility
remains pending arrangement. The [dated source and annex map](../research/week6/README.md)
is the detailed reference for transitions, exceptions and source access failures.

[中文](../zh/eu-preview.md)
