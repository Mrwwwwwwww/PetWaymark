"""EU evidence preview, never a complete legal package or transport graph.

Model/date diagnostics are separate from document validity and remain unenforced.
Only trusted repository inventory supplies source evidence and transition dates.
"""
from copy import deepcopy

from packages.engine.evaluate import classify, compare, day, evaluate, get, review_summary
from packages.engine.io import ROOT
from scripts.validate_data import read_json


def load_inventory(root=ROOT):
    return read_json(root / 'data/coverage/eu-members.json')


def row(ident, outcome, source_ids, locator):
    return dict(diagnostic_id=ident, outcome=outcome, enforceable=False,
                source_ids=source_ids, locator=locator)


def document_diagnostic(profile, inventory, *, scope):
    """Only model/date consistency; not issuance, endorsement or validity approval."""
    kind = 'passport' if scope == 'intra_eu' else 'certificate'
    model = get(profile, 'documents.' + kind + '_model')
    issued = get(profile, 'documents.' + kind + '_issued_at')
    record = next((r for r in inventory['document_models']
                   if r['id'] == model and r['scope'] == scope), None)
    outcome = 'missing' if model is None or issued is None else 'unsupported_model'
    if record and issued is not None:
        try:
            issue, entry = day(issued), day(get(profile, 'journey.entry_at'))
            if issue > entry:
                outcome = 'invalid'
            elif record['issued_before'] and issue >= day(record['issued_before']):
                outcome = 'model_issue_cutoff_failed'
            elif record['recognition_until'] and entry > day(record['recognition_until']):
                outcome = 'model_recognition_period_ended'
            elif model.startswith('eu.705.') and issue < day('2026-04-22'):
                outcome = 'model_not_yet_applicable'
            else:
                outcome = 'model_date_consistent'
        except ValueError:
            outcome = 'invalid'
    return row('eu.' + kind + '.model-date', outcome, ['eu.law.2026-705'],
               record['locator'] if record else 'Articles 1, 3, 6, 8; models not exhaustively compiled')


def identification_diagnostic(profile):
    method = get(profile, 'pet.identification_method')
    outcome = 'missing' if method is None else 'unsupported_method'
    if method == 'microchip':
        result = compare(dict(field='pet.microchip_present', operator='equals', value=True), profile)
        outcome = result['outcome']
    elif method == 'tattoo':
        applied, readable = get(profile, 'events.tattoo_at'), get(profile, 'pet.tattoo_readable')
        if applied is None or readable is None:
            outcome = 'missing'
        else:
            try:
                if type(readable) is not bool:
                    raise ValueError('expected boolean')
                outcome = 'exception_needs_confirmation' if readable and day(applied) < day('2011-07-03') else 'tattoo_exception_not_met'
            except ValueError:
                outcome = 'invalid'
    return row('eu.identification', outcome, ['eu.ec.intra-eu'], 'Identification; Exceptions / Identification')


def titre_diagnostics(profile):
    """Annex III research only. Unread country lists cannot yield an exemption."""
    branch = get(profile, 'journey.titre_branch')
    if branch != 'test_required':
        return [row('eu.titre.branch', 'missing' if branch is None else 'exception_needs_confirmation',
                    ['eu.law.2026-705', 'eu.law.2026-636'], 'Annex III II.3; current lists/return/transit pending')]
    rows = []
    for ident, requirement in [
        ('sample-after-primary', dict(field='events.rabies_vaccination_at', operator='elapsed_at_least',
                                     value=30, anchor='events.titre_sample_at')),
        ('sample-to-issue', dict(field='events.titre_sample_at', operator='elapsed_at_least',
                                value=90, anchor='documents.certificate_issued_at')),
    ]:
        result = compare(requirement, profile)
        rows.append(row('eu.titre.' + ident, result['outcome'], ['eu.law.2026-705'], 'Annex III II.3.1; note (6)'))
    # Booster continuity, lab designation/result and attached report are uncompiled.
    return rows


def assess(profile, *, assessment_at, rules, inventory):
    day(assessment_at)
    if not isinstance(profile, dict) or any(not isinstance(profile.get(k, {}), dict)
                                           for k in ('pet', 'journey', 'documents', 'events')):
        raise ValueError('profile groups must be objects')
    p, j = profile.get('pet', {}), profile.get('journey', {})
    reasons, gaps = classify(profile)
    members = tuple(m['member'] for m in inventory['members'])
    origin, destination = j.get('origin_member'), j.get('destination_member')
    if j.get('origin') != 'EU' or j.get('destination') != 'EU':
        gaps.append('eu_internal_preview_only')
    if origin not in members or destination not in members:
        gaps.append('eu_member_classification_unconfirmed')
    domestic = origin in members and origin == destination
    if p.get('service_animal') is not False:
        gaps.append('ordinary_pet_classification_unconfirmed')
    if type(j.get('pets_per_person')) is not int or j.get('pets_per_person') != 1:
        gaps.append('single_pet_scope_unconfirmed')
    if not domestic and j.get('owner_moving') is not True:
        gaps.append('owner_movement_unconfirmed')
    if not domestic and j.get('accompaniment') == 'authorized_person' and j.get('authorized_person_written') is not True:
        gaps.append('written_authorization_unconfirmed')
    if reasons:
        gaps.append('eu_classification_unconfirmed')
    try:
        day(j.get('entry_at'))
    except ValueError:
        gaps.append('travel_date_unknown_or_invalid')
    result = dict(preview_version='0.1.0', dataset_version=inventory['dataset_version'],
                  assessment_at=assessment_at, assessment_scope='eu_internal_evidence_preview',
                  movement_scope='domestic' if domestic else 'cross_member', status='unsupported',
                  candidates=[], excluded=[], recommendations=[], booking_confirmed=False,
                  verified_feasible_route_count=0, classification_resolved=not gaps,
                  eu_inventory=deepcopy(inventory), draft_diagnostics=[], explanations=[])
    if not gaps:
        if domestic:
            reasons.append('eu_domestic_rules_unreviewed')
        else:
            selected = [r for r in rules if r['scope']['movement_category'] == 'intra_eu_pet']
            evaluated = evaluate(profile, selected, assessment_at=assessment_at)
            result['explanations'] = evaluated['explanations']
            reasons += evaluated['reason_codes']
            result['draft_diagnostics'] = [identification_diagnostic(profile),
                                           document_diagnostic(profile, inventory, scope='intra_eu')]
            reasons.append('eu_cross_member_package_unreviewed')
    result['reason_codes'] = sorted(set(reasons + gaps + inventory['framework']['pending_checks'] + ['eu_member_overlays_unreviewed',
                                                        'eu_transport_and_custody_unverified']))
    return result


def checklist(result, *, language='zh-CN'):
    if language not in ('en', 'zh-CN'):
        raise ValueError('unsupported checklist language')
    zh = language == 'zh-CN'
    lines = ['欧盟证据研究预览 — 未订舱／未接单' if zh else 'EU evidence research preview — no booking or order',
             result['status'] + ' | ' + result['movement_scope'] + ' | ' + result['dataset_version'],
             ', '.join(result['reason_codes']),
             '文件诊断不证明有效；运输与原件责任待安排。' if zh else
             'Document diagnostics do not establish validity; transport and original-document responsibility pending arrangement.']
    inv = result['eu_inventory']
    for item in [inv['framework']] + inv['members']:
        lines.append(item.get('member', 'EU') + ' | ' + item.get('status', 'read_pending_review'))
        lines.append(', '.join(item['pending_checks']))
        for e in item['evidence']:
            lines.append(f"{e['source_id']} | {e['url']} | {e['accessed_at']} | {e['summary'][language]}")
    for r in result['explanations']:
        lines.append(r['rule_id'] + ' | ' + r['outcome'] + ' | ' + r['message'][language])
        lines.append(review_summary(r))
    for r in result['draft_diagnostics']:
        lines.append(r['diagnostic_id'] + ' | ' + r['outcome'] + ' | ' + ', '.join(r['source_ids']))
    for r in inv['document_models']:
        lines.append(f"{r['id']} | {r['scope']} | issued_before={r['issued_before']} | recognition_until={r['recognition_until']} | {r['source_id']} | {r['locator']}")
    for r in inv['exceptions']:
        lines.append(r['id'] + ' | ' + r['summary'][language] + ' | ' + ', '.join(r['pending_checks']))
    return '\n'.join(lines) + '\n'
