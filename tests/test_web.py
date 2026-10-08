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
