"""Offline research graph preview. Draft paths are never recommendations or bookings."""
from copy import deepcopy
import math
import re

from packages.engine.evaluate import classify, day, evaluate, get
from packages.engine.io import ROOT, load_repository
from scripts.validate_data import read_json


def load_graph(root=ROOT):
    load_repository(root)  # schemas and cross references, including graph evidence
    return read_json(root / 'data/corridors/cn-preview.json')


def paths(graph, origin, destination):
    """Enumerate simple directed paths in the small curated graph; no reverse inference."""
    outgoing = {}
    for leg in sorted(graph['segments'], key=lambda s: s['segment_id']):
        outgoing.setdefault(leg['from_node'], []).append(leg)

    def walk(node, seen, legs):
        if node == destination:
            yield legs
            return
        for leg in outgoing.get(node, []):
            if leg['to_node'] not in seen:
                yield from walk(leg['to_node'], seen | {leg['to_node']}, legs + [leg])
    return list(walk(origin, {origin}, []))


def limit_diagnostics(leg, profile):
    rows = []
    for limit in leg['limits']:
        value = get(profile, limit['field'])
        valid = type(value) in (int, float) and math.isfinite(value) and value > 0
        outcome = ('missing' if value is None else 'invalid' if not valid else
                   'pass' if value <= limit['maximum'] else 'fail')
        rows.append({**limit, 'outcome': outcome, 'enforceable': False})
    return rows


def preview(profile, graph, *, corridor_id, assessment_at):
    """Assess research paths. Public graph and coverage are trusted maintainer inputs.

    User input can reject a leg or supply readiness but cannot upgrade evidence,
    capacity, hours, rules, roles or coverage. No CN import rule is used domestically.
    """
    day(assessment_at)
    if not isinstance(profile, dict):
        raise ValueError('profile must be an object')
    for key in ('pet', 'journey', 'documents', 'events'):
        if not isinstance(profile.get(key, {}), dict):
            raise ValueError('profile groups must be objects')
    journey = profile.get('journey', {})
    if 'entry_at' in journey:
        day(journey['entry_at'])
    controls = profile.get('preview', {})
    if not isinstance(controls, dict) or set(controls) - {'journey_id', 'plan_revision', 'can_drive', 'segments'}:
        raise ValueError('unknown preview control')
    journey_id = controls.get('journey_id', 'local.preview')
    revision = controls.get('plan_revision', 1)
    if not isinstance(journey_id, str) or not re.fullmatch(r'[a-z0-9][a-z0-9.-]{0,63}', journey_id):
        raise ValueError('journey_id must be an opaque lowercase ID, not personal information')
    if type(revision) is not int or revision < 1:
        raise ValueError('plan_revision must be a positive integer')
    if controls.get('can_drive') is not None and type(controls['can_drive']) is not bool:
        raise ValueError('can_drive must be boolean or null')
    corridor = next((c for c in graph['corridors'] if c['id'] == corridor_id), None)
    if corridor is None:
        raise ValueError('unknown corridor ID')
    overrides = controls.get('segments', {})
    if not isinstance(overrides, dict) or not set(overrides) <= {s['segment_id'] for s in graph['segments']}:
        raise ValueError('unknown segment ID')
    for value in overrides.values():
        if not isinstance(value, dict) or set(value) - {'reported_acceptance', 'handover_window_met'}:
            raise ValueError('unknown segment control; evidence and assignment cannot be overridden')
        if value.get('reported_acceptance', 'unknown') not in ('unknown', 'declined'):
            raise ValueError('preview accepts only unknown or user-reported declined acceptance')
        if value.get('handover_window_met') is not None and type(value['handover_window_met']) is not bool:
            raise ValueError('handover_window_met must be boolean or null')
    # Reuse Week 3 classification, with mode supplied for each graph leg below.
    classification_profile = deepcopy(profile)
    classification_profile.setdefault('journey', {})['transport_mode'] = 'road'
    reasons, gaps = classify(classification_profile)
    if journey.get('origin') != 'CN' or journey.get('destination') != 'CN':
        gaps.append('domestic_cn_scope_only')
    if journey.get('pets_per_person') != 1 or type(journey.get('pets_per_person')) is not int:
        gaps.append('single_pet_scope_unconfirmed')
    if journey.get('accompaniment') not in ('owner', 'authorized_person', 'unaccompanied'):
        gaps.append('accompaniment_unconfirmed')
    if 'entry_at' not in journey:
        gaps.append('travel_date_unknown')
    result = dict(preview_version='0.1.0', dataset_version=graph['dataset_version'],
                  journey_id=journey_id, plan_revision=revision, assessment_at=assessment_at,
                  corridor_id=corridor_id, research_candidate_id=corridor['research_candidate_id'],
                  status='unsupported', candidates=[], excluded=[], reason_codes=sorted(set(reasons + gaps)),
                  recommendations=[], booking_confirmed=False, verified_feasible_route_count=0)
    if gaps:
        return result  # no route construction before classification is resolved
    for route in paths(graph, corridor['origin_node'], corridor['destination_node']):
        rows, blockers, route_gaps = [], [], set()
        for leg in route:
            product = leg['product']
            override = overrides.get(leg['segment_id'], {})
            acceptance = override.get('reported_acceptance', 'unknown')
            leg_reasons = []
            if acceptance == 'declined':
                leg_reasons.append('segment_declined')
            if override.get('handover_window_met') is False:
                leg_reasons.append('handover_window_missed')
            if product == 'owner_vehicle':
                if journey.get('accompaniment') != 'owner':
                    leg_reasons.append('owner_vehicle_requires_owner')
                if controls.get('can_drive') is False:
                    leg_reasons.append('driving_unavailable')
                elif controls.get('can_drive') is not True:
                    route_gaps.add('driving_readiness_unknown')
            if product == 'rail_owner_accompanied' or leg['mode'] == 'checked_baggage':
                if journey.get('accompaniment') == 'unaccompanied':
                    leg_reasons.append('accompanied_product_unavailable')
            if product in ('rail_unaccompanied', 'unaccompanied_animal_carrier'):
                if journey.get('accompaniment') != 'unaccompanied':
                    leg_reasons.append('unaccompanied_product_scope_mismatch')
            if profile.get('pet', {}).get('species') not in leg['species']:
                leg_reasons.append('species_product_mismatch')
            # Operational conflicts come from explicit input, not unreviewed legal rules.
            blockers.extend(leg_reasons)
            local = deepcopy(profile)
            local['journey']['transport_mode'] = leg['mode']
            local['journey']['carrier_acceptance'] = acceptance
            assessment = evaluate(local, [], assessment_at=assessment_at,
                                  coverage_gaps=leg['coverage_gaps'])
            route_gaps.update(assessment['coverage_gaps'])
            row = deepcopy(leg)
            row.update(rule_assessment=assessment, draft_diagnostics=limit_diagnostics(leg, profile),
                       reported_acceptance=acceptance, reason_codes=leg_reasons,
                       status='ineligible' if leg_reasons else 'unsupported')
            rows.append(row)
        candidate = dict(candidate_id='path.' + '.'.join(s['segment_id'] for s in route),
                         segment_ids=[s['segment_id'] for s in route], segments=rows,
                         status='ineligible' if blockers else 'unsupported',
                         reason_codes=sorted(set(blockers) | route_gaps),
                         door_to_door_minutes=None, total_cost_cny=None,
                         booking_confirmed=False, ranked=False)
        result['excluded' if blockers else 'candidates'].append(candidate)
    if not result['candidates']:
        result['status'] = 'ineligible' if result['excluded'] else 'unsupported'
        result['reason_codes'].append('all_paths_excluded' if result['excluded'] else 'no_connected_path')
    else:
        result['reason_codes'].append('research_candidates_unreviewed')
    return result


def checklist(result, graph, *, language='zh-CN'):
    """Printable plain text; public facility names only, no private profile dump."""
    if language not in ('zh-CN', 'en'):
        raise ValueError('unsupported checklist language')
    zh = language == 'zh-CN'
    names = {n['id']: n['name'][language] for n in graph['nodes']}
    pending = '待安排' if zh else 'pending arrangement'
    unknown = '待确认' if zh else 'needs confirmation'
    lines = [('宠途路标国内研究预览 — 未订舱／未接单' if zh else
              'PetWaymark domestic research preview — no booking or order'),
             f"{result['corridor_id']} | {result['status']} | {result['assessment_at']}",
             f"{result['journey_id']} | revision {result['plan_revision']} | {result['dataset_version']}",
             ('未知不能变成允许；候选不作排名。' if zh else 'Unknown is not permission; candidates are not ranked.'),
             ', '.join(result['reason_codes'])]
    role_names = {'escort': '陪同', 'custodian': '宠物保管', 'handover_recipient': '交接接收', 'document_custodian': '原件保管'}
    for group in ('candidates', 'excluded'):
        for route in result[group]:
            lines.extend(['', f"{group}: {route['candidate_id']} | {route['status']}",
                          ('门到门估时／费用：待确认' if zh else 'Door-to-door duration / cost: needs confirmation')])
            for leg in route['segments']:
                lines.append(f"[{leg['segment_id']}] {names[leg['from_node']]} → {names[leg['to_node']]} | {leg['mode']} / {leg['product']}")
                lines.append(f"{'交接地点' if zh else 'Handover location'}: {names[leg['handover']['location_node']]} ({unknown})")
                lines.append(f"{'交接窗口' if zh else 'Handover window'}: {unknown}")
                for role in leg['handover']['roles']:
                    lines.append(f"{role_names[role] if zh else role}: {pending}")
                lines.append(f"{'收运进度（输入报告）' if zh else 'Acceptance (input report)'}: {leg['reported_acceptance']}")
                lines.append(f"{'原因／缺口' if zh else 'Reasons / gaps'}: " + ', '.join(leg['reason_codes'] + leg['rule_assessment']['reason_codes']))
                for d in leg['draft_diagnostics']:
                    lines.append(f"{'草稿诊断（非执行规则）' if zh else 'Draft diagnostic (not enforced)'}: {d['field']} <= {d['maximum']} | {d['outcome']} | {d['source_id']}")
                for e in leg['evidence']:
                    lines.append(f"{e['source_id']} | {e['url']} | {e['locator']} | {e['accessed_at']}")
                    lines.append(e['summary'][language])
    return '\n'.join(lines) + '\n'
