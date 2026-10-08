"""Synthetic delay/buffer regressions; date arithmetic never grants permission."""
from copy import deepcopy
import unittest
from packages.engine.windows import certificate_margin
from packages.engine.outbound import assess, checklist
from packages.engine.io import ROOT
from scripts.validate_data import read_json


class WindowTests(unittest.TestCase):
    def test_boundary_delay_and_buffer_never_extend_deadline(self):
        for check, buffer, outcome, remaining in [
            ('2026-11-10', 0, 'within_research_window', 0),
            ('2026-11-10', 1, 'buffer_shortfall', 0),
            ('2026-11-11', 0, 'expired', -1),
            ('2026-10-30', 0, 'check_before_issue', 11)]:
            r = certificate_margin('2026-10-31', check, 10, buffer_days=buffer)
            self.assertEqual(r['deadline'], '2026-11-10')
            self.assertEqual((r['outcome'], r['remaining_days']), (outcome, remaining))
            self.assertEqual(r['planning_margin_days'], remaining - buffer)
            self.assertFalse(r['enforceable'])

    def test_missing_invalid_overflow_and_no_hour_coercion(self):
        for start, check, outcome in [(None, '2026-11-10', 'missing_date'),
                ('bad', '2026-11-10', 'invalid_date'),
                ('2026-11-01', '2026-11-10T12:00:00+01:00', 'invalid_date'),
                ('9999-12-31', '9999-12-31', 'invalid_date')]:
            r = certificate_margin(start, check, 10)
            self.assertEqual(r['outcome'], outcome)
            self.assertIsNone(r['remaining_days'])
        for value in (True, -1, 366, '2', 1.5):
            with self.assertRaises(ValueError): certificate_margin(None, None, 10, buffer_days=value)

    def test_eu_actual_check_and_issuer_route_recompute(self):
        p = read_json(ROOT / 'tests/fixtures/outbound/cn-eu-dog.json')
        p['planning'] = {'buffer_days': 2}
        p['documents'].update(issuer_route='official_vet', certificate_issued_at='2026-11-01')
        p['appointments']['document_check_at'] = '2026-11-10'
        before = deepcopy(p); r = assess(p, assessment_at='2026-10-08')
        row = r['certificate_margins'][0]
        self.assertEqual(row['outcome'], 'buffer_shortfall')
        self.assertEqual(row['remaining_days'], 1)
        self.assertEqual(p, before)
        for lang in ('en', 'zh-CN'): self.assertIn('planning_margin_days=-1', checklist(r, language=lang))
        p['appointments']['document_check_at'] = '2026-11-12'
        r = assess(p, assessment_at='2026-10-08')
        self.assertEqual(r['certificate_margins'][0]['outcome'], 'expired')
        self.assertEqual(r['status'], 'unsupported')
        p['documents'].update(issuer_route='authorized_then_endorsed', certificate_endorsed_at='2026-11-05')
        self.assertEqual(assess(p, assessment_at='2026-10-08')['certificate_margins'][0]['deadline'], '2026-11-15')
        p['documents']['issuer_route'] = 'unknown'
        self.assertEqual(assess(p, assessment_at='2026-10-08')['certificate_margins'][0]['outcome'], 'issuer_route_unconfirmed')

    def test_us_signature_not_endorsement_and_cat_exclusion(self):
        p = read_json(ROOT / 'tests/fixtures/outbound/cn-us-dog.json')
        p['documents'].update(certificate_issued_at='2026-10-11', certificate_endorsed_at='2026-11-09')
        self.assertEqual(assess(p, assessment_at='2026-10-08')['certificate_margins'][0]['remaining_days'], 0)
        p['journey']['entry_at'] = '2026-11-11'
        self.assertEqual(assess(p, assessment_at='2026-10-08')['certificate_margins'][0]['outcome'], 'expired')
        p = read_json(ROOT / 'tests/fixtures/outbound/cn-us-cat.json')
        self.assertEqual(assess(p, assessment_at='2026-10-08')['certificate_margins'], [])
        p['journey']['purpose'] = 'unknown'
        self.assertEqual(assess(p, assessment_at='2026-10-08')['certificate_margins'], [])
