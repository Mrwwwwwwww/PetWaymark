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
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--eu-preview', action='store_true', help='EU domestic/cross-member evidence preview, no transport routes')
    mode.add_argument('--corridor', choices=('dom.cn.east', 'dom.cn.south', 'dom.us.ca-ny', 'dom.us.ny-tx', 'dom.us.tx-ca'),
                        help='Week 4 domestic research graph preview')
    parser.add_argument('--format', choices=('json', 'checklist'), default='json')
    parser.add_argument('--language', choices=('zh-CN', 'en'), default='zh-CN')
    args = parser.parse_args()
    try:
        from scripts.validate_data import read_json
        payload = read_json(args.input)
        if not isinstance(payload, dict):
            raise ValueError('profile must be a JSON object')
        if args.eu_preview:
            from packages.engine.eu import assess, checklist, load_inventory
            result = assess(payload, assessment_at=args.assessment_at,
                            rules=load_repository(args.root), inventory=load_inventory(args.root))
            print(checklist(result, language=args.language) if args.format == 'checklist'
                  else json.dumps(result, ensure_ascii=False, indent=2), end='\n' if args.format == 'json' else '')
            return 0
        if args.corridor:
            from packages.engine.routes import load_graph, preview, checklist
            region = 'US' if args.corridor.startswith('dom.us.') else 'CN'
            graph = load_graph(args.root, region=region)
            overlays = read_json(args.root / 'data/coverage/us-state-overlays.json') if region == 'US' else None
            result = preview(payload, graph, corridor_id=args.corridor,
                             assessment_at=args.assessment_at, rules=load_repository(args.root), overlays=overlays)
            print(checklist(result, graph, language=args.language) if args.format == 'checklist'
                  else json.dumps(result, ensure_ascii=False, indent=2), end='\n' if args.format == 'json' else '')
            return 0
        if args.format != 'json':
            raise ValueError('checklist requires --corridor')
        rules = load_repository(args.root)
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
