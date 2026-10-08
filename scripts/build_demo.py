#!/usr/bin/env python3
"""Build static, synthetic-only examples with the production CLI; no live assessment."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
DATA_VERSION = '2026.10.08-draft.2'

def build(output):
    output.mkdir(parents=True, exist_ok=True)
    examples = []
    specs = []
    for group, mode in [('outbound', '--outbound-preview'), ('inbound', '--inbound-preview'), ('us-eu', '--us-eu-preview')]:
        for path in sorted((ROOT / 'tests/fixtures' / group).glob('*.json')):
            specs.append((path.stem, path, [mode]))
    for corridor in ['dom.cn.east', 'dom.cn.south', 'dom.us.ca-ny', 'dom.us.ny-tx', 'dom.us.tx-ca']:
        specs.append((corridor, ROOT / 'tests/fixtures/domestic/owner.json', ['--corridor', corridor]))
    for name in ['domestic', 'cross-member', 'owner-not-moving']:
        specs.append(('eu-' + name, ROOT / f'tests/fixtures/eu/{name}.json', ['--eu-preview']))
    specs.append(('missed-windows', ROOT / 'tests/fixtures/domestic/infeasible.json', ['--corridor', 'dom.cn.east']))
    for ident, path, args in specs:
        profile = json.loads(path.read_text())
        assert path.is_relative_to(ROOT / 'tests/fixtures')  # repository-owned synthetic fixtures
        # US graph fixtures require a matching origin/destination; use the audit fixture.
        if ident.startswith('dom.us.'):
            audit = json.loads((ROOT / 'tests/fixtures/regressions/week9.json').read_text())
            case = next(c for c in audit['cases'] if c.get('corridor') == ident)
            path = ROOT / case['fixture']
        base = [sys.executable, '-m', 'packages.cli', str(path), *args, '--assessment-at', '2026-10-08']
        def run(extra):
            return subprocess.check_output(base + extra, cwd=ROOT, text=True)
        result = json.loads(run([]))
        examples.append({'id': ident, 'result': result,
                         'checklists': {lang: run(['--format', 'checklist', '--language', lang]) for lang in ['en', 'zh-CN']}})
    bundle = {'engine_version': '0.1.0', 'data_version': DATA_VERSION, 'synthetic': True,
              'assessment_at': '2026-10-08', 'examples': examples}
    (output / 'examples.js').write_text('window.PETWAYMARK_DEMO = ' + json.dumps(bundle, ensure_ascii=False) + ';\n')
    for path in (ROOT / 'apps/pages').iterdir():
        if path.is_file(): shutil.copyfile(path, output / path.name)
    print(f'Built {len(examples)} synthetic bilingual examples at {output}')

if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--output', type=Path, default=ROOT / '_site')
    build(p.parse_args().output)
