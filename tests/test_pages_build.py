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


if __name__ == '__main__':
    unittest.main()
