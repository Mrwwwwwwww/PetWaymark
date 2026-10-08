"""Independent US/EU→CN carried-entry research; no inferred reverse approval."""
from packages.engine.emergency import checklist as emergency_checklist

from calendar import monthrange
from copy import deepcopy
from datetime import date
import math
from packages.engine.evaluate import compare, day, get
from packages.engine.outbound import bounded_days
from packages.engine.planning import costs, load_directory
from packages.engine.io import ROOT
from scripts.validate_data import read_json


def load_inventory(root=ROOT):
    return read_json(root / 'data/coverage/cn-inbound.json')


def sample_year(sample, entry):
    if sample is None or entry is None:return 'missing'
    try:
        start,end=day(sample),day(entry)
        anniversary=date(start.year+1,start.month,min(start.day,monthrange(start.year+1,start.month)[1]))
        return 'date_window_consistent' if start<=end<=anniversary else 'date_window_conflict'
    except (ValueError,OverflowError):return 'invalid'


def assess(profile, *, assessment_at, inventory=None, directory=None):
    day(assessment_at)
    groups=('pet','journey','documents','events','responsibility','cost_quotes')
    if not isinstance(profile,dict) or any(not isinstance(profile.get(k,{}),dict) for k in groups):
        raise ValueError('profile groups must be objects')
    inv=inventory if inventory is not None else load_inventory()
    p,j=profile.get('pet',{}),profile.get('journey',{})
    for key in ('origin','destination','origin_member','origin_subdivision','purpose','accompaniment','transport_mode','cn_entry_branch','transit','entry_airport'):
        if j.get(key) is not None and not isinstance(j[key],str):raise ValueError('journey selections must be strings')
    origin,species=j.get('origin'),p.get('species');gaps=[]
    if origin not in ('US','EU') or j.get('destination')!='CN':gaps.append('us_eu_to_cn_only')
    if species not in ('dog','cat'):gaps.append('species_unsupported')
    if p.get('service_animal') is not False:gaps.append('service_animal_separate_review')
    if j.get('purpose') not in ('relocation','holiday') or j.get('ownership_transfer') is not False:gaps.append('movement_classification_unknown')
    if type(j.get('pets_per_person')) is not int or j.get('pets_per_person')!=1:gaps.append('single_carried_pet_scope_conflict')
    if j.get('accompaniment') not in ('owner','authorized_person'):gaps.append('independent_cargo_not_carried_entry')
    if j.get('transport_mode') not in ('cabin','checked_baggage'):gaps.append('cargo_product_scope_unreviewed')
    if j.get('transit')!='none':gaps.append('transit_requirements_uncovered')
    for key in ('departure_at','entry_at'):
        try:day(j.get(key))
        except ValueError:gaps.append(key+'_unknown_or_invalid')
    if not any(x.endswith('unknown_or_invalid') for x in gaps) and day(j['departure_at'])>day(j['entry_at']):
        gaps.append('departure_after_entry')
    origin_source=inv['eu_origin_sources'].get(j.get('origin_member')) if origin=='EU' else 'us.aphis.cn-entry'
    if origin=='EU' and origin_source is None:gaps.append('eu_origin_member_export_uncovered')
    # Hawaii/Guam exemptions and other territories require their own official chain.
    if origin=='US' and j.get('origin_subdivision') not in ('US-CA','US-NY','US-TX'):
        gaps.append('us_origin_subdivision_or_exemption_unreviewed')
    r=dict(preview_version='0.1.0',dataset_version=inv['dataset_version'],assessment_at=assessment_at,
        assessment_scope='cn_inbound_evidence_preview',direction=str(origin)+'→CN',branch=str(origin).lower()+'_'+str(species),
        status='unsupported',classification_resolved=not gaps,candidates=[],excluded=[],recommendations=[],
        booking_confirmed=False,verified_feasible_route_count=0,timeline=[],draft_diagnostics=[],entry_point_diagnostics=[],
        document_checklist=[],evidence=deepcopy(inv['evidence']),costs=costs(profile.get('cost_quotes'),assessment_at=assessment_at),
        provider_directory=deepcopy(directory if directory is not None else load_directory()))
    reasons=list(inv['pending_checks'])+gaps
    if gaps:r['reason_codes']=sorted(set(reasons));return r
    def add(ident,outcome,sources,locator):
        r['draft_diagnostics'].append(dict(diagnostic_id=ident,outcome=outcome,enforceable=False,source_ids=sources,locator=locator))
        if outcome not in ('pass','date_window_consistent'):reasons.append(ident+'.'+outcome)
    def check(ident,field,op,value=None,anchor=None,source='cn.gacc.2019-5'):
        req=dict(field=field,operator=op,value=value)
        if anchor:req['anchor']=anchor
        add(ident,compare(req,profile)['outcome'],[source],field+' / '+str(anchor))
    def event(ident,field,en,zh,depends=()):
        value=get(profile,field)
        if value is not None:
            try:day(value)
            except ValueError:value=None;reasons.append(ident+'.invalid_date')
        r['timeline'].append(dict(event_id=ident,label={'en':en,'zh-CN':zh},date=value,depends_on=list(depends),earliest_date=None,latest_date=None,enforceable=False,date_policy='civil_day_research_estimate',source_ids=[origin_source]))
    for ident,field in [('cn.health-certificate','documents.health_certificate_present'),('cn.rabies-certificate','documents.rabies_certificate_present'),('cn.microchip','pet.microchip_present'),('cn.chip-readability','documents.chip_readable')]:
        check(ident,field,'equals',True)
    check('cn.rabies.valid-at-entry','journey.entry_at','on_or_before',anchor='events.rabies_valid_until')
    event('rabies.first','events.rabies_first_at','First rabies vaccination record','第一次狂犬病接种记录')
    event('rabies.second','events.rabies_second_at','Second rabies vaccination record','第二次狂犬病接种记录',['rabies.first'])
    branch=j.get('cn_entry_branch')
    if branch=='non_designated_titre':
        event('titre.sample','events.titre_sample_at','Antibody sample (no EU 90-day wait inferred)','抗体采血（不套欧盟90日等待）',['rabies.second'])
        if origin=='US':
            reasons.append('two_vaccination_records_and_complete_protocol_unreviewed')
            check('us.cn.rabies.record-order','events.rabies_first_at','on_or_before',anchor='events.rabies_second_at',source=origin_source)
            check('us.cn.rabies.before-entry','events.rabies_second_at','on_or_before',anchor='journey.entry_at',source=origin_source)
            check('us.cn.sample-after-second','events.rabies_second_at','on_or_before',anchor='events.titre_sample_at',source=origin_source)
            add('us.cn.sample-validity',sample_year(get(profile,'events.titre_sample_at'),j['entry_at']),[origin_source],'Sampling to entry: calendar year estimate; boundary interpretation needs review')
        else:reasons.append('eu_cn_titre_sampling_validity_and_vaccine_protocol_unreviewed')
        t=get(profile,'documents.titre_iu_ml')
        outcome=('missing' if t is None else 'invalid' if type(t) not in (int,float) or not math.isfinite(t) or t<0 else
                 'threshold_conflict_pending_clarification' if t==0.5 else 'pass' if t>0.5 else 'fail')
        add('cn.titre.threshold',outcome,['cn.gacc.2019-5']+(['us.aphis.cn-entry','us.aphis.cn-dog-model'] if origin=='US' and species=='dog' else []),'GACC above 0.5 wording; APHIS page at least 0.5 vs dog model greater than 0.5')
        check('cn.lab.acceptance-reported','documents.lab_acceptance','equals',True)
        reasons.append('reported_lab_acceptance_not_current_official_list_verification')
        r['entry_point_diagnostics'].append(dict(outcome='titre_branch_not_quarantine_exemption_approval',enforceable=False,source_ids=['cn.gacc.2019-5']))
    elif branch=='quarantine':
        add('cn.quarantine','facility_port_and_30_day_release_unconfirmed',['cn.gacc.2019-5'],'30-day quarantine; current designated facility list and actual release pending')
        r['entry_point_diagnostics'].append(dict(outcome='quarantine_port_current_facility_unverified',enforceable=False,source_ids=['cn.gacc.2019-5']))
    elif branch=='designated_origin':add('cn.designated-origin','current_origin_list_and_exemptions_unreviewed',['cn.gacc.2019-5'],'No EU-wide or US-wide designation inferred')
    else:add('cn.entry-branch','missing',['cn.gacc.2019-5'],'Choose research branch; never infer from country alone')
    event('clinical.exam','events.clinical_exam_at','Clinical examination by certifying vet','签证兽医临床检查')
    event('certificate.issue','documents.certificate_issued_at','Destination-specific export certificate issue','目的地专用出口检疫证签发',['clinical.exam'])
    event('certificate.endorsement','documents.certificate_endorsed_at','Competent authority endorsement / official certification','主管机关背书／官方认证',['certificate.issue'])
    event('document.delivery','events.document_delivery_at','Deliver originals / accepted print to carrying person','原件／认可打印件交给携带人',['certificate.endorsement'])
    event('departure','journey.departure_at','Departure','出发',['document.delivery'])
    event('entry','journey.entry_at','CN declaration, document and live-animal inspection','中国申报、文件及现场动物检疫',['departure'])
    for ident,start,end in [('exam-before-issue','events.clinical_exam_at','documents.certificate_issued_at'),('issue-before-endorsement','documents.certificate_issued_at','documents.certificate_endorsed_at'),('endorsement-before-delivery','documents.certificate_endorsed_at','events.document_delivery_at'),('delivery-before-departure','events.document_delivery_at','journey.departure_at')]:
        check('chain.'+ident,start,'on_or_before',anchor=end,source=origin_source)
    if origin=='US':
        add('us.cn.issue-window',bounded_days(get(profile,'documents.certificate_issued_at'),j['entry_at'],0,14),[origin_source],'Vet issue to CN ARRIVAL, not endorsement; no reset')
        for ident,field in [('vehcs','documents.vehcs_endorsed'),('identity','documents.traveler_identity_matches'),('one-per-certificate','documents.one_pet_per_certificate')]:
            check('us.cn.'+ident,field,'equals',True,source=origin_source)
        expected='us.cn.'+species+'.2026'
        add('us.cn.model','named_model_content_pending_review' if get(profile,'documents.certificate_model')==expected else 'model_missing_or_mismatch',['us.aphis.cn-'+species+'-model'],'Species-specific January 2026 model; cat PDF unavailable')
        if species=='dog':reasons.append('cn_local_dog_registration_requirements_unreviewed')
    else:add('eu.cn.export','member_destination_certificate_and_official_signing_route_unreviewed',[origin_source],'EU passport is not a substitute for CN official export certificate; no EU inbound ten-day window')
    doc_specs=[('export_certificate','Official export health certificate / accepted US VEHCS print','官方出口检疫证／认可的美国VEHCS打印件'),('rabies_certificate','Original current rabies certificate and copies','现行免疫证原件及复印件')]
    if branch=='non_designated_titre':doc_specs.append(('titre_report','Original accepted-lab report and copies','采信实验室报告原件及复印件'))
    if origin=='US':doc_specs += [('traveler_copy','Traveler passport copy (do not upload)','携带人护照复印件（勿上传）'),('pet_photo','Pet photo print and copy','宠物照片打印件及复印件')]
    for ident,en,zh in doc_specs:
        roles=profile.get('responsibility',{})
        allowed=('owner','authorized_person','veterinarian','government_vet','carrier','receiving_authority')
        r['document_checklist'].append(dict(document_id=ident,label={'en':en,'zh-CN':zh},issuing_role='veterinarian_and_origin_authority' if ident=='export_certificate' else 'issuer_pending_confirmation',carrying_role=roles.get('carrying_role') if roles.get('carrying_role') in allowed else 'pending_arrangement',delivery_role=roles.get('delivery_role') if roles.get('delivery_role') in allowed else 'pending_arrangement',receiving_role=roles.get('receiving_role') if roles.get('receiving_role') in allowed else 'pending_arrangement',custody_confirmed=False,source_ids=[origin_source,'cn.gacc.2019-5']))
    r['reason_codes']=sorted(set(reasons));return r


def checklist(result, *, language='zh-CN'):
    if language not in ('en','zh-CN'):raise ValueError('unsupported language')
    zh=language=='zh-CN'
    lines=['PetWaymark | '+result['direction'], '研究预览：未覆盖、未订舱；已验证可行路线0。' if zh else 'Research preview: unsupported, no booking; zero verified feasible routes.',result['dataset_version'],', '.join(result['reason_codes'])]
    for row in result['timeline']:lines.append(row['label'][language]+' | '+str(row['date']))
    for row in result['draft_diagnostics']:lines.append(row['diagnostic_id']+' | '+row['outcome'])
    for row in result['document_checklist']:lines.append(row['label'][language]+' | '+row['carrying_role']+' / '+row['delivery_role']+' / '+row['receiving_role']+' | custody_confirmed=false')
    lines.append('费用分项（未知金额不是零，无法合计）' if zh else 'Itemized costs (unknown is not zero; no total)')
    for row in result['costs']['items']:lines.append(row['label'][language]+' | '+row['status']+' | '+str({k:row[k] for k in ('currency','min','max','includes','excludes','quoted_at','expires_at','source')}))
    lines.append(result['provider_directory']['selection_policy'][language])
    for row in result['provider_directory']['providers']:lines.append(row['name']+' | '+row['capability_scope'][language]+' | external_confirmation=unknown | '+row['url']+' | '+row['checked_at']+' | '+row['affiliation'][language])
    for row in result['evidence']:lines.append(row['source_id']+' | '+row['status']+' | '+row['url'])
    return '\n'.join(lines)+'\n'+emergency_checklist(language)
