"""Loopback-only offline web preview using the same kernel as the CLI.

No accounts, remote services, model calls, profile storage or request-body logging.
This development server is not a public Internet deployment.
"""
import argparse
from datetime import date
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from packages.engine.io import ROOT, load_repository
from packages.engine.routes import preview, checklist
from packages.engine import eu, outbound
from packages.engine.evaluate import day
from scripts.validate_data import read_json

ASSETS = Path(__file__).parent
FIELDS = {'language', 'corridor', 'assessment_at', 'entry_at', 'species', 'service_animal',
          'purpose', 'ownership_transfer', 'accompaniment', 'can_drive', 'healthy',
          'health_certificate_present', 'output', 'owner_moving', 'owner_entry_at',
          'authorized_person_written', 'birth_date', 'rabies_vaccination_at',
          'primary_protocol_completed_at', 'identification_at', 'identification_method',
          'microchip_present', 'tattoo_at', 'tattoo_readable', 'passport_model', 'passport_issued_at', 'vaccination_branch'}
OUTBOUND_DATES = {'departure_at':'journey', 'certificate_issued_at':'documents',
    'certificate_endorsed_at':'documents','origin_certificate_issued_at':'documents',
    'titre_sample_at':'events','export_application_at':'events','export_inspection_at':'events',
    'document_delivery_at':'events','certificate_at':'appointments','document_check_at':'appointments',
    'receipt_entry_at':'documents'}
OUTBOUND_CHOICES = {'transport_mode':'journey','first_entry_member':'journey','destination_member':'journey',
    'entry_airport':'journey','travel_history_branch':'journey','rabies_vaccine_origin':'journey','titre_branch':'journey',
    'certificate_model':'documents','issuer_route':'documents','receipt_airport':'documents','acf_airport':'documents',
    'carrying_role':'responsibility','delivery_role':'responsibility','receiving_role':'responsibility',
    'entry_time':'journey','entry_timezone':'journey','onward_entry_time':'journey','onward_entry_timezone':'journey',
    'tapeworm_at':'events','tapeworm_timezone':'events'}
FIELDS.update(OUTBOUND_DATES)
FIELDS.update(OUTBOUND_CHOICES)
OUTBOUND_EXAMPLES = {'cn.outbound.us':{'destination':'US','name':{'en':'CN → US (documents)','zh-CN':'中国→美国（文件链）'}},
                     'cn.outbound.eu':{'destination':'EU','name':{'en':'CN → EU (documents)','zh-CN':'中国→欧盟（文件链）'}}}

EU_EXAMPLES = {'eu.' + a.lower() + '-' + b.lower():
               dict(origin_member=a, destination_member=b,
                    name={'en':a+' → '+b+' (EU evidence)', 'zh-CN':a+' → '+b+'（欧盟证据）'})
               for a,b in [('DE','DE'),('FR','FR'),('NL','NL'),('DE','FR'),('FR','NL'),('NL','DE'),('DE','IE')]}


def text(en, zh, language):
    return zh if language == 'zh-CN' else en


def boolean(value):
    if value not in ('true', 'false', 'unknown', ''):
        raise ValueError('invalid boolean selection')
    return {'true': True, 'false': False}.get(value)


def profile_from_form(fields):
    """Allow only anonymous planning inputs; never accept evidence/booking overrides."""
    if set(fields) - FIELDS:
        raise ValueError('unknown form field')
    corridor = fields.get('corridor', '')
    region = 'EU' if corridor in EU_EXAMPLES else 'US' if corridor.startswith('dom.us.') else 'CN'
    journey = dict(origin=region, destination=region, pets_per_person=1,
                   purpose=fields.get('purpose'), accompaniment=fields.get('accompaniment'),
                   ownership_transfer=boolean(fields.get('ownership_transfer', 'unknown')))
    if fields.get('entry_at'):
        journey['entry_at'] = fields['entry_at']
    profile = dict(pet={'species': fields.get('species'),
                     'service_animal': boolean(fields.get('service_animal', 'unknown')),
                     'healthy': boolean(fields.get('healthy', 'unknown'))},
                journey=journey,
                documents={'health_certificate_present': boolean(fields.get('health_certificate_present', 'unknown'))},
                preview={'can_drive': boolean(fields.get('can_drive', 'unknown'))})
    if region == 'EU':
        case = EU_EXAMPLES[corridor]
        journey.update(origin_member=case['origin_member'], destination_member=case['destination_member'],
                       owner_moving=boolean(fields.get('owner_moving','unknown')),
                       authorized_person_written=boolean(fields.get('authorized_person_written','unknown')),
                       transport_mode='road', vaccination_branch=fields.get('vaccination_branch','unknown'))
        for name, group in [('birth_date','pet'),('owner_entry_at','journey'),('passport_issued_at','documents'),
                            ('rabies_vaccination_at','events'),('primary_protocol_completed_at','events'),
                            ('identification_at','events'),('tattoo_at','events')]:
            if fields.get(name):
                day(fields[name])
                profile.setdefault(group,{})[name] = fields[name]
        for name in ('identification_method','passport_model'):
            if fields.get(name) not in (None,'','unknown'):
                profile['pet' if name=='identification_method' else 'documents'][name]=fields[name]
        for name in ('microchip_present','tattoo_readable'):
            profile['pet'][name]=boolean(fields.get(name,'unknown'))
    if corridor in OUTBOUND_EXAMPLES:
        journey.update(origin='CN',destination=OUTBOUND_EXAMPLES[corridor]['destination'],
            owner_moving=boolean(fields.get('owner_moving','unknown')),
            authorized_person_written=boolean(fields.get('authorized_person_written','unknown')),
            vaccination_branch=fields.get('vaccination_branch','unknown'))
        profile['pet'].update(identification_method=fields.get('identification_method','unknown'),
            microchip_present=boolean(fields.get('microchip_present','unknown')),
            tattoo_readable=boolean(fields.get('tattoo_readable','unknown')))
        dates={**OUTBOUND_DATES,'owner_entry_at':'journey','birth_date':'pet',
            'identification_at':'events','rabies_vaccination_at':'events','primary_protocol_completed_at':'events','tattoo_at':'events'}
        for name,group in dates.items():
            if fields.get(name):
                day(fields[name]);profile.setdefault(group,{})[name]=fields[name]
        for name,group in OUTBOUND_CHOICES.items():
            if fields.get(name) not in (None,'','unknown'):
                profile.setdefault(group,{})[name]=fields[name]
    return profile


class App:
    def __init__(self, root=ROOT):
        self.rules = load_repository(root)
        self.graphs = {region: read_json(root / f'data/corridors/{region.lower()}-preview.json') for region in ('CN', 'US')}
        self.overlays = read_json(root / 'data/coverage/us-state-overlays.json')
        self.corridors = {c['id']: (region, c) for region, g in self.graphs.items() for c in g['corridors']}
        self.eu_inventory = eu.load_inventory(root)
        self.outbound_inventory = outbound.load_inventory(root)
        self.corridors.update({ident:('OUTBOUND',case) for ident,case in OUTBOUND_EXAMPLES.items()})
        self.corridors.update({ident:('EU',case) for ident,case in EU_EXAMPLES.items()})

    def assess(self, fields):
        language = fields.get('language', 'zh-CN')
        if language not in ('en', 'zh-CN'):
            raise ValueError('unsupported language')
        if fields.get('output', 'html') not in ('html', 'json'):
            raise ValueError('unsupported output')
        profile = profile_from_form(fields)
        region, _ = self.corridors[fields['corridor']]
        if region == 'OUTBOUND':
            result = outbound.assess(profile, assessment_at=fields['assessment_at'], inventory=self.outbound_inventory, eu_inventory=self.eu_inventory)
            result['corridor_id'] = fields['corridor']
            return result, outbound.checklist(result, language=language)
        if region == 'EU':
            result = eu.assess(profile, assessment_at=fields['assessment_at'],
                               rules=self.rules, inventory=self.eu_inventory)
            result['corridor_id'] = fields['corridor']
            return result, eu.checklist(result, language=language)
        graph = self.graphs[region]
        result = preview(profile, graph, corridor_id=fields['corridor'],
                         assessment_at=fields['assessment_at'], rules=self.rules,
                         overlays=self.overlays if region == 'US' else None)
        return result, checklist(result, graph, language=language)

    def render(self, fields=None, result=None, printed=None, error=None):
        values = dict(language='zh-CN', corridor='dom.us.ca-ny', assessment_at=date.today().isoformat())
        values.update(fields or {})
        language = values['language'] if values['language'] in ('en', 'zh-CN') else 'zh-CN'
        def tr(en, zh): return text(en, zh, language)
        def select(name, label, options):
            body = ''.join(f'<option value="{escape(value)}"' + (' selected' if values.get(name, 'unknown') == value else '') + f'>{escape(title)}</option>' for value, title in options)
            return f'<label>{escape(label)}<select name="{name}">{body}</select></label>'
        def tri(name, en, zh, true_en='Yes', true_zh='是', false_en='No', false_zh='否'):
            return select(name,tr(en,zh),[('unknown',tr('Unknown','未知')),('true',tr(true_en,true_zh)),('false',tr(false_en,false_zh))])
        corridor_options = []
        for ident, (region, c) in self.corridors.items():
            if region in ('EU','OUTBOUND'):
                corridor_options.append((ident,c['name'][language])); continue
            names = {n['id']: n['name'][language] for n in self.graphs[region]['nodes']}
            corridor_options.append((ident, names[c['origin_node']]+' → '+names[c['destination_node']]))
        controls = select('corridor',tr('Research direction','研究方向'),corridor_options)
        for name,en,zh in [('assessment_at','Assessment date','评估日期'),('entry_at','Travel date','出行日期')]:
            controls += f'<label>{tr(en,zh)}<input type="date" name="{name}" value="{escape(values.get(name,""))}"'+(' required' if name=='assessment_at' else '')+'></label>'
        controls += select('species',tr('Animal','动物'),[('unknown',tr('Unknown','未知')),('dog',tr('Dog','犬')),('cat',tr('Cat','猫'))])
        controls += tri('service_animal','Service animal?','是否服务动物？')
        controls += select('purpose',tr('Purpose','用途'),[('unknown',tr('Unknown','未知')),('relocation',tr('Relocation','迁居')),('holiday',tr('Holiday','旅行')),('boarding',tr('Institution-led boarding','机构寄游'))])
        controls += tri('ownership_transfer','Ownership transfer?','是否变更所有权？')
        controls += select('accompaniment',tr('Accompaniment','陪同'),[('unknown',tr('Unknown','未知')),('owner',tr('Owner on the same journey','主人同行')),('authorized_person',tr('Authorized person','授权人员')),('unaccompanied',tr('Animal without accompanying passenger','宠物无陪同旅客'))])
        controls += tri('can_drive','Owner driving available?','主人能否驾车？')
        controls += tri('healthy','Healthy animal (reported, not a diagnosis)?','报告健康状况（非诊断）？')
        controls += tri('health_certificate_present','Health certificate present?','是否已有健康证？')
        eu_controls = tri('owner_moving','Owner also travelling? (EU)','主人是否也移动？（欧盟）')
        eu_controls += tri('authorized_person_written','Written responsible-person authorisation?','是否有责任人员书面授权？')
        for name,en,zh in [('owner_entry_at','Owner travel date','主人移动日期'),('birth_date','Animal birth date','宠物出生日期'),
                           ('identification_at','Identification/read date','标识／读取日期'),('rabies_vaccination_at','Rabies vaccination date','狂犬病接种日期'),
                           ('primary_protocol_completed_at','Primary protocol completion','初次接种程序完成'),('tattoo_at','Tattoo application date','纹身施加日期'),
                           ('passport_issued_at','Passport issue date','护照签发日期')]:
            eu_controls += f'<label>{tr(en,zh)}<input type="date" name="{name}" value="{escape(values.get(name,""))}"></label>'
        eu_controls += select('vaccination_branch',tr('Rabies vaccination branch','狂犬病接种分支'),[('unknown',tr('Unknown','未知')),('primary',tr('Primary protocol','初次程序')),('booster',tr('Booster (continuity unreviewed)','加强针（连续性未核）'))])
        eu_controls += select('identification_method',tr('Identification method','标识方式'),[('unknown',tr('Unknown','未知')),('microchip',tr('Microchip','芯片')),('tattoo',tr('Tattoo exception','纹身例外'))])
        eu_controls += tri('microchip_present','Microchip present?','是否有芯片？')
        eu_controls += tri('tattoo_readable','Tattoo clearly readable?','纹身是否清晰可读？')
        eu_controls += select('passport_model',tr('Passport model (not a validity check)','护照范本（不校验完整有效性）'),[('unknown',tr('Unknown','未知')),('eu.705.passport','2026/705 Annex I'),('eu.577.passport','577/2013 Annex III')])
        controls += '<details><summary>'+tr('EU evidence inputs','欧盟证据输入')+'</summary><div class="fields">'+eu_controls+'</div></details>'
        outbound_controls = ''
        date_labels = {
            'departure_at':('Departure date','出发日期'),
            'certificate_issued_at':('Veterinarian signature/issue date','兽医签署／签发日期'),
            'certificate_endorsed_at':('Authority endorsement date','主管机关背书日期'),
            'origin_certificate_issued_at':('CN export certificate issue date','中国出口证签发日期'),
            'titre_sample_at':('Antibody sample date','抗体采血日期'),
            'export_application_at':('Origin application date','属地申请日期'),
            'export_inspection_at':('Origin inspection date','属地查验日期'),
            'document_delivery_at':('Proposed original document delivery date','拟原件交付日期'),
            'certificate_at':('Proposed final issue/endorsement appointment','拟最终签发／背书预约日期'),
            'document_check_at':('EU documentary/identity check date','欧盟文件／标识检查日期'),
            'receipt_entry_at':('CDC receipt arrival date','CDC回执抵达日期')}
        for name,(en,zh) in date_labels.items():
            outbound_controls += f'<label>{tr(en,zh)}<input type="date" name="{name}" value="{escape(values.get(name,""))}"></label>'
        def choices(name,en,zh,options):
            return select(name,tr(en,zh),[('unknown',tr('Unknown','未知'))]+[(key,tr(a,b)) for key,a,b in options])
        outbound_controls += choices('transport_mode','Air transport product','航空产品',[('cabin','Cabin','客舱'),('checked_baggage','Checked baggage','旅客托运行李'),('manifest_cargo','Separate live-animal cargo','独立活体货运')])
        for name,en,zh in [('first_entry_member','First EU entry member','欧盟首入境成员国'),('destination_member','Final EU member','欧盟最终成员国')]:
            outbound_controls += select(name,tr(en,zh),[('unknown',tr('Unknown','未知'))]+[(m['member'],m['member']) for m in self.eu_inventory['members']])
        for name,en,zh in [('entry_airport','Arrival airport (listing is not capacity)','抵达机场（列名非运力）'),('receipt_airport','CDC receipt airport','CDC回执机场'),('acf_airport','Reserved ACF airport','预约设施机场')]:
            outbound_controls += select(name,tr(en,zh),[('unknown',tr('Unknown','未知'))]+[(key,key) for key in self.outbound_inventory['us_acf_airports']+['EWR','FRA','CDG','AMS']])
        outbound_controls += choices('travel_history_branch','Dog six-month history (CN is high risk)','犬六个月旅行史（中国大陆为高风险）',[('high_risk_in_6_months','High risk in six months','六个月内高风险'),('only_low_risk_6_months','Only low risk (conflicts with CN origin)','仅低风险（与中国大陆起运冲突）')])
        outbound_controls += choices('rabies_vaccine_origin','Dog vaccine origin','犬疫苗来源',[('foreign','Outside US','美国境外'),('US','US-issued (separate branch uncompiled)','美国签发（独立分支未编译）')])
        outbound_controls += choices('titre_branch','Antibody branch','抗体分支',[('test_required','Test required','需要检测'),('quarantine','US quarantine alternative','美国隔离备选'),('return','EU return exception unreviewed','欧盟返程例外未核'),('listed_origin','EU listed-origin exception unreviewed','欧盟列名来源例外未核')])
        outbound_controls += select('certificate_model',tr('EU certificate model','欧盟证书范本'),[('unknown',tr('Unknown','未知')),('eu.705.ahc','2026/705 Annex III'),('eu.577.ahc','577/2013 Annex IV')])
        outbound_controls += choices('issuer_route','EU issue/endorsement route','欧盟签发／背书路径',[('official_vet','Official veterinarian issue','官方兽医签发'),('authorized_then_endorsed','Authorised veterinarian then authority endorsement','授权兽医签发后主管机关背书')])
        role_options=[('owner','Owner','主人'),('authorized_person','Authorised person','授权人员'),('origin_customs','Origin customs','属地海关'),('government_vet','Government vet','政府兽医'),('veterinarian','Veterinarian','兽医'),('importer','Importer','进口人'),('carrier','Carrier','承运方'),('receiving_authority','Receiving authority','接收机关')]
        for name,en,zh in [('carrying_role','Document carrying role (pending arrangement)','文件携带角色（仍待安排）'),('delivery_role','Document delivery role','文件交付角色'),('receiving_role','Document receiving role','文件接收角色')]:
            outbound_controls += choices(name,en,zh,role_options)
        for name,en,zh in [('entry_time','Protected first-member entry time, offset required','受保护首入境成员国时间，须带时差'),('onward_entry_time','Protected onward-member entry time, offset required','受保护后续成员国时间，须带时差'),('tapeworm_at','Dog treatment time, offset required','犬处理时间，须带时差')]:
            outbound_controls += f'<label>{tr(en,zh)}<input type="text" name="{name}" value="{escape(values.get(name,""))}" placeholder="2026-11-10T10:00:00+00:00"></label>'
        for name,en,zh in [('entry_timezone','First-member IANA time zone','首入境IANA时区'),('onward_entry_timezone','Onward-member IANA time zone','后续成员国IANA时区'),('tapeworm_timezone','Treatment IANA time zone','处理IANA时区')]:
            outbound_controls += select(name,tr(en,zh),[('unknown',tr('Unknown','未知'))]+[(z,z) for z in ('Asia/Shanghai','Europe/Dublin','Europe/Helsinki','Europe/Malta','Europe/Amsterdam','Europe/Berlin','Europe/Paris')])
        controls += '<details id="outbound-inputs"><summary>'+tr('CN outbound document and appointment inputs','中国出境文件与预约输入')+'</summary><p>'+tr('Anonymous planning dates only. No contact details or document upload. Open EU inputs above for vaccination and owner dates.','仅填匿名规划日期，不填联系人或上传文件。接种与主人日期请展开上方欧盟证据输入。')+'</p><div class="fields">'+outbound_controls+'</div></details>'
        results = ''
        if error:
            results += '<p role="alert">'+escape(tr('Input error: ','输入错误：')+error)+'</p>'
        if result:
            status = tr('Unsupported: evidence incomplete','未覆盖：证据不完整') if result['status']=='unsupported' else tr('Ineligible within this graph and input','此图和输入中的路径已排除')
            results += f'<section aria-labelledby="result-title"><h2 id="result-title">{status}</h2><p><code>{result["status"]}</code> · {escape(result["dataset_version"])}</p>'
            results += '<p>'+tr('No booking or order. Zero verified feasible routes. Duration, distance, cost, acceptance and responsible entities need confirmation.','未订舱／未接单，已验证可行路线为零。时间、里程、费用、收运和责任主体待确认。')+'</p>'
            results += '<h3>'+tr('Reasons and coverage gaps','原因与覆盖缺口')+'</h3><p class="codes">'+escape(', '.join(result['reason_codes']))+'</p>'
            if 'state_overlays' in result:
                results += '<h3>'+tr('CA / NY / TX evidence inventory','CA／NY／TX证据清单')+'</h3><ul>'
                for state in result['state_overlays']:
                    state_status = tr('Source unavailable','来源不可读') if state['status']=='source_unavailable' else tr('Read; independent review pending','已读；独立复核待完成')
                    results += f'<li><strong>{state["subdivision"]}</strong>: {state_status}<p class="codes">{escape(", ".join(state["pending_checks"]))}</p>'
                    for e in state['evidence']:
                        results += f'<p>{escape(e["summary"][language])} <a href="{escape(e["url"],quote=True)}">{escape(e["source_id"])}</a> · {e["accessed_at"]}</p>'
                    results += '</li>'
                results += '</ul>'
            if 'eu_inventory' in result:
                inv = result['eu_inventory']
                results += '<h3>'+tr('EU framework and 27-member gaps','欧盟框架与27成员国缺口')+'</h3><p>'+tr('Evidence preview: no operational routes compiled. Cross-member requirements do not establish domestic law.','证据预览：尚无经核实运输路线。跨成员国要求不作为国内法律。')+'</p>'
                for item in [inv['framework']] + inv['members']:
                    results += '<details><summary>'+escape(item.get('member','EU')+' · '+item.get('status','read_pending_review'))+'</summary><p class="codes">'+escape(', '.join(item['pending_checks']))+'</p>'
                    for e in item['evidence']:
                        results += f'<p><a href="{escape(e["url"],quote=True)}">{escape(e["source_id"])}</a> · {e["accessed_at"]} · {escape(e["summary"][language])}</p>'
                    results += '</details>'
                results += '<h3>'+tr('Draft diagnostics — not enforced','草稿诊断 — 不执行')+'</h3>'
                for row in result['explanations']:
                    results += '<p>'+escape(row['rule_id']+' | '+row['outcome']+' | '+row['message'][language])+'</p>'
                for row in result['draft_diagnostics']:
                    results += '<p><code>'+escape(row['diagnostic_id']+' | '+row['outcome'])+'</code></p>'
                results += '<details><summary>'+tr('2026 document models and exceptions','2026文件范本与例外')+'</summary>'
                for model in inv['document_models']:
                    results += '<p>'+escape(model['id']+' | '+model['scope']+' | issued_before='+str(model['issued_before'])+' | recognition_until='+str(model['recognition_until']))+'</p>'
                for exception in inv['exceptions']:
                    results += '<p>'+escape(exception['summary'][language])+'</p>'
                results += '</details>'
            if result.get('assessment_scope')=='cn_outbound_evidence_preview':
                results += '<h3>'+tr('Document timeline — research dates only','文件时间轴 — 仅研究日期')+'</h3><p>'+tr('Issue, endorsement, arrival and checks have separate anchors. Civil-day estimates do not establish hour deadlines. Appointment conflicts appear above.','签发、背书、抵达及检查分开锚定。日级估算不证明小时期限；预约冲突列于上方。')+'</p><ol>'
                for row in result['timeline']:
                    results += '<li>'+escape(row['label'][language])+' · '+escape(str(row['date']))+'<p>'+escape(str(row['earliest_date'])+' … '+str(row['latest_date']))+'</p></li>'
                results += '</ol><h3>'+tr('Entry-point and document diagnostics — draft','口岸及文件诊断 — 草稿')+'</h3>'
                for row in result['entry_point_diagnostics']+result['draft_diagnostics']:
                    results += '<p><code>'+escape(row.get('diagnostic_id','entry_point')+' | '+row['outcome'])+'</code></p>'
                results += '<h3>'+tr('Original-document responsibilities — pending arrangement','原件责任 — 待安排')+'</h3><ul>'
                for row in result['document_checklist']:
                    results += '<li>'+escape(row['label'][language])+'<p>'+escape(tr('Issuing: ','签发：')+row['issuing_role']+' | '+tr('Carrying: ','携带：')+row['carrying_role']+' | '+tr('Delivery: ','交付：')+row['delivery_role']+' | '+tr('Receiving: ','接收：')+row['receiving_role'])+'</p></li>'
                results += '</ul><h3>'+tr('Readings and access gaps','查阅及读取缺口')+'</h3>'
                for row in result['evidence']:
                    results += '<details><summary>'+escape(row['source_id']+' · '+row['status'])+'</summary><p>'+escape(row['summary'][language])+' <a href="'+escape(row['url'],quote=True)+'">'+escape(row['source_id'])+'</a></p></details>'
            region = self.corridors[result['corridor_id']][0]
            names = {n['id']:n['name'][language] for n in self.graphs[region]['nodes']} if region not in ('EU','OUTBOUND') else {}
            products = {
                'owner_vehicle': tr('Owner vehicle', '主人车辆'),
                'unaccompanied_animal_carrier': tr('Unaccompanied animal carrier', '独行活体承运'),
                'ground_transfer': tr('Ground transfer', '道路接驳'),
                'as_passenger_pet_cabin': tr('Passenger cabin', '旅客客舱'),
                'as_passenger_pet_baggage': tr('Passenger baggage', '旅客行李'),
                'as_manifest_pet_cargo': tr('Separate animal cargo', '独立活体货运'),
                'mu_passenger_pet_baggage': tr('Passenger baggage', '旅客行李'),
                'cz_passenger_pet_baggage': tr('Passenger baggage', '旅客行李'),
                'rail_owner_accompanied': tr('Accompanied rail', '铁路同行'),
                'rail_unaccompanied': tr('Unaccompanied rail', '铁路独行'),
            }
            for group in ('candidates','excluded'):
                title = tr('Unranked research candidates','未排名研究候选') if group=='candidates' else tr('Excluded paths','已排除路径')
                results += f'<h3>{title} ({len(result[group])})</h3>'
                for route in result[group]:
                    results += f'<details><summary>{escape(" → ".join([names[route["segments"][0]["from_node"]]]+[names[s["to_node"]] for s in route["segments"]]))} · <code>{route["status"]}</code><br>{escape(" → ".join(products[leg["product"]] for leg in route["segments"]))}</summary><p class="codes">{escape(", ".join(route["reason_codes"]))}</p><ol>'
                    for leg in route['segments']:
                        results += f'<li>{escape(names[leg["from_node"]])} → {escape(names[leg["to_node"]])}<br><code>{escape(leg["segment_id"])}</code> · {escape(leg["mode"])} / {escape(leg["product"])}<p>'+tr('Arrival handover: exact location/window need confirmation; escort, custody, recipient and original-document custodian pending arrangement.','到达交接：精确地点／窗口待确认；陪同、保管、接收和原件保管均待安排。')+'</p>'
                        for row in leg['rule_assessment']['explanations']:
                            results += f'<p>{escape(row["message"][language])} · <code>{row["outcome"]}</code> · '+tr('Draft; not enforced','草稿；非执行规则')+'</p>'
                        for e in leg['evidence']:
                            results += f'<p><a href="{escape(e["url"],quote=True)}">{escape(e["source_id"])}</a> · {e["accessed_at"]} · {escape(e["summary"][language])}</p>'
                        results += '</li>'
                    results += '</ol></details>'
            results += '<button type="button" id="print">'+tr('Print handover checklist','打印交接清单')+'</button><details class="printable"><summary>'+tr('Complete printable checklist','完整可打印清单')+'</summary><pre>'+escape(printed)+'</pre></details></section>'
        return f'''<!doctype html><html lang="{language}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>PetWaymark · {tr('Journey evidence preview','旅程证据预览')}</title><link rel="stylesheet" href="/style.css"><script src="/app.js" defer></script></head><body><main><header><p>PetWaymark · 宠途路标</p><h1>{tr('Plan with visible unknowns','把未知留在计划里')}</h1><p>{tr('Free, neutral, public-benefit open source. No booking, orders or provider ranking.','公益、免费、中立开源。未订舱、不接单、不排名服务商。')}</p></header><aside>{tr('Research preview. Unknown is not permission. Airports and map distance do not establish animal transport capacity. This anonymous form is processed on this computer without storage; do not enter private identifiers.','研究预览。未知不等于允许，机场和地图距离不能证明活体运力。匿名表单仅在本机处理，不存储；勿输入个人标识。')}</aside><p class="examples">{tr('Synthetic examples:','合成示例：')} <a href="/?language={language}&example=owner">{tr('Owner','主人同行')}</a> · <a href="/?language={language}&example=unaccompanied">{tr('Unaccompanied','宠物独行')}</a> · <a href="/?language={language}&example=eu-owner">{tr('EU cross-member','欧盟跨成员国')}</a> · <a href="/?language={language}&example=eu-boarding">{tr('Owner stays home','主人不移动')}</a> · <a href="/?language={language}&example=outbound-us">{tr('CN → US','中国→美国')}</a> · <a href="/?language={language}&example=outbound-eu">{tr('CN → EU','中国→欧盟')}</a></p><form action="/assess" method="post"><input type="hidden" name="language" value="{language}"><div class="fields">{controls}</div><div class="actions"><button type="submit">{tr('Assess research candidates','评估研究候选')}</button><button type="submit" name="output" value="json">{tr('Export redacted JSON','导出脱敏JSON')}</button><button type="button" id="language" data-language="{'en' if language=='zh-CN' else 'zh-CN'}">{'English' if language=='zh-CN' else '中文'}</button></div></form>{results}<footer>{tr('Single privately owned dog/cat only. Unsupported states, emergency overlays, transit rules, actual operating carrier and custody remain pending. Commercial names identify source policy scope only.','仅单只自有犬猫。未覆盖州、应急叠加、途经规则、实际承运与保管待核。商业名称仅标识来源政策范围。')}</footer></main></body></html>'''


def make_handler(app):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass  # No profile, query, request or client logs.

        def send(self, code, body, content_type='text/html; charset=utf-8', download=False):
            data = body.encode('utf-8')
            self.send_response(code)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(data)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Referrer-Policy', 'same-origin')
            self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'none'; form-action 'self'; frame-ancestors 'none'; base-uri 'none'")
            if download:
                self.send_header('Content-Disposition', 'attachment; filename="petwaymark-preview.json"')
            self.end_headers()
            self.wfile.write(data)

        def local_request(self):
            allowed = {f'127.0.0.1:{self.server.server_port}', f'localhost:{self.server.server_port}'}
            host = self.headers.get('Host', '')
            origin = self.headers.get('Origin')
            return host in allowed and (origin is None or origin in {'http://'+h for h in allowed})

        def do_GET(self):
            if not self.local_request():
                self.send(403, 'Local requests only'); return
            request = urlsplit(self.path)
            if request.path in ('/style.css','/app.js'):
                name = request.path[1:]
                self.send(200, (ASSETS / name).read_text(), 'text/css' if name.endswith('css') else 'text/javascript'); return
            if request.path != '/':
                self.send(404, 'Not found'); return
            query = parse_qs(request.query)
            language = query.get('language', ['zh-CN'])[0]
            if language not in ('en','zh-CN'):
                self.send(400, 'Unsupported language'); return
            fields = {'language':language}
            example = query.get('example', [''])[0]
            if example in ('owner','unaccompanied','eu-owner','eu-boarding','outbound-us','outbound-eu'):
                fields.update(corridor='dom.us.ca-ny', species='dog', service_animal='false',
                              purpose='relocation', ownership_transfer='false', accompaniment=example,
                              can_drive='true', healthy='true', health_certificate_present='true',
                              assessment_at='2026-10-08', entry_at='2026-11-10')
                if example.startswith('eu-'):
                    fields.update(corridor='eu.de-fr',accompaniment='owner',owner_moving='true',owner_entry_at='2026-11-10',
                                  vaccination_branch='primary',birth_date='2024-01-01',identification_method='microchip',microchip_present='true',
                                  identification_at='2024-03-01',rabies_vaccination_at='2026-09-01',primary_protocol_completed_at='2026-09-01',
                                  passport_model='eu.577.passport',passport_issued_at='2025-01-01')
                if example=='eu-boarding':
                    fields.update(purpose='boarding',accompaniment='authorized_person',owner_moving='false',owner_entry_at='',authorized_person_written='true')
            if example.startswith('outbound-') and example in ('outbound-us','outbound-eu'):
                dest=example.removeprefix('outbound-')
                fields.update(corridor='cn.outbound.'+dest,accompaniment='owner',owner_moving='true',owner_entry_at='2026-11-10',
                    departure_at='2026-11-09',vaccination_branch='primary',birth_date='2024-01-01',identification_at='2026-06-01',
                    identification_method='microchip',microchip_present='true',rabies_vaccination_at='2026-06-01',primary_protocol_completed_at='2026-06-01',
                    transport_mode='checked_baggage',travel_history_branch='high_risk_in_6_months',rabies_vaccine_origin='foreign',titre_branch='test_required',
                    titre_sample_at='2026-07-01',certificate_issued_at='2026-11-01',certificate_endorsed_at='2026-11-05',origin_certificate_issued_at='2026-11-05',
                    document_delivery_at='2026-11-06',certificate_at='2026-11-05',document_check_at='2026-11-10',receipt_entry_at='2026-11-10',
                    first_entry_member='NL',destination_member='DE',entry_airport='JFK' if dest=='us' else 'AMS',receipt_airport='JFK',acf_airport='JFK',
                    certificate_model='eu.705.ahc',issuer_route='authorized_then_endorsed')
            self.send(200, app.render(fields))

        def do_POST(self):
            if not self.local_request():
                self.send(403, 'Local requests only'); return
            if self.path != '/assess':
                self.send(404, 'Not found'); return
            fields = {}
            try:
                length = int(self.headers.get('Content-Length','0'))
                if not 0 < length <= 16384:
                    raise ValueError('form length out of range')
                if self.headers.get('Content-Type','').split(';')[0] != 'application/x-www-form-urlencoded':
                    raise ValueError('expected form data')
                parsed = parse_qs(self.rfile.read(length).decode('utf-8'), keep_blank_values=True, max_num_fields=len(FIELDS))
                if any(len(v)!=1 for v in parsed.values()):
                    raise ValueError('duplicate form field')
                fields = {k:v[0] for k,v in parsed.items()}
                result, printed = app.assess(fields)
            except (ValueError, KeyError, UnicodeError):
                # Echo only validated form fields; errors never reveal raw request contents.
                safe = {k:v for k,v in fields.items() if k in FIELDS}
                self.send(400, app.render(safe, error='Please check selections and YYYY-MM-DD dates.')); return
            if fields.get('output') == 'json':
                self.send(200, json.dumps(result,ensure_ascii=False,indent=2)+'\n', 'application/json; charset=utf-8', download=True)
            else:
                self.send(200, app.render(fields,result,printed))
    return Handler


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8766)
    args = parser.parse_args()
    app = App()
    with ThreadingHTTPServer(('127.0.0.1', args.port), make_handler(app)) as server:
        print(f'PetWaymark local preview: http://127.0.0.1:{server.server_port} (Ctrl+C to stop)', flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == '__main__':
    main()
