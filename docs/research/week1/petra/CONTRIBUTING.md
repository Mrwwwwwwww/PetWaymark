# Contributing

This is Phase B2 of Petra's open-rules plan (`strategy/open-rules.md`
§8): an automated-provenance-plus-human-review contribution gate. This
file is the whole contribution path — read it before opening a pull
request.

## What you can change

A pull request edits **exactly one** corridor file under `corridors/` (or
proposes a new one) — never more than one file, and never anything else in
this repository. The automated checks below reject anything wider.

Every pull request description must use the pull request template and
state:

- the **primary source URL** for the change;
- the **date you checked it** (`retrieved_at`);
- the **record or field** you are changing (the corridor's
  `requirements[]` key, `manual_checklist[]` title, or another named
  field);
- the class you claim for the change, per `strategy/open-rules.md` §5:
  **authoritative**, **guidance**, or **interpretation**.

A pull request that doesn't fill in the template is closed by the bot with
a comment pointing back here — no human review time is spent on it.

## Automated checks

Every pull request runs the same gate this repository's own CI runs
(`.github/gate/`, `.github/workflows/contribution-gate.yml`) before any
human looks at it:

- **Schema** — the file matches this dataset's schema.
- **Source freshness** — every requirement or checklist item you changed
  carries a `sources[]` entry with a `retrieved_at` date within 90 days.
- **Source domain** — every source you cite resolves to a domain on this
  repository's government/agency allowlist
  (`.github/source-domains.json`). A domain not on the list is not a
  "this domain is wrong" verdict — it means a human has to add it first
  (see "New sources" below).
- **Protected fields** — you may not set `version`, `history_url`,
  `license`, `license_scope`, `no_warranty`, or `last_reviewed`. Those
  are set by Petra's own publish process.
- **Disclaimer and licence text** — you may not change the
  `disclaimer`, `license`, `license_scope`, or `no_warranty` fields'
  text.
- **Single-corridor scope** — the diff touches exactly one corridor file.
- **Canonical formatting** — the file is 2-space-indented JSON with a
  single trailing newline.

Failing any check turns the pull request red, with a named reason, before
any human spends time on it.

## Human review

A green PR is reviewed by the owner (or a named reviewer) against the cited source under the Rule 8 standard — the reviewer opens the source and confirms the claim before merging. Merging is a human act; no auto-merge. A reviewer who cannot confirm the source declines with reason.

Two outcomes only: merged or closed-with-reason; nothing sits open past 14 days without a comment.

## New sources

If your source's domain isn't on the allowlist yet, say so in the pull
request — adding a domain to `.github/source-domains.json`'s
`owner_additions` is a human decision, not something the automated checks
can do for you.

## Attribution and licensing

Your git commit identity, as you submit it, is your attribution — there is
no separate contributor list.

By submitting a pull request, you license your submission to Petra under CC BY 4.0 for republication. Participation in this repository is never treated as marketing consent (`strategy/open-rules.md` §2 boundary).

## If you can't open a pull request

A typo report, a general question, or a correction you can't shape into
the one-corridor-one-source form above still goes to:

    stefan@petraverify.id

Subject: `Correction: <corridor or record>`. Reports without a primary
source and a date cannot be verified and will not be actioned as
corrections (`RULES.md` Rule 8).
