"""Live local HTTP checks use the shared kernel, not rendered snapshots."""
from copy import deepcopy
from http.server import ThreadingHTTPServer
import json
from threading import Thread
import unittest
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from apps.web.server import App, make_handler
from packages.engine.routes import preview
from packages.engine import eu, outbound, inbound
from packages.engine.io import ROOT
from scripts.validate_data import read_json
from apps.web.server import profile_from_form


class WebTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app=App()
        cls.server=ThreadingHTTPServer(('127.0.0.1',0),make_handler(cls.app))
        cls.thread=Thread(target=cls.server.serve_forever,daemon=True)
        cls.thread.start()
        cls.base=f'http://127.0.0.1:{cls.server.server_port}'

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown();cls.server.server_close();cls.thread.join()

    def fields(self,**changes):
        f=dict(language='zh-CN',corridor='dom.us.ca-ny',assessment_at='2026-10-08',entry_at='2026-11-10',
               species='dog',service_animal='false',purpose='relocation',ownership_transfer='false',
               accompaniment='owner',can_drive='true',healthy='true',health_certificate_present='true',output='json')
        f.update(changes);return f

    def post(self, fields, headers=None):
        req=Request(self.base+'/assess',data=urlencode(fields).encode(),headers={'Content-Type':'application/x-www-form-urlencoded',**(headers or {})})
        try:
            with urlopen(req) as r:return r.status,r.headers,r.read().decode()
        except HTTPError as e:return e.code,e.headers,e.read().decode()

    def outbound_fields(self,dest='eu',species='dog',**changes):
        profile=read_json(ROOT/f'tests/fixtures/outbound/cn-{dest}-{species}.json')
        f=self.fields(corridor='cn.outbound.'+dest,species=species)
        for group in ('pet','journey','documents','events','appointments'):
            for key,value in profile.get(group,{}).items():
                if key in ('origin','destination','pets_per_person'):continue
                f[key]=str(value).lower() if type(value) is bool else str(value)
        f.update(changes);return f

    def test_outbound_http_shared_kernel_and_bilingual_print(self):
        for dest in ('us','eu'):
            for species in ('dog','cat'):
                f=self.outbound_fields(dest,species)
                expected=outbound.assess(profile_from_form(f),assessment_at=f['assessment_at'])
                expected['corridor_id']=f['corridor']
                for language in ('en','zh-CN'):
                    code,_,body=self.post({**f,'language':language});self.assertEqual(code,200)
                    self.assertEqual(json.loads(body),expected)
                    code,_,html=self.post({**f,'language':language,'output':'html'})
                    self.assertEqual(code,200);self.assertIn('class="printable"',html)
                    self.assertIn('original_document_custody_and_delivery_unconfirmed',html)
                    self.assertIn('certificate.issue' if dest=='eu' or species=='dog' else 'cn.export_issue',html)
                    self.assertEqual(self.app.assess({**f,'language':language})[1],outbound.checklist(expected,language=language))

    def test_outbound_appointment_and_entry_conflicts_visible(self):
        f=self.outbound_fields(certificate_at='2026-10-30',output='html')
        code,_,html=self.post(f);self.assertEqual(code,200)
        self.assertIn('appointment.certificate-window.date_window_conflict',html)
        f=self.outbound_fields('us',entry_airport='EWR')
        code,_,body=self.post(f);self.assertEqual(code,200)
        self.assertIn('us_entry_point.not_in_read_list',json.loads(body)['reason_codes'])

    def test_outbound_invalid_dates_and_evidence_overrides_rejected(self):
        for changes in [dict(certificate_at='2026-02-30'),dict(certificate_issued_at='bad'),dict(reviewed_by='PRIVATE'),dict(custody_confirmed='true'),dict(booking_confirmed='true')]:
            code,_,html=self.post(self.outbound_fields(**changes));self.assertEqual(code,400)
            self.assertNotIn('PRIVATE',html)

    def test_outbound_unsafe_owner_classification_stops_diagnostics(self):
        for change in [dict(owner_moving='false'),dict(accompaniment='unaccompanied'),dict(accompaniment='authorized_person',authorized_person_written='false')]:
            code,_,body=self.post(self.outbound_fields(**change));self.assertEqual(code,200)
            r=json.loads(body);self.assertFalse(r['classification_resolved']);self.assertEqual(r['timeline'],[])

    def test_bilingual_http_equals_cli_kernel_all_corridors(self):
        for corridor in self.app.corridors:
            for species in ('dog','cat','unknown'):
                for accompaniment in ('owner','unaccompanied','unknown'):
                    f=self.fields(corridor=corridor,species=species,accompaniment=accompaniment)
                    code,headers,zh=self.post(f);self.assertEqual(code,200)
                    code,_,en=self.post({**f,'language':'en'});self.assertEqual(code,200)
                    self.assertEqual(json.loads(zh),json.loads(en))
                    self.assertEqual(json.loads(zh),self.app.assess(f)[0])
                    self.assertEqual(headers['Cache-Control'],'no-store')
                    self.assertNotIn('Set-Cookie',headers)

    def test_html_languages_share_codes_and_show_no_booking(self):
        for lang,phrase in [('zh-CN','未订舱'),('en','No booking')]:
            code,_,html=self.post(self.fields(output='html',language=lang))
            self.assertEqual(code,200)
            self.assertIn(phrase,html)
            self.assertIn('us_state_packages_unreviewed',html)
            self.assertIn('source_unavailable',html)
            self.assertIn('class="printable"',html)

    def test_unknown_boolean_does_not_become_permission(self):
        for field in ('ownership_transfer','service_animal'):
            code,_,body=self.post(self.fields(**{field:'unknown'}))
            self.assertEqual(code,200);self.assertEqual(json.loads(body)['candidates'],[])
        code,_,body=self.post(self.fields(entry_at=''))
        self.assertEqual(code,200);self.assertIn('travel_date_unknown',json.loads(body)['reason_codes'])

    def test_negative_and_missing_draft_diagnostics_visible_on_web(self):
        for field in ('healthy','health_certificate_present'):
            for value,outcome in [('true','pass'),('false','fail'),('unknown','missing')]:
                f=self.fields(corridor='dom.us.tx-ca' if field=='healthy' else 'dom.us.ca-ny',
                              accompaniment='owner' if field=='healthy' else 'unaccompanied',**{field:value})
                code,_,body=self.post(f);self.assertEqual(code,200)
                result=json.loads(body)
                rows=[row for p in result['candidates'] for leg in p['segments'] for row in leg['rule_assessment']['explanations'] if row['outcome']!='not_applicable']
                self.assertTrue(rows)
                self.assertTrue(any(row['outcome']==outcome for row in rows))
                self.assertTrue(all(not row['enforceable'] for row in rows))
                self.assertEqual(result['status'],'unsupported')

    def test_malformed_dates_selection_and_private_fields_rejected(self):
        for change in [dict(entry_at='2026-02-30'),dict(assessment_at='yesterday'),dict(healthy='yes'),dict(corridor='absent'),dict(language='fr'),dict(booking_confirmed='true'),dict(contact='PRIVATE-MARKER')]:
            code,_,body=self.post(self.fields(**change));self.assertEqual(code,400)
            self.assertNotIn('PRIVATE-MARKER',body)

    def test_cross_origin_and_bad_host_rejected(self):
        for headers in [{'Origin':'https://example.org'},{'Origin':'null'},{'Host':'example.org'}]:
            code,_,_=self.post(self.fields(),headers);self.assertEqual(code,403)

    def test_duplicate_and_oversized_form_rejected(self):
        for fields in [list(self.fields().items())+[('healthy','false')],{'species':'x'*17000}]:
            code,_,_=self.post(fields);self.assertEqual(code,400)

    def test_html_escape_and_no_mutation(self):
        f=self.fields(purpose='<script>alert(1)</script>',output='html');before=deepcopy(f)
        code,_,html=self.post(f);self.assertEqual(code,200)
        self.assertNotIn('<script>alert(1)</script>',html);self.assertEqual(f,before)

    def test_get_assets_examples_and_no_repository_files(self):
        for path in ('/','/?language=en&example=owner','/?example=unaccompanied','/style.css','/app.js'):
            with urlopen(self.base+path) as r:self.assertEqual(r.status,200)
        for path in ('/data/sources/catalog.json','/../../LICENSE','/?language=fr'):
            with self.assertRaises(HTTPError):urlopen(self.base+path)

    def eu_fields(self, **changes):
        return self.fields(corridor='eu.de-fr',owner_moving='true',owner_entry_at='2026-11-10',
                           birth_date='2024-01-01',identification_method='microchip',microchip_present='true',
                           identification_at='2024-03-01',rabies_vaccination_at='2026-09-01',
                           primary_protocol_completed_at='2026-09-01',vaccination_branch='primary',
                           passport_model='eu.577.passport',passport_issued_at='2025-01-01',**changes)

    def test_eu_http_matches_shared_kernel_bilingual_and_print(self):
        for corridor in ('eu.de-de','eu.fr-fr','eu.nl-nl','eu.de-fr','eu.fr-nl','eu.nl-de','eu.de-ie'):
            f=self.eu_fields();f['corridor']=corridor
            code,_,body=self.post(f);self.assertEqual(code,200)
            r=json.loads(body)
            expected=eu.assess(profile_from_form(f),assessment_at=f['assessment_at'],rules=self.app.rules,inventory=self.app.eu_inventory)
            expected['corridor_id']=corridor
            self.assertEqual(r,expected);self.assertTrue(r['classification_resolved'])
            self.assertEqual(r['status'],'unsupported');self.assertEqual(len(r['eu_inventory']['members']),27)
            self.assertEqual(sum(m['status']=='local_overlay_uncovered' for m in r['eu_inventory']['members']),24)
            code,_,en=self.post({**f,'language':'en'});self.assertEqual(code,200);self.assertEqual(json.loads(en),r)
            for lang in ('en','zh-CN'):
                code,_,html=self.post({**f,'output':'html','language':lang});self.assertEqual(code,200)
                self.assertIn('local_overlay_uncovered',html);self.assertIn('eu.577.ahc',html)
                self.assertIn('class="printable"',html);self.assertIn('2026_131_independent_review_pending',html)

    def test_eu_owner_stays_home_stops_before_document_diagnostics(self):
        f=self.eu_fields();f.update(purpose='boarding',owner_moving='false',owner_entry_at='',accompaniment='authorized_person',authorized_person_written='true')
        code,_,body=self.post(f);self.assertEqual(code,200);r=json.loads(body)
        self.assertFalse(r['classification_resolved']);self.assertEqual(r['explanations'],[])
        self.assertEqual(r['draft_diagnostics'],[]);self.assertEqual(r['candidates'],[])
        self.assertIn('owner_not_moving_separate_classification',r['reason_codes'])

    def test_eu_invalid_dates_and_input_promotion_rejected(self):
        for field in ('owner_entry_at','birth_date','passport_issued_at','rabies_vaccination_at'):
            f=self.eu_fields();f[field]='2026-02-30';self.assertEqual(self.post(f)[0],400)
        f=self.eu_fields();f['verified_rule_count']='10';self.assertEqual(self.post(f)[0],400)

    def test_eu_get_examples_show_preserved_classification_fields(self):
        for example in ('eu-owner','eu-boarding'):
            with urlopen(self.base+'/?example='+example) as response:
                html=response.read().decode();self.assertIn('value="eu.de-fr" selected',html)
                self.assertIn('name="owner_moving"',html)


    def inbound_fields(self,origin='us',species='dog',**changes):
        profile=read_json(ROOT/f'tests/fixtures/inbound/{origin}-cn-{species}.json')
        f=self.fields(corridor='cn.inbound.'+origin,species=species)
        from apps.web.server import FIELDS
        for group in ('pet','journey','documents','events','responsibility'):
            for key,value in profile[group].items():
                if key in FIELDS and value is not None:
                    f[key]=str(value).lower() if isinstance(value,bool) else str(value)
        f.update(changes);return f

    def test_inbound_http_bilingual_kernel_cost_directory_and_print(self):
        for origin in ('us','eu'):
            for species in ('dog','cat'):
                f=self.inbound_fields(origin,species)
                expected=inbound.assess(profile_from_form(f),assessment_at=f['assessment_at'])
                expected['corridor_id']=f['corridor']
                for language in ('en','zh-CN'):
                    code,_,body=self.post({**f,'language':language})
                    self.assertEqual(code,200);self.assertEqual(json.loads(body),expected)
                    code,_,html=self.post({**f,'language':language,'output':'html'})
                    self.assertEqual(code,200);self.assertIn('external_confirmation=unknown',html)
                    self.assertIn('Air France',html);self.assertIn('Alaska Air Cargo',html)
                    self.assertEqual(self.app.assess({**f,'language':language})[1],inbound.checklist(expected,language=language))
                self.assertEqual(len(expected['costs']['unquoted_items']),11)
                self.assertIsNone(expected['costs']['total']);self.assertFalse(expected['booking_confirmed'])

    def test_inbound_http_scope_stop_and_threshold_conflict(self):
        for changes in ({'accompaniment':'unaccompanied'},{'transport_mode':'manifest_cargo'},{'transit':'HK'},{'origin_subdivision':'US-HI'}):
            code,_,body=self.post(self.inbound_fields(**changes));self.assertEqual(code,200)
            result=json.loads(body);self.assertFalse(result['classification_resolved'])
            self.assertEqual(result['draft_diagnostics'],[]);self.assertEqual(result['document_checklist'],[])
        code,_,html=self.post(self.inbound_fields(titre_iu_ml='0.5',output='html'))
        self.assertEqual(code,200);self.assertIn('threshold_conflict_pending_clarification',html)
        code,_,html=self.post(self.inbound_fields(certificate_issued_at='2026-10-26',output='html'))
        self.assertEqual(code,200);self.assertIn('us.cn.issue-window.date_window_conflict',html)

    def test_inbound_http_rejects_private_promotion_quotes_and_invalid_inputs(self):
        for changes in ({'verified_rule_count':'1'},{'external_confirmation':'confirmed'},{'cost_quotes':'{}'},{'chip_number':'secret'},{'rabies_valid_until':'bad'},{'titre_iu_ml':'nan'},{'lab_acceptance':'yes'}):
            self.assertEqual(self.post(self.inbound_fields(**changes))[0],400)

    def test_inbound_examples_and_all_direction_species_person_language_http_matrix(self):
        for example in ('inbound-us','inbound-eu'):
            with urlopen(self.base+'/?example='+example) as response:
                html=response.read().decode();self.assertIn('id="inbound-inputs"',html)
                self.assertIn('value="cn.inbound.'+example.removeprefix('inbound-')+'" selected',html)
        for origin in ('us','eu'):
            for species in ('dog','cat','ferret'):
                for person in ('owner','authorized_person','unaccompanied'):
                    for language in ('en','zh-CN'):
                        code,_,body=self.post(self.inbound_fields(origin,accompaniment=person,species=species if species!='ferret' else 'dog',language=language) | ({'species':'ferret'} if species=='ferret' else {}))
                        self.assertEqual(code,200)
                        result=json.loads(body);self.assertEqual(result['classification_resolved'],species!='ferret' and person!='unaccompanied')
                        self.assertEqual(result['status'],'unsupported')
