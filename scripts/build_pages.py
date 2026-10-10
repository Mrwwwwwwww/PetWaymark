#!/usr/bin/env python3
"""Build an offline Chinese question checklist; never evaluate eligibility."""
import argparse
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
QUESTIONS = {
    'journey.pets_per_person': '随行宠物数量有没有限制？',
    'pet.microchip_present': '芯片是否需要？型号和记录怎么确认？',
    'documents.official_health_certificate_valid': '是否需要出发国官方检疫证明？在哪里办，出发时是否有效？',
    'documents.cdc_receipt_present': '美国入境的犬是否需要申报回执？哪些旅行史条件适用？',
    'pet.birth_date': '年龄是否符合接种或入境条件？需要什么出生日期记录？',
    'pet.appears_healthy_on_arrival': '猫入境时有哪些健康检查？还要确认哪些州或地区要求？',
    'pet.universal_scanner_readable': '芯片能否被要求的设备读取？怎么核对？',
    'pet.healthy': '当地是否需要健康检查或证明？',
    'events.identification_at': '芯片和接种有没有先后要求？现有记录是否适用？',
    'events.primary_protocol_completed_at': '接种后有没有等待期？加强针和首次接种是否不同？',
}


def payload(root=ROOT):
    catalog = json.loads((root / 'data/sources/catalog.json').read_text())
    sources = {s['id']: s for s in catalog['sources']}
    records = []
    # Carrier research is deliberately excluded: the page recommends no brands.
    for group in ['cn', 'us', 'eu']:
        for path in sorted((root / 'data/rules' / group).glob('*.json')):
            rule = json.loads(path.read_text())
            field = rule['requirement']['field']
            if field not in QUESTIONS:
                raise ValueError(f'Add a reviewed question mapping for {rule["id"]}: {field}')
            records.append({
                'id': rule['id'], 'scope': rule['scope'], 'validity': rule['validity'],
                'review': rule['review'], 'question': QUESTIONS[field],
                'source_ids': rule['source_ids'], 'license': rule['license'],
                'unknowns': rule.get('pending_checks', []),
                'sources': [sources[s] for s in rule['source_ids']],
            })
    return {'dataVersion': json.loads((root / 'data/VERSION.json').read_text())['dataset_version'],
            'builtAt': '2026-10-10', 'verifiedRoutes': 0,
            'testingPoints': json.loads((root / 'apps/pages/testing-points.json').read_text()),
            'locations': json.loads((root / 'apps/pages/locations.json').read_text()), 'rules': records}


def data_script(root=ROOT):
    return 'window.PETWAYMARK_PAGE = ' + json.dumps(payload(root), ensure_ascii=False, separators=(',', ':')) + ';\n'


def build(output, root=ROOT):
    output.mkdir(parents=True, exist_ok=True)
    for name in ['index.html', 'result.html', 'style.css', 'app.js']:
        shutil.copyfile(root / 'apps/pages' / name, output / name)
    (output / 'page-data.js').write_text(data_script(root), encoding='utf-8')
    # Retired generated artifacts only; historical source remains in git.
    for name in ['demo.js', 'examples.js', 'correction.js']:
        (output / name).unlink(missing_ok=True)
    print(f'Built static question checklist at {output}; zero verified routes')


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--output', type=Path, default=ROOT / '_site')
    p.add_argument('--write-source', action='store_true', help='Refresh committed offline page data')
    p.add_argument('--check', action='store_true', help='Check committed page data is reproducible')
    args = p.parse_args()
    source = ROOT / 'apps/pages/page-data.js'
    if args.check:
        if source.read_text() != data_script():
            raise SystemExit('Page data drift: run build_pages.py --write-source after reviewing changes')
        print('Committed page data matches original rules and place slice')
    else:
        if args.write_source:
            source.write_text(data_script(), encoding='utf-8')
        build(args.output)
