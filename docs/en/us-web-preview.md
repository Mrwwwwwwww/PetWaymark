# US research preview and bilingual local web

Python 3.11+, with the dependencies installed as in the [README](../../README.md):

```sh
python -m apps.web.server --port 8766
```

Open `http://127.0.0.1:8766`. Choose a direction, assessment/travel dates, dog/cat,
service-animal classification, purpose, ownership transfer and accompaniment.
Unknown values stay unknown. The form covers one animal; entering private
identifiers is unnecessary. Synthetic owner/unaccompanied links prefill clearly
fictional inputs. Set non-service-animal and no ownership transfer explicitly for
ordinary pet travel. Institution-led boarding is outside this preview.

Assess, change language without losing form values, export redacted JSON or print
the complete handover checklist. Results are unsupported research candidates, or
paths excluded within the graph/input, never confirmations or recommendations.
Exact windows and escort/custody/recipient/document roles remain pending.
The web and CLI use the same kernel; only translated labels/messages change.
No accounts, model keys, cloud services, tracking, cookies or paid runtime needed.
The server listens only on the user's computer; this is a local demo, not a hosted
static website. The [delivery decision](../decisions/0005-local-bilingual-web.md)
records that tradeoff. Ctrl+C stops it; `--port` selects an unused local port.

| Direction | Small-city / hub example | Evidence boundary |
|---|---|---|
| `dom.us.ca-ny` | Ventura → LAX → JFK → Kingston | NY official body unavailable; entry, actual flight and facilities pending |
| `dom.us.ny-tx` | Kingston → JFK → DFW → Denton | TX pet policy read; age, initial-dose, local and emergency conditions unreviewed |
| `dom.us.tx-ca` | Denton → DFW → LAX → Ventura | CA source read; NWS-origin overlays and full annex unreviewed |

Each also compares full-road candidates. Owner vehicles, passenger cabin/baggage
and separate unaccompanied animal carrier/cargo are distinct. Parcel delivery
cannot substitute for live-animal first/last legs. Airline names identify policy
scope only. Airport nodes are illustrative geography: they establish neither
operating flights nor facilities, species eligibility, slots or road connectivity.
Distance, duration and costs remain null. Other/transit states remain uncovered.

CLI examples (all inputs are synthetic):

```sh
python -m packages.cli tests/fixtures/us-domestic/owner.json --corridor dom.us.ca-ny --assessment-at 2026-10-08 --format checklist --language en
python -m packages.cli tests/fixtures/us-domestic/unaccompanied.json --corridor dom.us.ny-tx --assessment-at 2026-10-08
python -m packages.cli tests/fixtures/us-domestic/owner.json --corridor dom.us.tx-ca --assessment-at 2026-10-08
python -m unittest discover -s tests -v
```

[State inventory](../../data/coverage/us-state-overlays.json),
[US graph](../../data/corridors/us-preview.json),
[source reading and unavailable pages](../research/week5/README.md).
CA/TX are read pending independent review; NY is source unavailable. Two partial
constraints remain drafts, not full state/carrier packages. Certificate presence
alone never proves valid content/date. International CDC dog history is not used
for a US domestic journey. No human approval or feasible route is claimed.

The local API accepts the same anonymous URL-encoded form at `/assess`; `output=json`
returns the redacted assessment. There is no personal-profile upload or public API.
The UI uses native forms; JavaScript handles language preservation and printing.
HTTP integration tests cover bilingual status/reason equality across every current
direction, dog/cat/unknown and owner/unaccompanied/unknown combinations.
