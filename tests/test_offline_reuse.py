"""Safety boundaries for version-pinned read-only downstream reuse."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from examples.offline.read_only import read_only, verify_pin
from packages.engine.io import ROOT
from packages.engine.emergency import checklist


class OfflineReuseTests(unittest.TestCase):
    def test_offline_draft_projection_preserves_unknown_and_bytes(self):
        files = [p for p in (ROOT / 'data').rglob('*') if p.is_file()]
        before = {p:hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
        with patch('socket.socket', side_effect=AssertionError('Network forbidden')):
            result = read_only()
        self.assertEqual(result['status'], 'unsupported')
        self.assertFalse(result['booking_confirmed'])
        self.assertEqual(result['external_progress']['carrier_acceptance'], 'unknown')
        self.assertIn('critical_coverage_unreviewed', result['coverage_gaps'])
        self.assertTrue(result['sources'])
        self.assertEqual(result['rules'][0]['review']['status'], 'draft')
        self.assertEqual(result['rules'][0]['review']['reviewed_by'], [])
        self.assertEqual(result['rules'][0]['synthetic_expression_diagnostic']['outcome'], 'pass')
        self.assertNotIn('profile', result)
        self.assertEqual(before, {p:hashlib.sha256(p.read_bytes()).hexdigest() for p in files})

    def test_pin_drift_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory); (root/'file').write_text('changed')
            with self.assertRaisesRegex(ValueError, 'Pinned file drift'):
                verify_pin(root, {'sha256':{'file':hashlib.sha256(b'original').hexdigest()}})

    def test_emergency_bilingual_suggestions_no_rescue_promise(self):
        en, zh = checklist('en'), checklist('zh-CN')
        self.assertEqual(en.count('[ ]'), 6); self.assertEqual(zh.count('[ ]'), 6)
        self.assertIn('Copies do not replace required originals', en)
        self.assertIn('副本不能替代所需原件', zh)
        self.assertIn('recalculate', en); self.assertIn('重算', zh)
        self.assertIn('not official requirements', en); self.assertIn('非官方要求', zh)
        with self.assertRaises(ValueError): checklist('fr')
