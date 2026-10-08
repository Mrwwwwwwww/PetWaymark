"""Contract rejection tests, independent of the future rule evaluation engine."""
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from validate_data import read_json, unique_object, validators


class ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schemas = validators(ROOT)

    def test_all_schemas_are_valid_draft_2020_12(self):
        self.assertEqual(len(self.schemas), 5)

    def test_calendar_month_requirement(self):
        check = self.schemas["common.schema.json"].evolve(
            schema={"$ref": "https://petwaymark.org/schemas/0.1.0/common.schema.json#/$defs/requirement"})
        valid = {"field": "pet.birth_date", "operator": "calendar_age_at_least",
                 "value": 6, "unit": "month", "anchor": "journey.entry_at"}
        self.assertTrue(check.is_valid(valid))
        self.assertFalse(check.is_valid({**valid, "unit": "30_day_month"}))
        self.assertFalse(check.is_valid({**valid, "value": "6"}))
        self.assertFalse(check.is_valid({**valid, "anchor": "unknown_event"}))

    def test_missing_information_cannot_be_allowed(self):
        check = self.schemas["rule.schema.json"]
        self.assertEqual(check.schema["properties"]["on_missing"]["enum"], ["needs_confirmation"])

    def test_invalid_calendar_date(self):
        catalog = read_json(ROOT / "data/sources/catalog.json")
        catalog["sources"][0]["accessed_at"] = "2026-02-30"
        self.assertFalse(self.schemas["source-catalog.schema.json"].is_valid(catalog))

    def test_non_https_source(self):
        catalog = read_json(ROOT / "data/sources/catalog.json")
        catalog["sources"][0]["url"] = "http://example.org"
        self.assertFalse(self.schemas["source-catalog.schema.json"].is_valid(catalog))

    def test_unknown_source_properties_rejected(self):
        catalog = read_json(ROOT / "data/sources/catalog.json")
        catalog["sources"][0]["human_verified"] = True
        self.assertFalse(self.schemas["source-catalog.schema.json"].is_valid(catalog))

    def test_duplicate_json_keys_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
            json.loads('{"on_missing":"needs_confirmation","on_missing":"allow"}',
                       object_pairs_hook=unique_object)


if __name__ == "__main__":
    unittest.main()
