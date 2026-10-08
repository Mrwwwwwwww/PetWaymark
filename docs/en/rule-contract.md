# Rule and source contract 0.1.0

Week 3 now implements the offline kernel and executes all nine boundary cases.
The Week 2 descriptions below remain historical; the fixture phase label is retained
for compatibility. See the [offline kernel guide](offline-engine.md).

[中文](../zh/rule-contract.md)

The four [JSON Schemas](../../packages/schema/) use Draft 2020-12: shared definitions,
rule, source catalog and synthetic boundary case. Their `https://petwaymark.org/schemas/`
IDs are logical identifiers, not a registered domain or hosted endpoint. Validation
resolves them from local files and never downloads schemas. Code and schemas use
Apache-2.0; original curated records use CC BY 4.0. Official texts are not relicensed.

## Rule records

`schema_version`, stable `id`, increasing `revision`, `record_class`, `authority`,
`scope`, `validity`, `requirement`, failure/missing policy, exceptions, evidence,
source IDs, review, supersession, bilingual message, pending checks and license are
required. Unknown properties and ambiguous expression shapes are rejected. Schema
versions describe format; rule revisions describe content. Changing a rule's meaning
requires a revision and regression case; replacing a different rule uses `supersedes`.

Classes remain separate: `law`, `official_guidance`, `carrier_policy`,
`project_interpretation`. A government explanatory page is guidance, even when it
links to legislation. Rules stack across departure, transit, first entry, destination,
state/member country and actual carrier. An empty subdivision list supplies no local
overlay. Rules are necessary constraints, never a complete permission package.

Scope specifies origin/destination, species, modes, movement category, accompaniment,
travel history and vaccination branch. Missing classification means confirmation,
not a wildcard. `any_non_eu` excludes EU origin; `any` deliberately leaves origin
unrestricted. `exclusions` records gaps that cannot be inferred away. Owner,
authorized person and unaccompanied are separate categories; authorization alone
does not establish a non-commercial movement classification.

Expressions are a deliberately small contract for Week 3: boolean `equals`, numeric
`at_most`, `calendar_age_at_least` (months or weeks), date `on_or_before`, and
`elapsed_at_least` (days). The implementation must handle missing dates before any
comparison. Natural months use calendar arithmetic, not 30-day multiplication.
Weeks are seven calendar days. Day windows require the applicable jurisdiction's
day-counting convention; local time and IANA zone support are a Week 3 design task.
No operator executes in this week's validator. `on_missing` is always
`needs_confirmation`; `on_fail` is `block` or `needs_confirmation`. Exception records
have their own ID, scope note and evidenced source; this version routes them to
confirmation rather than implementing automatic overrides.

`effective_from/to` are source-derived dates, not retrieval dates. `null` means not
recorded, including an unknown end date; it does not guarantee indefinite validity.
`applies_at` chooses entry or vaccination. `accessed_at` is source reading;
`last_verified_at`, reviewer records and `review_due_at` are human review. Date strings
are validated as real ISO calendar dates. Publication gates must also check freshness
and travel date; schema validation alone does not make a record usable.

`draft → verified → stale/disputed/retired`: verified requires known effective start,
two distinct human reviewer IDs, verification and a later review due date, evidence
and no pending checks. Automation cannot certify that a named reviewer actually
reviewed: maintainer review must establish that fact. AI must never populate human
signatures. Drafts do not claim a completed review. Historical verified records can
remain structurally valid after review expiry, but the engine must reject their use
as current verified constraints. Missing, disputed, stale and retired critical data
cannot support a definitive result.

## Sources and validation

[catalog.json](../../data/sources/catalog.json) is the Week 2 source registry; the
Week 1 index is preserved as a historical research queue. Stable source IDs resolve
to issuing authority, actual publisher, kind, canonical HTTPS URL, bilingual title,
language, reading date/method, status, license boundary and unresolved checks. A
government republication identifies both publisher and issuing authority. Evidence
stores the exact registry URL/date/language plus a heading/article locator and short
original summary or optional content hash. We do not store entire official pages.
Source reading is not project rule approval. Failed retrieval must stay unavailable;
never substitute a guessed quotation or access date.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python scripts/check_scaffold.py
.venv/bin/python scripts/validate_data.py
.venv/bin/python -m unittest discover -s tests -v
```

After dependency installation, all checks work offline, without model keys. CI runs
them on Python 3.11 and 3.13. `validate_data.py --root PATH` supports an isolated data
copy. It checks schemas, strict JSON, duplicate IDs/keys, reference resolution,
source/evidence agreement, authority, exception references and review/date invariants.
It does not verify legal truth, live links, real reviewer identity, carrier capacity
or route eligibility. Boundary fixtures have `phase=week3_engine_target`: their
input/expected assertions are schema checked now and must become executable tests
when Week 3 implements the engine. Passing them structurally is not passing engine
regression tests. New rules need positive, negative and missing-input engine cases
before publication.

See [planning extension decision](../decisions/0002-planning-extension-contract.md).
