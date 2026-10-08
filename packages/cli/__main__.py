"""Offline PetWaymark assessment; no model key or network required."""
import argparse
import json
from pathlib import Path
import sys

from packages.engine import evaluate
from packages.engine.io import ROOT, boundary_profile, load_repository


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path, help='nested profile JSON or synthetic boundary fixture')
    parser.add_argument('--assessment-at', required=True, help='explicit YYYY-MM-DD assessment date')
    parser.add_argument('--root', type=Path, default=ROOT, help='validated data repository')
    args = parser.parse_args()
    try:
        from scripts.validate_data import read_json
        rules = load_repository(args.root)
        payload = read_json(args.input)
        if not isinstance(payload, dict):
            raise ValueError('profile must be a JSON object')
        if payload.get('synthetic') is True and 'input' in payload:
            ids = payload['rule_ids']
            known = {r['id'] for r in rules}
            if not set(ids) <= known:
                raise ValueError('unresolved fixture rule IDs')
            rules = [r for r in rules if r['id'] in ids]
            profile = boundary_profile(payload['input'])
        else:
            profile = payload
        if any(not isinstance(profile.get(k, {}), dict) for k in ('pet', 'journey', 'documents', 'events')):
            raise ValueError('profile groups must be objects')
        result = evaluate(profile, rules, assessment_at=args.assessment_at)
    except (ValueError, OSError, KeyError) as exc:
        print(f'FAIL: {exc}', file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
