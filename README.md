# PetWaymark · 宠途路标

[简体中文](README.zh-CN.md)

An open, bilingual planning project for dog and cat journeys that combine ground transport, rail and air travel across China, the United States and the European Union.

PetWaymark is a purely public-benefit open-source project whose primary purpose is to help pet owners. It is free and open, with no affiliation to any commercial brand. Any compliant service provider may connect on equal terms through open interfaces. The project does not operate transport or other commercial services, accept orders or favor any provider. Planned service connections link or redirect users to providers' own channels; compliance, privacy and animal welfare remain requirements.

**Week 5 local bilingual web and CN/US domestic research preview — CA/NY/TX inventory and three US small-city examples; zero verified feasible routes.** The planned scope is one privately owned dog or cat, with purpose, ownership changes, accompaniment and owner travel dates assessed separately. Service animals need a separate review path. Draft road/rail/air-ground paths are unranked and remain unsupported; actual slots, schedules and prices are unknown.

The planned outputs are route alternatives, document timelines, itemized costs, handover checklists and explanations linked to official evidence. Unknown rules must never become permission. Kernel result states are `eligible`, `conditional`, `ineligible` and `unsupported`; none confirms a booking or carrier acceptance.

## Start here

Reading needs no account or model key. Python 3.11+ checks the scaffold and rule contracts; install development dependencies once:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python scripts/check_scaffold.py
.venv/bin/python scripts/validate_data.py
.venv/bin/python -m packages.cli tests/fixtures/boundaries/boundary.unknown-carrier.json --assessment-at 2026-10-08
.venv/bin/python -m packages.cli tests/fixtures/domestic/owner.json --corridor dom.cn.east --assessment-at 2026-10-08 --format checklist --language en
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m apps.web.server --port 8766
```

Open `http://127.0.0.1:8766` for the anonymous local web form; Ctrl+C stops it.
No hosted static site is claimed. CA/TX sources are read pending independent review;
NY's current official page was unavailable. All twelve constraints remain drafts.

- [US candidates and local web](docs/en/us-web-preview.md) · [中文](docs/zh/us-web-preview.md)
- [Week 5 sources and gaps](docs/research/week5/README.md) · [Local web decision](docs/decisions/0005-local-bilingual-web.md)
- [Domestic preview and printable checklist](docs/en/domestic-preview.md) · [中文](docs/zh/domestic-preview.md)
- [Week 4 sources and gaps](docs/research/week4/README.md) · [Graph decision](docs/decisions/0004-domestic-preview.md)
- [Offline kernel and CLI](docs/en/offline-engine.md) · [中文](docs/zh/offline-engine.md)
- [Week 3 official-source reading](docs/research/week3/README.md) · [Date and trust decision](docs/decisions/0003-offline-evaluation.md)
- [Roadmap / 路线图](ROADMAP.md) · [Changes / 变更](CHANGELOG.md)
- [Rule and source contract](docs/en/rule-contract.md) · [中文](docs/zh/rule-contract.md)
- [Draft rule inventory](data/rules/README.md) · [Week 2 source reading](docs/research/week2/README.md)
- [Planning extensions](docs/decisions/0002-planning-extension-contract.md)
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
| `data/rules/{cn,us,eu,carriers}` | Versioned rule records; production publication requires human review |
| `data/{sources,airports,corridors,providers,coverage}` | Evidence references, transport facilities, routes, neutral directory and explicit gaps |
| `tests/{fixtures,regression}` | Synthetic boundary contracts and future engine regressions |
| `docs/{zh,en,decisions}`, `scripts`, `.github` | Documentation, decisions, validation and contribution templates |

China↔US, China↔EU and US↔EU remain six separate directions. Initial EU country research targets are Germany, France and the Netherlands. All candidates currently remain `unsupported`; airport codes in research do not prove that a route or animal transport product is available. No live prices, flight availability or pet-space inventory is connected.

## Licenses

Original code and documentation: [Apache-2.0](LICENSE). Original curated data under `data/`: [CC BY 4.0](LICENSE-DATA), with [scope details](data/README.md). Petra research snapshots retain their own CC BY 4.0 terms and attribution in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). Linked official texts, trademarks and third-party databases are not relicensed by this project.

No external repository, account, package or domain was created during Week 1.
