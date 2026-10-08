# US ↔ EU document and return research preview

Free public-benefit planning; no booking, orders or carrier/provider ranking.
Every current public route is unsupported. Draft diagnostic passes are not permission.
Independent human reviews and verified feasible routes are zero.

```sh
python -m packages.cli tests/fixtures/us-eu/us-eu-dog.json --us-eu-preview --assessment-at 2026-10-08
python -m packages.cli tests/fixtures/us-eu/eu-us-cat.json --us-eu-preview --assessment-at 2026-10-08 --format checklist --language en
python scripts/audit_coverage.py --check
python -m apps.web.server --port 8766
```

Visit `http://127.0.0.1:8766/?example=us-eu` or `/?example=eu-us`, select dog/cat,
enter only anonymous dates and reported readiness. Language change preserves input
and reasons; export and print use the CLI kernel. Invalid submitted values are
rejected without echoing their text. No account, upload, storage, network/model key
or provider contact is needed. This loopback server is not hosted static deployment.

US→EU is a separate accredited-vet certificate chain, with signature, endorsement,
printed-document delivery, departure, arrival and entry checks. Manufacturer immunity
period is required explicitly; a guessed 21-day period is not filled in. Primary US
vaccination's one-year research limit is checked separately from self-reported expiry.
The EU old-model issue cutoff and APHIS old-model endorsement cutoff are separate;
model-date consistency does not establish document validity or a booked inspection.
Passport return uses distinct checks for EU-vet vaccination records and US
revaccination; it is not a general substitute for a new certificate.

EU→US cats use healthy-arrival research and retain local export, state, carrier and
inspection gaps. Dog form, age and chip rules are not applied to cats. Dog history
is a six-month self-report rather than inferred from EU departure. Missing history
stops branch-specific inference; conflicting last-high-risk-exit dates stop the
receipt-only diagnostics. No complete chronological history or full country list is
verified by this form. All states, Hawaii and territories need local requirements.

Low-risk dog receipt country and reported expiry remain distinct. High-risk dogs
have independent US-vaccinated and foreign-vaccinated branches. The former checks
proof prepared before original US departure and the legacy export issue cutoff;
missing valid proof requires the separate foreign high-risk fallback, not exemption.
The latter retains foreign form/endorsement, sample-to-entry and actual ACF/airport,
accepted-lab, titer/quarantine gaps. Unknown vaccine origin remains unresolved.
No facility reservation, official form content or entry permission is confirmed.

Final pickup timestamps require a UTC offset and IANA timezone, for example
`2026-11-01T01:30:00-05:00` and `America/New_York`. Repeated DST times are distinct,
spring gaps are invalid. Arrival after the reported pickup deadline marks a blocked
handover requiring a recovery plan. Unknown required overnight care or an unassigned
custodian stays unresolved. An available carer is only self-reported; custody and
external confirmation never become confirmed. These diagnostics do not fabricate
transport schedules, opening hours, carers, capacity or contacts.

The engine `assess_round_trip(first, returning, assessment_at=..., previous_dataset_version=...)`
reassesses opposite directions against current trusted data and flags dataset changes.
It checks species/dates, not identity or that two profiles belong to the same pet.
There is no automatic reversal, booking or hosted round-trip workflow.

The [48-case audit and six-direction matrix](../../data/coverage/week9-matrix.md)
executes domestic CN east/south, US CA/NY/TX and EU domestic/cross-member examples,
all six independent international directions and dog/cat baselines. It includes
age, certificates, actual rule cutovers, return history, unsupported transit,
missed final pickup, overnight uncertainty and DST. JSON retains exact observed
outcomes, sources, dates and gaps. `--check` and CI reject generated drift.
Synthetic cases are not actual users, quotations, reviews or verified routes.

[Reading record](../research/week9/README.md) · [Decision](../decisions/0009-us-eu-and-audit.md).
Current 2026/636 annex access failed again. First US→EU guidance is France-specific;
other destinations, full member export procedures, lab/current lists and independent
reviews remain incomplete. No whole-EU titer exemption or transport route is asserted.
