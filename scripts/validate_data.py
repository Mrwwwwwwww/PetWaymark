#!/usr/bin/env python3
"""Offline schema and reference integrity checks; no eligibility/legal evaluation."""

import argparse
from datetime import date
import json
from pathlib import Path
import sys

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[1]


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object)


def validators(root):
    schemas = [read_json(p) for p in sorted((root / "packages/schema").glob("*.schema.json"))]
    for schema in schemas:
        Draft202012Validator.check_schema(schema)
    registry = Registry().with_resources((s["$id"], Resource.from_contents(s)) for s in schemas)
    return {s["$id"].rsplit("/", 1)[-1]: Draft202012Validator(
        s, registry=registry, format_checker=FormatChecker()) for s in schemas}


def validate_repository(root=ROOT):
    errors = []
    counts = {"rules": 0, "sources": 0, "cases": 0}
    vs = validators(root)

    def load(path, schema):
        try:
            data = read_json(path)
        except (ValueError, OSError) as exc:
            errors.append(f"{path.relative_to(root)}: {exc}")
            return None
        problems = sorted(vs[schema].iter_errors(data), key=lambda e: str(e.json_path))
        for problem in problems:
            errors.append(f"{path.relative_to(root)} {problem.json_path}: {problem.message}")
        return None if problems else data

    def collect(paths, schema, key):
        records = {}
        for path in sorted(paths):
            record = load(path, schema)
            if record is None:
                continue
            counts[key] += 1
            if record["id"] in records:
                errors.append(f"duplicate {key} ID: {record['id']}")
            records[record["id"]] = record
        return records

    catalog = load(root / "data/sources/catalog.json", "source-catalog.schema.json")
    sources = {}
    for source in (catalog or {}).get("sources", []):
        counts["sources"] += 1
        if source["id"] in sources:
            errors.append(f"duplicate source ID: {source['id']}")
        sources[source["id"]] = source
    rules = collect((root / "data/rules").rglob("*.json"), "rule.schema.json", "rules")
    cases = collect((root / "tests/fixtures/boundaries").glob("*.json"),
                    "boundary-case.schema.json", "cases")

    for ident, rule in rules.items():
        def fail(message):
            errors.append(f"{ident}: {message}")

        ids = set(rule["source_ids"])
        if not ids <= sources.keys():
            fail("unresolved source reference")
        evidence_ids = {e["source_id"] for e in rule["evidence"]}
        if ids != evidence_ids:
            fail("each source must have evidence and each evidence must be declared")
        for evidence in rule["evidence"]:
            source = sources.get(evidence["source_id"])
            if source and (evidence["url"] != source["url"] or
                           evidence["accessed_at"] != source["accessed_at"] or
                           evidence["language"] != source["language"]):
                fail("evidence URL/date/language differs from source catalog")
        if rule["record_class"] in {"law", "official_guidance"}:
            if any(sources[s]["kind"] != "government" or sources[s]["authority"] != rule["authority"]
                   for s in ids if s in sources):
                fail("official rule requires matching government authority")
        if rule["record_class"] == "carrier_policy":
            if any(sources[s]["kind"] != "carrier" or sources[s]["authority"] != rule["authority"]
                   for s in ids if s in sources):
                fail("carrier policy requires matching carrier authority")
        if len({e["id"] for e in rule["exceptions"]}) != len(rule["exceptions"]):
            fail("duplicate exception ID")
        for exception in rule["exceptions"]:
            if not set(exception["source_ids"]) <= ids:
                fail("exception source must be declared with evidence")
        if ident in rule["supersedes"] or not set(rule["supersedes"]) <= rules.keys():
            fail("invalid supersedes reference")
        validity = rule["validity"]
        if (validity["effective_from"] and validity["effective_to"] and
                validity["effective_from"] > validity["effective_to"]):
            fail("reversed validity dates")
        review = rule["review"]
        if review["status"] == "draft" and (review["last_verified_at"] is not None or review["reviewed_by"]):
            fail("draft must not claim completed human review")
        if review["status"] == "verified":
            reviewers = review["reviewed_by"]
            if len({r["id"] for r in reviewers}) < 2:
                fail("verified requires two distinct human reviewers")
            if review["review_due_at"] <= review["last_verified_at"]:
                fail("review due date must follow verification")
            if review["last_verified_at"] > date.today().isoformat():
                fail("verification date is in the future")
            if any(r["reviewed_at"] > review["last_verified_at"] for r in reviewers):
                fail("reviewer date exceeds completed verification date")
            if any(e["accessed_at"] > review["last_verified_at"] for e in rule["evidence"]):
                fail("evidence access follows verification")
            if any(sources[s]["status"] != "read_pending_review" for s in ids if s in sources):
                fail("verified rule has unavailable/disputed source")
            # Stale historical versions remain valid records. Week 3 must gate by evaluation date.

    for ident, case in cases.items():
        refs = set(case["rule_ids"])
        excluded = set(case["expected"]["not_applicable_rule_ids"])
        if not refs <= rules.keys() or not excluded <= refs:
            errors.append(f"{ident}: unresolved case rule reference")
        for rid in excluded & rules.keys():
            rule = rules[rid]
            inp = case["input"]
            scope = rule["scope"]
            # The fixture must exhibit an actual scope mismatch, not just assert one.
            mismatch = (inp["species"] not in scope["species"] or
                        inp["destination"] != scope["destination"] or
                        scope["origin"] not in {"any", "any_non_eu", inp["origin"]} or
                        (scope["origin"] == "any_non_eu" and inp["origin"] == "EU") or
                        (scope["travel_history_branch"] == "only_low_risk_6_months" and
                         inp.get("travel_history_branch") == "high_risk_in_6_months"))
            if not mismatch:
                errors.append(f"{ident}: no scope mismatch for excluded rule {rid}")
    for graph_path in sorted((root / "data/corridors").glob("*-preview.json")):
        graph = load(graph_path, "corridor-graph.schema.json")
        if graph:
            errors.extend(validate_graph(graph, sources))
    overlay_path = root / "data/coverage/us-state-overlays.json"
    if overlay_path.exists():
        overlay = load(overlay_path, "state-overlays.schema.json")
        if overlay:
            errors.extend(validate_overlays(overlay, sources, rules))
    return errors, counts


def validate_graph(graph, sources):
    """Preview topology/evidence integrity; never establishes transport permission."""
    errors = []
    for key, ident in (("nodes", "id"), ("segments", "segment_id"), ("corridors", "id")):
        ids = [r[ident] for r in graph[key]]
        if len(ids) != len(set(ids)):
            errors.append(f"graph: duplicate {key} ID")
    nodes = {n["id"] for n in graph["nodes"]}
    segments = {s["segment_id"] for s in graph["segments"]}
    for leg in graph["segments"]:
        name = leg["segment_id"]
        if not {leg["from_node"], leg["to_node"], leg["handover"]["location_node"]} <= nodes:
            errors.append(f"{name}: unresolved graph node")
        if leg["handover"]["location_node"] != leg["to_node"]:
            errors.append(f"{name}: handover must use arrival node")
        if leg["from_node"] == leg["to_node"]:
            errors.append(f"{name}: self-loop is not a transport leg")
        if not set(leg["supersedes_segment_ids"]) <= segments or name in leg["supersedes_segment_ids"]:
            errors.append(f"{name}: unresolved or self supersession")
        ids = set(leg["source_ids"])
        if ids != {e["source_id"] for e in leg["evidence"]}:
            errors.append(f"{name}: graph evidence must match source IDs")
        if len(leg["evidence"]) != len(ids):
            errors.append(f"{name}: duplicate graph evidence")
        if not ids <= sources.keys():
            errors.append(f"{name}: unresolved graph source")
        for evidence in leg["evidence"]:
            source = sources.get(evidence["source_id"])
            if source and any(evidence[k] != source[k] for k in ("url", "accessed_at", "language")):
                errors.append(f"{name}: graph evidence differs from source catalog")
        if any(l["source_id"] not in ids for l in leg["limits"]):
            errors.append(f"{name}: limit source must be declared")
        product = leg["product"]
        expected = ("rail" if product.startswith("rail_") else "checked_baggage" if "baggage" in product
                    else "cabin" if product.endswith("_cabin") else "manifest_cargo" if product.endswith("_cargo") else "road")
        if leg["mode"] != expected:
            errors.append(f"{name}: product/mode mismatch")
    for corridor in graph["corridors"]:
        if not set(corridor.get('segment_ids', [])) <= segments:
            errors.append(f"{corridor['id']}: unresolved corridor segment")
        if not {corridor["origin_node"], corridor["destination_node"]} <= nodes:
            errors.append(f"{corridor['id']}: unresolved corridor node")
        if corridor["origin_node"] == corridor["destination_node"]:
            errors.append(f"{corridor['id']}: corridor endpoints must differ")
    return errors


def validate_overlays(overlay, sources, rules):
    errors = []
    if {s['subdivision'] for s in overlay['states']} != {'US-CA', 'US-NY', 'US-TX'}:
        errors.append('overlays: missing or duplicate target state')
    for state in overlay['states']:
        ids = set(state['source_ids'])
        if not ids <= sources.keys() or not set(state['rule_ids']) <= rules.keys():
            errors.append('overlays: unresolved source or rule')
        if state['status'] == 'source_unavailable':
            if state['evidence'] or state['rule_ids'] or any(sources.get(i, {}).get('status') != 'unavailable' for i in ids):
                errors.append('overlays: unavailable source cannot claim reading or rules')
        elif ids != {e['source_id'] for e in state['evidence']}:
            errors.append('overlays: missing reading evidence')
        for e in state['evidence']:
            source = sources.get(e['source_id'], {})
            if any(e[k] != source.get(k) for k in ('url', 'accessed_at', 'language')):
                errors.append('overlays: evidence differs from catalog')
        for rid in state['rule_ids']:
            rule = rules.get(rid)
            if rule and (rule['review']['status'] != 'draft' or rule['scope']['subdivisions'] != [state['subdivision']]):
                errors.append('overlays: rule scope/review mismatch')
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    try:
        errors, counts = validate_repository(args.root)
    except (ValueError, OSError, KeyError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    if errors:
        print("\n".join("FAIL: " + e for e in errors), file=sys.stderr)
        return 1
    print(f"PASS: {counts['rules']} rules; {counts['sources']} sources; {counts['cases']} boundary cases.")
    print("Structure/references only; engine assertions and human legal review are not executed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
