#!/usr/bin/env python3
"""Execute numbered synthetic regressions and reproduce the six-direction matrix."""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from packages.engine import eu, inbound, outbound, us_eu
from packages.engine.handover import assess as handover_assess
from packages.engine.io import load_repository
from packages.engine.routes import preview
from scripts.validate_data import read_json

DIRECTIONS = ('CN→US', 'CN→EU', 'US→CN', 'EU→CN', 'US→EU', 'EU→US')
DEFINITIONS = {
    'unsupported': {'en':'Scope or evidence incomplete; no permission.', 'zh-CN':'范围或证据不全，不表示允许。'},
    'conditional': {'en':'Reviewed rule eligibility with unresolved operations; not a confirmed route.', 'zh-CN':'已复核规则满足但操作条件待确认，非确认路线。'},
    'ineligible': {'en':'Explicit operational contradiction excludes every candidate; draft legal failures alone do not reject.', 'zh-CN':'明确操作冲突排除全部候选；草稿法律诊断失败本身不裁定拒绝。'},
    'verified_supported': {'en':'Reviewed current rules and evidenced dated whole-route capacity/custody. None exists.', 'zh-CN':'现行规则已复核且全程日期限定运力与责任有证据；当前无此路线。'},
}


def run(root=ROOT, manifest=None):
    manifest = manifest if manifest is not None else read_json(root / 'tests/fixtures/regressions/week9.json')
    if manifest.get('synthetic') is not True or len(manifest.get('cases', [])) < 30:
        raise ValueError('audit requires >=30 explicitly synthetic cases')
    rules = load_repository(root)
    inventories = {name:mod.load_inventory(root) for name,mod in [('eu',eu),('outbound',outbound),('inbound',inbound),('us_eu',us_eu)]}
    graphs = {region:read_json(root / f'data/corridors/{region.lower()}-preview.json') for region in ('CN','US')}
    overlays = read_json(root / 'data/coverage/us-state-overlays.json')
    directory = read_json(root / 'data/providers/directory.json')
    ids = set(); results = []; baseline = {}
    for case in manifest['cases']:
        ident = case['id']
        if ident in ids: raise ValueError('duplicate regression ID')
        ids.add(ident)
        path = (root / case['fixture']).resolve()
        if not path.is_relative_to((root / 'tests/fixtures').resolve()): raise ValueError('fixture outside tests/fixtures')
        profile = deepcopy(read_json(path))
        for key,value in case['patch'].items():
            parts = key.split('.')
            if len(parts) != 2: raise ValueError('patch must target a profile field')
            profile.setdefault(parts[0], {})[parts[1]] = deepcopy(value)
        before = deepcopy(profile); at = manifest['assessment_at']; engine = case['engine']
        if engine == 'routes':
            region = 'US' if case['corridor'].startswith('dom.us.') else 'CN'
            r = preview(profile,graphs[region],corridor_id=case['corridor'],assessment_at=at,rules=rules,overlays=overlays if region=='US' else None)
        elif engine == 'eu': r = eu.assess(profile,assessment_at=at,rules=rules,inventory=inventories['eu'])
        elif engine == 'outbound': r = outbound.assess(profile,assessment_at=at,inventory=inventories['outbound'],eu_inventory=inventories['eu'])
        elif engine == 'inbound': r = inbound.assess(profile,assessment_at=at,inventory=inventories['inbound'],directory=directory)
        elif engine == 'us_eu': r = us_eu.assess(profile,assessment_at=at,inventory=inventories['us_eu'],eu_inventory=inventories['eu'])
        else: raise ValueError('unknown regression engine')
        if profile != before: raise AssertionError(ident + ': input mutated')
        expected = case['expected']; diagnostics = {x['diagnostic_id']:x['outcome'] for x in r.get('draft_diagnostics',[])}
        for key in ('status', 'classification_resolved'):
            if key in expected and r.get(key) != expected[key]:
                raise AssertionError(f'{ident}: {key}: {r.get(key)} != {expected[key]}')
        if r['booking_confirmed'] is not False or r['verified_feasible_route_count'] != 0 or r['recommendations']:
            raise AssertionError(ident + ': unreviewed route promoted')
        if expected.get('reason') and expected['reason'] not in r['reason_codes']:
            raise AssertionError(ident + ': missing expected reason')
        if 'diagnostic' in expected:
            d = expected['diagnostic']
            if diagnostics.get(d['id']) != d['outcome']:
                raise AssertionError(f"{ident}: {d['id']}: {diagnostics.get(d['id'])} != {d['outcome']}")
        handover = handover_assess(case.get('handover', {}))
        for key in ('pickup_outcome', 'overnight_outcome'):
            if key in expected and handover[key] != expected[key]: raise AssertionError(ident + ': ' + key)
        results.append(dict(id=ident,area=case['area'],engine=engine,fixture=case['fixture'],expected=deepcopy(expected),
                            status=r['status'],classification_resolved=r.get('classification_resolved'),
                            diagnostics=diagnostics,reason_codes=r['reason_codes'],final_handover=handover,passed=True))
        if case['area'] in DIRECTIONS and case['area'] not in baseline: baseline[case['area']] = r
    if set(baseline) != set(DIRECTIONS): raise AssertionError('six independent directions not exercised')
    covered_areas={c['area'] for c in results}
    if not all(any(c['area'].startswith(prefix) for c in results) for prefix in ('CN east','CN south','US CA','US NY','US TX','EU domestic','EU cross-member')):
        raise AssertionError('domestic areas missing')
    matrix=[]
    for direction in DIRECTIONS:
        r=baseline[direction]
        species={}
        for kind in ('dog','cat'):
            selected=[x for x in results if x['area']==direction and x['fixture'].endswith('-'+kind+'.json') and not x['expected'].get('diagnostic') and x['expected'].get('classification_resolved') is True]
            if not selected: raise AssertionError('missing dog/cat directional baseline')
            species[kind]=dict(route_status=selected[0]['status'],baseline_case=selected[0]['id'])
        matrix.append(dict(direction=direction,dataset_version=r['dataset_version'],species=species,
                           case_ids=[x['id'] for x in results if x['area']==direction],
                           status_counts={s:sum(x['status']==s for x in results if x['area']==direction) for s in DEFINITIONS},
                           evidence=deepcopy(r['evidence']),pending_checks=r['reason_codes'],
                           verified_feasible_route_count=0,independent_review_complete=False))
    return dict(audit_version=manifest['version'],assessment_at=manifest['assessment_at'],synthetic=True,
                actual_usage_count=0,verified_feasible_route_count=0,case_count=len(results),
                passed_count=len(results),domestic_areas=sorted(covered_areas-set(DIRECTIONS)),
                status_definitions=DEFINITIONS,status_counts={s:sum(x['status']==s for x in results) for s in DEFINITIONS},
                six_direction_matrix=matrix,cases=results)


def markdown(audit):
    lines=['# Week 9 coverage audit / 第9周覆盖审计', '',
           f"{audit['passed_count']}/{audit['case_count']} executed synthetic cases pass; verified feasible routes 0, actual usage 0.",
           f"{audit['passed_count']}/{audit['case_count']}个合成案例实际执行通过；已验证可行路线0，真实采用0。", '',
           'Reproduce / 复跑：`python scripts/audit_coverage.py --check`。Generated outputs must match; failures exit nonzero.', '',
           'Route status differs from draft diagnostic outcomes and final-handover readiness. Unknown never grants permission.',
           '路线状态、草稿诊断与末段交接准备分别展示；未知不表示允许。', '']
    for status,desc in DEFINITIONS.items(): lines += [f"- `{status}`: {desc['en']} / {desc['zh-CN']}"]
    lines += ['', '| Direction / 方向 | Dog / 犬 | Cat / 猫 | Executed / 执行 | Verified / 已验证 |', '|---|---|---|---|---|']
    for row in audit['six_direction_matrix']:
        lines.append(f"| {row['direction']} | {row['species']['dog']['route_status']} ({row['species']['dog']['baseline_case']}) | {row['species']['cat']['route_status']} ({row['species']['cat']['baseline_case']}) | {len(row['case_ids'])} | 0 |")
    lines += ['', 'Full source URLs, access dates, evidence states and pending checks are in [week9-audit.json](week9-audit.json).',
              '完整来源URL、查阅日期、证据状态、缺项及逐案例诊断见同目录JSON。每个方向独立内核输出，未整体宣称成员国覆盖。', '',
              '| Case / 案例 | Area / 地区方向 | Fixture | Observed status / 观察状态 | Assertion / 断言 |', '|---|---|---|---|---|']
    for case in audit['cases']:
        expected=case['expected']; detail = json.dumps({k:v for k,v in expected.items() if k!='status'},ensure_ascii=False,sort_keys=True)
        lines.append(f"| {case['id']} | {case['area']} | `{case['fixture']}` | {case['status']} | {detail} |")
    lines += ['', 'Final pickup is evaluated with explicit offset plus IANA timezone; DST folds are distinguished and nonexistent times rejected.',
              'Required overnight care with unknown availability or an unassigned custodian stays unresolved. Self-report cannot confirm custody.',
              '末段使用显式UTC偏移及IANA时区，区分DST重复时刻并拒绝不存在时刻；必需过夜照护未知、保管人未安排不被补齐，自报不能确认责任。', '',
              'Independent human reviews, full current annexes, EU local export procedures, US state/emergency overlays, actual operating capacity, originals and recovery custody remain pending.',
              '独立人工复核、完整现行附件、欧盟地方出口、美国州／应急叠加、实际运力、原件和异常责任仍待完成。', '']
    return '\n'.join(lines)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    mode=parser.add_mutually_exclusive_group();mode.add_argument('--write',action='store_true');mode.add_argument('--check',action='store_true')
    args=parser.parse_args()
    try:
        audit=run(); payloads={'week9-audit.json':json.dumps(audit,ensure_ascii=False,indent=2)+'\n','week9-matrix.md':markdown(audit)}
        for name,payload in payloads.items():
            path=ROOT/'data/coverage'/name
            if args.write: path.write_text(payload,encoding='utf-8')
            elif args.check and (not path.exists() or path.read_text(encoding='utf-8') != payload):
                raise ValueError('generated audit drift: '+name)
        print(f"PASS: {audit['passed_count']} executed cases; six independent directions; zero verified feasible routes or actual usage.")
        return 0
    except (AssertionError, ValueError, KeyError, OSError) as exc:
        print('FAIL: '+str(exc),file=sys.stderr);return 1


if __name__=='__main__': sys.exit(main())
