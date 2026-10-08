# Petra open rules

This repository is the public, versioned export of Petra's corridor pet-travel
rule data: requirements, applicability, timing windows, exemptions, review
dates, and primary-source provenance for each origin→destination corridor
Petra publishes. It is populated automatically from the same generator that
renders [petraverify.id/corridors](https://petraverify.id/corridors) and the
site's `/corridors/*/index.json` dataset endpoints — never hand-edited here.

This document states Petra's own published positions on what this dataset is,
what stays out of it, how records are classified, and its freshness
disclaimer, quoted from `strategy/open-rules.md` — the governing ruling in the
Petra monorepo — because a downstream recipient of this repository may never
see that document or petraverify.id at all.

## 1. Open data, not open source

This is open data, not open source:

> This is open *data*, not open source. The distinction is load-bearing: the
> dataset contains **sourced rule assertions and clearly labeled Petra
> interpretations**; no evaluator code or internal rule implementation is
> included.

Petra publishes the *facts* — what a corridor's rules require, and where they
come from — not the software that decides whether a specific animal, on a
specific date, is ready to travel. That software, and everything it takes to
build it, is proprietary and stays that way.

## 2. What stays closed

Three things are never in this repository, regardless of how the dataset
schema evolves:

- **The evaluator** — what counts as complete, correctly sequenced, and ready
  for a given animal on a given date; the qualification/caveat model;
  readiness projection. This is the product.
- **The outcome corpus** — which packets cleared, at which desk, on which day,
  rejected for what. Not issuer-attested, held by no one else, the thing that
  compounds. Observed desk outcomes remain outside this dataset.
- **The issuance rails** — keys, signing, anchoring, the verifier.

## 3. Record classes

Every requirement and manual-checklist item in this dataset carries a `class`
field. Petra's own recorded principle for what that field means:

> Published records must distinguish authoritative requirements (enacted law,
> regulation), official procedural guidance (agency-published process), and
> Petra-authored interpretation of ambiguous material. Carrier requirements
> and port- or desk-level practice are either labeled as such or excluded.
> Observed outcomes are excluded. ... Where a record's class cannot yet be
> derived from the ruleset, it is labeled *interpretation* — never silently promoted to *authoritative*.

As of the current generator, every requirement and manual-checklist record
this dataset publishes resolves to `interpretation`: the underlying ruleset
schema does not yet carry a field that distinguishes enacted law from agency
guidance from Petra's own reading of ambiguous material. That is a property
of the source data today, not a downgrade applied here — see `class` in
every record.

## 4. Disclaimer

Every record and the dataset index carry this disclaimer verbatim, in the
`disclaimer` field:

> Review dates describe Petra's review history; they are not a promise that no authority has changed its requirements since that review.

This dataset is provided "as is", without warranty of any kind — see the
`no_warranty` field on every record, and `LICENSE` for the licence and its
scope. Nothing here is legal advice, and nothing here substitutes for
confirming current requirements directly with the destination authority
before travel.

## What's in this repository

- `index.json` — the dataset index: one summary entry per corridor.
- `corridors/<slug>.json` — one full record per corridor (requirements,
  caveats, manual checklist, sources, tier, disclaimer, licence).
- `CHANGELOG.md` — a generated, per-corridor, field-level changelog. No
  hand-written entries; see that file's own header.
- `LICENSE` — CC BY 4.0, with the scope exclusions Petra's licence actually
  carries (linked primary sources and third-party material are not Petra's
  to license).

## Corrections and contributions

See `CONTRIBUTING.md`. This repository accepts issues and pull requests,
gated by an automated provenance check and human review; Discussions are
off.

## Provenance

Published by [stefanfeissli/petra](https://github.com/stefanfeissli/petra)
(private) — the evaluator, ruleset engine, and everything else that produces
a readiness verdict live there and are not published. This repository is one
direction only: a sanitized export, never written back to.

---

*Sourced from `strategy/open-rules.md` §1, §4, §5, §6 in the Petra monorepo
(owner ruling, 2026-09-03, execution gated per that document's §7/§8).*
