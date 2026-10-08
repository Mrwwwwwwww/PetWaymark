# CN outbound document preview

This offline research tool separates CN→US and CN→EU dog/cat document chains.
Every public result remains `unsupported`; no reviewed legal package, route,
booking or actual original-document delivery is asserted. No account, model key,
paid API, uploads or private identifiers are needed.

```sh
.venv/bin/python -m packages.cli tests/fixtures/outbound/cn-us-dog.json --outbound-preview --assessment-at 2026-10-08 --format checklist --language en
.venv/bin/python -m packages.cli tests/fixtures/outbound/cn-eu-cat.json --outbound-preview --assessment-at 2026-10-08
.venv/bin/python -m apps.web.server --port 8766
```

Open `http://127.0.0.1:8766/?example=outbound-us` or `/?example=outbound-eu`.
Select species and accompaniment, open EU evidence inputs for owner/vaccine dates,
and CN outbound inputs for documents, appointments and responsibility roles.
The form, CLI, JSON download and printable checklist call the same module.
Switching language preserves inputs and reason codes. This is a loopback development
server; hosted static delivery remains deferred.

The four [synthetic fixtures](../../tests/fixtures/outbound/) are independent
US/EU dog/cat examples. Owner, authorised-person and unaccompanied cases are tested
for each; EU unaccompanied, owner-not-moving, missing written authorisation and
owner dates outside the ordinary branch stop diagnostics. Cargo product alone
does not decide EU legal classification. US dog history/vaccine origin is separate
from EU owner timing. CN mainland origin cannot assert only-low-risk history.
US-vaccinated dogs and service animals stop at their uncompiled branches.

| Input / output | Meaning |
|---|---|
| `journey.departure_at`, `entry_at` | Separate origin departure and destination entry civil dates. |
| `first_entry_member`, `destination_member`, `entry_airport` | First EU entry and onward destination are distinct; source-read points are never approved capacity. |
| `events.rabies_vaccination_at`, `primary_protocol_completed_at`, `titre_sample_at` | Primary vaccine, protocol and sample anchors; booster continuity is unreviewed. |
| `documents.origin_certificate_issued_at` | CN origin export document, distinct from foreign-entry form/certificate. |
| `certificate_issued_at`, `certificate_endorsed_at`, `issuer_route` | US veterinary signature versus government endorsement; EU official issue versus authorised issue subsequently endorsed. |
| `appointments.certificate_at`, `document_check_at` | Proposed final issue/endorsement and EU check dates; conflicts become explicit reason codes, never auto-booking. |
| `events.document_delivery_at`, `responsibility.*_role` | Proposed delivery date and anonymous carrying/delivery/receiving role categories; custody always unconfirmed. |
| `entry_time` / `entry_timezone`, `onward_entry_time` / `onward_entry_timezone`, `events.tapeworm_at` / `tapeworm_timezone` | Protected-zone dog treatment research only: offset-bearing ISO timestamp plus IANA zone; separate onward-zone arrival when needed. |

Timeline rows distinguish application, origin inspection/issue, identification,
vaccination/protocol, sample, entry-document issue/endorsement, entry and delivery.
Dependencies and available bounds are visible; missing dates stay null. Bounds are
civil-day research estimates, not office hours, holidays, appointment availability,
certificate authenticity, lab acceptance or transport suitability. No automatic
calendar/holiday scheduler is implemented. UTC hour checks reject missing offsets,
zone mismatches and nonexistent local times; explicit offsets distinguish DST folds.

US dog filters include the read ACF airport list, SEA cargo-only restriction,
LAX transfer caveat and receipt/facility airport/date matching. US cats do not receive
the dog form, antibody or ACF chain; state, USDA, carrier and arrival-health requirements
remain pending. EU AMS is a partial 2024 list reading; DE/FRA, FR/CDG and other points
remain unreviewed after the Commission index failed. Entry and onward overlays,
commercial inspection centres, facility opening hours and actual acceptance are separate.

See [Week 7 source readings and gaps](../research/week7/README.md),
[coverage inventory](../../data/coverage/cn-outbound.json) and
[design decision](../decisions/0007-cn-outbound-timeline.md).
Two actual qualified independent human reviews, current CN local/cargo procedures,
full EU annexes/lists, US state/APHIS and operational transport evidence are still
required before any claim of verified feasible travel. No reverse journey is inferred.
