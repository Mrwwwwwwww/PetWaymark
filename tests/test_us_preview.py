"""US research boundaries: synthetic inputs never establish legal or carrier approval."""
from copy import deepcopy
import unittest
from packages.engine.io import ROOT, load_repository
from packages.engine.evaluate import evaluate
from packages.engine.routes import load_graph, preview, checklist
from scripts.validate_data import read_json, validators, validate_graph, validate_overlays


class USPreviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rules = load_repository()
        cls.graph = load_graph(region='US')
        cls.overlays = read_json(ROOT / 'data/coverage/us-state-overlays.json')
        cls.sources = {s['id']: s for s in read_json(ROOT / 'data/sources/catalog.json')['sources']}

    def profile(self, name='owner'):
        return read_json(ROOT / f'tests/fixtures/us-domestic/{name}.json')

    def run_preview(self, p=None, corridor='dom.us.ca-ny', graph=None):
        return preview(p or self.profile(), graph or self.graph, corridor_id=corridor,
                       assessment_at='2026-10-08', rules=self.rules, overlays=self.overlays)

    def test_three_small_city_examples_draft_and_unranked(self):
        for c in self.graph['corridors']:
            r = self.run_preview(corridor=c['id'])
            self.assertEqual(r['status'], 'unsupported')
            self.assertTrue(r['candidates'])
            self.assertFalse(r['booking_confirmed'])
            self.assertEqual(r['recommendations'], [])
            for route in r['candidates']:
                self.assertFalse(route['ranked'])
                self.assertIsNone(route['door_to_door_minutes'])

    def test_corridors_do_not_mix_other_research_directions(self):
        for c in self.graph['corridors']:
            result=self.run_preview(corridor=c['id'])
            allowed=set(c['segment_ids'])
            for route in result['candidates']+result['excluded']:
                self.assertTrue(set(route['segment_ids']) <= allowed)
            self.assertEqual(len(result['candidates']),3)

    def test_parcel_cannot_fill_first_or_last_live_animal_leg(self):
        for endpoint in ('from_node','to_node'):
            graph=deepcopy(self.graph)
            city='us.ventura' if endpoint=='from_node' else 'us.kingston'
            changed=set()
            for leg in graph['segments']:
                if leg[endpoint]==city and leg['product']=='unaccompanied_animal_carrier':
                    leg['product']='parcel_delivery';changed.add(leg['segment_id'])
            result=self.run_preview(self.profile('unaccompanied'),graph=graph)
            for route in result['candidates']:
                self.assertFalse(set(route['segment_ids']) & changed)
            self.assertEqual(result['status'],'ineligible')

    def test_graph_integrity_and_parcel_rejection(self):
        self.assertTrue(validators(ROOT)['corridor-graph.schema.json'].is_valid(self.graph))
        self.assertEqual(validate_graph(self.graph, self.sources), [])
        corrupt=deepcopy(self.graph);corrupt['corridors'][0]['segment_ids'].append('segment.absent')
        self.assertTrue(any('unresolved corridor segment' in e for e in validate_graph(corrupt,self.sources)))
        g = deepcopy(self.graph)
        g['segments'][0]['product'] = 'parcel_delivery'
        self.assertFalse(validators(ROOT)['corridor-graph.schema.json'].is_valid(g))
        r = self.run_preview(graph=g)
        self.assertTrue(any('parcel_cannot_transport_live_animal' in p['reason_codes'] for p in r['excluded']))

    def test_unaccompanied_cannot_use_passenger_products(self):
        r = self.run_preview(self.profile('unaccompanied'))
        self.assertTrue(any(s['mode'] == 'manifest_cargo' for p in r['candidates'] for s in p['segments']))
        for p in r['candidates']:
            self.assertTrue(all(s['product'] != 'owner_vehicle' and s['mode'] not in ('cabin','checked_baggage') for s in p['segments']))
        self.assertTrue(any('accompanied_product_unavailable' in p['reason_codes'] for p in r['excluded']))

    def test_owner_cannot_use_unaccompanied_product(self):
        r = self.run_preview()
        for p in r['candidates']:
            self.assertTrue(all(s['mode'] != 'manifest_cargo' and s['product'] != 'unaccompanied_animal_carrier' for s in p['segments']))

    def test_last_leg_decline_excludes_whole_path(self):
        p = self.profile('unaccompanied')
        ids = [s['segment_id'] for s in self.graph['segments'] if s['to_node'] == 'us.kingston']
        p['preview']['segments'] = {i:{'reported_acceptance':'declined'} for i in ids}
        r = self.run_preview(p)
        self.assertEqual(r['status'], 'ineligible')
        self.assertEqual(r['candidates'], [])
        self.assertIn('all_paths_excluded', r['reason_codes'])

    def test_missed_handover_excludes_entire_path(self):
        p = self.profile('unaccompanied')
        ids = [s['segment_id'] for s in self.graph['segments'] if s['to_node'] == 'us.kingston']
        p['preview']['segments'] = {i:{'handover_window_met':False} for i in ids}
        self.assertEqual(self.run_preview(p)['status'], 'ineligible')

    def test_domestic_does_not_require_cdc_import_history(self):
        r = self.run_preview()
        self.assertNotIn('travel_history_unconfirmed', r['reason_codes'])
        p = self.profile(); p['journey']['transport_mode'] = 'road'
        assessed = evaluate(p, self.rules, assessment_at='2026-10-08')
        self.assertTrue(all(row['outcome'] == 'not_applicable' for row in assessed['explanations'] if row['rule_id'].startswith('us.cdc.')))

    def test_classification_first(self):
        for change in [('ownership_transfer',True),('purpose','boarding'),('accompaniment','unknown')]:
            p=self.profile();p['journey'][change[0]]=change[1]
            self.assertEqual(self.run_preview(p)['candidates'], [])

    def test_every_new_constraint_positive_negative_missing_invalid(self):
        for rule in self.rules:
            if rule['id'] not in ('us.ca.domestic.health','us.as.cargo.health-certificate'): continue
            for value,outcome in [(True,'pass'),(False,'fail'),(None,'missing'),('yes','invalid')]:
                p=self.profile('unaccompanied');p['journey'].update(subdivision='US-CA',transport_mode=rule['scope']['transport_modes'][0])
                group,key=rule['requirement']['field'].split('.');p.setdefault(group,{})[key]=value
                result=evaluate(p,[rule],assessment_at='2026-10-08')
                row=result['explanations'][0]
                self.assertEqual(row['outcome'],outcome)
                self.assertFalse(row['enforceable'])
                self.assertEqual(result['status'],'unsupported')

    def test_known_other_state_mismatch_does_not_compare(self):
        p=self.profile();p['journey'].update(subdivision='US-TX',transport_mode='road')
        rule=next(r for r in self.rules if r['id']=='us.ca.domestic.health')
        self.assertEqual(evaluate(p,[rule],assessment_at='2026-10-08')['explanations'][0]['outcome'],'not_applicable')

    def test_inventory_unavailable_is_not_reviewed(self):
        self.assertEqual(validate_overlays(self.overlays,self.sources,{r['id']:r for r in self.rules}),[])
        o=deepcopy(self.overlays);o['states'][1]['evidence']=deepcopy(o['states'][0]['evidence'])
        self.assertTrue(validate_overlays(o,self.sources,{r['id']:r for r in self.rules}))
        o=deepcopy(self.overlays);o['states'][1]['subdivision']='US-CA'
        self.assertTrue(validate_overlays(o,self.sources,{r['id']:r for r in self.rules}))

    def test_bilingual_print_and_private_profile_redaction(self):
        p=self.profile();p['contact']='PRIVATE';before=deepcopy(p);r=self.run_preview(p)
        for lang in ('zh-CN','en'):
            output=checklist(r,self.graph,language=lang)
            self.assertIn('unsupported',output);self.assertIn('US-NY | source_unavailable',output)
            self.assertNotIn('PRIVATE',output)
        self.assertEqual(p,before)

    def test_inputs_cannot_claim_booked_or_override_evidence(self):
        p=self.profile();p['preview']['booking_confirmed']=True
        with self.assertRaises(ValueError): self.run_preview(p)
