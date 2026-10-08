"""Synthetic independent directional branches, windows and evidence failures."""
from copy import deepcopy
from datetime import timedelta
import json
import subprocess
import sys
import unittest
from packages.engine.io import ROOT
from packages.engine.outbound import assess, bounded_days, checklist, instant, load_inventory
from packages.engine.evaluate import day
from scripts.validate_data import read_json, validate_outbound, validators


class OutboundTests(unittest.TestCase):
    def profile(self,dest='eu',species='dog'):
        return read_json(ROOT/f'tests/fixtures/outbound/cn-{dest}-{species}.json')

    def run_profile(self,p):return assess(p,assessment_at='2026-10-08')
    def outcomes(self,p):return {r['diagnostic_id']:r['outcome'] for r in self.run_profile(p)['draft_diagnostics']}

    def test_independent_dog_cat_owner_authorized_unaccompanied_cases(self):
        for dest in ('us','eu'):
            for species in ('dog','cat'):
                for accompaniment in ('owner','authorized_person','unaccompanied'):
                    with self.subTest(dest=dest,species=species,accompaniment=accompaniment):
                        p=self.profile(dest,species);p['journey'].update(accompaniment=accompaniment,authorized_person_written=True)
                        r=self.run_profile(p)
                        self.assertEqual(r['classification_resolved'],dest!='eu' or accompaniment!='unaccompanied')
                        self.assertEqual(r['status'],'unsupported');self.assertFalse(r['booking_confirmed'])
                        self.assertEqual(r['verified_feasible_route_count'],0);self.assertEqual(r['recommendations'],[])
                        self.assertTrue(all(not d['enforceable'] for d in r['draft_diagnostics']))
                        if not r['classification_resolved']:self.assertEqual(r['timeline'],[])

    def test_reverse_and_unknown_classification_stop(self):
        for key,value in [('origin','US'),('destination','CN'),('purpose','boarding'),('ownership_transfer',True),('pets_per_person',True),('accompaniment','unknown'),('first_entry_member','GB'),('destination_member',None),('owner_moving',False),('entry_at','2026-02-30')]:
            p=self.profile();p['journey'][key]=value;r=self.run_profile(p)
            self.assertFalse(r['classification_resolved']);self.assertEqual(r['draft_diagnostics'],[])
        p=self.profile();p['pet']['service_animal']=True;self.assertFalse(self.run_profile(p)['classification_resolved'])

    def test_eu_owner_relationship_both_five_day_boundaries(self):
        for delta in (-6,-5,0,5,6):
            p=self.profile();p['journey'].update(accompaniment='authorized_person',authorized_person_written=True,
                owner_entry_at=(day(p['journey']['entry_at'])+timedelta(days=delta)).isoformat())
            self.assertEqual(self.run_profile(p)['classification_resolved'],abs(delta)<=5)
        p['journey']['authorized_person_written']=False;self.assertFalse(self.run_profile(p)['classification_resolved'])
        p=self.profile();p['journey']['owner_entry_at']='2026-11-11';self.assertFalse(self.run_profile(p)['classification_resolved'])

    def test_us_not_subject_to_eu_owner_dates_or_false_low_risk(self):
        p=self.profile('us');p['journey'].update(owner_moving=False,owner_entry_at='2027-01-01',accompaniment='unaccompanied')
        self.assertTrue(self.run_profile(p)['classification_resolved'])
        for history in ('only_low_risk_6_months',None):
            p['journey']['travel_history_branch']=history;self.assertFalse(self.run_profile(p)['classification_resolved'])
        p=self.profile('us');p['journey']['rabies_vaccine_origin']='US';self.assertFalse(self.run_profile(p)['classification_resolved'])

    def test_us_cat_never_receives_dog_rules_or_timeline(self):
        p=self.profile('us','cat');p.pop('documents');p.pop('events');r=self.run_profile(p)
        self.assertTrue(r['classification_resolved'])
        self.assertEqual(self.outcomes(p)['us.cat.cdc'],'not_applicable')
        self.assertFalse(any(e['event_id'].startswith(('rabies','titre','certificate.')) for e in r['timeline']))
        self.assertFalse(any(d['document_id'].startswith('us.') for d in r['document_checklist']))
        self.assertIn('us_cat_arrival_health_inspection_and_state_rules_pending',r['reason_codes'])

    def test_eu_sample_wait_anchors_issue_not_entry_or_endorsement(self):
        p=self.profile();p['events']['titre_sample_at']='2026-08-04'
        for issue,outcome in [('2026-11-01','fail'),('2026-11-02','pass')]:
            p['documents']['certificate_issued_at']=issue
            self.assertEqual(self.outcomes(p)['titre.wait'],outcome)

    def test_us_sample_wait_anchors_entry_and_quarantine_separate(self):
        p=self.profile('us')
        for sample,outcome in [('2026-10-13','pass'),('2026-10-14','fail')]:
            p['events']['titre_sample_at']=sample;self.assertEqual(self.outcomes(p)['titre.wait'],outcome)
        p['journey']['titre_branch']='quarantine';out=self.outcomes(p)
        self.assertNotIn('titre.wait',out);self.assertEqual(out['us.titre.quarantine'],'quarantine_reservation_unconfirmed')

    def test_identification_age_protocol_sample_positive_negative_missing(self):
        cases=[('identification.before-vaccine','events','identification_at','2026-06-02'),
               ('vaccination.minimum-age','pet','birth_date','2026-05-01'),
               ('rabies.protocol-wait','events','primary_protocol_completed_at','2026-11-01'),
               ('titre.sample-after-primary','events','titre_sample_at','2026-06-30')]
        for ident,group,key,bad in cases:
            p=self.profile();self.assertEqual(self.outcomes(p)[ident],'pass')
            p[group][key]=bad;self.assertEqual(self.outcomes(p)[ident],'fail')
            p[group].pop(key);self.assertEqual(self.outcomes(p)[ident],'missing')
            p[group][key]='bad';self.assertEqual(self.outcomes(p)[ident],'invalid')
        p=self.profile();p['journey']['vaccination_branch']='booster';out=self.outcomes(p)
        self.assertNotIn('titre.sample-after-primary',out);self.assertNotIn('vaccination.minimum-age',out)
        self.assertIn('booster_or_unknown_continuity_unreviewed',out.values())

    def test_eu_official_issue_vs_authorized_endorsement_and_check(self):
        p=self.profile();p['documents']['certificate_issued_at']='2026-10-30'
        p['documents']['issuer_route']='official_vet'
        self.assertEqual(self.outcomes(p)['eu.certificate.entry-window'],'date_window_conflict')
        p['documents']['issuer_route']='authorized_then_endorsed'
        self.assertEqual(self.outcomes(p)['eu.certificate.entry-window'],'date_window_consistent')
        p['appointments']['document_check_at']='2026-11-16'
        self.assertEqual(self.outcomes(p)['eu.certificate.check-window'],'date_window_conflict')
        p['documents']['issuer_route']='unknown';self.assertEqual(self.outcomes(p)['eu.certificate.entry-window'],'issuer_route_unconfirmed')

    def test_us_signed_thirty_day_window_not_endorsement_reset(self):
        p=self.profile('us');p['documents']['certificate_endorsed_at']='2026-11-09'
        for signed,expected in [('2026-10-11','date_window_consistent'),('2026-10-10','date_window_conflict'),('2026-11-11','date_window_conflict')]:
            p['documents']['certificate_issued_at']=signed;self.assertEqual(self.outcomes(p)['us.form.entry-window'],expected)

    def test_appointment_outside_window_or_sample_wait(self):
        p=self.profile()
        for date,expected in [('2026-10-31','date_window_consistent'),('2026-10-30','date_window_conflict'),('2026-11-11','date_window_conflict')]:
            p['appointments']['certificate_at']=date;self.assertEqual(self.outcomes(p)['appointment.certificate-window'],expected)
        p['events']['titre_sample_at']='2026-08-08';p['appointments']['certificate_at']='2026-11-05'
        self.assertEqual(self.outcomes(p)['appointment.sample-wait'],'date_window_conflict')
        p['appointments']['certificate_at']='bad';self.assertEqual(self.outcomes(p)['appointment.certificate-window'],'invalid')

    def test_document_delivery_precedes_departure_and_follows_endorsement(self):
        p=self.profile();p['events']['document_delivery_at']='2026-11-10'
        self.assertEqual(self.outcomes(p)['documents.delivery-before-departure'],'date_window_conflict')
        p['events']['document_delivery_at']='2026-11-04'
        self.assertEqual(self.outcomes(p)['documents.delivery-after-endorsement'],'fail')
        p.pop('responsibility',None);r=self.run_profile(p)
        self.assertTrue(all(d['carrying_role']=='pending_arrangement' for d in r['document_checklist']))
        p['responsibility']=dict(carrying_role='owner',delivery_role='carrier',receiving_role='receiving_authority',custody_confirmed=True)
        self.assertTrue(all(not d['custody_confirmed'] for d in self.run_profile(p)['document_checklist']))

    def test_ports_airport_matching_and_mode_specific_filters(self):
        p=self.profile('us')
        for airport,mode,expected in [('JFK','cabin','listed_pending_confirmation'),('EWR','manifest_cargo','not_in_read_list'),('SEA','cabin','listed_product_conflict'),('SEA','manifest_cargo','listed_pending_confirmation')]:
            p['journey'].update(entry_airport=airport,transport_mode=mode)
            self.assertEqual(self.run_profile(p)['entry_point_diagnostics'][0]['outcome'],expected)
        self.assertEqual(self.outcomes(p)['us.acf_airport'],'airport_mismatch')
        p=self.profile();self.assertEqual(self.run_profile(p)['entry_point_diagnostics'][0]['outcome'],'listed_pending_confirmation')
        p['journey'].update(first_entry_member='DE',entry_airport='AMS')
        self.assertEqual(self.run_profile(p)['entry_point_diagnostics'][0]['outcome'],'entry_point_unreviewed')

    def test_certificate_transition_cannot_be_used_as_validity(self):
        p=self.profile();p['documents'].update(certificate_model='eu.577.ahc',certificate_issued_at='2026-10-01')
        self.assertEqual(self.outcomes(p)['eu.certificate.model'],'model_issue_cutoff_failed')
        self.assertEqual(self.run_profile(p)['status'],'unsupported')

    def test_tapeworm_hours_and_dog_cat_distinction(self):
        p=self.profile();p['journey'].update(first_entry_member='IE',destination_member='IE',entry_time='2026-11-10T10:00:00+00:00',entry_timezone='Europe/Dublin')
        p['events']['tapeworm_timezone']='Asia/Shanghai'
        for stamp,expected in [('2026-11-09T18:00:00+08:00','date_window_consistent'),('2026-11-09T18:00:01+08:00','date_window_conflict'),('2026-11-05T18:00:00+08:00','date_window_consistent'),('2026-11-05T17:59:59+08:00','date_window_conflict')]:
            p['events']['tapeworm_at']=stamp;self.assertEqual(self.outcomes(p)['eu.dog.tapeworm-hours'],expected)
        p['pet']['species']='cat';self.assertNotIn('eu.dog.tapeworm-hours',self.outcomes(p))

    def test_dst_fold_offsets_and_gap_rejection(self):
        first=instant('2026-11-01T01:30:00-04:00','America/New_York')
        second=instant('2026-11-01T01:30:00-05:00','America/New_York')
        self.assertEqual((second-first).total_seconds(),3600)
        for stamp,zone in [('2026-03-08T02:30:00-05:00','America/New_York'),('2026-11-01T01:30:00','America/New_York'),('2026-11-01T01:30:00+08:00','America/New_York'),('2026-01-01T01:00:00+00:00','Invalid/Zone')]:
            with self.assertRaises(ValueError):instant(stamp,zone)

    def test_all_date_helpers_preserve_missing_and_invalid(self):
        self.assertEqual(bounded_days(None,'2026-11-10',0,10),'missing')
        self.assertEqual(bounded_days('bad','2026-11-10',0,10),'invalid')
        for group in ('pet','journey','events','documents','appointments','responsibility'):
            p=self.profile();p[group]=[]
            with self.assertRaises(ValueError):self.run_profile(p)
        p=self.profile();p['journey']['first_entry_member']=[]
        with self.assertRaises(ValueError):self.run_profile(p)

    def test_dag_dates_no_input_mutation_or_private_export(self):
        p=self.profile();p['contact']='PRIVATE';p['documents']['chip_number']='PRIVATE';p['responsibility']={'carrying_role':'PRIVATE'}
        before=deepcopy(p);r=self.run_profile(p)
        ids={e['event_id'] for e in r['timeline']}
        seen=set()
        for e in r['timeline']:
            self.assertTrue(set(e['depends_on'])<=seen);seen.add(e['event_id'])
        self.assertNotIn('PRIVATE',json.dumps(r));self.assertEqual(p,before)
        for language in ('en','zh-CN'):self.assertNotIn('PRIVATE',checklist(r,language=language))
        p['journey']['titre_branch']='return';r=self.run_profile(p)
        self.assertTrue(all(set(e['depends_on'])<={x['event_id'] for x in r['timeline']} for e in r['timeline']))
        self.assertIn('eu.titre.exception.exception_unreviewed',r['reason_codes'])

    def test_inventory_rejects_drift_promotion_duplicates_and_false_listing(self):
        inv=load_inventory();sources={s['id']:s for s in read_json(ROOT/'data/sources/catalog.json')['sources']}
        self.assertTrue(validators(ROOT)['cn-outbound.schema.json'].is_valid(inv));self.assertEqual(validate_outbound(inv,sources),[])
        for change in ('drift','duplicate','promote','port'):
            bad=deepcopy(inv)
            if change=='drift':bad['evidence'][0]['url']='https://example.com/'
            if change=='duplicate':bad['evidence'].append(bad['evidence'][0])
            if change=='promote':bad['reviewed_by']=['invented']
            if change=='port':bad['us_acf_airports'].append('EWR')
            self.assertTrue(validate_outbound(bad,sources))

    def test_cli_shared_json_and_bilingual_checklist(self):
        for dest in ('us','eu'):
            for species in ('dog','cat'):
                args=[sys.executable,'-m','packages.cli',str(ROOT/f'tests/fixtures/outbound/cn-{dest}-{species}.json'),'--outbound-preview','--assessment-at','2026-10-08']
                r=self.run_profile(self.profile(dest,species))
                self.assertEqual(json.loads(subprocess.run(args,cwd=ROOT,capture_output=True,text=True,check=True).stdout),r)
                for language in ('en','zh-CN'):
                    self.assertEqual(subprocess.run(args+['--format','checklist','--language',language],cwd=ROOT,capture_output=True,text=True,check=True).stdout,checklist(r,language=language))
