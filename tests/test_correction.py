"""Protect minimum public correction context against private profile leakage."""
import json
import unittest
from apps.correction import context, panel


class CorrectionTests(unittest.TestCase):
    def test_allowlist_ignores_private_profile_dates_and_identifiers(self):
        private='PRIVATE-PASSPORT-CHIP-PHONE-ADDRESS'
        row={'journey_id':private, 'profile':{'pet':private},'journey':{'entry_at':'2099-01-01'},
             'documents':private,'reason_codes':['draft_rule'],
             'dataset_version':private, 'engine_version':private,
             'explanations':[{'rule_id':'us.cdc.dog.low-risk.minimum-age','message':private,'evidence':private}]}
        result=context(row,'en')
        self.assertEqual(set(result),{'engine_version','dataset_version','rule_ids','reason_codes','language'})
        self.assertEqual(result['rule_ids'],['us.cdc.dog.low-risk.minimum-age'])
        self.assertNotIn(private,json.dumps(result));self.assertNotIn('2099',json.dumps(result))

    def test_nested_rule_ids_deduplicated_unknown_ids_omitted(self):
        ident='us.cdc.dog.low-risk.minimum-age'
        result=context({'candidates':[{'segments':[{'rule_assessment':{'matched_rule_ids':[ident,ident,'PRIVATE']}}]}]},'zh-CN')
        self.assertEqual(result['rule_ids'],[ident]);self.assertEqual(result['language'],'zh-CN')

    def test_without_rule_id_still_has_feedback_context_and_safe_markup(self):
        result=context({'reason_codes':['unknown_rule','<script>private</script>']},'en')
        self.assertEqual(result['rule_ids'],[]);self.assertEqual(result['reason_codes'],['unknown_rule'])
        self.assertIn('correction-context',panel({'reason_codes':['unknown_rule']},'en'))
        with self.assertRaises(ValueError):context({},'fr')

    def test_long_reason_lists_retained_for_offline_copy(self):
        codes=['diagnostic.'+str(i) for i in range(300)]
        self.assertEqual(set(context({'reason_codes':codes},'en')['reason_codes']),set(codes))
