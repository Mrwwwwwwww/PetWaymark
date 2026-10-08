"""Independent CN outbound research timelines; never legal or booking approval."""
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from packages.engine.evaluate import compare, day, get
from packages.engine.eu import document_diagnostic, identification_diagnostic, load_inventory as load_eu
from packages.engine.io import ROOT
from scripts.validate_data import read_json


def load_inventory(root=ROOT):
    return read_json(root / 'data/coverage/cn-outbound.json')


def instant(value, zone):
    """Offset plus IANA zone disambiguates folds; roundtrip rejects spring gaps."""
    if not isinstance(value,str) or 'T' not in value or not isinstance(zone,str):
        raise ValueError('timestamp needs explicit offset and IANA timezone')
    try:
        parsed=datetime.fromisoformat(value)
        if parsed.tzinfo is None:raise ValueError('missing offset')
        local=parsed.astimezone(ZoneInfo(zone))
        if local.replace(tzinfo=None)!=parsed.replace(tzinfo=None) or local.utcoffset()!=parsed.utcoffset():
            raise ValueError('invalid local time or offset')
        return parsed.astimezone(timezone.utc)
    except (TypeError,ZoneInfoNotFoundError) as exc:raise ValueError('invalid timezone') from exc


def bounded_days(start,end,minimum,maximum):
    if start is None or end is None:return 'missing'
    try:
        delta=(day(end)-day(start)).days
        return 'date_window_consistent' if minimum<=delta<=maximum else 'date_window_conflict'
    except ValueError:return 'invalid'


def assess(profile, *, assessment_at, inventory=None, eu_inventory=None):
    day(assessment_at)
    if not isinstance(profile,dict) or any(not isinstance(profile.get(k,{}),dict)
            for k in ('pet','journey','events','documents','appointments','responsibility')):
        raise ValueError('profile groups must be objects')
    inv=inventory if inventory is not None else load_inventory()
    eu_inv=eu_inventory if eu_inventory is not None else load_eu()
    p,j=profile.get('pet',{}),profile.get('journey',{})
    for key in ('origin','destination','first_entry_member','destination_member','entry_airport',
                'purpose','accompaniment','transport_mode','travel_history_branch','rabies_vaccine_origin',
                'vaccination_branch','titre_branch'):
        if j.get(key) is not None and not isinstance(j[key],str):raise ValueError('journey selections must be strings')
    if p.get('species') is not None and not isinstance(p['species'],str):raise ValueError('species must be a string')
    dest,species=j.get('destination'),p.get('species');gaps=[]
    if j.get('origin')!='CN' or dest not in ('US','EU'):gaps.append('cn_outbound_direction_only')
    if species not in ('dog','cat'):gaps.append('species_unsupported')
    if p.get('service_animal') is not False:gaps.append('ordinary_pet_classification_unconfirmed')
    if j.get('purpose') not in ('relocation','holiday') or j.get('ownership_transfer') is not False:gaps.append('movement_classification_unconfirmed')
    if type(j.get('pets_per_person')) is not int or j.get('pets_per_person')!=1:gaps.append('single_pet_scope_unconfirmed')
    if j.get('accompaniment') not in ('owner','authorized_person','unaccompanied'):gaps.append('accompaniment_unknown')
    if j.get('transport_mode') not in ('cabin','checked_baggage','manifest_cargo'):gaps.append('air_transport_scope_unconfirmed')
    for key in ('departure_at','entry_at'):
        try:day(j.get(key))
        except ValueError:gaps.append(key+'_unknown_or_invalid')
    if not gaps and day(j['departure_at'])>day(j['entry_at']):gaps.append('departure_after_entry')
    if dest=='EU':
        members={m['member'] for m in eu_inv['members']}
        if j.get('first_entry_member') not in members or j.get('destination_member') not in members:gaps.append('first_entry_or_destination_member_unconfirmed')
        if j.get('owner_moving') is not True:gaps.append('owner_not_moving_separate_classification')
        if j.get('accompaniment')=='unaccompanied':gaps.append('eu_unaccompanied_classification_uncovered')
        if j.get('accompaniment')=='authorized_person' and j.get('authorized_person_written') is not True:gaps.append('written_authorization_unconfirmed')
        try:
            delta=abs((day(j.get('entry_at'))-day(j.get('owner_entry_at'))).days)
            if delta>(0 if j.get('accompaniment')=='owner' else 5):gaps.append('owner_date_relationship_conflict')
        except ValueError:gaps.append('owner_date_relationship_unknown')
    if dest=='US' and species=='dog':
        if j.get('travel_history_branch')!='high_risk_in_6_months':gaps.append('cn_dog_high_risk_history_unconfirmed')
        if j.get('rabies_vaccine_origin')!='foreign':gaps.append('us_vaccinated_or_unknown_dog_branch_uncovered')
    branch=(('us_foreign_vaccinated_high_risk_dog' if species=='dog' else 'us_cat') if dest=='US' else 'eu_'+str(species))
    result=dict(preview_version='0.1.0',dataset_version=inv['dataset_version'],assessment_at=assessment_at,
        assessment_scope='cn_outbound_evidence_preview',direction='CN→'+dest if dest in ('US','EU') else 'unsupported',branch=branch,
        status='unsupported',classification_resolved=not gaps,candidates=[],excluded=[],recommendations=[],booking_confirmed=False,
        verified_feasible_route_count=0,timeline=[],draft_diagnostics=[],entry_point_diagnostics=[],document_checklist=[],evidence=deepcopy(inv['evidence']))
    reasons=list(inv['pending_checks'])+gaps
    if gaps:result['reason_codes']=sorted(set(reasons));return result
    def add(ident,outcome,sources,locator):
        result['draft_diagnostics'].append(dict(diagnostic_id=ident,outcome=outcome,enforceable=False,source_ids=sources,locator=locator))
        if outcome not in ('pass','date_window_consistent','model_date_consistent','not_applicable'):reasons.append(ident+'.'+outcome)
    def constraint(ident,field,op,value,anchor,source,locator,unit=None):
        req=dict(field=field,operator=op,value=value,anchor=anchor)
        if unit:req['unit']=unit
        add(ident,compare(req,profile)['outcome'],[source],locator)
    def event(ident,field,en,zh,depends=(),earliest=None,latest=None,source=None):
        value=get(profile,field)
        if value is not None:
            try:day(value)
            except ValueError:value=None;reasons.append(ident+'.invalid_date')
        result['timeline'].append(dict(event_id=ident,label={'en':en,'zh-CN':zh},date=value,depends_on=list(depends),
            earliest_date=earliest,latest_date=latest,date_policy='civil_day_research_estimate',source_ids=[source] if source else [],enforceable=False))
    def shift(value,n):
        try:return (day(value)+timedelta(days=n)).isoformat()
        except (ValueError,OverflowError):return None
    departure,entry=j['departure_at'],j['entry_at']
    event('cn.export_application','events.export_application_at','Apply to origin customs','向属地海关申请',source='cn.gacc.pet-export-portal')
    event('cn.export_inspection','events.export_inspection_at','Attend agreed origin inspection','按约定参加属地查验',['cn.export_application'],source='cn.luohu.pet-export')
    event('cn.export_issue','documents.origin_certificate_issued_at','Origin export certificate issue','中国出口证签发',['cn.export_inspection'],source='cn.samr.carried-export')
    constraint('cn.application-before-inspection','events.export_application_at','on_or_before',None,'events.export_inspection_at','cn.gacc.pet-export-portal','Project planning order; local schedule unverified')
    constraint('cn.inspection-before-issue','events.export_inspection_at','on_or_before',None,'documents.origin_certificate_issued_at','cn.luohu.pet-export','Local inspection then export document; current scope pending')
    docs=[('cn.export_certificate','Origin export health certificate','中国出口动物卫生证书','origin_customs','cn.gacc.pet-export-portal')]
    if dest=='EU' or species=='dog':
        source='eu.ec.non-eu' if dest=='EU' else 'us.cdc.foreign-high-risk'
        if dest=='EU':
            ident=identification_diagnostic(profile)
            add(ident['diagnostic_id'],ident['outcome'],['eu.law.2026-131-readable'],'Article 13: transponder or pre-2011 readable tattoo; scanner specification pending')
        else:
            add('us.microchip',compare(dict(field='pet.microchip_present',operator='equals',value=True),profile)['outcome'],[source],'Universal-scanner-readable chip; no chip number collected')
        event('identification','events.identification_at','Identification/read','标识／读取',source=source)
        event('rabies.vaccine','events.rabies_vaccination_at','Rabies vaccine','狂犬病接种',['identification'],source=source)
        constraint('identification.before-vaccine','events.identification_at','on_or_before',None,'events.rabies_vaccination_at',source,'Identification before valid vaccination')
        if j.get('vaccination_branch')=='primary':constraint('vaccination.minimum-age','pet.birth_date','calendar_age_at_least',12,'events.rabies_vaccination_at',source,'Primary vaccination minimum age',unit='week')
        if j.get('vaccination_branch')!='primary':add('rabies.protocol','booster_or_unknown_continuity_unreviewed',[source],'Valid vaccine series; no inference from one booster date')
        elif dest=='EU':
            event('rabies.protocol','events.primary_protocol_completed_at','Primary protocol completion','初次程序完成',['rabies.vaccine'],source=source)
            constraint('rabies.protocol-order','events.rabies_vaccination_at','on_or_before',None,'events.primary_protocol_completed_at',source,'Completion follows vaccination')
            constraint('rabies.protocol-wait','events.primary_protocol_completed_at','elapsed_at_least',21,'journey.departure_at',source,'Primary completion to movement')
        else:constraint('rabies.primary-wait','events.rabies_vaccination_at','elapsed_at_least',28,'journey.entry_at',source,'First vaccine to entry')
        if dest=='EU' or j.get('titre_branch')=='test_required':
            if dest=='EU' and j.get('titre_branch')!='test_required':add('eu.titre.exception','exception_unreviewed',['eu.law.2026-636'],'List/return/transit exceptions not compiled')
            else:
                event('titre.sample','events.titre_sample_at','Antibody sample collection','抗体采血',['rabies.vaccine'],earliest=shift(get(profile,'events.rabies_vaccination_at'),30) if j.get('vaccination_branch')=='primary' else None,latest=shift(get(profile,'documents.certificate_issued_at') if dest=='EU' else entry,-90 if dest=='EU' else -28),source=source)
                if j.get('vaccination_branch')=='primary':constraint('titre.sample-after-primary','events.rabies_vaccination_at','elapsed_at_least',30,'events.titre_sample_at',source,'Primary vaccine to sample; continuity exceptions pending')
                constraint('titre.wait','events.titre_sample_at','elapsed_at_least',90 if dest=='EU' else 28,'documents.certificate_issued_at' if dest=='EU' else 'journey.entry_at',source,'Sample to ISSUE (EU) / ENTRY (US)')
                docs.append(('titre.report','Designated-lab result and attached report','指定实验室结果及报告附件','designated_lab',source));reasons.append('titre_result_lab_and_vaccine_continuity_unreviewed')
        elif j.get('titre_branch')=='quarantine':add('us.titre.quarantine','quarantine_reservation_unconfirmed',[source],'No valid titer: 28-day quarantine reservation; no automatic release')
        else:add('us.titre.branch','missing',[source],'Valid titer or quarantine branch required')
    if dest=='US' and species=='dog':
        source='us.cdc.foreign-high-risk'
        constraint('us.dog.minimum-age','pet.birth_date','calendar_age_at_least',6,'journey.entry_at',source,'Age at entry',unit='month')
        event('certificate.issue','documents.certificate_issued_at','Veterinarian signs foreign vaccine form','兽医签署境外免疫表',['rabies.vaccine'],earliest=shift(departure,-30),latest=departure,source=source)
        add('us.form.departure-window',bounded_days(get(profile,'documents.certificate_issued_at'),departure,0,30),[source],'Completion before travel')
        add('us.form.entry-window',bounded_days(get(profile,'documents.certificate_issued_at'),entry,0,30),[source],'30-day single-entry validity after veterinarian signature')
        event('certificate.endorsement','documents.certificate_endorsed_at','Official government veterinarian endorsement','政府官方兽医背书',['certificate.issue'],latest=departure,source=source)
        constraint('us.form.endorsement-order','documents.certificate_issued_at','on_or_before',None,'documents.certificate_endorsed_at',source,'Signature before endorsement')
        constraint('us.form.endorsement-before-travel','documents.certificate_endorsed_at','on_or_before',None,'journey.departure_at',source,'Endorse before use')
        docs += [('us.foreign_form','Printed signed and endorsed foreign vaccination form','签署并背书的境外免疫表打印件','veterinarian_and_government_vet',source),('us.import_receipt','CDC import receipt (arrival date and airport)','CDC入境表回执（日期及机场）','importer',source),('us.acf_reservation','ACF reservation confirmation','设施预约确认','importer_and_acf',source)]
        airport=j.get('entry_airport');mode=j['transport_mode']
        outcome='missing' if not airport else 'listed_pending_confirmation' if airport in inv['us_acf_airports'] else 'not_in_read_list'
        if airport=='SEA' and mode!='manifest_cargo':outcome='listed_product_conflict'
        result['entry_point_diagnostics'].append(dict(outcome=outcome,source_ids=['us.cdc.acf-list'],enforceable=False));reasons.append('us_entry_point.'+outcome)
        if airport=='LAX':reasons.append('lax_non_cargo_transfer_and_clearance_pending')
        for key in ('receipt_airport','acf_airport'):
            value=get(profile,'documents.'+key)
            add('us.'+key,'missing' if not value or not airport else 'pass' if value==airport else 'airport_mismatch',[source],'Arrival / receipt / reserved facility airport must match')
        add('us.receipt.date',bounded_days(get(profile,'documents.receipt_entry_at'),entry,0,0),[source],'Receipt arrival date, single entry')
        reasons.append('us_acf_services_release_and_onward_transfer_unconfirmed')
    elif dest=='US':
        add('us.cat.cdc','not_applicable',['us.cdc.animals'],'CDC dog form/titer/ACF chain does not apply to cats')
        reasons.append('us_cat_arrival_health_inspection_and_state_rules_pending')
        result['entry_point_diagnostics'].append(dict(outcome='cat_facility_requirements_unreviewed',source_ids=['us.cdc.animals'],enforceable=False))
    else:
        source='eu.law.2026-131-readable';route=get(profile,'documents.issuer_route')
        anchor='documents.certificate_issued_at' if route=='official_vet' else 'documents.certificate_endorsed_at' if route=='authorized_then_endorsed' else None
        event('certificate.issue','documents.certificate_issued_at','Animal health certificate issue','动物卫生证书签发',['titre.sample'] if j.get('titre_branch')=='test_required' else ['rabies.vaccine'],earliest=max(filter(None,[shift(get(profile,'events.titre_sample_at'),90),shift(entry,-10) if route=='official_vet' else None]),default=None),latest=entry,source=source)
        event('certificate.endorsement','documents.certificate_endorsed_at','Authority endorsement if authorised issuer','授权签发时由主管机关背书',['certificate.issue'],earliest=shift(entry,-10) if route=='authorized_then_endorsed' else None,latest=entry,source=source)
        add('eu.certificate.entry-window',bounded_days(get(profile,anchor),entry,0,10) if anchor else 'issuer_route_unconfirmed',[source],'Article 19(b): official issue OR authorised issue subsequently endorsed → entry')
        add('eu.certificate.check-window',bounded_days(get(profile,anchor),get(profile,'appointments.document_check_at'),0,10) if anchor else 'issuer_route_unconfirmed',['eu.ec.non-eu'],'Documentary/identity checks; sea extension not implemented')
        constraint('eu.check-after-entry','journey.entry_at','on_or_before',None,'appointments.document_check_at','eu.ec.non-eu','Entry then documentary checks')
        if anchor=='documents.certificate_endorsed_at':constraint('eu.certificate.endorsement-order','documents.certificate_issued_at','on_or_before',None,anchor,source,'Article 19(a)')
        add('eu.certificate.model',document_diagnostic(profile,eu_inv,scope='third_country_entry')['outcome'],['eu.law.2026-705'],'Model issue and recognition transitions only')
        docs += [('eu.ahc','Animal health certificate plus certified vaccination attachments','动物卫生证书及免疫认证附件','official_or_authorized_vet_and_authority',source),('eu.declaration','Non-commercial declaration and written authorisation if needed','非商业声明及所需书面授权','owner_or_authorized_person',source)]
        listed=any(e['airport']==j.get('entry_airport') and e['member']==j['first_entry_member'] for e in inv['eu_entry_points'])
        outcome='listed_pending_confirmation' if listed else 'entry_point_unreviewed'
        result['entry_point_diagnostics'].append(dict(outcome=outcome,source_ids=['eu.nvwa.entry-points'] if listed else ['eu.ec.entry-points-attempt'],enforceable=False));reasons.append('eu_entry_point.'+outcome)
        if j['first_entry_member']!=j['destination_member']:reasons.append('eu_onward_destination_overlay_unreviewed')
        if species=='dog' and ({j['first_entry_member'],j['destination_member']} & {'FI','IE','MT'}):
            protected_first=j['first_entry_member'] in ('FI','IE','MT')
            start=get(profile,'events.tapeworm_at');end=j.get('entry_time' if protected_first else 'onward_entry_time')
            end_zone=j.get('entry_timezone' if protected_first else 'onward_entry_timezone')
            try:
                if start is None or end is None:outcome='missing'
                else:
                    hours=(instant(end,end_zone)-instant(start,get(profile,'events.tapeworm_timezone'))).total_seconds()/3600
                    outcome='date_window_consistent' if 24<=hours<=120 else 'date_window_conflict'
                    if protected_first and end[:10]!=entry:outcome='invalid'
            except ValueError:outcome='invalid'
            add('eu.dog.tapeworm-hours',outcome,[source],'Article 14(d); UTC hours with explicit offsets and IANA zones')
            reasons.append('tapeworm_product_certification_and_onward_zone_entry_unreviewed')
    event('entry','journey.entry_at','Entry and official checks','入境及官方检查',['certificate.issue'] if dest=='EU' or species=='dog' else [],source='eu.ec.non-eu' if dest=='EU' else 'us.cdc.animals')
    event('documents.delivery','events.document_delivery_at','Arrange document handover before departure','安排出发前文件交付',['cn.export_issue'],latest=departure)
    add('documents.delivery-before-departure',bounded_days(get(profile,'events.document_delivery_at'),departure,0,36500),['cn.gacc.pet-export-portal'],'Project planning check, not statutory deadline')
    constraint('documents.delivery-after-origin-issue','documents.origin_certificate_issued_at','on_or_before',None,'events.document_delivery_at','cn.samr.carried-export','Project dependency: origin document exists before delivery')
    if dest=='EU' or species=='dog':constraint('documents.delivery-after-issue','documents.certificate_issued_at','on_or_before',None,'events.document_delivery_at','eu.law.2026-131-readable' if dest=='EU' else 'us.cdc.foreign-high-risk','Project dependency: document exists before delivery')
    if (dest=='US' and species=='dog') or get(profile,'documents.issuer_route')=='authorized_then_endorsed':
        constraint('documents.delivery-after-endorsement','documents.certificate_endorsed_at','on_or_before',None,'events.document_delivery_at','us.cdc.foreign-high-risk' if dest=='US' else 'eu.law.2026-131-readable','Project dependency: endorsed document before delivery')
    proposed=get(profile,'appointments.certificate_at')
    if proposed is not None:
        out=bounded_days(proposed,entry,0,10 if dest=='EU' else 30) if dest=='EU' or species=='dog' else 'window_unreviewed'
        add('appointment.certificate-window',out,['eu.law.2026-131-readable'] if dest=='EU' else ['us.cdc.foreign-high-risk'] if species=='dog' else ['us.cdc.animals'],'Proposed final issue/endorsement appointment, not scheduling')
        if dest=='EU' and j.get('titre_branch')=='test_required':add('appointment.sample-wait',bounded_days(get(profile,'events.titre_sample_at'),proposed,90,36500),['eu.ec.non-eu'],'Proposed appointment cannot bypass sample-to-issue wait')
    allowed={'owner','authorized_person','origin_customs','government_vet','veterinarian','importer','carrier','receiving_authority'};roles=profile.get('responsibility',{})
    for ident,en,zh,issuer,source in docs:
        result['document_checklist'].append(dict(document_id=ident,label={'en':en,'zh-CN':zh},issuing_role=issuer,
            **{key:roles[key] if isinstance(roles.get(key),str) and roles[key] in allowed else 'pending_arrangement' for key in ('carrying_role','delivery_role','receiving_role')},custody_confirmed=False,source_ids=[source]))
    reasons += ['original_document_custody_and_delivery_unconfirmed','transport_acceptance_and_transit_unverified','document_full_content_and_validity_unreviewed']
    result['reason_codes']=sorted(set(reasons));return result


def checklist(result, *, language='zh-CN'):
    if language not in ('en','zh-CN'):raise ValueError('unsupported language')
    lines=['中国出境文件链研究预览 — 未订舱／未接单' if language=='zh-CN' else 'CN outbound document research preview — no booking or order',
        result['direction']+' | '+result['branch']+' | '+result['status']+' | '+result['dataset_version'],', '.join(result['reason_codes']),
        '日期诊断不证明文件有效；日级估算不是小时窗口，角色自报不证明原件已交付。' if language=='zh-CN' else 'Dates do not prove validity; civil-day estimates are not hour windows; reported roles do not prove delivery.']
    for row in result['timeline']:lines.append(row['event_id']+' | '+row['label'][language]+' | '+str(row['date'])+' | '+str(row['earliest_date'])+' … '+str(row['latest_date'])+' | '+', '.join(row['depends_on']))
    for row in result['draft_diagnostics']:lines.append(row['diagnostic_id']+' | '+row['outcome']+' | '+', '.join(row['source_ids'])+' | '+row['locator'])
    for row in result['entry_point_diagnostics']:lines.append(row['outcome']+' | '+', '.join(row['source_ids']))
    for row in result['document_checklist']:lines.append(row['label'][language]+' | '+row['issuing_role']+' | '+row['carrying_role']+' | '+row['delivery_role']+' | '+row['receiving_role'])
    for row in result['evidence']:lines.append(row['source_id']+' | '+row['url']+' | '+row['status']+' | '+row['locator']+' | '+row['summary'][language])
    return '\n'.join(lines)+'\n'
