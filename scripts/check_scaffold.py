#!/usr/bin/env python3
"""Offline Week 1 integrity checks; not a legal review or production rule schema."""

import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
ERRORS = []


def check(condition, message):
    if not condition:
        ERRORS.append(message)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def main():
    required_dirs = [
        "apps/web", "packages/schema", "packages/engine", "packages/cli",
        "packages/mcp", "data/rules/cn", "data/rules/us", "data/rules/eu",
        "data/rules/carriers", "data/sources", "data/airports", "data/corridors",
        "data/providers", "data/coverage", "tests/fixtures", "tests/regression",
        "docs/zh", "docs/en", "docs/decisions", "scripts",
        ".github/ISSUE_TEMPLATE", ".github/workflows",
    ]
    required_files = [
        "README.md", "README.zh-CN.md", "LICENSE", "LICENSE-DATA", "NOTICE",
        "THIRD_PARTY_NOTICES.md", "CONTRIBUTING.md", "GOVERNANCE.md",
        "CODE_OF_CONDUCT.md", "SECURITY.md", "licenses/CC-BY-4.0.txt",
        "docs/zh/corridors.md", "docs/zh/name-check.md",
        "docs/zh/interviews.md", "docs/en/interviews.md",
        "docs/decisions/0001-petra-reuse.md", "docs/research/week1/README.md",
        ".github/PULL_REQUEST_TEMPLATE.md",
    ] + [f".github/ISSUE_TEMPLATE/{name}.md" for name in (
        "rule_error", "route_problem", "provider_correction", "feature_request", "translation"
    )]
    for name in required_dirs:
        check((ROOT / name).is_dir(), f"missing directory: {name}")
        check(any((ROOT / name).rglob('*')), f"directory has no tracked placeholder/content: {name}")
    for name in required_files:
        check((ROOT / name).is_file(), f"missing file: {name}")

    parsed = {}
    for path in ROOT.rglob("*.json"):
        if '.git' in path.parts:
            continue
        try:
            parsed[path.relative_to(ROOT).as_posix()] = json.loads(
                path.read_text(encoding='utf-8'), object_pairs_hook=unique_object)
        except (ValueError, OSError) as exc:
            ERRORS.append(f"{path.relative_to(ROOT)}: {exc}")

    research = 'docs/research/week1/'
    manifest = parsed.get(research + 'petra-manifest.json', {})
    files = manifest.get('files', [])
    check(len(files) == 6, 'expected six pinned Petra files')
    for item in files:
        path = ROOT / research / 'petra' / item['path']
        check(path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() == item['sha256'],
              f"Petra snapshot hash mismatch: {item['path']}")
        check('/' + manifest['commit'] + '/' in item['url'], 'Petra URL is not commit-pinned')
    index = parsed.get(research + 'petra/index.json', {})
    check(index.get('version') == manifest.get('dataset_version'), 'Petra version mismatch')
    check(len(index.get('corridors', [])) == manifest.get('corridor_count'), 'Petra count mismatch')
    check(len(manifest.get('inventory', [])) == manifest.get('corridor_count'), 'inventory count mismatch')
    fetches = parsed.get(research + 'official-fetches.json', [])
    for source_id, local_path in [('apache-license', 'LICENSE'), ('cc-license', 'licenses/CC-BY-4.0.txt')]:
        evidence = next((f for f in fetches if f['id'] == source_id), {})
        path = ROOT / local_path
        check(path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() == evidence.get('content_sha256'),
              f'license hash mismatch: {local_path}')

    sources = parsed.get('data/sources/week1-research-index.json', {}).get('sources', [])
    source_ids = {s['id'] for s in sources}
    check(len(sources) == len(source_ids) and bool(sources), 'source IDs absent/duplicated')
    for source in sources:
        check(urlsplit(source['url']).scheme == 'https', f"invalid source URL: {source['id']}")
        check(source.get('human_reviewed_at') is None and source.get('status') == 'pending_rule_review',
              f"Week 1 source cannot imply human approval: {source['id']}")
    coverage = parsed.get('data/coverage/week1-candidates.json', {})
    candidates = coverage.get('candidates', [])
    check(len(candidates) == 15, 'expected 15 research candidates')
    check(len({r['id'] for r in candidates}) == len(candidates), 'duplicate corridor IDs')
    directions = {(r['origin_region'], r['destination_region']) for r in candidates if r['kind'] == 'international'}
    check(directions == {('CN', 'US'), ('US', 'CN'), ('CN', 'EU'), ('EU', 'CN'), ('US', 'EU'), ('EU', 'US')},
          'six independent international directions required')
    check(sum(r['kind'] == 'international' for r in candidates) == 6, 'expected six international candidates')
    check(sum(r['kind'] == 'domestic' for r in candidates) == 8, 'expected eight domestic candidates')
    check(sum(r['kind'] == 'intra_eu' for r in candidates) == 1, 'expected one intra-EU candidate')
    check(coverage.get('verified_production_rules') == 0, 'Week 1 has no verified rules')
    for row in candidates:
        ident = row['id']
        check(row.get('coverage_status') == 'unsupported', f'{ident}: unsupported required')
        check(row.get('carrier_acceptance') == 'unknown', f'{ident}: carrier is unconfirmed')
        check(row.get('human_reviewed_at') is None and row.get('verified_rule_ids') == [],
              f'{ident}: fabricated review/verified rule')
        check(set(row.get('species', [])) == {'dog', 'cat'}, f'{ident}: species missing')
        check(set(row.get('accompaniment_cases', [])) == {'owner_accompanied', 'pet_separate_from_owner'},
              f'{ident}: accompaniment cases missing')
        check(bool(row.get('missing')) and bool(row.get('source_ids')), f'{ident}: missing research gaps or sources')
        check(set(row.get('source_ids', [])) <= source_ids, f'{ident}: unresolved source reference')
    # Week 1 coverage is preserved as a research snapshot. Week 2 rule records
    # are validated separately by validate_data.py, not by this integrity check.

    # Check inline Markdown file targets; skip original third-party snapshots.
    link_count = 0
    for path in ROOT.rglob('*.md'):
        if '.git' in path.parts or (ROOT / research / 'petra') in path.parents:
            continue
        for target in re.findall(r'\]\(([^\s)]+)(?:\s+"[^"\n]*")?\)', path.read_text(encoding='utf-8')):
            url = urlsplit(target.strip('<>'))
            if url.scheme or target.startswith(('#', '//')) or not url.path:
                continue
            link_count += 1
            check((path.parent / unquote(url.path)).exists(),
                  f'{path.relative_to(ROOT)}: broken local link {target}')
    if ERRORS:
        print('\n'.join('FAIL: ' + error for error in ERRORS), file=sys.stderr)
        return 1
    print(f'PASS: {len(parsed)} JSON files; {len(files)} Petra hashes; 2 license hashes; '
          f'{len(candidates)} unsupported candidates; {link_count} local links.')
    print('Scope: scaffold integrity only; no legal, live-link, booking or application validation.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
