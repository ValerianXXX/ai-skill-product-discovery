"""Prospective fairness contracts; no model calls or provider credentials."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from shared_evidence_contract import digest, load_round, request_for
from shared_evidence_benchmark import run
from shared_policy_coverage import validate_policy_coverage


class PolicyCoverageTests(unittest.TestCase):
    def setUp(self):
        self.catalog, self.corpus = load_round(round_id='2026-11-01')

    def document(self, corpus, ident):
        return next(item for item in corpus['documents'] if item['id'] == ident)

    def test_historical_upper_only_snapshot_fails_new_preflight(self):
        _, old = load_round()
        with self.assertRaisesRegex(ValueError, 'POLICY_'):
            validate_policy_coverage(old)

    def test_lower_bounds_and_each_extra_household_person_cannot_disagree(self):
        for key in ['1', '4', '8', 'additional_person']:
            with self.subTest(key=key):
                value = deepcopy(self.corpus)
                self.document(value, 'assistance-rules')['content']['fera_income_lower_limit'][key] += 1
                with self.assertRaisesRegex(ValueError, 'POLICY_FERA_RANGE'):
                    validate_policy_coverage(value)

    def test_missing_or_contradictory_decision_rules_are_rejected(self):
        changes = [
            ('carePrecedence', None), ('fractionalIncome', None), ('freshness', None),
            ('missingIncome', None), ('inputValidation', None), ('householdsAboveEight', None),
            ('incomeDecisionOrder', []), ('output', None)]
        for key, replacement in changes:
            with self.subTest(key=key):
                value = deepcopy(self.corpus)
                self.document(value, 'screening-policy')['content'][key] = replacement
                with self.assertRaisesRegex(ValueError, 'POLICY_'):
                    validate_policy_coverage(value)
        value = deepcopy(self.corpus)
        self.document(value, 'screening-policy')['content']['fractionalIncome']['roundingPolicy'] = 'round_to_dollar'
        with self.assertRaisesRegex(ValueError, 'POLICY_'):
            validate_policy_coverage(value)

    def test_product_freshness_convention_cannot_be_labeled_official_policy(self):
        value = deepcopy(self.corpus)
        self.document(value, 'screening-policy')['kind'] = 'OFFICIAL_FACT_TRANSCRIPTION'
        with self.assertRaisesRegex(ValueError, 'POLICY_PROVENANCE'):
            validate_policy_coverage(value)

    def test_all_tasks_supply_identical_policy_and_format_to_general_arms(self):
        self.assertEqual(len(self.catalog['tasks']), 12)
        self.assertEqual(sum(len(t['expected']) for t in self.catalog['tasks']), 95)
        for task in self.catalog['tasks']:
            with self.subTest(task=task['id']):
                model = request_for(task, self.corpus, 'model', [])
                agent = request_for(task, self.corpus, 'agent', [])
                self.assertEqual(model['sharedEvidence'], agent['sharedEvidence'])
                self.assertEqual(model['responseContract'], agent['responseContract'])
                self.assertIn('formatRules', model['responseContract'])
                self.assertNotIn('expected', json.dumps(model))
                self.assertNotIn('requiredCitations', json.dumps(model))
                ids = {d['id'] for d in model['sharedEvidence']}
                self.assertIn('screening-policy' if task['operation'] == 'assistance' else 'workflow-policy', ids)

    def test_maintenance_updates_lower_and_upper_rules_and_is_not_official(self):
        original = digest(self.corpus)
        catalog, corpus = load_round(maintenance=True, round_id='2026-11-01')
        self.assertEqual(len(catalog['tasks']), 1)
        doc = self.document(corpus, 'assistance-rules')
        self.assertEqual(doc['content']['care_income_upper_limit']['4'], 70000)
        self.assertEqual(doc['content']['fera_income_lower_limit']['4'], 70001)
        self.assertEqual(doc['content']['fera_income_upper_limit']['4'], 85000)
        self.assertIsNone(doc['url'])
        self.assertIsNone(doc['content']['source']['url'])
        self.assertIsNone(self.document(corpus, 'screening-policy')['content']['officialFacts']['sourceUrl'])
        validate_policy_coverage(corpus)
        self.assertEqual(digest(load_round(round_id='2026-11-01')[1]), original)

    def test_new_round_rejects_old_calibration_and_unallocated_model_budget(self):
        with self.assertRaisesRegex(ValueError, 'ROUND_FORMAT_ALREADY_DECLARED'):
            load_round(clarified=True, round_id='2026-11-01')
        with tempfile.TemporaryDirectory() as tmp, patch('shared_evidence_benchmark.subprocess.run') as process:
            output = Path(tmp) / 'not-started'
            with self.assertRaisesRegex(ValueError, 'NEW_ROUND_MODEL_BUDGET_UNALLOCATED'):
                run('model', output, command=['unreachable-provider'], round_id='2026-11-01')
            process.assert_not_called()
            self.assertFalse(output.exists())

    def test_unknown_round_is_not_an_arbitrary_filesystem_loader(self):
        for value in ('../2026-10-29', '2026-11-02', '', None):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, 'ROUND_IDENTITY'):
                load_round(round_id=value)


if __name__ == '__main__':
    unittest.main()
