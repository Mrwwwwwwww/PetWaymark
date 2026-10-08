# Independent US/EU → China research preview

Free offline dog/cat document planning, itemized cost gaps and a neutral public
policy directory. Every result remains `unsupported`: no independent legal review,
verified route, booking, quarantine exemption or actual custody confirmation.

```sh
.venv/bin/python -m packages.cli tests/fixtures/inbound/us-cn-dog.json --inbound-preview --assessment-at 2026-10-08 --format checklist --language en
.venv/bin/python -m packages.cli tests/fixtures/inbound/eu-cn-cat.json --inbound-preview --assessment-at 2026-10-08
.venv/bin/python -m apps.web.server --port 8766
```

Open `http://127.0.0.1:8766/?example=inbound-us` or `/?example=inbound-eu`.
The local form, CLI, redacted download and print use the same kernel. Language
switching preserves fields and reasons. Use US/EU→CN inputs for branch, origin,
health records and reported lab/identity information; shared international inputs
hold issue/endorsement/departure/sample/delivery dates and anonymous roles.
Microchip presence is in the evidence inputs. No account, uploads or model key.

Only single ordinary privately owned dogs/cats carried by an owner or responsible
person, cabin or passenger baggage, no transit, are in this research scope.
Separate cargo and animals without an accompanying traveler stop before the
carried-entry diagnostics. US-CA/NY/TX are initial mainland examples; Hawaii/Guam
exceptions and other US areas remain uncompiled. EU exports are independently
limited to partial DE/FR/NL process readings; the other 24 members are uncompiled.
EU owner five-day, EU-entry ten-day and EU antibody ninety-day windows are never
reversed into China requirements. An EU passport cannot replace an official
China export health certificate. China-specific member certificates and actual
signing/legalisation routes remain unreviewed.

Choose a **research** branch explicitly: non-designated origin with antibody report,
quarantine, or designated-origin exception. Country and airport alone never establish
an exemption or facility. Current GACC origin/lab/port lists, attachments and
supersession need review. Quarantine does not waive mandatory documents or chip
requirements and does not promise release. APHIS dog PDF has a no-chip quarantine
note conflicting with GACC's general chip requirement; the preview keeps the chip
gap and does not grant a waiver. Arrival inspection is always unconfirmed.

US issue-to-arrival checks and chronological delivery checks are independent of
endorsement: later endorsement does not reset issue time. Exact titer 0.5 stays
in conflict pending clarification. Calendar anniversary validity is a civil-date
research estimate, including leap-day clamping; it does not decide an official
expiry instant. The dog model is only read, and the cat PDF was unavailable.
Original vaccine/report copies may be retained on arrival; carrying, delivery and
receiving roles are reported planning roles, `custody_confirmed=false`.

Eleven cost items preserve unknown amount, currency, inclusions/exclusions,
quotation date/expiry and source. Unknown is not zero; no total, currency conversion
or low-price ranking. CLI-only optional `cost_quotes` accepts anonymous manual
notes keyed by cost item, with `currency/min/max/quoted_at/expires_at/includes/excludes/source`.
Incomplete, future-dated and expired notes are visible; expiry date is conservatively
excluded. Even a complete manual note is unconfirmed. The web shows unknown
costs and sends no quotation request. These notes are never persisted.

The [directory](../../data/providers/directory.json) lists three public policy
samples alphabetically. It separates public listing, partially read capability and
actual external confirmation (unknown). Each entry has a source, checked date,
limited scope and affiliation disclosure. Alaska cargo is a US domestic lead, not
China capacity; passenger baggage policies do not establish separate cargo service.
No recommendation, referral, order button, price or specific leg acceptance.
Equal inclusion criteria and missing operating-entity/qualification/last-mile
confirmation apply to all samples; submit corrections through the repository's
provider correction template without private identifiers.

[Reading record](../research/week8/README.md) · [decision](../decisions/0008-cn-inbound-planning.md).
Tests and synthetic fixtures are not users, adoption or qualified human reviews.
Hosted static delivery, actual carrier acceptance and last-mile care remain pending.
