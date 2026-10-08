"""Synthetic independent US/EU documents and return impacts, no verified permission."""
from copy import deepcopy
import json
import subprocess
import sys
import unittest
from packages.engine.io import ROOT
from packages.engine.us_eu import assess, assess_round_trip, checklist, load_inventory
from scripts.validate_data import read_json, validate_us_eu, validators


class UsEuTests(unittest.TestCase):
    def profile(self, direction='us-eu', species='dog'):
        return read_json(ROOT / f'tests/fixtures/us-eu/{direction}-{species}.json')

    def run_profile(self, p): return assess(p, assessment_at='2026-10-08')
    def outcomes(self, p): return {d['diagnostic_id']:d['outcome'] for d in self.run_profile(p)['draft_diagnostics']}

    def test_independent_directions_species_and_accompaniment(self):
        for direction in ('us-eu', 'eu-us'):
            for species in ('dog', 'cat'):
                for who in ('owner', 'authorized_person', 'unaccompanied'):
                    with self.subTest(direction=direction,species=species,who=who):
                        p=self.profile(direction,species);p['journey'].update(accompaniment=who,authorized_person_written=True)
                        r=self.run_profile(p)
                        self.assertEqual(r['classification_resolved'],who!='unaccompanied')
                        self.assertEqual(r['status'],'unsupported');self.assertFalse(r['booking_confirmed'])
                        self.assertEqual(r['verified_feasible_route_count'],0);self.assertEqual(r['recommendations'],[])
                        self.assertTrue(all(not d['enforceable'] for d in r['draft_diagnostics']))

    def test_wrong_directions_and_scope_stop(self):
        for group,key,value in [('journey','origin','CN'),('journey','destination','US'),('journey','transit','HK'),('journey','transport_mode','manifest_cargo'),('journey','pets_per_person',True),('journey','purpose','sale'),('journey','owner_moving',False),('journey','entry_at','bad'),('pet','service_animal',True),('pet','species','rabbit')]:
            p=self.profile();p[group][key]=value;r=self.run_profile(p)
            self.assertFalse(r['classification_resolved']);self.assertEqual(r['timeline'],[])
            self.assertEqual(r['draft_diagnostics'],[])

    def test_owner_five_days_and_written_authority(self):
        p=self.profile();p['journey'].update(accompaniment='authorized_person',authorized_person_written=True)
        for date,ok in [('2026-11-05',True),('2026-11-15',True),('2026-11-16',False)]:
            p['journey']['owner_entry_at']=date;self.assertEqual(self.run_profile(p)['classification_resolved'],ok)
        p['journey'].update(owner_entry_at='2026-11-10',authorized_person_written=False)
        self.assertFalse(self.run_profile(p)['classification_resolved'])

    def test_us_cat_does_not_receive_dog_requirements(self):
        p=self.profile('eu-us','cat');p.pop('documents');p.pop('events');p['pet'].pop('birth_date');p['pet'].pop('microchip_present')
        out=self.outcomes(p);self.assertEqual(out,{'us.cat-health':'pass','us.cat-dog-rules':'not_applicable'})
        self.assertEqual(self.run_profile(p)['document_checklist'],[])
        p['journey']['destination_subdivision']='US-HI';self.assertIn('us_destination_state_or_territory_uncompiled',self.run_profile(p)['reason_codes'])

    def test_manufacturer_period_not_assumed_twenty_one(self):
        p=self.profile();p['events'].update(primary_protocol_completed_at='2026-10-15',rabies_vaccination_at='2026-10-15',manufacturer_immunity_days=30)
        self.assertEqual(self.outcomes(p)['eu.manufacturer-wait'],'fail')
        p['events']['manufacturer_immunity_days']=21;self.assertEqual(self.outcomes(p)['eu.manufacturer-wait'],'pass')
        for value,expected in [(None,'missing'),(True,'invalid'),(20,'invalid')]:
            p['events']['manufacturer_immunity_days']=value;self.assertEqual(self.outcomes(p)['eu.manufacturer-wait'],expected)

    def test_primary_validity_is_one_year_even_if_reported_three_year(self):
        p=self.profile();p['events'].update(rabies_vaccination_at='2025-06-01',primary_protocol_completed_at='2025-06-01',rabies_valid_until='2028-06-01')
        self.assertEqual(self.outcomes(p)['eu.us-primary-one-year'],'fail')
        p['events']['rabies_vaccination_at']='bad';self.assertEqual(self.outcomes(p)['eu.us-primary-one-year'],'invalid')

    def test_us_issue_thirty_days_endorsement_ten_check_separate(self):
        p=self.profile();p['documents'].update(certificate_issued_at='2026-10-11',certificate_endorsed_at='2026-10-31')
        self.assertEqual(self.outcomes(p)['eu.issue-to-entry'],'date_window_consistent')
        self.assertEqual(self.outcomes(p)['eu.endorsement-to-check'],'date_window_consistent')
        p['appointments']['document_check_at']='2026-11-11';self.assertEqual(self.outcomes(p)['eu.endorsement-to-check'],'date_window_conflict')
        p['documents']['certificate_issued_at']='2026-10-10';self.assertEqual(self.outcomes(p)['eu.issue-to-entry'],'date_window_conflict')
        p['documents']['certificate_endorsed_at']='2026-11-11';self.assertEqual(self.outcomes(p)['eu.endorsement-before-departure'],'fail')

    def test_old_model_issue_and_aphis_endorsement_cutovers(self):
        p=self.profile();p['documents'].update(certificate_model='eu.577.ahc',certificate_issued_at='2026-09-30',certificate_endorsed_at='2026-10-01')
        out=self.outcomes(p);self.assertEqual(out['eu.certificate-model'],'model_date_consistent')
        self.assertEqual(out['eu.aphis-old-model-endorsement'],'fail')
        p['documents']['certificate_issued_at']='2026-10-01';self.assertEqual(self.outcomes(p)['eu.certificate-model'],'model_issue_cutoff_failed')

    def test_passport_us_revaccination_changes_return_documents(self):
        p=self.profile();p['documents'].update(eu_document_route='passport_return',passport_model='eu.705.passport',passport_issued_at='2026-05-01',passport_eu_vet_rabies=True,revaccinated_in_us=False)
        self.assertEqual(self.outcomes(p)['eu.passport-us-revaccination'],'pass')
        p['documents']['revaccinated_in_us']=True;self.assertEqual(self.outcomes(p)['eu.passport-us-revaccination'],'fail')
        self.assertNotIn('eu.endorsement-to-entry',self.outcomes(p));self.assertEqual(self.run_profile(p)['status'],'unsupported')

    def test_low_risk_history_missing_and_contradictory_stop_receipt_only(self):
        p=self.profile('eu-us')
        self.assertEqual(self.run_profile(p)['branch'],'us_dog_low_risk')
        p['journey']['history_complete']=False;self.assertNotIn('us.dog-age',self.outcomes(p))
        p['journey'].update(history_complete=True,last_high_risk_exit_at='2026-05-10')
        self.assertEqual(self.outcomes(p)['us.six-month-history'],'history_conflict')
        p['journey']['last_high_risk_exit_at']='2026-05-09';self.assertIn('us.dog-age',self.outcomes(p))
        p['journey']['last_high_risk_exit_at']='2026-11-11';self.assertEqual(self.outcomes(p)['us.history-date'],'invalid')

    def test_receipt_country_expiry_and_age_boundaries(self):
        p=self.profile('eu-us');p['documents'].update(receipt_departure_member='DE',receipt_expires_at='2026-11-09')
        out=self.outcomes(p);self.assertEqual(out['us.receipt-country'],'country_mismatch');self.assertEqual(out['us.receipt-not-expired'],'fail')
        for birth,expected in [('2026-05-10','pass'),('2026-05-11','fail')]:
            p['pet']['birth_date']=birth;self.assertEqual(self.outcomes(p)['us.dog-age'],expected)
        p['documents']['receipt_issued_at']='2026-05-10';self.assertEqual(self.outcomes(p)['us.receipt-six-months'],'date_window_consistent')
        p['documents']['receipt_issued_at']='2026-05-09';self.assertEqual(self.outcomes(p)['us.receipt-six-months'],'date_window_conflict')

    def test_high_risk_foreign_not_receipt_only(self):
        p=self.profile('eu-us');p['journey']['travel_history_branch']='high_risk_in_6_months'
        self.assertEqual(self.run_profile(p)['branch'],'us_dog_foreign_vaccinated_high_risk')
        self.assertNotIn('us.receipt-six-months',self.outcomes(p))
        self.assertIn('us.foreign-high-risk-package',self.outcomes(p))

    def test_us_vaccinated_form_before_original_departure_and_legacy_cutoff(self):
        p=self.profile('eu-us');p['journey'].update(travel_history_branch='high_risk_in_6_months',rabies_vaccine_origin='US',original_us_exit_at='2026-09-01')
        p['documents'].update(us_return_document='us_rabies_form',us_form_issued_at='2026-08-30',us_form_endorsed_at='2026-08-31',receipt_entry_at='2026-11-10')
        self.assertEqual(self.outcomes(p)['us.return-form-before-exit'],'pass')
        p['documents']['us_form_endorsed_at']='2026-09-02';self.assertEqual(self.outcomes(p)['us.return-form-before-exit'],'fail')
        p['documents']['us_return_document']='legacy_export'
        for issued,outcome in [('2025-07-31','pass'),('2025-08-01','fail')]:
            p['documents']['us_export_issued_at']=issued;self.assertEqual(self.outcomes(p)['us.legacy-export-cutoff'],outcome)
        p['documents'].pop('us_return_document');self.assertEqual(self.outcomes(p)['us.return-document'],'foreign_high_risk_fallback_required')

    def test_titre_wait_is_issue_not_arrival_and_no_list_exemption(self):
        p=self.profile();p['journey']['titre_branch']='test_required';p['events']['titre_sample_at']='2026-08-04'
        self.assertEqual(self.outcomes(p)['eu.titre-to-issue'],'fail')
        p['documents']['certificate_issued_at']='2026-11-02';self.assertEqual(self.outcomes(p)['eu.titre-to-issue'],'pass')
        for branch in ('listed_origin','return',None):
            p['journey']['titre_branch']=branch;self.assertEqual(self.outcomes(p)['eu.titre-branch'],'current_list_and_history_unreviewed')

    def test_round_trip_recomputes_current_rules_and_history(self):
        a,b=self.profile(),self.profile('eu-us');b['journey'].update(departure_at='2026-12-01',entry_at='2026-12-02',travel_history_branch='high_risk_in_6_months')
        r=assess_round_trip(a,b,assessment_at='2026-10-08',previous_dataset_version='0.1.0-week8')
        self.assertIn('dataset_changed_reassess_both_legs',r['reason_codes'])
        self.assertEqual(r['legs'][1]['branch'],'us_dog_foreign_vaccinated_high_risk')
        self.assertEqual(r['verified_feasible_route_count'],0)
        with self.assertRaises(ValueError):assess_round_trip(a,a,assessment_at='2026-10-08')
        b['pet']['species']='cat'
        with self.assertRaises(ValueError):assess_round_trip(a,b,assessment_at='2026-10-08')

    def test_privacy_immutability_dag_invalid_types(self):
        p=self.profile();p['contact']='PRIVATE';p['documents']['chip_number']='PRIVATE';p['responsibility']['carrying_role']='PRIVATE';before=deepcopy(p)
        r=self.run_profile(p);self.assertEqual(p,before);self.assertNotIn('PRIVATE',json.dumps(r))
        seen=set()
        for e in r['timeline']:self.assertTrue(set(e['depends_on'])<=seen);seen.add(e['event_id'])
        for group in ('journey','events','documents','responsibility'):
            bad=deepcopy(p);bad[group]=[]
            with self.assertRaises(ValueError):self.run_profile(bad)
        p['journey']['first_entry_member']=[]
        with self.assertRaises(ValueError):self.run_profile(p)

    def test_inventory_drift_duplicate_and_fake_review_rejected(self):
        inv=load_inventory();sources={s['id']:s for s in read_json(ROOT/'data/sources/catalog.json')['sources']}
        self.assertTrue(validators(ROOT)['us-eu.schema.json'].is_valid(inv));self.assertEqual(validate_us_eu(inv,sources),[])
        for kind in ('drift','duplicate','promote'):
            bad=deepcopy(inv)
            if kind=='drift':bad['evidence'][0]['url']='https://example.com/'
            if kind=='duplicate':bad['evidence'].append(deepcopy(bad['evidence'][0]))
            if kind=='promote':bad['reviewed_by']=['invented']
            self.assertTrue(validate_us_eu(bad,sources))

    def test_cli_and_bilingual_checklist_same_kernel(self):
        for direction in ('us-eu','eu-us'):
            for species in ('dog','cat'):
                cmd=[sys.executable,'-m','packages.cli',f'tests/fixtures/us-eu/{direction}-{species}.json','--us-eu-preview','--assessment-at','2026-10-08']
                r=self.run_profile(self.profile(direction,species))
                self.assertEqual(json.loads(subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,check=True).stdout),r)
                for lang in ('en','zh-CN'):
                    self.assertEqual(subprocess.run(cmd+['--format','checklist','--language',lang],cwd=ROOT,capture_output=True,text=True,check=True).stdout,checklist(r,language=lang))
