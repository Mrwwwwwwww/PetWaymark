"""Mutation tests exercise the data gate on isolated copies, not production data."""
from copy import deepcopy
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from validate_data import read_json, validate_repository


class DataIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in ("packages/schema", "data/rules", "tests/fixtures/boundaries"):
            shutil.copytree(ROOT / name, self.root / name)
        (self.root / "data/sources").mkdir()
        shutil.copy2(ROOT / "data/sources/catalog.json", self.root / "data/sources/catalog.json")
        self.path = self.root / "data/rules/us/us.cdc.dog.low-risk.minimum-age.json"
        self.rule = read_json(self.path)

    def save(self, value=None, path=None):
        (path or self.path).write_text(json.dumps(self.rule if value is None else value), encoding="utf-8")

    def rejected(self, phrase):
        errors, _ = validate_repository(self.root)
        self.assertTrue(any(phrase in error for error in errors), errors)

    def verified_test_record(self):
        # These synthetic reviewer identities exist only in a temporary test copy.
        self.rule["review"] = {
            "status": "verified", "last_verified_at": "2026-10-08",
            "review_due_at": "2027-01-06", "reviewed_by": [
                {"id": "synthetic-reviewer-a", "role": "human_domain_reviewer", "reviewed_at": "2026-10-08"},
                {"id": "synthetic-reviewer-b", "role": "human_domain_reviewer", "reviewed_at": "2026-10-08"}]}
        self.rule["pending_checks"] = []

    def test_current_dataset_is_draft_only_and_complete(self):
        errors, counts = validate_repository(self.root)
        self.assertEqual(errors, [])
        self.assertEqual(counts, {"rules": 10, "sources": 12, "cases": 9})
        for path in (self.root / "data/rules").rglob("*.json"):
            rule = read_json(path)
            self.assertEqual(rule["review"]["status"], "draft")
            self.assertEqual(rule["review"]["reviewed_by"], [])

    def test_missing_cannot_turn_into_allow(self):
        self.rule["on_missing"] = "allow"
        self.save()
        self.rejected("on_missing")

    def test_bad_operator_and_unknown_field(self):
        self.rule["requirement"] = {"field": "pet.weight", "operator": "calendar_age_at_least",
                                    "value": 6, "unit": "month", "anchor": "journey.entry_at"}
        self.save()
        self.rejected("requirement")

    def test_missing_source(self):
        self.rule["source_ids"] = ["source.absent"]
        self.save()
        self.rejected("unresolved source reference")

    def test_evidence_drift(self):
        self.rule["evidence"][0]["accessed_at"] = "2026-10-07"
        self.save()
        self.rejected("differs from source catalog")

    def test_duplicate_rule_id(self):
        self.save(deepcopy(self.rule), self.path.with_name("duplicate.json"))
        self.rejected("duplicate rules ID")

    def test_duplicate_source_id(self):
        path = self.root / "data/sources/catalog.json"
        catalog = read_json(path)
        duplicate = deepcopy(catalog["sources"][0])
        duplicate["publisher"] = "Different synthetic publisher"
        catalog["sources"].append(duplicate)
        self.save(catalog, path)
        self.rejected("duplicate source ID")

    def test_wrong_authority(self):
        self.rule["authority"] = "unrelated-authority"
        self.save()
        self.rejected("matching government authority")

    def test_reverse_effective_dates(self):
        self.rule["validity"]["effective_to"] = "2024-07-31"
        self.save()
        self.rejected("reversed validity")

    def test_unreviewed_promotion(self):
        self.rule["review"]["status"] = "verified"
        self.save()
        self.rejected("review")

    def test_repeated_reviewer_is_not_two_people(self):
        self.verified_test_record()
        self.rule["review"]["reviewed_by"][1]["id"] = "synthetic-reviewer-a"
        self.rule["review"]["reviewed_by"][1]["reviewed_at"] = "2026-10-07"
        self.save()
        self.rejected("two distinct human reviewers")

    def test_reversed_review_window(self):
        self.verified_test_record()
        self.rule["review"]["review_due_at"] = "2026-10-08"
        self.save()
        self.rejected("due date must follow")

    def test_unsupported_exception_source(self):
        self.rule["exceptions"] = [{"id": "synthetic.exception", "scope_note": {"en": "Synthetic", "zh-CN": "合成"},
                                   "source_ids": ["eu.ec.non-eu"], "disposition": "needs_confirmation"}]
        self.save()
        self.rejected("exception source must be declared")

    def test_unresolved_case_reference(self):
        path = next((self.root / "tests/fixtures/boundaries").glob("*.json"))
        case = read_json(path)
        case["rule_ids"] = ["rule.absent"]
        self.save(case, path)
        self.rejected("unresolved case rule reference")

    def test_species_mismatch_assertion_is_checked(self):
        path = self.root / "tests/fixtures/boundaries/boundary.cat-not-dog.json"
        case = read_json(path)
        case["input"]["species"] = "dog"
        self.save(case, path)
        self.rejected("no scope mismatch")

    def test_real_order_field_is_forbidden(self):
        self.rule["order_id"] = "synthetic-order"
        self.save()
        self.rejected("Additional properties")


if __name__ == "__main__":
    unittest.main()
