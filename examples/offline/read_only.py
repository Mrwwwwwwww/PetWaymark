"""Pinned read-only integration example; synthetic input only, no network or writes.

Run from the checkout root: python -m examples.offline.read_only
"""
import hashlib
import json
from pathlib import Path

from packages.engine import compare, evaluate
from packages.engine.io import ROOT, boundary_profile, load_repository

EXAMPLE = Path(__file__).parent


def verify_pin(root=ROOT, lock=None):
    lock = lock or json.loads((EXAMPLE / 'lock.json').read_text())
    for name, expected in lock['sha256'].items():
        if hashlib.sha256((root / name).read_bytes()).hexdigest() != expected:
            raise ValueError('Pinned file drift: ' + name)
    return lock


def read_only(root=ROOT):
    lock = verify_pin(root)
    rules = load_repository(root)
    manifest = json.loads((root / 'data/VERSION.json').read_text())
    # Check every packaged data byte, not just the inventory itself.
    for name, expected in manifest['files'].items():
        if hashlib.sha256((root / name).read_bytes()).hexdigest() != expected:
            raise ValueError('Dataset file drift: ' + name)
    case = json.loads((root / 'tests/fixtures/boundaries/boundary.unknown-carrier.json').read_text())
    profile = boundary_profile(case['input'])
    selected = [r for r in rules if r['id'] in case['rule_ids']]
    result = evaluate(profile, selected, assessment_at=lock['assessment_at'])
    source_ids = {sid for rule in selected for sid in rule['source_ids']}
    catalog = json.loads((root / 'data/sources/catalog.json').read_text())
    # Public constraint/evidence projection. Never include the original profile.
    return {
        'synthetic': True, 'interface_version': 'offline-example.1',
        'engine_version': result['engine_version'], 'dataset_version': manifest['dataset_version'],
        'assessment_at': result['assessment_at'], 'status': result['status'],
        'reason_codes': result['reason_codes'], 'coverage_gaps': result['coverage_gaps'],
        'booking_confirmed': result['booking_confirmed'], 'external_progress': result['external_progress'],
        'rules': [{'id': r['id'], 'review': r['review'], 'evidence': r['evidence'],
                   'source_ids': r['source_ids'], 'requirement': r['requirement'],
                   'synthetic_expression_diagnostic': compare(r['requirement'], profile)} for r in selected],
        'sources': [s for s in catalog['sources'] if s['id'] in source_ids],
        'limitations': ['drafts_not_permission', 'single_constraint_not_complete_journey',
                        'no_independent_adoption', 'no_orders_or_rule_writes'],
    }


if __name__ == '__main__':
    print(json.dumps(read_only(), ensure_ascii=False, indent=2))
