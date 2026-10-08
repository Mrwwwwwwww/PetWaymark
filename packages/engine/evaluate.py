"""Evaluate trusted rule records after schema/reference validation (contract 0.1.0)."""
from calendar import monthrange
from datetime import date, timedelta
import math
import re


def day(value):
    """Only an explicit local civil date; timestamps need a future zoned policy."""
    if not isinstance(value, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
        raise ValueError('expected YYYY-MM-DD local civil date')
    return date.fromisoformat(value)


def get(data, path):
    value = data
    for part in path.split('.'):
        if not isinstance(value, dict):
            return None
        value = value.get(part)
    return value


def compare(requirement, profile):
    """Return pass/fail/missing/invalid plus exact missing fields; never coerce types."""
    fields = [requirement['field']]
    fields += [requirement[k] for k in ('anchor', 'other_field') if k in requirement]
    values = [get(profile, f) for f in fields]
    missing = [f for f, v in zip(fields, values) if v is None]
    if missing:
        return {'outcome': 'missing', 'fields': missing}
    op = requirement['operator']
    try:
        if op == 'equals':
            if type(values[0]) is not bool:
                raise ValueError('expected boolean')
            ok = values[0] == requirement['value']
        elif op == 'at_most':
            v = values[0]
            if type(v) not in (int, float) or not math.isfinite(v) or v < 1 or int(v) != v:
                raise ValueError('expected positive integer count')
            ok = v <= requirement['value']
        elif op in ('calendar_age_at_least', 'on_or_before', 'elapsed_at_least'):
            start, end = map(day, values)
            if op == 'on_or_before':
                ok = start <= end
            elif op == 'elapsed_at_least':
                # Event day is day zero; elapsed civil days, not 24-hour durations.
                ok = (end - start).days >= requirement['value']
            elif requirement['unit'] == 'week':
                ok = end >= start + timedelta(weeks=requirement['value'])
            elif requirement['unit'] == 'month':
                total = start.year * 12 + start.month - 1 + requirement['value']
                year, month = divmod(total, 12)
                month += 1
                threshold = date(year, month, min(start.day, monthrange(year, month)[1]))
                ok = end >= threshold
            else:
                raise ValueError('unsupported age unit')
        else:
            raise ValueError('unsupported expression')
    except (ValueError, TypeError, OverflowError):
        return {'outcome': 'invalid', 'fields': fields}
    return {'outcome': 'pass' if ok else 'fail', 'fields': []}


def classify(profile):
    """Classification is conservative; not a replacement for jurisdiction rules."""
    p, j = profile.get('pet', {}), profile.get('journey', {})
    reasons, gaps = [], []
    if p.get('species') not in ('dog', 'cat'):
        gaps.append('species_unsupported')
    if p.get('service_animal') is True:
        gaps.append('service_animal_separate_review')
    if j.get('origin') not in ('CN', 'US', 'EU') or j.get('destination') not in ('CN', 'US', 'EU'):
        gaps.append('region_uncovered')
    if j.get('ownership_transfer') is not False:
        gaps.append('ownership_classification_unconfirmed')
    if j.get('purpose') not in ('relocation', 'holiday'):
        gaps.append('movement_classification_unconfirmed')
    if j.get('accompaniment') not in ('owner', 'authorized_person', 'unaccompanied'):
        reasons.append('accompaniment_unknown')
    if j.get('transport_mode') not in ('cabin', 'checked_baggage', 'manifest_cargo', 'road', 'rail'):
        reasons.append('transport_mode_unknown')
    if j.get('destination') == 'US' and j.get('origin') != 'US' and p.get('species') == 'dog':
        history = j.get('travel_history_branch')
        if history == 'high_risk_in_6_months':
            gaps.append('high_risk_branch_uncovered')
        elif history != 'only_low_risk_6_months':
            gaps.append('travel_history_unconfirmed')
    eu_domestic = (j.get('origin') == j.get('destination') == 'EU' and
                   j.get('origin_member') is not None and
                   j.get('origin_member') == j.get('destination_member'))
    if j.get('destination') == 'EU' and not eu_domestic:
        if j.get('owner_moving') is False:
            gaps.append('owner_not_moving_separate_classification')
        if j.get('accompaniment') == 'unaccompanied':
            gaps.append('movement_classification_unconfirmed')
        if j.get('accompaniment') in ('owner', 'authorized_person'):
            try:
                delta = abs((day(j.get('entry_at')) - day(j.get('owner_entry_at'))).days)
                limit = 0 if j['accompaniment'] == 'owner' else 5
                if delta > limit:
                    gaps.append('movement_classification_unconfirmed')
            except ValueError:
                gaps.append('movement_classification_unconfirmed')
        # Certificate transition has no reviewed executable record in this package.
        if get(profile, 'documents.certificate_model') is not None:
            gaps.append('certificate_transition_unreviewed')
    return reasons, gaps


def scope_check(rule, profile):
    """Known mismatch wins over unknown fields; a mismatch never runs comparisons."""
    s, p, j = rule['scope'], profile.get('pet', {}), profile.get('journey', {})
    mismatches, missing = [], []
    if s['movement_category'] == 'intra_eu_pet':
        origin, destination = j.get('origin_member'), j.get('destination_member')
        if origin is None or destination is None:
            missing.append('eu_member_classification')
        elif origin == destination:
            mismatches.append('cross_member_scope_mismatch')
    if (s['movement_category'] in ('all_imports', 'carried_entry') and
            j.get('origin') is not None and j.get('origin') == j.get('destination')):
        mismatches.append('international_entry_scope_mismatch')
    checks = [('species', p.get('species'), s['species']),
              ('destination', j.get('destination'), [s['destination']]),
              ('transport_mode', j.get('transport_mode'), s['transport_modes']),
              ('accompaniment', j.get('accompaniment'), s['accompaniment'])]
    if s['origin'] != 'any':
        checks.append(('origin', j.get('origin'), ['CN', 'US'] if s['origin'] == 'any_non_eu' else [s['origin']]))
    for key in ('travel_history_branch', 'vaccination_branch'):
        if s[key] == 'pending_classification':
            missing.append(key)
        elif s[key] != 'any':
            checks.append((key, j.get(key), [s[key]]))
    if s['subdivisions']:
        checks.append(('subdivision', j.get('subdivision'), s['subdivisions']))
    for field, value, allowed in checks:
        if field == 'accompaniment' and s['movement_category'] == 'non_commercial_pet' and value == 'unaccompanied':
            missing.append('movement_category')
            continue
        if value is None or value == 'unknown':
            missing.append(field)
        elif value not in allowed:
            mismatches.append(field + '_scope_mismatch')
    if s['movement_category'] == 'carried_entry' and j.get('accompaniment') == 'unaccompanied':
        mismatches.append('movement_category_scope_mismatch')
    return mismatches, missing


def review_gate(rule, assessment_at, profile):
    review, validity = rule['review'], rule['validity']
    if review['status'] != 'verified':
        return review['status'] + '_rule'
    try:
        verified, due = day(review['last_verified_at']), day(review['review_due_at'])
        reviewers = review['reviewed_by']
        if (verified > assessment_at or due <= verified or assessment_at >= due or
                len({r['id'] for r in reviewers}) < 2 or rule['pending_checks'] or
                any(r['role'] != 'human_domain_reviewer' or day(r['reviewed_at']) > verified for r in reviewers) or
                any(day(e['accessed_at']) > verified for e in rule['evidence'])):
            return 'review_unusable'
        anchor = 'journey.entry_at' if validity['applies_at'] == 'entry_at' else 'events.rabies_vaccination_at'
        applies = day(get(profile, anchor))
        if applies >= due:
            return 'review_expires_before_travel'
        if applies < day(validity['effective_from']):
            return 'rule_not_yet_effective'
        if validity['effective_to'] and applies > day(validity['effective_to']):
            return 'rule_expired'
    except (ValueError, TypeError, KeyError):
        return 'validity_or_review_unknown'
    return None


def diagnostic(requirement, result):
    field, outcome = requirement['field'], result['outcome']
    if outcome == 'missing':
        if field == 'pet.birth_date':
            return 'missing_birth_date'
        if field == 'pet.microchip_present':
            return 'microchip_unknown'
        return 'missing_input'
    if outcome == 'invalid':
        return 'invalid_input'
    if outcome == 'fail':
        if requirement['operator'] == 'calendar_age_at_least' and requirement.get('unit') == 'month' and requirement['value'] == 6:
            return 'calendar_age_below_six_months'
        return 'condition_failed'
    return 'condition_satisfied'


def review_summary(row):
    """Public review dates only; null means no recorded verification/deadline."""
    review = row['review']
    return ('review_status=' + review['status'] +
            ' | last_verified_at=' + str(review['last_verified_at']) +
            ' | review_due_at=' + str(review['review_due_at']) +
            ' | ' + ', '.join(row['reason_codes']))


def evaluate(profile, rules, *, assessment_at, coverage_gaps=None, resolved_scope_rule_ids=()):
    """Assess a validated package. coverage_gaps is trusted maintainer metadata.

    Default coverage is unreviewed. [] may be used only with an audited complete
    constraint package (or explicitly synthetic tests), never pet-owner input.
    Each scope exclusion also needs its rule ID in resolved_scope_rule_ids.
    """
    as_of = day(assessment_at)
    reasons, gaps = classify(profile)
    classification_gaps = list(gaps)
    gaps += ['critical_coverage_unreviewed'] if coverage_gaps is None else list(coverage_gaps)
    rows, excluded, blocked, conditional = [], [], False, bool(reasons)
    ids = [r['id'] for r in rules]
    if len(ids) != len(set(ids)):
        gaps.append('duplicate_rule_ids')
    for rule in sorted(rules, key=lambda r: r['id']):
        mismatch, missing_scope = scope_check(rule, profile)
        row = {'rule_id': rule['id'], 'revision': rule['revision'],
               'message': rule['message'], 'evidence': rule['evidence'],
               'source_ids': rule['source_ids'], 'scope_missing': missing_scope,
               'review': rule['review'], 'validity': rule['validity']}
        if mismatch:
            excluded.append(rule['id'])
            reasons += mismatch
            row.update(outcome='not_applicable', reason_codes=mismatch)
            rows.append(row)
            continue
        gate = review_gate(rule, as_of, profile)
        if gate:
            gaps.append(gate)
        if rule['id'] not in resolved_scope_rule_ids:
            gaps.append('rule_scope_exclusions_unreviewed')
        result = compare(rule['requirement'], profile)
        code = diagnostic(rule['requirement'], result)
        reasons.append(code)
        if missing_scope:
            conditional = True
            reasons.append('scope_input_missing')
        enforceable = not gate and not missing_scope and not classification_gaps
        # A failed comparison with a possible sourced exception cannot block automatically.
        if enforceable and result['outcome'] == 'fail' and not rule['exceptions']:
            blocked |= rule['on_fail'] == 'block'
            conditional |= rule['on_fail'] == 'needs_confirmation'
        elif result['outcome'] != 'pass':
            conditional = True
        if rule['exceptions'] and result['outcome'] != 'pass':
            conditional = True
            reasons.append('exception_needs_confirmation')
        row.update(outcome=result['outcome'], missing_fields=result['fields'],
                   enforceable=enforceable, reason_codes=([gate] if gate else []) + [code])
        rows.append(row)
    if not rows or all(r['outcome'] == 'not_applicable' for r in rows):
        gaps.append('applicable_rules_uncovered')
    acceptance = profile.get('journey', {}).get('carrier_acceptance', 'unknown')
    if acceptance not in ('unknown', 'externally_confirmed', 'declined'):
        acceptance = 'unknown'
    if acceptance == 'unknown':
        reasons.append('carrier_acceptance_unknown')
    # Mismatch reasons are explanatory and do not make another matched rule conditional.
    status = 'ineligible' if blocked else 'unsupported' if gaps else 'conditional' if conditional else 'eligible'
    return {'engine_version': '0.1.0', 'assessment_at': assessment_at,
            'assessment_scope': 'supplied_constraint_package', 'status': status,
            'reason_codes': sorted(set(reasons + gaps)), 'coverage_gaps': sorted(set(gaps)),
            'matched_rule_ids': [r['rule_id'] for r in rows if r['outcome'] != 'not_applicable'],
            'not_applicable_rule_ids': excluded, 'explanations': rows,
            'external_progress': {'carrier_acceptance': acceptance},
            'booking_confirmed': False}
