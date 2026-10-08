"""Synthetic mutation checks prevent research gaps being promoted to transport."""
from copy import deepcopy
import unittest
from packages.engine.io import ROOT
from scripts.validate_data import read_json, validators, validate_deep_review


class DeepReviewTests(unittest.TestCase):
    def setUp(self):
        self.inventory = read_json(ROOT / 'data/coverage/week11-deep-review.json')
        self.graph = read_json(ROOT / 'data/corridors/cn-preview.json')
        self.sources = {s['id']: s for s in read_json(ROOT / 'data/sources/catalog.json')['sources']}

    def test_two_complete_research_chains_remain_unsupported(self):
        validators(ROOT)['deep-review.schema.json'].validate(self.inventory)
        self.assertEqual(validate_deep_review(self.inventory, self.graph, self.sources), [])
        self.assertEqual(sum(len(c['segments']) for c in self.inventory['corridors']), 18)
        self.assertEqual(self.inventory['verified_feasible_routes'], 0)

    def test_listing_or_licence_cannot_promote_capacity(self):
        for field in ('registration', 'license_status', 'capability', 'dated_acceptance'):
            bad = deepcopy(self.inventory)
            bad['ground_qualification_checks'][0][field] = 'confirmed'
            self.assertFalse(validators(ROOT)['deep-review.schema.json'].is_valid(bad))
        bad = deepcopy(self.inventory); bad['corridors'][0]['status'] = 'eligible'
        self.assertFalse(validators(ROOT)['deep-review.schema.json'].is_valid(bad))

    def test_scope_missing_leg_and_source_drift_fail(self):
        for change in ('missing', 'product', 'jurisdiction', 'evidence'):
            bad = deepcopy(self.inventory)
            leg = bad['corridors'][0]['segments'][0]
            if change == 'missing': bad['corridors'][0]['segments'].pop()
            if change == 'product': leg['product'] = 'rail_unaccompanied'
            if change == 'jurisdiction': leg['origin_jurisdiction'] = 'CN-BJ'
            if change == 'evidence': leg['evidence'][0]['url'] = 'https://example.org/'
            self.assertTrue(validate_deep_review(bad, self.graph, self.sources))

    def test_unavailable_registry_is_only_an_access_gap(self):
        bad = deepcopy(self.inventory)
        bad['ground_qualification_checks'][0]['evidence'][0]['source_id'] = 'cn.samr.registry-attempt'
        self.assertTrue(validate_deep_review(bad, self.graph, self.sources))
