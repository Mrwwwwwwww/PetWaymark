# PetWaymark · 宠途路标

[简体中文](README.zh-CN.md)

An open, bilingual planning project for dog and cat journeys that combine ground transport, rail and air travel across China, the United States and the European Union.

PetWaymark is a purely public-benefit open-source project whose primary purpose is to help pet owners. It is free and open, with no affiliation to any commercial brand. Any compliant service provider may connect on equal terms through open interfaces. The project does not operate transport or other commercial services, accept orders or favor any provider. Planned service connections link or redirect users to providers' own channels; compliance, privacy and animal welfare remain requirements.

**Week 1 scaffold — no working planner or verified travel routes yet.** The planned scope is one privately owned dog or cat, with purpose, ownership changes, accompaniment and owner travel dates assessed separately. Service animals need a separate review path.

The planned outputs are route alternatives, document timelines, itemized costs, handover checklists and explanations linked to official evidence. Unknown rules must never become permission. Intended result states are `eligible`, `conditional`, `ineligible` and `unsupported`; none confirms a booking or carrier acceptance.

## Start here

No installation, API key or account is needed to read this scaffold. There is no build or application command in Week 1. From this directory, run the document/data scaffold check with Python 3:

```sh
python3 scripts/check_scaffold.py
```

- [Candidate corridors and coverage boundaries](docs/zh/corridors.md)
- [Coverage inventory](data/coverage/week1-candidates.json)
- [Petra reuse decision and field mapping](docs/decisions/0001-petra-reuse.md)
- [Name and domain checks](docs/zh/name-check.md)
- Interview preparation: [English](docs/en/interviews.md) · [中文](docs/zh/interviews.md)
- [Evidence and research snapshots](docs/research/week1/README.md)
- [Contributing](CONTRIBUTING.md), [governance](GOVERNANCE.md), [conduct](CODE_OF_CONDUCT.md), [security](SECURITY.md)

## Layout

| Directory | Intended purpose |
|---|---|
| `apps/web` | Bilingual demo and printable plans |
| `packages/schema`, `packages/engine`, `packages/cli`, `packages/mcp` | Versioned data contracts, deterministic evaluation, local tooling, later read-only integrations |
| `data/rules/{cn,us,eu,carriers}` | Reviewed rule records; currently empty |
| `data/{sources,airports,corridors,providers,coverage}` | Evidence references, transport facilities, routes, neutral directory and explicit gaps |
| `tests/{fixtures,regression}` | Future synthetic or consented anonymized cases |
| `docs/{zh,en,decisions}`, `scripts`, `.github` | Documentation, decisions, validation and contribution templates |

China↔US, China↔EU and US↔EU remain six separate directions. Initial EU country research targets are Germany, France and the Netherlands. All candidates currently remain `unsupported`; airport codes in research do not prove that a route or animal transport product is available. No live prices, flight availability or pet-space inventory is connected.

## Licenses

Original code and documentation: [Apache-2.0](LICENSE). Original curated data under `data/`: [CC BY 4.0](LICENSE-DATA), with [scope details](data/README.md). Petra research snapshots retain their own CC BY 4.0 terms and attribution in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). Linked official texts, trademarks and third-party databases are not relicensed by this project.

No external repository, account, package or domain was created during Week 1.
