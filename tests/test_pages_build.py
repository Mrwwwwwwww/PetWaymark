"""The owner adapter must preserve unknowns and avoid shipping research tools."""
import json
from pathlib import Path
import tempfile
import unittest

from scripts.build_pages import ROOT, build, data_script, payload


class PagesBuildTests(unittest.TestCase):
    def test_rule_scope_review_and_null_validity_survive(self):
        data = payload()
        for row in data['rules']:
            source = next(json.loads(p.read_text()) for p in (ROOT/'data/rules').rglob('*.json')
                          if json.loads(p.read_text())['id'] == row['id'])
            for key in ['scope', 'review', 'validity', 'source_ids', 'license']:
                self.assertEqual(row[key], source[key], (row['id'], key))
            self.assertEqual(row['unknowns'], source['pending_checks'])
            self.assertIsNone(row['review']['last_verified_at'])
        self.assertEqual(data['verifiedRoutes'], 0)

    def test_questions_do_not_publish_unreviewed_limits(self):
        for row in payload()['rules']:
            self.assertNotIn('requirement', row)
            self.assertIn('？', row['question'])
            self.assertFalse(any(c.isdigit() for c in row['question']))
            self.assertNotIn('必须', row['question'])

    def test_source_references_are_complete(self):
        for row in payload()['rules']:
            self.assertEqual(row['source_ids'], [s['id'] for s in row['sources']])
            self.assertTrue(all(s['url'].startswith('https://') for s in row['sources']))

    def test_build_copies_only_owner_files_and_retires_known_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            for name in ['examples.js','demo.js','correction.js']:
                (out/name).write_text('old research output')
            build(out)
            self.assertEqual({p.name for p in out.iterdir()},
                             {'index.html','result.html','app.js','style.css','page-data.js'})
            self.assertEqual((out/'page-data.js').read_text(), data_script())
        self.assertEqual((ROOT/'apps/pages/page-data.js').read_text(), data_script())

    def test_geonames_slice_matches_preserved_records(self):
        rows = {r[0]:r for r in (line.split('\t') for line in
                (ROOT/'apps/pages/geonames-subset.tsv').read_text().splitlines())}
        data = payload()['locations']
        self.assertEqual(data['license'], 'CC-BY-4.0')
        for cc, country in data['countries'].items():
            for city in country['cities']:
                r = rows[city['id']]
                self.assertEqual(r[8], cc)
                self.assertEqual(city['adminCodes'], r[10:14])
                self.assertEqual(city['originalName'], r[1])
                for area in city['areas']:
                    self.assertEqual(area['type'], 'ADM3')
                    self.assertEqual(area['adminCodes'][:2], city['adminCodes'][:2])
                    self.assertEqual(rows[area['id']][10:14], area['adminCodes'])
                    self.assertEqual(area['review'], 'source_codes_only_not_government_verified')
                for parent in city['parents']:
                    self.assertIn(parent['id'], rows)
                    self.assertEqual(parent['adminCodes'], rows[parent['id']][10:14])


class PlacesV2Tests(unittest.TestCase):
    def test_all_mainland_prefectures_and_provinces_covered(self):
        data = payload()['locations']['countries']['CN']
        source = json.loads((ROOT/'apps/pages/china-cities.json').read_text())
        prefectures = {r['code']:r['name'] for r in source if r['name'] not in
                       ['市辖区','县','省直辖县级行政区划','自治区直辖县级行政区划']}
        self.assertEqual(len(prefectures),333)
        self.assertEqual(sum(n.endswith('市') for n in prefectures.values()),293)
        codes = {c['adminCodes'][1]:c for c in data['cities']}
        self.assertFalse(set(prefectures)-set(codes))
        for code,name in prefectures.items():
            self.assertTrue(codes[code]['name'].startswith(name),(code,name,codes[code]['name']))
        provinces = json.loads((ROOT/'apps/pages/china-provinces.json').read_text())
        self.assertEqual(len(provinces),31)
        names = {a['name'] for a in data['subdivisions']}
        self.assertFalse({p['name'] for p in provinces}-names)
        self.assertEqual(len(names),34)
        self.assertEqual({a['jurisdiction'] for a in data['subdivisions'] if 'jurisdiction' in a}, {'HK','MO','TW'})

    def test_global_parent_codes_and_licenses(self):
        data = payload()['locations']
        admins = {r[0]:r for r in (line.split('\t') for line in
                  (ROOT/'apps/pages/geonames-admin1-subset.tsv').read_text().splitlines())}
        self.assertGreaterEqual(len(data['countries']),240)
        for cc,country in data['countries'].items():
            names = [c['name'] for c in country['cities']]
            self.assertEqual(len(names),len(set(names)),cc)
            for a in country['subdivisions']:
                if 'jurisdiction' not in a:
                    row = admins[cc+'.'+a['code']]
                    self.assertEqual(a['id'],row[3])
                    self.assertEqual(a['originalName'],row[1])
            for c in country['cities']:
                if c['subdivision']:
                    self.assertIn(cc+'.'+c['subdivision'],admins)
                    self.assertEqual(c['subdivision'],c['adminCodes'][0])
        self.assertTrue(all(s['license']=='WTFPL-2.0' for s in data['supplementaryInputs'].values()))

    def test_testing_points_remain_explicitly_unknown(self):
        data=payload()
        cities={c['id'] for c in data['locations']['countries']['CN']['cities']}
        self.assertEqual(cities,{p['cityId'] for p in data['testingPoints']})
        for p in data['testingPoints']:
            self.assertEqual(p['country'],'CN')
            self.assertEqual(p['status'],'pending')
            for k in ['name','address','phone','sourceURL','verifiedAt']:
                self.assertIsNone(p[k])

if __name__ == '__main__':
    unittest.main()
