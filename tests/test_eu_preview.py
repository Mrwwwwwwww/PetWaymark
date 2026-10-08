"""Synthetic EU branches; no test input constitutes legal or document approval."""
from copy import deepcopy
import json
import subprocess
import sys
import unittest

from packages.engine.io import ROOT, load_repository
from packages.engine.evaluate import evaluate
from packages.engine.eu import assess, checklist, document_diagnostic, identification_diagnostic, load_inventory, titre_diagnostics
from scripts.validate_data import read_json, validate_eu_inventory, validators


class EUPreviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rules = load_repository()
        cls.inventory = load_inventory()
        cls.sources = {s['id']: s for s in read_json(ROOT / 'data/sources/catalog.json')['sources']}

    def profile(self, name='cross-member'):
        return read_json(ROOT / f'tests/fixtures/eu/{name}.json')

    def assess(self, p):
        return assess(p, assessment_at='2026-10-08', rules=self.rules, inventory=self.inventory)

    def test_domestic_and_cross_member_dog_cat_examples(self):
        for member in ('DE','FR','NL'):
            for destination in ('DE','FR','NL'):
                for species in ('dog','cat'):
                    p=self.profile();p['journey'].update(origin_member=member,destination_member=destination);p['pet']['species']=species
                    r=self.assess(p)
                    self.assertTrue(r['classification_resolved'])
                    self.assertEqual(r['status'],'unsupported');self.assertFalse(r['booking_confirmed'])
                    self.assertEqual(r['candidates'],[]);self.assertEqual(r['recommendations'],[])
                    self.assertEqual(r['verified_feasible_route_count'],0)
                    self.assertEqual(bool(r['explanations']),member!=destination)

    def test_domestic_does_not_impose_cross_member_dates_documents(self):
        p=self.profile('domestic');p['journey'].pop('owner_entry_at');p['journey'].pop('owner_moving');p.pop('documents');p.pop('events')
        r=self.assess(p);self.assertTrue(r['classification_resolved']);self.assertEqual(r['draft_diagnostics'],[])
        self.assertIn('eu_domestic_rules_unreviewed',r['reason_codes'])
        r=evaluate(p,self.rules,assessment_at='2026-10-08')
        for row in r['explanations']:
            if row['rule_id'].startswith('eu.ec.intra.'):
                self.assertEqual(row['outcome'],'not_applicable')

    def test_owner_not_moving_stops_before_diagnostics(self):
        for purpose in ('boarding_without_owner_travel','holiday','relocation'):
            p=self.profile('owner-not-moving');p['journey']['purpose']=purpose
            r=self.assess(p);self.assertFalse(r['classification_resolved'])
            self.assertIn('owner_not_moving_separate_classification',r['reason_codes'])
            self.assertEqual(r['explanations'],[]);self.assertEqual(r['draft_diagnostics'],[])

    def test_unknown_classification_and_invalid_owner_dates_stop(self):
        for key,value in [('purpose','unknown'),('ownership_transfer',None),('accompaniment','unknown'),('owner_moving',None),('destination_member','GB'),('origin_member',None),('owner_entry_at','2026-02-30')]:
            p=self.profile();p['journey'][key]=value
            r=self.assess(p);self.assertFalse(r['classification_resolved']);self.assertEqual(r['explanations'],[])

    def test_authorized_person_five_days_both_sides_and_written_authority(self):
        for date,ok in [('2026-11-05',True),('2026-11-15',True),('2026-11-04',False),('2026-11-16',False)]:
            p=self.profile();p['journey'].update(accompaniment='authorized_person',authorized_person_written=True,owner_entry_at=date)
            self.assertEqual(self.assess(p)['classification_resolved'],ok)
        for value in (None,False,'true'):
            p=self.profile();p['journey'].update(accompaniment='authorized_person',authorized_person_written=value)
            self.assertFalse(self.assess(p)['classification_resolved'])

    def test_cargo_does_not_define_legal_classification(self):
        p=self.profile();p['journey']['transport_mode']='manifest_cargo'
        self.assertTrue(self.assess(p)['classification_resolved'])
        p['journey']['accompaniment']='unaccompanied'
        self.assertFalse(self.assess(p)['classification_resolved'])

    def test_all_intra_constraints_positive_negative_missing_invalid(self):
        for rule in self.rules:
            if rule['scope']['movement_category']!='intra_eu_pet':continue
            field=rule['requirement']['field'];group,key=field.split('.')
            bad={'pet.birth_date':'2026-09-01','events.identification_at':'2026-09-02','events.primary_protocol_completed_at':'2026-11-01'}[field]
            for value,outcome in [(self.profile()[group][key],'pass'),(bad,'fail'),(None,'missing'),('bad-date','invalid')]:
                p=self.profile();p[group][key]=value
                r=evaluate(p,[rule],assessment_at='2026-10-08');row=r['explanations'][0]
                self.assertEqual(row['outcome'],outcome);self.assertFalse(row['enforceable']);self.assertEqual(r['status'],'unsupported')

    def test_tattoo_cutoff_readability_missing_and_invalid(self):
        for date,readable,outcome in [('2011-07-02',True,'exception_needs_confirmation'),('2011-07-03',True,'tattoo_exception_not_met'),('2011-07-02',False,'tattoo_exception_not_met'),(None,True,'missing'),('2011-02-30',True,'invalid'),('2011-07-02','true','invalid')]:
            p=self.profile();p['pet'].update(identification_method='tattoo',tattoo_readable=readable);p['events']['tattoo_at']=date
            r=identification_diagnostic(p);self.assertEqual(r['outcome'],outcome);self.assertFalse(r['enforceable'])

    def test_passport_transition_issued_before_not_expiry(self):
        for date,outcome in [('2027-12-31','model_date_consistent'),('2028-01-01','model_issue_cutoff_failed')]:
            p=self.profile();p['journey']['entry_at']='2028-01-10';p['documents'].update(passport_issued_at=date)
            self.assertEqual(document_diagnostic(p,self.inventory,scope='intra_eu')['outcome'],outcome)
        p=self.profile();p['journey']['entry_at']='2030-01-01'
        self.assertEqual(document_diagnostic(p,self.inventory,scope='intra_eu')['outcome'],'model_date_consistent')

    def test_health_certificate_issue_and_recognition_cutoffs(self):
        for issue,entry,outcome in [('2026-09-30','2026-10-08','model_date_consistent'),('2026-10-01','2026-10-08','model_issue_cutoff_failed'),('2026-09-30','2027-04-01','model_recognition_period_ended')]:
            p=self.profile();p['journey']['entry_at']=entry;p['documents'].update(certificate_model='eu.577.ahc',certificate_issued_at=issue)
            self.assertEqual(document_diagnostic(p,self.inventory,scope='third_country_entry')['outcome'],outcome)
        # Consistent model is not proof of the 10-day window or full certificate validity.
        p=self.profile();p['journey']['entry_at']='2026-12-01';p['documents'].update(certificate_model='eu.577.ahc',certificate_issued_at='2026-09-30')
        self.assertFalse(document_diagnostic(p,self.inventory,scope='third_country_entry')['enforceable'])

    def test_document_missing_invalid_model_future_issue(self):
        for model,issue,outcome in [(None,None,'missing'),('unknown','2026-10-01','unsupported_model'),('eu.705.passport','2026-02-30','invalid'),('eu.705.passport','2026-11-11','invalid'),('eu.705.passport','2026-04-21','model_not_yet_applicable')]:
            p=self.profile();p['documents'].update(passport_model=model,passport_issued_at=issue)
            self.assertEqual(document_diagnostic(p,self.inventory,scope='intra_eu')['outcome'],outcome)

    def test_titre_wait_uses_issue_not_entry_and_exemptions_never_pass(self):
        p=self.profile();p['journey'].update(titre_branch='test_required',entry_at='2027-01-01');p['events']['titre_sample_at']='2026-10-01';p['documents']['certificate_issued_at']='2026-12-29'
        self.assertEqual(titre_diagnostics(p)[1]['outcome'],'fail')
        p['documents']['certificate_issued_at']='2026-12-30'
        self.assertEqual(titre_diagnostics(p)[1]['outcome'],'pass')
        for branch in ('listed_origin','return','secured_transit','unknown',None):
            p['journey']['titre_branch']=branch
            self.assertNotEqual(titre_diagnostics(p)[0]['outcome'],'pass')

    def test_inventory_27_members_and_24_explicit_local_gaps(self):
        self.assertTrue(validators(ROOT)['eu-members.schema.json'].is_valid(self.inventory))
        rows=self.inventory['members'];self.assertEqual(len(rows),27)
        self.assertEqual(sum(m['status']=='local_overlay_uncovered' for m in rows),24)
        self.assertTrue(all(m['rule_ids']==[] for m in rows))
        p=self.profile();p['journey']['destination_member']='IE';r=self.assess(p)
        self.assertTrue(r['classification_resolved']);self.assertEqual(r['status'],'unsupported')

    def test_inventory_rejects_evidence_promotion_duplicate_and_drift(self):
        mapping={r['id']:r for r in self.rules}
        self.assertEqual(validate_eu_inventory(self.inventory,self.sources,mapping),[])
        for change in ('duplicate','drift','unavailable','promotion'):
            inv=deepcopy(self.inventory)
            if change=='duplicate':inv['members'][1]['member']=inv['members'][0]['member']
            if change=='drift':inv['framework']['evidence'][0]['accessed_at']='2026-10-07'
            if change=='unavailable':inv['framework']['evidence'][0]['source_id']='eu.law.2026-131'
            if change=='promotion':inv['members'][0]['status']='partial_read_pending_review'
            self.assertTrue(validate_eu_inventory(inv,self.sources,mapping))

    def test_checklists_redact_private_inputs_and_do_not_mutate(self):
        p=self.profile();p['contact']='PRIVATE-MARKER';before=deepcopy(p);r=self.assess(p)
        for language in ('en','zh-CN'):
            output=checklist(r,language=language);self.assertNotIn('PRIVATE-MARKER',output)
            self.assertIn('2026_131_full_text_unavailable',output);self.assertIn('local_overlay_uncovered',output)
            self.assertIn('eu.577.ahc',output);self.assertIn('2011',output)
        self.assertEqual(p,before)

    def test_cli_json_and_bilingual_checklist_share_eu_assessment(self):
        for name in ('domestic','cross-member','owner-not-moving'):
            args=[sys.executable,'-m','packages.cli',str(ROOT/f'tests/fixtures/eu/{name}.json'),
                  '--eu-preview','--assessment-at','2026-10-08']
            completed=subprocess.run(args,cwd=ROOT,capture_output=True,text=True,check=True)
            self.assertEqual(json.loads(completed.stdout),self.assess(self.profile(name)))
            for language in ('en','zh-CN'):
                completed=subprocess.run(args+['--format','checklist','--language',language],cwd=ROOT,capture_output=True,text=True,check=True)
                self.assertEqual(completed.stdout,checklist(self.assess(self.profile(name)),language=language))
