"""Public matrix derives from executed production engines, not hand-maintained claims."""
from copy import deepcopy
import json
import unittest
from packages.engine.io import ROOT
from packages.engine.handover import assess
from scripts.audit_coverage import markdown, run
from scripts.validate_data import read_json


class CoverageAuditTests(unittest.TestCase):
    def test_48_numbered_cases_reproduce_committed_artifacts(self):
        audit=run();self.assertEqual(audit['case_count'],48);self.assertEqual(audit['passed_count'],48)
        self.assertEqual(read_json(ROOT/'data/coverage/week9-audit.json'),audit)
        self.assertEqual((ROOT/'data/coverage/week9-matrix.md').read_text(),markdown(audit))
        self.assertEqual(audit['status_counts'],dict(unsupported=47,conditional=0,ineligible=1,verified_supported=0))
        self.assertEqual(audit['actual_usage_count'],0);self.assertEqual(audit['verified_feasible_route_count'],0)
        self.assertEqual(len(audit['six_direction_matrix']),6)
        self.assertTrue(all(set(x['species'])=={'dog','cat'} for x in audit['six_direction_matrix']))

    def test_bad_expectation_duplicate_and_fixture_escape_fail_audit(self):
        base=read_json(ROOT/'tests/fixtures/regressions/week9.json')
        for kind in ('expectation','duplicate','escape','short','synthetic'):
            bad=deepcopy(base)
            if kind=='expectation':bad['cases'][0]['expected']['status']='verified_supported'
            if kind=='duplicate':bad['cases'][1]['id']=bad['cases'][0]['id']
            if kind=='escape':bad['cases'][0]['fixture']='../WEEKLY_RULES.md'
            if kind=='short':bad['cases']=bad['cases'][:29]
            if kind=='synthetic':bad['synthetic']=False
            with self.assertRaises((ValueError,AssertionError)):run(manifest=bad)

    def record(self):
        return dict(arrival_time='2026-11-01T01:30:00-04:00',arrival_timezone='America/New_York',
                    pickup_deadline='2026-11-01T01:30:00-04:00',pickup_timezone='America/New_York',
                    overnight_required=True,overnight_care_available=None)

    def test_pickup_equal_deadline_dst_fold_and_nonexistent_time(self):
        h=self.record();self.assertEqual(assess(h)['pickup_outcome'],'within_reported_window')
        h['arrival_time']='2026-11-01T01:30:00-05:00';self.assertEqual(assess(h)['pickup_outcome'],'window_missed')
        h['arrival_time']='2026-03-08T02:30:00-05:00';self.assertEqual(assess(h)['pickup_outcome'],'invalid_time')
        h['arrival_time']='2026-11-01T01:30:00';self.assertEqual(assess(h)['pickup_outcome'],'invalid_time')

    def test_unknown_or_unassigned_overnight_never_becomes_confirmation(self):
        h=self.record();self.assertEqual(assess(h)['overnight_outcome'],'care_unknown')
        h['overnight_care_available']=True;self.assertEqual(assess(h)['overnight_outcome'],'custodian_unassigned')
        h['overnight_custodian_role']='owner';r=assess(h)
        self.assertEqual(r['overnight_outcome'],'self_reported_pending_confirmation')
        self.assertFalse(r['custody_confirmed']);self.assertEqual(r['external_confirmation'],'unknown')
        h['overnight_care_available']=False;self.assertEqual(assess(h)['status'],'blocked')
        self.assertEqual(assess({})['overnight_outcome'],'requirement_unknown')

    def test_unsafe_custody_and_nonboolean_controls_rejected(self):
        for record in [dict(custody_confirmed=True),dict(overnight_required='true'),dict(overnight_custodian_role='PRIVATE')]:
            with self.assertRaises(ValueError):assess(record)
        h=self.record();before=deepcopy(h);self.assertNotIn('arrival_time',assess(h));self.assertEqual(h,before)
