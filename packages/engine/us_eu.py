"""Independent US↔EU document research. Draft diagnostics never grant permission."""
from copy import deepcopy
from datetime import timedelta

from packages.engine.evaluate import compare, day, get
from packages.engine.eu import document_diagnostic, load_inventory as load_eu
from packages.engine.io import ROOT
from packages.engine.outbound import bounded_days, instant
from scripts.validate_data import read_json


def load_inventory(root=ROOT):
    return read_json(root / 'data/coverage/us-eu.json')


def calendar_shift(value, months):
    """Civil-month estimate; last day clamps, not a legal/hour deadline."""
    from calendar import monthrange
    d = day(value)
    n = d.year * 12 + d.month - 1 + months
    y, m = divmod(n, 12)
    return d.replace(year=y, month=m + 1, day=min(d.day, monthrange(y, m + 1)[1]))


def assess(profile, *, assessment_at, inventory=None, eu_inventory=None):
    day(assessment_at)
    groups = ('pet', 'journey', 'documents', 'events', 'appointments', 'responsibility')
    if not isinstance(profile, dict) or any(not isinstance(profile.get(k, {}), dict) for k in groups):
        raise ValueError('profile groups must be objects')
    inv = inventory if inventory is not None else load_inventory()
    eu_inv = eu_inventory if eu_inventory is not None else load_eu()
    p, j, d = (profile.get(k, {}) for k in ('pet', 'journey', 'documents'))
    for key in ('origin', 'destination', 'first_entry_member', 'destination_member', 'origin_member',
                'purpose', 'accompaniment', 'transport_mode', 'transit', 'travel_history_branch',
                'rabies_vaccine_origin', 'vaccination_branch', 'titre_branch', 'destination_subdivision'):
        if j.get(key) is not None and not isinstance(j[key], str):
            raise ValueError('journey selections must be strings')
    if p.get('species') is not None and not isinstance(p['species'], str):
        raise ValueError('species must be a string')
    origin, dest, species = j.get('origin'), j.get('destination'), p.get('species')
    gaps = []
    if (origin, dest) not in (('US', 'EU'), ('EU', 'US')): gaps.append('us_eu_direction_only')
    if species not in ('dog', 'cat'): gaps.append('species_unsupported')
    if p.get('service_animal') is not False: gaps.append('ordinary_pet_classification_unconfirmed')
    if j.get('purpose') not in ('relocation', 'holiday') or j.get('ownership_transfer') is not False:
        gaps.append('movement_classification_unconfirmed')
    if type(j.get('pets_per_person')) is not int or j['pets_per_person'] != 1:
        gaps.append('single_pet_scope_unconfirmed')
    if j.get('accompaniment') not in ('owner', 'authorized_person', 'unaccompanied'):
        gaps.append('accompaniment_unknown')
    if j.get('transport_mode') not in ('cabin', 'checked_baggage'):
        gaps.append('independent_cargo_uncompiled')
    if j.get('accompaniment') == 'unaccompanied': gaps.append('unaccompanied_export_classification_uncompiled')
    if j.get('transit') != 'none': gaps.append('transit_uncompiled')
    for key in ('departure_at', 'entry_at'):
        try: day(j.get(key))
        except ValueError: gaps.append(key + '_unknown_or_invalid')
    if not any(x.endswith('_unknown_or_invalid') for x in gaps) and day(j['departure_at']) > day(j['entry_at']):
        gaps.append('departure_after_entry')
    members = {m['member'] for m in eu_inv['members']}
    if dest == 'EU':
        if j.get('first_entry_member') not in members or j.get('destination_member') not in members:
            gaps.append('eu_member_unconfirmed')
        if j.get('owner_moving') is not True: gaps.append('owner_not_moving_separate_classification')
        if j.get('accompaniment') == 'authorized_person' and j.get('authorized_person_written') is not True:
            gaps.append('written_authorization_unconfirmed')
        try:
            delta = abs((day(j.get('owner_entry_at')) - day(j.get('entry_at'))).days)
            if delta > (0 if j.get('accompaniment') == 'owner' else 5): gaps.append('owner_date_relationship_conflict')
        except ValueError: gaps.append('owner_date_relationship_unknown')
    if origin == 'EU' and j.get('origin_member') not in members: gaps.append('eu_origin_member_unconfirmed')
    from packages.engine.handover import assess as assess_handover
    final_handover = assess_handover(profile.get('handover', {}))
    r = dict(final_handover=final_handover, preview_version='0.1.0', dataset_version=inv['dataset_version'], assessment_at=assessment_at,
             assessment_scope='us_eu_evidence_preview', direction=f'{origin}→{dest}' if not 'us_eu_direction_only' in gaps else 'unsupported',
             branch=('eu_' if dest == 'EU' else 'us_') + str(species), status='unsupported',
             classification_resolved=not gaps, candidates=[], excluded=[], recommendations=[],
             booking_confirmed=False, verified_feasible_route_count=0, timeline=[], draft_diagnostics=[],
             entry_point_diagnostics=[], document_checklist=[], evidence=deepcopy(inv['evidence']))
    reasons = list(inv['pending_checks']) + final_handover['reason_codes'] + gaps + ['return_leg_requires_independent_reassessment']
    if gaps:
        r['reason_codes'] = sorted(set(reasons)); return r

    def add(ident, outcome, source, locator):
        r['draft_diagnostics'].append(dict(diagnostic_id=ident, outcome=outcome, enforceable=False,
                                           source_ids=[source], locator=locator))
        if outcome not in ('pass', 'date_window_consistent', 'model_date_consistent', 'not_applicable'):
            reasons.append(ident + '.' + outcome)
    def requirement(ident, field, op, value, anchor, source, locator, unit=None):
        if op == 'on_or_before' and anchor is None:
            actual = get(profile, field)
            try:
                outcome = 'missing' if actual is None else 'pass' if day(actual) <= day(value) else 'fail'
            except ValueError: outcome = 'invalid'
            add(ident, outcome, source, locator)
            return
        if op == 'on_or_after':
            field, anchor, op = anchor, field, 'on_or_before'
        req = dict(field=field, operator=op, value=value)
        if anchor is not None: req['anchor'] = anchor
        if unit: req['unit'] = unit
        add(ident, compare(req, profile)['outcome'], source, locator)
    def event(ident, field, en, zh, deps=()):
        value = get(profile, field)
        try: day(value)
        except ValueError: value = None
        r['timeline'].append(dict(event_id=ident, date=value, label={'en':en, 'zh-CN':zh},
                                  depends_on=list(deps), earliest_date=None, latest_date=None,
                                  date_policy='civil_day_research_estimate', enforceable=False))
    def document(ident, en, zh, issuer, source):
        roles = profile.get('responsibility', {})
        allowed = ('owner', 'authorized_person', 'veterinarian', 'government_vet', 'carrier', 'receiving_authority')
        row = dict(document_id=ident, label={'en':en, 'zh-CN':zh}, issuing_role=issuer,
                   custody_confirmed=False, source_ids=[source])
        for key in ('carrying_role', 'delivery_role', 'receiving_role'):
            row[key] = roles.get(key) if roles.get(key) in allowed else 'pending_arrangement'
        r['document_checklist'].append(row)
    entry, departure = j['entry_at'], j['departure_at']
    if dest == 'EU':
        source = 'us.aphis.eu-france'
        if j['first_entry_member'] != 'FR': reasons.append('us_export_destination_specific_guidance_unread')
        if j['first_entry_member'] != j['destination_member']: reasons.append('eu_onward_movement_local_requirements_pending')
        requirement('eu.microchip', 'pet.microchip_present', 'equals', True, None, source, 'Step 1; scanner compliance pending')
        requirement('eu.identification-before-vaccine', 'events.identification_at', 'on_or_before', None,
                    'events.rabies_vaccination_at', source, 'Step 1: chip scan before vaccine')
        requirement('eu.vaccine-valid-at-entry', 'events.rabies_valid_until', 'on_or_after', None,
                    'journey.entry_at', source, 'Vaccine expiry; actual document expiry pending')
        if j.get('vaccination_branch') == 'primary':
            requirement('eu.primary-age', 'pet.birth_date', 'calendar_age_at_least', 12,
                        'events.rabies_vaccination_at', source, 'Primary vaccination; model II.3', unit='week')
            requirement('eu.primary-protocol-order', 'events.rabies_vaccination_at', 'on_or_before', None,
                        'events.primary_protocol_completed_at', source, 'Primary series completion order')
            try:
                vaccinated = get(profile, 'events.rabies_vaccination_at')
                outcome = 'missing' if vaccinated is None else 'pass' if day(entry) <= calendar_shift(vaccinated, 12) else 'fail'
            except (ValueError, OverflowError): outcome = 'invalid'
            add('eu.us-primary-one-year', outcome, source, 'Step 1: US primary validity limited to one year; civil estimate only')
            wait = get(profile, 'events.manufacturer_immunity_days')
            if type(wait) is not int or wait < 21:
                add('eu.manufacturer-wait', 'missing' if wait is None else 'invalid', source, 'Step 1: manufacturer immunity period')
            else:
                requirement('eu.manufacturer-wait', 'events.primary_protocol_completed_at', 'elapsed_at_least', wait,
                            'journey.departure_at', source, 'Step 1: max(21 days, manufacturer period)')
        else: add('eu.vaccine-continuity', 'booster_continuity_unreviewed', source, 'Step 1: continuity needs full records')
        route = d.get('eu_document_route')
        if route == 'passport_return':
            ps = 'us.aphis.eu-passport'
            requirement('eu.passport-vaccine-record', 'documents.passport_eu_vet_rabies', 'equals', True, None, ps, 'Return passport requires EU-vet vaccine record')
            requirement('eu.passport-us-revaccination', 'documents.revaccinated_in_us', 'equals', False, None, ps, 'US revaccination requires health certificate')
            md = document_diagnostic(profile, eu_inv, scope='intra_eu')
            add('eu.passport-model', md['outcome'], 'eu.law.2026-705', md['locator'])
            reasons.append('eu_passport_return_eligibility_and_titre_history_unreviewed')
            document('eu.passport', 'Existing EU passport (return only)', '既有欧盟护照（仅返程）', 'eu_authorized_vet', ps)
        elif route == 'health_certificate':
            md = document_diagnostic(profile, eu_inv, scope='third_country_entry')
            add('eu.certificate-model', md['outcome'], 'eu.law.2026-705', md['locator'])
            # APHIS specific endorsement cutover is separate from the EU model issue cutoff.
            if d.get('certificate_model') == 'eu.577.ahc':
                requirement('eu.aphis-old-model-endorsement', 'documents.certificate_endorsed_at', 'on_or_before',
                            '2026-09-30', None, source, 'New Health Certificates notice')
            add('eu.issue-to-entry', bounded_days(d.get('certificate_issued_at'), entry, 0, 30), source, 'Step 2: accredited-vet issue validity')
            add('eu.endorsement-to-check', bounded_days(d.get('certificate_endorsed_at'), get(profile, 'appointments.document_check_at'), 0, 10),
                'us.aphis.eu-model-2026', 'Notes (b): endorsement until identity/documentary checks')
            add('eu.endorsement-to-entry', bounded_days(d.get('certificate_endorsed_at'), entry, 0, 10), source, 'Step 3: endorsement within 10 days of arrival')
            requirement('eu.issue-before-endorsement', 'documents.certificate_issued_at', 'on_or_before', None,
                        'documents.certificate_endorsed_at', source, 'Steps 2–3')
            requirement('eu.check-after-entry', 'journey.entry_at', 'on_or_before', None,
                        'appointments.document_check_at', 'us.aphis.eu-model-2026', 'Notes (b): check at designated entry point')
            requirement('eu.endorsement-before-departure', 'documents.certificate_endorsed_at', 'on_or_before', None,
                        'journey.departure_at', source, 'Endorse before export')
            event('certificate.issue', 'documents.certificate_issued_at', 'US accredited vet issue', '美国认可兽医签发')
            event('certificate.endorsement', 'documents.certificate_endorsed_at', 'APHIS endorsement', 'APHIS背书', ('certificate.issue',))
            event('documents.delivery', 'events.document_delivery_at', 'Endorsed print delivery', '背书打印件交付', ('certificate.endorsement',))
            add('eu.delivery-after-endorsement', bounded_days(d.get('certificate_endorsed_at'), get(profile, 'events.document_delivery_at'), 0, 365), source, 'Planning order only')
            add('eu.delivery-before-departure', bounded_days(get(profile, 'events.document_delivery_at'), departure, 0, 365), source, 'Printed certificate must travel with pet')
            document('eu.ahc', 'Printed endorsed EU certificate and declaration', '背书欧盟证书打印件及声明', 'us_accredited_vet_and_aphis', source)
        else: add('eu.document-route', 'missing', source, 'Health certificate or independently checked return passport')
        # Current 2026/636 annex still inaccessible. Never invent a US titre exemption.
        add('eu.titre-branch', 'current_list_and_history_unreviewed', 'us.aphis.eu-model-2026', 'II.3.1: listed origin, transit and return are distinct')
        if j.get('titre_branch') == 'test_required':
            requirement('eu.titre-sample-wait', 'events.rabies_vaccination_at', 'elapsed_at_least', 30,
                        'events.titre_sample_at', 'us.aphis.eu-model-2026', 'II.3.1: primary vaccine to sample')
            requirement('eu.titre-to-issue', 'events.titre_sample_at', 'elapsed_at_least', 90,
                        'documents.certificate_issued_at', 'us.aphis.eu-model-2026', 'II.3.1: sample to issue, not entry')
        if species == 'dog' and any(j.get(k) in ('FI', 'IE', 'MT') for k in ('first_entry_member', 'destination_member')):
            first = j['first_entry_member'] in ('FI', 'IE', 'MT')
            field = 'entry' if first else 'onward_entry'
            try:
                treatment = instant(get(profile, 'events.tapeworm_at'), get(profile, 'events.tapeworm_timezone'))
                target = instant(j.get(field + '_time'), j.get(field + '_timezone'))
                local_date = j.get(field + '_time', '').split('T')[0]
                if local_date != (entry if first else j.get('onward_entry_at')): raise ValueError('arrival date mismatch')
                hours = (target - treatment).total_seconds() / 3600
                outcome = 'date_window_consistent' if 24 <= hours <= 120 else 'date_window_conflict'
            except ValueError: outcome = 'invalid_or_missing'
            add('eu.dog-tapeworm-hours', outcome, 'us.aphis.eu-passport', '24–120 hours; first/onward arrival separate; source conflicts pending')
        reasons.append('eu_travellers_entry_point_current_designation_unconfirmed')
    elif species == 'cat':
        source = 'us.cdc.animals'
        requirement('us.cat-health', 'pet.healthy', 'equals', True, None, source, 'Cats: healthy arrival and inspection')
        add('us.cat-dog-rules', 'not_applicable', source, 'No dog CDC form/age/chip rules applied')
        reasons.append('eu_member_export_and_us_cat_state_carrier_requirements_pending')
    else:
        history = j.get('travel_history_branch')
        hs = 'us.cdc.high-risk-list'
        if j.get('history_complete') is not True or history not in ('only_low_risk_6_months', 'high_risk_in_6_months'):
            add('us.six-month-history', 'missing', hs, 'Complete six-month locations; self-report is not verified evidence')
            reasons.append('us_dog_history_branch_unresolved')
        else:
            conflict = False
            last = j.get('last_high_risk_exit_at')
            if last is not None:
                try:
                    date = day(last)
                    conflict = history == 'only_low_risk_6_months' and calendar_shift(entry, -6) <= date <= day(entry)
                    if date > day(entry): raise ValueError('future history')
                except ValueError:
                    add('us.history-date', 'invalid', hs, 'Last high-risk departure within six civil months'); conflict = True
            if conflict:
                add('us.six-month-history', 'history_conflict', hs, 'Current departure country cannot erase high-risk visits')
            else:
                source = 'us.cdc.low-risk' if history == 'only_low_risk_6_months' else 'us.cdc.us-vaccinated-return' if j.get('rabies_vaccine_origin') == 'US' else 'us.cdc.foreign-high-risk'
                r['branch'] = 'us_dog_' + ('low_risk' if history == 'only_low_risk_6_months' else 'us_vaccinated_high_risk' if j.get('rabies_vaccine_origin') == 'US' else 'foreign_vaccinated_high_risk')
                requirement('us.dog-age', 'pet.birth_date', 'calendar_age_at_least', 6, 'journey.entry_at', source, 'Age on return/entry', unit='month')
                requirement('us.dog-chip', 'pet.microchip_present', 'equals', True, None, source, 'Universal-scanner-readable chip; actual read pending')
                requirement('us.dog-health', 'pet.healthy', 'equals', True, None, source, 'Appears healthy at entry')
                requirement('us.receipt-present', 'documents.receipt_present', 'equals', True, None, source, 'Dog Import Form receipt')
                document('us.receipt', 'CDC dog import receipt', 'CDC犬入境回执', 'importer', source)
                if history == 'only_low_risk_6_months':
                    add('us.receipt-country', 'missing' if not d.get('receipt_departure_member') else 'pass' if d['receipt_departure_member'] == j['origin_member'] else 'country_mismatch', source, 'Receipt departure country must match actual departure')
                    add('us.receipt-six-months', 'missing' if not d.get('receipt_issued_at') else _receipt_window(d.get('receipt_issued_at'), entry), source, 'Six-month civil estimate; printed expiry controls')
                    requirement('us.receipt-not-expired', 'documents.receipt_expires_at', 'on_or_after', None, 'journey.entry_at', source, 'Actual receipt expiry independently checked')
                elif j.get('rabies_vaccine_origin') == 'US':
                    kind = d.get('us_return_document')
                    if kind == 'us_rabies_form':
                        add('us.return-form-order', bounded_days(d.get('us_form_issued_at'), d.get('us_form_endorsed_at'), 0, 365), source, 'Specific form signature before USDA endorsement')
                        requirement('us.return-form-before-exit', 'documents.us_form_endorsed_at', 'on_or_before', None, 'journey.original_us_exit_at', source, 'USDA endorsement before original US departure')
                        requirement('us.return-form-vaccine-valid', 'events.rabies_valid_until', 'on_or_after', None, 'journey.entry_at', source, 'Current vaccine validity; original form content pending')
                    elif kind == 'legacy_export':
                        requirement('us.legacy-export-cutoff', 'documents.us_export_issued_at', 'on_or_before', '2025-07-31', None, source, 'Export certificate replacement cutoff')
                        reasons.append('us_legacy_export_content_database_and_current_vaccine_unreviewed')
                    else: add('us.return-document', 'foreign_high_risk_fallback_required', source, 'Missing valid US proof: use separate foreign-vaccinated requirements, not exemption')
                    add('us.high-risk-receipt-date', bounded_days(d.get('receipt_entry_at'), entry, 0, 0), source, 'Single entry on stated arrival date')
                    document('us.return-form', 'Specific endorsed US rabies form / eligible legacy export', '专用美国免疫背书表／符合条件的旧出口证', 'us_accredited_vet_and_usda', source)
                    reasons.append('us_return_form_microchip_vaccine_protocol_and_port_match_unreviewed')
                elif j.get('rabies_vaccine_origin') == 'foreign':
                    add('us.foreign-high-risk-package', 'acf_and_document_chain_unreviewed', source, 'No low-risk receipt-only exemption; vaccine origin unknown is unresolved')
                    reasons.append('us_foreign_high_risk_acf_titre_quarantine_and_airport_pending')
                    add('us.foreign-form-window', bounded_days(d.get('certificate_issued_at'), entry, 0, 30), source, 'Single-entry form validity from veterinarian signature')
                    requirement('us.foreign-form-order', 'documents.certificate_issued_at', 'on_or_before', None,
                                'documents.certificate_endorsed_at', source, 'Origin official government vet endorsement')
                    requirement('us.foreign-endorsement-before-departure', 'documents.certificate_endorsed_at', 'on_or_before', None,
                                'journey.departure_at', source, 'Form must be endorsed before use')
                    requirement('us.foreign-chip-before-vaccine', 'events.identification_at', 'on_or_before', None,
                                'events.rabies_vaccination_at', source, 'Chip before valid vaccine')
                    requirement('us.foreign-vaccine-valid', 'events.rabies_valid_until', 'on_or_after', None,
                                'journey.entry_at', source, 'No vaccine lapse; full series pending')
                    if j.get('vaccination_branch') == 'primary':
                        requirement('us.foreign-primary-age', 'pet.birth_date', 'calendar_age_at_least', 12,
                                    'events.rabies_vaccination_at', source, 'First vaccine minimum age; manufacturer may require older', unit='week')
                        requirement('us.foreign-primary-wait', 'events.rabies_vaccination_at', 'elapsed_at_least', 28,
                                    'journey.entry_at', source, 'First valid vaccine to entry')
                    else: add('us.foreign-vaccine-continuity', 'unreviewed', source, 'Booster continuity needs full records')
                    if j.get('titre_branch') == 'test_required':
                        requirement('us.foreign-sample-wait', 'events.rabies_vaccination_at', 'elapsed_at_least', 30,
                                    'events.titre_sample_at', source, 'First valid vaccine to sample; full protocol pending')
                        requirement('us.foreign-titre-to-entry', 'events.titre_sample_at', 'elapsed_at_least', 28,
                                    'journey.entry_at', source, 'Sample to entry, not 90-day EU issue wait')
                    else: add('us.foreign-titre-or-quarantine', 'reservation_unconfirmed', source, 'Without valid accepted titre, quarantine reservation required')
                    add('us.high-risk-receipt-date', bounded_days(d.get('receipt_entry_at'), entry, 0, 0), source, 'Single entry on stated arrival date')
                    for key in ('receipt_airport', 'acf_airport'):
                        outcome = 'missing' if not d.get(key) or not j.get('entry_airport') else 'pass' if d[key] == j['entry_airport'] else 'airport_mismatch'
                        add('us.' + key, outcome, source, 'Actual receipt, arrival and ACF reservation airports must match')
                    event('certificate.issue', 'documents.certificate_issued_at', 'Origin veterinarian signs foreign form', '起运兽医签署境外免疫表')
                    event('certificate.endorsement', 'documents.certificate_endorsed_at', 'Origin official government vet endorsement', '起运国官方兽医背书', ('certificate.issue',))
                    document('us.foreign-form', 'Printed signed and endorsed foreign form', '签署并背书境外免疫表打印件', 'origin_vet_and_government_vet', source)
                    document('us.acf', 'Actual ACF reservation and required accepted titre report', '实际设施预约及所需采信抗体报告', 'importer_and_acf', source)
                else:
                    r['branch'] = 'us_dog_high_risk_vaccine_origin_unresolved'
                    add('us.vaccine-origin', 'missing', hs, 'Do not assume unknown vaccine origin is foreign or US')

        reasons.append('eu_member_export_procedure_unreviewed')
    if dest == 'US' and j.get('destination_subdivision') not in ('US-CA', 'US-NY', 'US-TX'):
        reasons.append('us_destination_state_or_territory_uncompiled')
    event('departure', 'journey.departure_at', 'Departure', '出发')
    event('entry', 'journey.entry_at', 'Arrival (inspection not guaranteed)', '抵达（不保证查验完成）', ('departure',))
    r['reason_codes'] = sorted(set(reasons)); return r


def _receipt_window(issue, entry):
    try:
        return 'date_window_consistent' if day(issue) <= day(entry) <= calendar_shift(issue, 6) else 'date_window_conflict'
    except (ValueError, OverflowError): return 'invalid'


def assess_round_trip(first, returning, *, assessment_at, previous_dataset_version=None, inventory=None):
    """Recompute both independent directions on current data; prior result grants nothing."""
    inv = inventory if inventory is not None else load_inventory()
    a = assess(first, assessment_at=assessment_at, inventory=inv)
    b = assess(returning, assessment_at=assessment_at, inventory=inv)
    if {a['direction'], b['direction']} != {'US→EU', 'EU→US'}:
        raise ValueError('round trip needs two opposite US/EU directions')
    if get(first, 'pet.species') != get(returning, 'pet.species'):
        raise ValueError('round trip species mismatch')
    reasons = ['both_legs_reassessed_independently', 'no_outbound_permission_inherited']
    if day(get(returning, 'journey.departure_at')) < day(get(first, 'journey.entry_at')):
        reasons.append('return_before_first_arrival')
    if previous_dataset_version is not None and previous_dataset_version != inv['dataset_version']:
        reasons.append('dataset_changed_reassess_both_legs')
    return dict(status='unsupported', legs=[a, b], reason_codes=reasons, booking_confirmed=False,
                verified_feasible_route_count=0)


def checklist(result, *, language='zh-CN'):
    if language not in ('en', 'zh-CN'): raise ValueError('unsupported language')
    lines = ['PetWaymark | ' + result['direction'],
             '研究预览：未覆盖、未订舱；返程须独立重评。' if language == 'zh-CN' else
             'Research preview: unsupported, no booking; return needs independent reassessment.',
             result['dataset_version'], ', '.join(result['reason_codes'])]
    lines.append('final_pickup | ' + result['final_handover']['pickup_outcome'])
    lines.append('overnight_care | ' + result['final_handover']['overnight_outcome'] + ' | custody_confirmed=false')
    for row in result['timeline']: lines.append(row['label'][language] + ' | ' + str(row['date']))
    for row in result['draft_diagnostics']: lines.append(row['diagnostic_id'] + ' | ' + row['outcome'])
    for row in result['document_checklist']:
        lines.append(row['label'][language] + ' | ' + ' / '.join(row[k] for k in ('carrying_role', 'delivery_role', 'receiving_role')) + ' | custody_confirmed=false')
    for row in result['evidence']: lines.append(row['source_id'] + ' | ' + row['url'] + ' | ' + row['accessed_at'])
    return '\n'.join(lines) + '\n'
