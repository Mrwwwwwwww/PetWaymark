"""Independent reverse chains, documentary conflicts and neutral planning notes."""
from copy import deepcopy
import json
import subprocess
import sys
import unittest
from packages.engine.io import ROOT
from packages.engine.inbound import assess, checklist, load_inventory, sample_year
from packages.engine.planning import costs, load_directory
from scripts.validate_data import read_json, validate_inbound, validators


class InboundTests(unittest.TestCase):
    def profile(self,origin='us',species='dog'):
        return read_json(ROOT/f'tests/fixtures/inbound/{origin}-cn-{species}.json')
    def run_profile(self,p):return assess(p,assessment_at='2026-10-08')
    def outcomes(self,p):return {d['diagnostic_id']:d['outcome'] for d in self.run_profile(p)['draft_diagnostics']}

    def test_independent_four_branches_and_carried_person(self):
        for origin in ('us','eu'):
            for species in ('dog','cat'):
                for person in ('owner','authorized_person','unaccompanied'):
                    with self.subTest(origin=origin,species=species,person=person):
                        p=self.profile(origin,species);p['journey']['accompaniment']=person
                        p['journey']['owner_moving']=False;p['journey']['owner_entry_at']='2030-01-01'
                        r=self.run_profile(p)
                        self.assertEqual(r['classification_resolved'],person!='unaccompanied')
                        self.assertEqual(r['branch'],origin.upper().lower()+'_'+species)
                        self.assertEqual(r['status'],'unsupported');self.assertEqual(r['recommendations'],[])
                        self.assertEqual(r['verified_feasible_route_count'],0);self.assertFalse(r['booking_confirmed'])
                        self.assertTrue(all(not d['enforceable'] for d in r['draft_diagnostics']))
                        self.assertTrue(all(not d['custody_confirmed'] for d in r['document_checklist']))
                        if person=='unaccompanied':self.assertEqual(r['timeline'],[])

    def test_cargo_forward_direction_unknown_and_service_stop(self):
        for group,key,value in [('journey','transport_mode','manifest_cargo'),('journey','origin','CN'),('journey','destination','EU'),('journey','pets_per_person',True),('journey','pets_per_person',2),('journey','purpose','boarding'),('journey','ownership_transfer',None),('journey','transit','HK'),('journey','entry_at','2026-02-30'),('journey','departure_at','2026-12-01'),('pet','species','ferret'),('pet','service_animal',True)]:
            p=self.profile();p[group][key]=value;r=self.run_profile(p)
            self.assertFalse(r['classification_resolved']);self.assertEqual(r['draft_diagnostics'],[])
            self.assertEqual(r['document_checklist'],[])

    def test_no_eu_wide_export_or_us_hawaii_inference(self):
        for member in ('DE','FR','NL','IE',None):
            p=self.profile('eu');p['journey']['origin_member']=member
            self.assertEqual(self.run_profile(p)['classification_resolved'],member in ('DE','FR','NL'))
        for state in ('US-CA','US-NY','US-TX','US-HI','GU',None):
            p=self.profile();p['journey']['origin_subdivision']=state
            self.assertEqual(self.run_profile(p)['classification_resolved'],state in ('US-CA','US-NY','US-TX'))

    def test_us_fourteen_day_issue_window_not_endorsement(self):
        for issue,outcome in [('2026-10-26','date_window_conflict'),('2026-10-27','date_window_consistent'),('2026-11-10','date_window_consistent'),('2026-11-11','date_window_conflict'),(None,'missing'),('bad','invalid')]:
            p=self.profile();p['documents']['certificate_issued_at']=issue
            p['documents']['certificate_endorsed_at']='2026-11-09'
            self.assertEqual(self.outcomes(p)['us.cn.issue-window'],outcome)

    def test_reverse_chain_does_not_inherit_eu_wait_or_us_dog_min_age(self):
        p=self.profile();p['events']['titre_sample_at']='2026-11-09'
        self.assertEqual(self.outcomes(p)['us.cn.sample-after-second'],'pass')
        self.assertEqual(self.outcomes(p)['us.cn.sample-validity'],'date_window_consistent')
        self.assertNotIn('us.dog.minimum-age',self.outcomes(p))
        p=self.profile('eu');p['documents']['certificate_issued_at']='2026-10-01'
        self.assertNotIn('eu.certificate.entry-window',self.outcomes(p))
        self.assertNotIn('us.cn.issue-window',self.outcomes(p));self.assertNotIn('us.cn.sample-validity',self.outcomes(p))
        self.assertIn('eu_cn_titre_sampling_validity_and_vaccine_protocol_unreviewed',self.run_profile(p)['reason_codes'])

    def test_titre_threshold_missing_invalid_fail_conflict_pass(self):
        for value,outcome in [(None,'missing'),(True,'invalid'),('0.6','invalid'),(-1,'invalid'),(float('nan'),'invalid'),(0.49,'fail'),(0.5,'threshold_conflict_pending_clarification'),(0.51,'pass')]:
            for origin in ('us','eu'):
                p=self.profile(origin);p['documents']['titre_iu_ml']=value
                self.assertEqual(self.outcomes(p)['cn.titre.threshold'],outcome)
                self.assertEqual(self.run_profile(p)['status'],'unsupported')

    def test_sample_second_vaccine_same_day_and_one_year_leap(self):
        for sample,outcome in [('2026-05-31','fail'),('2026-06-01','pass'),(None,'missing'),('bad','invalid')]:
            p=self.profile();p['events']['titre_sample_at']=sample
            self.assertEqual(self.outcomes(p)['us.cn.sample-after-second'],outcome)
        for entry,outcome in [('2025-02-28','date_window_consistent'),('2025-03-01','date_window_conflict'),('2024-02-28','date_window_conflict')]:
            self.assertEqual(sample_year('2024-02-29',entry),outcome)
        self.assertEqual(sample_year('2025-11-10','2026-11-10'),'date_window_consistent')
        self.assertEqual(sample_year('2025-11-09','2026-11-10'),'date_window_conflict')

    def test_document_boolean_positive_negative_missing_invalid(self):
        for key,ident in [('health_certificate_present','cn.health-certificate'),('rabies_certificate_present','cn.rabies-certificate'),('chip_readable','cn.chip-readability'),('lab_acceptance','cn.lab.acceptance-reported'),('vehcs_endorsed','us.cn.vehcs'),('traveler_identity_matches','us.cn.identity'),('one_pet_per_certificate','us.cn.one-per-certificate')]:
            for value,outcome in [(True,'pass'),(False,'fail'),(None,'missing'),('true','invalid')]:
                p=self.profile();p['documents'][key]=value
                self.assertEqual(self.outcomes(p)[ident],outcome)
        p=self.profile();p['pet']['microchip_present']=False
        self.assertEqual(self.outcomes(p)['cn.microchip'],'fail')

    def test_expired_rabies_and_invalid_date_never_permission(self):
        for expiry,outcome in [('2026-11-09','fail'),('2026-11-10','pass'),(None,'missing'),('bad','invalid')]:
            p=self.profile();p['events']['rabies_valid_until']=expiry
            self.assertEqual(self.outcomes(p)['cn.rabies.valid-at-entry'],outcome)

    def test_quarantine_is_not_a_waiver_or_release(self):
        p=self.profile();p['journey'].update(cn_entry_branch='quarantine',entry_airport='CAN')
        p['documents']['health_certificate_present']=False
        out=self.outcomes(p);self.assertEqual(out['cn.health-certificate'],'fail')
        self.assertNotIn('cn.titre.threshold',out)
        self.assertIn('facility_port_and_30_day_release_unconfirmed',out.values())
        self.assertEqual(self.run_profile(p)['entry_point_diagnostics'][0]['outcome'],'quarantine_port_current_facility_unverified')
        for branch in ('designated_origin',None):
            p['journey']['cn_entry_branch']=branch
            self.assertEqual(self.run_profile(p)['status'],'unsupported')
            self.assertNotIn('cn.titre.threshold',self.outcomes(p))

    def test_model_species_cannot_be_swapped_or_promoted(self):
        p=self.profile('us','cat');p['documents']['certificate_model']='us.cn.dog.2026'
        self.assertEqual(self.outcomes(p)['us.cn.model'],'model_missing_or_mismatch')
        p['documents']['certificate_model']='us.cn.cat.2026'
        r=self.run_profile(p);self.assertEqual(self.outcomes(p)['us.cn.model'],'named_model_content_pending_review')
        self.assertTrue(any(e['source_id']=='us.aphis.cn-cat-model' and e['status']=='unavailable' for e in r['evidence']))

    def test_early_delivery_and_post_departure_endorsement(self):
        p=self.profile();p['events']['document_delivery_at']='2026-11-04'
        self.assertEqual(self.outcomes(p)['chain.endorsement-before-delivery'],'fail')
        p['events']['document_delivery_at']='2026-11-10'
        self.assertEqual(self.outcomes(p)['chain.delivery-before-departure'],'fail')
        p['documents']['certificate_endorsed_at']='2026-10-26'
        self.assertEqual(self.outcomes(p)['chain.issue-before-endorsement'],'fail')

    def test_anonymous_output_input_unchanged_and_no_review_overrides(self):
        p=self.profile();p['responsibility']['carrying_role']='private-name'
        p.update(booking_confirmed=True,verified_rule_count=100);old=deepcopy(p)
        r=self.run_profile(p);self.assertEqual(p,old)
        self.assertNotIn('private-name',json.dumps(r));self.assertFalse(r['booking_confirmed'])
        for lang in ('en','zh-CN'):
            output=checklist(r,language=lang);self.assertIn('external_confirmation=unknown',output)
            self.assertIn('custody_confirmed=false',output)

    def test_cli_four_fixture_json_and_bilingual_parity(self):
        for origin in ('us','eu'):
            for species in ('dog','cat'):
                path=ROOT/f'tests/fixtures/inbound/{origin}-cn-{species}.json'
                args=[sys.executable,'-m','packages.cli',str(path),'--inbound-preview','--assessment-at','2026-10-08']
                r=self.run_profile(self.profile(origin,species))
                proc=subprocess.run(args,cwd=ROOT,capture_output=True,text=True)
                self.assertEqual(proc.returncode,0,proc.stderr);self.assertEqual(json.loads(proc.stdout),r)
                for lang in ('en','zh-CN'):
                    proc=subprocess.run(args+['--format','checklist','--language',lang],cwd=ROOT,capture_output=True,text=True)
                    self.assertEqual(proc.stdout,checklist(r,language=lang))

    def test_inventory_drift_and_fabricated_review_rejected(self):
        inv=load_inventory();sources={s['id']:s for s in read_json(ROOT/'data/sources/catalog.json')['sources']}
        self.assertEqual(validate_inbound(inv,sources),[])
        for field,value in [('url','https://example.org'),('status','read_pending_review')]:
            altered=deepcopy(inv);altered['evidence'][3][field]=value
            self.assertTrue(validate_inbound(altered,sources))
        for field,value in [('review_status','verified'),('reviewed_by',['AI']),('verified_rule_count',1)]:
            altered=deepcopy(inv);altered[field]=value
            self.assertTrue(list(validators(ROOT)['cn-inbound.schema.json'].iter_errors(altered)))

    def test_bad_group_types_rejected(self):
        for group in ('pet','journey','documents','events','responsibility','cost_quotes'):
            p=self.profile();p[group]=[]
            with self.assertRaises(ValueError):self.run_profile(p)


class PlanningTests(unittest.TestCase):
    def quote(self):return dict(currency='USD',min=10,max=20,quoted_at='2026-10-01',expires_at='2026-10-09',includes=['synthetic base fee'],excludes=['synthetic tax'],source='https://example.org/synthetic-quote')
    def test_unknown_costs_are_not_zero_or_total(self):
        r=costs(assessment_at='2026-10-08')
        self.assertEqual(len(r['items']),11);self.assertEqual(len(r['unquoted_items']),11)
        self.assertIsNone(r['total']);self.assertIsNone(r['total_currency']);self.assertFalse(r['comparable'])
        self.assertTrue(all(row['min'] is None and row['includes'] is None and row['excludes'] is None for row in r['items']))

    def test_manual_notes_complete_missing_expired_future_and_mixed_currency(self):
        q=self.quote();r=costs({'main_transport':q},assessment_at='2026-10-08')
        self.assertEqual(r['items'][6]['status'],'manual_note_complete_unconfirmed')
        self.assertEqual(costs({'main_transport':q},assessment_at='2026-10-09')['items'][6]['status'],'expired')
        for field in q:
            partial=deepcopy(q);partial.pop(field)
            self.assertEqual(costs({'main_transport':partial},assessment_at='2026-10-08')['items'][6]['status'],'incomplete')
        q['quoted_at']='2026-10-09';q['expires_at']='2026-10-10'
        self.assertEqual(costs({'main_transport':q},assessment_at='2026-10-08')['items'][6]['status'],'future_dated')
        eur=self.quote();eur['currency']='EUR';r=costs({'main_transport':self.quote(),'taxes':eur},assessment_at='2026-10-08')
        self.assertIsNone(r['total']);self.assertEqual(r['items'][-1]['currency'],'EUR')

    def test_invalid_quotes_do_not_become_prices(self):
        for field,value in [('min',True),('min',-1),('max',float('inf')),('max',1),('currency','usd'),('currency','ZZZZ'),('quoted_at','bad'),('expires_at','2026-09-01'),('includes','all'),('source','javascript:evil'),('source','https:///')]:
            q=self.quote();q[field]=value
            with self.assertRaises(ValueError):costs({'main_transport':q},assessment_at='2026-10-08')
        with self.assertRaises(ValueError):costs({'unknown':{}},assessment_at='2026-10-08')

    def test_directory_public_capability_not_external_confirmation(self):
        d=load_directory();self.assertEqual(len(d['providers']),3)
        self.assertEqual(d['providers'],sorted(d['providers'],key=lambda p:p['name']))
        for p in d['providers']:
            self.assertEqual(p['external_confirmation'],'unknown');self.assertIsNone(p['confirmation_reference'])
            altered=deepcopy(d);altered['providers'][0]['external_confirmation']='confirmed'
            self.assertTrue(list(validators(ROOT)['provider-directory.schema.json'].iter_errors(altered)))
