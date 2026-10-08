"""Executed domestic path and handover regressions; no real inventory is invented."""
from copy import deepcopy
import json
import subprocess
import sys
import unittest

from packages.engine.io import ROOT
from packages.engine.routes import checklist, load_graph, paths, preview
from scripts.validate_data import read_json


class RouteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.graph = load_graph()
        cls.owner = read_json(ROOT / 'tests/fixtures/domestic/owner.json')

    def run_preview(self, profile=None, graph=None, corridor='dom.cn.east'):
        return preview(self.owner if profile is None else profile,
                       self.graph if graph is None else graph,
                       corridor_id=corridor, assessment_at='2026-10-08')

    def test_two_cn_corridors_include_road_rail_and_air(self):
        for corridor in ('dom.cn.east', 'dom.cn.south'):
            with self.subTest(corridor=corridor):
                result = self.run_preview(corridor=corridor)
                self.assertEqual(result['status'], 'unsupported')
                self.assertEqual(len(result['candidates']), 3)
                self.assertEqual({s['mode'] for c in result['candidates'] for s in c['segments']},
                                 {'road', 'rail', 'checked_baggage'})
                self.assertEqual(result['recommendations'], [])
                self.assertEqual(result['verified_feasible_route_count'], 0)
                self.assertFalse(result['booking_confirmed'])
                for c in result['candidates']:
                    self.assertIsNone(c['door_to_door_minutes'])
                    self.assertIsNone(c['total_cost_cny'])
                    self.assertFalse(c['ranked'])

    def test_unaccompanied_products_are_separate(self):
        profile = read_json(ROOT / 'tests/fixtures/domestic/unaccompanied.json')
        for corridor in ('dom.cn.east', 'dom.cn.south'):
            result = self.run_preview(profile, corridor=corridor)
            self.assertEqual(len(result['candidates']), 2)
            products = {s['product'] for c in result['candidates'] for s in c['segments']}
            self.assertIn('rail_unaccompanied', products)
            self.assertIn('unaccompanied_animal_carrier', products)
            self.assertNotIn('owner_vehicle', products)
            self.assertFalse(any('baggage' in p for p in products))

    def test_explicit_infeasible_counterexample(self):
        p = read_json(ROOT / 'tests/fixtures/domestic/infeasible.json')
        r = self.run_preview(p)
        self.assertEqual(r['status'], 'ineligible')
        self.assertEqual(r['candidates'], [])
        reasons = {reason for c in r['excluded'] for reason in c['reason_codes']}
        self.assertTrue({'driving_unavailable', 'segment_declined', 'handover_window_missed'} <= reasons)
        self.assertFalse(r['booking_confirmed'])

    def test_declined_final_transfer_excludes_air_only(self):
        p = deepcopy(self.owner)
        p['preview']['segments'] = {'cn.east.can-egress': {'reported_acceptance': 'declined'}}
        r = self.run_preview(p)
        self.assertEqual(len(r['candidates']), 2)
        self.assertFalse(any('cn.east.air' in c['segment_ids'] for c in r['candidates']))
        self.assertTrue(any('segment_declined' in c['reason_codes'] for c in r['excluded']))

    def test_missed_access_window_excludes_rail(self):
        p = deepcopy(self.owner)
        p['preview']['segments'] = {'cn.east.rail-access': {'handover_window_met': False}}
        r = self.run_preview(p)
        self.assertFalse(any('rail' in s['mode'] for c in r['candidates'] for s in c['segments']))

    def test_missing_drive_readiness_stays_unknown(self):
        p = deepcopy(self.owner)
        p['preview'].pop('can_drive')
        r = self.run_preview(p)
        drive = next(c for c in r['candidates'] if c['segment_ids'] == ['cn.east.drive'])
        self.assertIn('driving_readiness_unknown', drive['reason_codes'])
        self.assertEqual(drive['status'], 'unsupported')

    def test_each_draft_limit_positive_negative_missing_invalid(self):
        leg = next(s for s in self.graph['segments'] if s['product'] == 'rail_owner_accompanied')
        for limit in leg['limits']:
            field = limit['field'].split('.')[1]
            for value, expected in ((limit['maximum'], 'pass'), (limit['maximum'] + .1, 'fail'),
                                    (None, 'missing'), ('15', 'invalid'), (True, 'invalid'),
                                    (float('nan'), 'invalid'), (0, 'invalid')):
                with self.subTest(field=field, value=value):
                    p = deepcopy(self.owner)
                    p['pet'][field] = value
                    r = self.run_preview(p)
                    row = next(s for c in r['candidates'] for s in c['segments']
                               if s['segment_id'] == leg['segment_id'])
                    d = next(d for d in row['draft_diagnostics'] if d['field'] == limit['field'])
                    self.assertEqual(d['outcome'], expected)
                    self.assertFalse(d['enforceable'])
                    self.assertEqual(row['status'], 'unsupported')

    def test_classification_precedes_graph_construction(self):
        for group, field, value in (('pet', 'species', 'rabbit'), ('pet', 'service_animal', True),
                                    ('journey', 'ownership_transfer', True), ('journey', 'purpose', 'sale'),
                                    ('journey', 'origin', 'US'), ('journey', 'pets_per_person', 2),
                                    ('journey', 'accompaniment', None)):
            p = deepcopy(self.owner)
            p[group][field] = value
            r = self.run_preview(p)
            self.assertEqual(r['status'], 'unsupported')
            self.assertEqual(r['candidates'], [])
            self.assertEqual(r['excluded'], [])
            self.assertTrue(r['reason_codes'])

    def test_missing_travel_date_does_not_build_paths(self):
        p = deepcopy(self.owner)
        del p['journey']['entry_at']
        r = self.run_preview(p)
        self.assertIn('travel_date_unknown', r['reason_codes'])
        self.assertEqual(r['candidates'], [])

    def test_cn_import_rules_are_not_applied_domestically(self):
        r = self.run_preview()
        self.assertTrue(all(s['rule_assessment']['matched_rule_ids'] == []
                            for c in r['candidates'] for s in c['segments']))
        self.assertTrue(all('applicable_rules_uncovered' in s['rule_assessment']['coverage_gaps']
                            for c in r['candidates'] for s in c['segments']))

    def test_stable_ids_after_graph_reordering(self):
        graph = deepcopy(self.graph)
        graph['segments'].reverse()
        graph['nodes'].reverse()
        self.assertEqual(self.run_preview(), self.run_preview(graph=graph))

    def test_explicit_revision_preserves_segment_identity(self):
        p = deepcopy(self.owner)
        p['preview']['plan_revision'] = 2
        p['journey']['entry_at'] = '2026-11-11'
        a, b = self.run_preview(), self.run_preview(p)
        self.assertEqual([c['segment_ids'] for c in a['candidates']], [c['segment_ids'] for c in b['candidates']])
        self.assertEqual(b['plan_revision'], 2)

    def test_no_implicit_reverse_or_cycles(self):
        graph = deepcopy(self.graph)
        corridor = graph['corridors'][0]
        self.assertEqual(paths(graph, corridor['destination_node'], corridor['origin_node']), [])
        cycle = deepcopy(graph['segments'][0])
        cycle.update(segment_id='synthetic.cycle', from_node='cn.pvg', to_node='cn.huzhou')
        graph['segments'].append(cycle)
        self.assertEqual(self.run_preview(), self.run_preview(graph=graph))

    def test_missing_physical_connection_is_visible(self):
        graph = deepcopy(self.graph)
        graph['segments'] = []
        r = self.run_preview(graph=graph)
        self.assertEqual(r['status'], 'unsupported')
        self.assertIn('no_connected_path', r['reason_codes'])

    def test_inputs_unchanged_and_private_profile_not_exported(self):
        p, graph = deepcopy(self.owner), deepcopy(self.graph)
        p['documents'] = {'secret': 'PRIVATE-RAW-DOCUMENT'}
        p['owner'] = {'address': 'PRIVATE-EXACT-ADDRESS'}
        before = deepcopy((p, graph))
        r = self.run_preview(p, graph)
        self.assertEqual((p, graph), before)
        self.assertNotIn('PRIVATE-', json.dumps(r))

    def test_bilingual_checklist_preserves_status_ids_and_pending_roles(self):
        r = self.run_preview()
        before = deepcopy(r)
        for lang, pending in (('zh-CN', '待安排'), ('en', 'pending arrangement')):
            text = checklist(r, self.graph, language=lang)
            self.assertIn('unsupported', text)
            self.assertIn(pending, text)
            self.assertIn('cn.east.air', text)
            self.assertIn('https://www.rails.cn/', text)
        self.assertEqual(r, before)

    def test_untrusted_controls_cannot_promote_or_assign(self):
        for override in ({'reported_acceptance': 'externally_confirmed'}, {'handover_window_met': 'false'},
                         {'roles': {'custodian': 'carrier'}}, {'coverage_gaps': []}):
            p = deepcopy(self.owner)
            p['preview']['segments'] = {'cn.east.air': override}
            with self.assertRaises(ValueError):
                self.run_preview(p)

    def test_invalid_controls_and_dates_rejected(self):
        for controls in ({'can_drive': 'false'}, {'plan_revision': True}, {'journey_id': 'Someone@example.com'},
                         {'segments': {'unknown.segment': {}}}, {'booking_confirmed': True}):
            p = deepcopy(self.owner)
            p['preview'] = controls
            with self.assertRaises(ValueError):
                self.run_preview(p)
        with self.assertRaises(ValueError):
            preview(self.owner, self.graph, corridor_id='dom.cn.east', assessment_at='2026-02-30')
        p = deepcopy(self.owner)
        p['journey']['entry_at'] = '2026-11-10T10:00:00Z'
        with self.assertRaises(ValueError):
            self.run_preview(p)

    def test_cli_json_and_print_without_model_key(self):
        command = [sys.executable, '-m', 'packages.cli', 'tests/fixtures/domestic/infeasible.json',
                   '--corridor', 'dom.cn.east', '--assessment-at', '2026-10-08']
        run = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(json.loads(run.stdout)['status'], 'ineligible')
        run = subprocess.run(command + ['--format', 'checklist', '--language', 'en'],
                             cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertIn('pending arrangement', run.stdout)
        self.assertIn('segment_declined', run.stdout)
