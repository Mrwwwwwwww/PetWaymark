# Third-party notices / 第三方归属

## Petra open rules

- Creator and copyright: **Petra (petraverify.id)**.
- Source: https://github.com/stefanfeissli/petra-open-rules
- Public export commit: `eb6496d32e2951c984644a743dfb6d080fd998ce`.
- Dataset version: `d7b4411b411758c43b97496e4cbc7d3c3b003483` (a distinct upstream identifier).
- License: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); [original scope and disclaimer](docs/research/week1/petra/LICENSE).
- Files: `docs/research/week1/petra/` contains unmodified README, LICENSE, CONTRIBUTING, index and two corridor JSON snapshots. The hashes and pinned URLs are in [the manifest](docs/research/week1/petra-manifest.json).
- Changes: snapshots unchanged; inventory is a reduced field extraction; our comparison and mapping add analysis. No executable rules were imported. The extracted inventory retains CC BY 4.0 for Petra-derived content.
- Petra's license excludes linked primary-source texts, quoted third-party material and marks. Preserve those exclusions. Petra review dates are historical records, not assurances of current rules. No Petra endorsement is claimed.

`docs/research/week1/petra/**` and Petra-derived portions of `petra-manifest.json` are exceptions to the default Apache documentation license.

## Other evidence

IANA bootstrap data in `docs/research/week1/iana-rdap-bootstrap.json` is a research snapshot from https://data.iana.org/rdap/dns.json; its source terms remain applicable. It is excluded from PetWaymark's license grants. Registry responses and official-page metadata are evidence, not project-licensed copies of the underlying registry databases or official texts. No registrant personal information is retained.

The Apache and Creative Commons license texts are included as license instruments, not relicensed project content. No OSM, OurAirports, commercial customer records or provider database has been imported. If introduced later, record their specific license and provenance before distribution.

## GeoNames place slice (2026-10-10)

GeoNames, https://www.geonames.org/ ; downloads: https://download.geonames.org/export/dump/ . Licensed CC BY 4.0, https://creativecommons.org/licenses/by/4.0/ . Readme retained in `licenses/GEONAMES-README.txt`. The small country/city/area slice is in `apps/pages/locations.json`, with original source rows and archive checksums. PetWaymark contributors added Chinese display names, selected records and mapped source administrative codes into the picker. This is not a government-verified or complete administrative database. Source data is supplied without warranty of accuracy, timeliness or completeness. See `apps/pages/LOCATIONS.md` for scope and gaps.

## China province/prefecture names (2023 snapshot)

Source: modood/Administrative-divisions-of-China, commit `c49d495b40ac73eb1a66f6eeae5f8fd10696f035`, https://github.com/modood/Administrative-divisions-of-China/tree/c49d495b40ac73eb1a66f6eeae5f8fd10696f035 . License declared by upstream: WTFPL 2.0, retained in `licenses/CHINA-ADMIN-WTFPL.txt`. Only `dist/provinces.json` and `dist/cities.json` are retained under `apps/pages/china-*.json`. Names/codes are factual extracts used to cross-check GeoNames display labels; source scope is 2023-06-30 and upstream has stopped updating. This is not a grant to reproduce underlying government website text or an assurance of current boundaries. Source URLs and hashes are in locations.json supplementaryInputs. Those snapshots retain their upstream license instead of the project's Apache or CC defaults.

The v2 GeoNames slice expands to countryInfo, admin1CodesASCII, cities15000 and CN dumps. Source rows, source codes, attribution and original names are retained. Consult `apps/pages/LOCATIONS.md` for the exact selection and coverage limits.
