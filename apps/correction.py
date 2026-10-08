"""Minimum technical context for user-initiated public corrections, no profiles."""
import json
import re
from packages.engine.io import ROOT

CONTAINERS = ('explanations', 'draft_diagnostics', 'candidates', 'excluded', 'segments',
              'rule_assessment', 'final_handover')


def context(result, language, root=ROOT):
    if language not in ('en', 'zh-CN'):
        raise ValueError('unsupported correction language')
    known = {json.loads(p.read_text())['id'] for p in (root/'data/rules').rglob('*.json')}
    rules, codes = set(), set()

    def visit(row):
        if isinstance(row, list):
            for item in row: visit(item)
        elif isinstance(row, dict):
            for value in [row.get('rule_id'), *row.get('matched_rule_ids', []), *row.get('rule_ids', [])]:
                if isinstance(value, str) and value in known: rules.add(value)
            for value in row.get('reason_codes', []):
                if isinstance(value, str) and re.fullmatch(r'[a-z][a-z0-9_.:-]{0,119}', value):
                    codes.add(value)
            for key in CONTAINERS:
                if key in row: visit(row[key])
    visit(result)
    return {'engine_version':'0.1.0',
            'dataset_version':json.loads((root/'data/VERSION.json').read_text())['dataset_version'],
            'rule_ids':sorted(rules), 'reason_codes':sorted(codes), 'language':language}


def panel(result, language):
    # Escape markup in inert JSON even though projection only contains technical tokens.
    payload=json.dumps(context(result, language), ensure_ascii=False).replace('<', chr(92)+'u003c')
    return '<div id="correction"></div><script type="application/json" id="correction-context">'+payload+'</script>'
