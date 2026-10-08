"""Executed regressions; synthetic verified records never enter data/rules."""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from packages.engine import compare, evaluate
from packages.engine.io import boundary_profile, load_repository

AS_OF = '2026-10-08'


def profile():
    return {'pet': {'species': 'dog', 'birth_date': '2020-01-31', 'service_animal': False,
                    'microchip_present': True, 'universal_scanner_readable': True},
            'journey': {'origin': 'EU', 'destination': 'US', 'entry_at': '2026-11-01',
                        'owner_entry_at': '2026-11-01', 'purpose': 'relocation',
                        'ownership_transfer': False, 'accompaniment': 'owner',
                        'transport_mode': 'cabin', 'travel_history_branch': 'only_low_risk_6_months',
                        'carrier_acceptance': 'unknown', 'pets_per_person': 1},
            'documents': {'cdc_receipt_present': True},
            'events': {}}


def synthetic(rule):
    """In-memory hypothetical review metadata; these are not human signatures."""
    r = deepcopy(rule)
    r['review'] = {'status': 'verified', 'last_verified_at': AS_OF,
                   'review_due_at': '2027-01-01', 'reviewed_by': [
                       {'id': 'SYNTHETIC-NOT-A-PERSON-A', 'role': 'human_domain_reviewer', 'reviewed_at': AS_OF},
                       {'id': 'SYNTHETIC-NOT-A-PERSON-B', 'role': 'human_domain_reviewer', 'reviewed_at': AS_OF}]}
    r['validity']['effective_from'] = '2024-08-01'
    r['pending_checks'] = []
    r['scope']['exclusions'] = {'en': 'Synthetic constraint-only scope; not a route.',
                                'zh-CN': '合成单项条件范围，不是路线。'}
    return r


class ExpressionTests(unittest.TestCase):
    def test_five_shapes_positive_negative_missing_and_invalid(self):
        cases = [
            ({'field': 'pet.microchip_present', 'operator': 'equals', 'value': True},
             {'pet': {'microchip_present': True}}, {'pet': {'microchip_present': False}},
             {'pet': {'microchip_present': 'true'}}),
            ({'field': 'journey.pets_per_person', 'operator': 'at_most', 'value': 1},
             {'journey': {'pets_per_person': 1}}, {'journey': {'pets_per_person': 2}},
             {'journey': {'pets_per_person': True}}),
            ({'field': 'pet.birth_date', 'operator': 'calendar_age_at_least', 'unit': 'month',
              'value': 6, 'anchor': 'journey.entry_at'},
             {'pet': {'birth_date': '2026-03-01'}, 'journey': {'entry_at': '2026-09-01'}},
             {'pet': {'birth_date': '2026-03-01'}, 'journey': {'entry_at': '2026-08-30'}},
             {'pet': {'birth_date': '2026-02-30'}, 'journey': {'entry_at': '2026-11-01'}}),
            ({'field': 'events.identification_at', 'operator': 'on_or_before',
              'other_field': 'events.rabies_vaccination_at'},
             {'events': {'identification_at': '2026-01-01', 'rabies_vaccination_at': '2026-01-01'}},
             {'events': {'identification_at': '2026-01-02', 'rabies_vaccination_at': '2026-01-01'}},
             {'events': {'identification_at': 'bad', 'rabies_vaccination_at': '2026-01-01'}}),
            ({'field': 'events.primary_protocol_completed_at', 'operator': 'elapsed_at_least',
              'value': 21, 'unit': 'day', 'anchor': 'journey.entry_at'},
             {'events': {'primary_protocol_completed_at': '2026-03-08'}, 'journey': {'entry_at': '2026-03-29'}},
             {'events': {'primary_protocol_completed_at': '2026-03-08'}, 'journey': {'entry_at': '2026-03-28'}},
             {'events': {'primary_protocol_completed_at': '2026-03-08T01:00:00-05:00'}, 'journey': {'entry_at': '2026-03-29'}}),
        ]
        for req, positive, negative, invalid in cases:
            with self.subTest(operator=req['operator']):
                for expected, inp in [('pass', positive), ('fail', negative), ('missing', {}), ('invalid', invalid)]:
                    self.assertEqual(compare(req, inp)['outcome'], expected)

    def test_month_end_and_leap_day(self):
        req = {'field': 'pet.birth_date', 'operator': 'calendar_age_at_least', 'unit': 'month',
               'value': 1, 'anchor': 'journey.entry_at'}
        for birth, entry, result in [('2024-01-31', '2024-02-29', 'pass'),
                                     ('2024-01-31', '2024-02-28', 'fail'),
                                     ('2025-01-31', '2025-02-28', 'pass')]:
            self.assertEqual(compare(req, {'pet': {'birth_date': birth}, 'journey': {'entry_at': entry}})['outcome'], result)
        req['value'] = 12
        self.assertEqual(compare(req, {'pet': {'birth_date': '2024-02-29'}, 'journey': {'entry_at': '2025-02-28'}})['outcome'], 'pass')

    def test_weeks_and_reversed_dates(self):
        req = {'field': 'pet.birth_date', 'operator': 'calendar_age_at_least', 'unit': 'week',
               'value': 12, 'anchor': 'events.rabies_vaccination_at'}
        for entry, result in [('2026-03-26', 'pass'), ('2026-03-25', 'fail'), ('2025-12-31', 'fail')]:
            self.assertEqual(compare(req, {'pet': {'birth_date': '2026-01-01'}, 'events': {'rabies_vaccination_at': entry}})['outcome'], result)

    def test_nonfinite_fractional_negative_counts(self):
        req = {'field': 'journey.pets_per_person', 'operator': 'at_most', 'value': 1}
        for value in [float('nan'), float('inf'), -1, 0, 0.5, '1']:
            self.assertEqual(compare(req, {'journey': {'pets_per_person': value}})['outcome'], 'invalid')


class EngineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rules = load_repository()
        cls.age = next(r for r in cls.rules if r['id'] == 'us.cdc.dog.low-risk.minimum-age')

    def assess(self, p=None, rules=None, **kwargs):
        records = rules if rules is not None else [synthetic(self.age)]
        if kwargs.get('coverage_gaps') == []:
            kwargs.setdefault('resolved_scope_rule_ids', [r['id'] for r in records])
        return evaluate(p or profile(), records, assessment_at=AS_OF, **kwargs)

    def test_all_nine_week2_boundaries(self):
        paths = list((ROOT / 'tests/fixtures/boundaries').glob('*.json'))
        self.assertEqual(len(paths), 9)
        for path in paths:
            case = json.loads(path.read_text())
            with self.subTest(case=case['id']):
                selected = [r for r in self.rules if r['id'] in case['rule_ids']]
                result = self.assess(boundary_profile(case['input']), selected)
                self.assertEqual(result['status'], case['expected']['status'])
                self.assertTrue(set(case['expected']['reason_codes']) <= set(result['reason_codes']))
                self.assertEqual(result['not_applicable_rule_ids'], case['expected']['not_applicable_rule_ids'])

    def test_synthetic_eligible_preserves_unknown_acceptance(self):
        result = self.assess(coverage_gaps=[])
        self.assertEqual(result['status'], 'eligible')
        self.assertEqual(result['external_progress']['carrier_acceptance'], 'unknown')
        self.assertFalse(result['booking_confirmed'])
        row = result['explanations'][0]
        self.assertEqual(row['revision'], 1)
        self.assertTrue(row['evidence'][0]['url'].startswith('https://www.cdc.gov/'))
        self.assertTrue(row['evidence'][0]['locator'])

    def test_missing_and_failure_statuses(self):
        p = profile(); p['pet']['birth_date'] = None
        self.assertEqual(self.assess(p, coverage_gaps=[])['status'], 'conditional')
        p['pet']['birth_date'] = '2026-10-01'
        self.assertEqual(self.assess(p, coverage_gaps=[])['status'], 'ineligible')
        r = synthetic(self.age); r['on_fail'] = 'needs_confirmation'
        self.assertEqual(self.assess(p, [r], coverage_gaps=[])['status'], 'conditional')

    def test_unreviewed_states_never_enforce(self):
        p = profile(); p['pet']['birth_date'] = '2026-10-01'
        for status in ('draft', 'stale', 'disputed', 'retired'):
            r = deepcopy(self.age); r['review']['status'] = status
            result = self.assess(p, [r], coverage_gaps=[])
            self.assertEqual(result['status'], 'unsupported')
            self.assertFalse(result['explanations'][0]['enforceable'])

    def test_expired_future_and_invalid_review(self):
        for mutate in [lambda r: r['review'].update(review_due_at=AS_OF),
                       lambda r: r['review'].update(last_verified_at='2026-10-09'),
                       lambda r: r['review'].update(reviewed_by=[]),
                       lambda r: r['validity'].update(effective_from=None),
                       lambda r: r['validity'].update(effective_from='2026-12-01'),
                       lambda r: r['validity'].update(effective_to='2026-10-31'),
                       lambda r: r['review'].update(review_due_at='2026-11-01')]:
            r = synthetic(self.age); mutate(r)
            self.assertEqual(self.assess(rules=[r], coverage_gaps=[])['status'], 'unsupported')

    def test_scope_before_comparison(self):
        for field, value in [('species', 'cat'), ('species', 'ferret')]:
            p = profile(); p['pet'][field] = value; p['pet']['birth_date'] = 'bad'
            result = self.assess(p, coverage_gaps=[])
            self.assertEqual(result['explanations'][0]['outcome'], 'not_applicable')
            self.assertNotIn('invalid_input', result['reason_codes'])
        p = profile(); p['journey']['travel_history_branch'] = 'high_risk_in_6_months'
        self.assertEqual(self.assess(p, coverage_gaps=[])['status'], 'unsupported')

    def test_classification_and_transport_missing_never_allow(self):
        for field, value in [('purpose', 'unknown'), ('ownership_transfer', True),
                             ('ownership_transfer', None), ('accompaniment', None),
                             ('transport_mode', None), ('travel_history_branch', None)]:
            p = profile(); p['journey'][field] = value
            self.assertNotEqual(self.assess(p, coverage_gaps=[])['status'], 'eligible')
        p = profile(); p['pet']['service_animal'] = True
        self.assertEqual(self.assess(p, coverage_gaps=[])['status'], 'unsupported')

    def test_owner_timing_and_owner_not_moving(self):
        r = synthetic(next(r for r in self.rules if r['id'] == 'eu.ec.rabies.minimum-vaccination-age'))
        p = profile(); p['journey'].update(origin='US', destination='EU', accompaniment='authorized_person')
        p['events']['rabies_vaccination_at'] = '2026-01-01'
        p['journey']['owner_entry_at'] = '2026-10-27'
        self.assertEqual(self.assess(p, [r], coverage_gaps=[])['status'], 'eligible')
        for change in [{'owner_entry_at': '2026-10-26'}, {'owner_entry_at': None},
                       {'purpose': 'boarding_without_owner_travel'}, {'accompaniment': 'unaccompanied'}]:
            other = deepcopy(p); other['journey'].update(change)
            self.assertEqual(self.assess(other, [r], coverage_gaps=[])['status'], 'unsupported')

    def test_exceptions_require_confirmation(self):
        r = synthetic(self.age); r['exceptions'] = [{'id': 'synthetic.exception'}]
        p = profile(); p['pet']['birth_date'] = '2026-10-01'
        self.assertEqual(self.assess(p, [r], coverage_gaps=[])['status'], 'conditional')

    def test_empty_duplicate_and_exclusions_are_gaps(self):
        self.assertEqual(self.assess(rules=[], coverage_gaps=[])['status'], 'unsupported')
        r = synthetic(self.age)
        self.assertEqual(self.assess(rules=[r, r], coverage_gaps=[])['status'], 'unsupported')
        r['scope']['exclusions']['en'] = 'unreviewed destination state'
        self.assertEqual(self.assess(rules=[r], coverage_gaps=[], resolved_scope_rule_ids=[])['status'], 'unsupported')
        self.assertEqual(self.assess()['status'], 'unsupported')

    def test_synthetic_records_follow_schema(self):
        from scripts.validate_data import validators
        checker = validators(ROOT)['rule.schema.json']
        for rule in self.rules:
            checker.validate(synthetic(rule))

    def test_public_package_remains_unsupported(self):
        self.assertTrue(all(r['review']['status'] == 'draft' for r in self.rules))
        self.assertEqual(self.assess(rules=self.rules)['status'], 'unsupported')

    def test_declined_carrier_does_not_rewrite_rule_status(self):
        p = profile(); p['journey']['carrier_acceptance'] = 'declined'
        result = self.assess(p, coverage_gaps=[])
        self.assertEqual(result['status'], 'eligible')
        self.assertEqual(result['external_progress']['carrier_acceptance'], 'declined')
        self.assertFalse(result['booking_confirmed'])

    def test_deterministic_without_mutation(self):
        p, rules = profile(), [synthetic(self.age)]
        before = deepcopy((p, rules))
        result = self.assess(p, rules, coverage_gaps=[])
        self.assertEqual(result, self.assess(p, rules, coverage_gaps=[]))
        self.assertEqual((p, rules), before)

    def test_cli_offline_and_errors(self):
        cmd = [sys.executable, '-m', 'packages.cli', 'tests/fixtures/boundaries/boundary.unknown-carrier.json', '--assessment-at', AS_OF]
        result = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, env={'PATH': '/nonexistent'})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['status'], 'unsupported')
        result = subprocess.run(cmd[:-1] + ['not-a-date'], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn('FAIL', result.stderr)


if __name__ == '__main__':
    unittest.main()
