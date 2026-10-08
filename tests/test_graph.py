"""Reject graph/evidence corruption without editing public data."""
from copy import deepcopy
import unittest
from packages.engine.io import ROOT
from scripts.validate_data import read_json, validators, validate_graph


class GraphTests(unittest.TestCase):
    def setUp(self):
        self.graph = read_json(ROOT / 'data/corridors/cn-preview.json')
        self.sources = {s['id']: s for s in read_json(ROOT / 'data/sources/catalog.json')['sources']}
        self.schema = validators(ROOT)['corridor-graph.schema.json']

    def test_public_graph_remains_draft_and_unknown(self):
        self.assertTrue(self.schema.is_valid(self.graph))
        self.assertEqual(validate_graph(self.graph, self.sources), [])
        self.assertEqual(len(self.graph['corridors']), 2)
        for s in self.graph['segments']:
            self.assertEqual(s['review_status'], 'draft')
            self.assertIsNone(s['estimate_minutes'])
            self.assertTrue(all(v is None for v in s['handover']['roles'].values()))

    def test_no_unreviewed_promotion(self):
        self.graph['segments'][0]['review_status'] = 'verified'
        self.assertFalse(self.schema.is_valid(self.graph))

    def test_unresolved_node(self):
        self.graph['segments'][0]['to_node'] = 'node.absent'
        self.assertTrue(any('node' in e for e in validate_graph(self.graph, self.sources)))

    def test_duplicate_segment(self):
        self.graph['segments'].append(deepcopy(self.graph['segments'][0]))
        self.assertTrue(any('duplicate segments' in e for e in validate_graph(self.graph, self.sources)))

    def test_evidence_drift(self):
        self.graph['segments'][0]['evidence'][0]['url'] = 'https://example.org/other'
        self.assertTrue(any('differs' in e for e in validate_graph(self.graph, self.sources)))

    def test_unresolved_source(self):
        self.graph['segments'][0]['source_ids'].append('source.absent')
        self.assertTrue(any('source' in e for e in validate_graph(self.graph, self.sources)))

    def test_limit_must_have_source(self):
        self.graph['segments'][-1]['limits'][0]['source_id'] = 'source.absent'
        self.assertTrue(any('limit source' in e for e in validate_graph(self.graph, self.sources)))

    def test_product_is_separate_from_mode(self):
        self.graph['segments'][0]['mode'] = 'rail'
        self.assertTrue(any('product/mode' in e for e in validate_graph(self.graph, self.sources)))

    def test_private_order_fields_rejected(self):
        self.graph['segments'][0]['order_id'] = 'synthetic'
        self.assertFalse(self.schema.is_valid(self.graph))
