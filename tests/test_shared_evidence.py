from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from shared_evidence_contract import digest, evaluate, load_round, request_for, validate_answer
from shared_evidence_broker import broker
from shared_evidence_benchmark import model_answer, read_summary, run, save_artifact, verify_artifact


class SharedEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.catalog, self.corpus = load_round()
        self.task = self.catalog['tasks'][0]

    def answer(self, task=None):
        task = task or self.task
        return {'fields': deepcopy(task['expected']),
                'citations': [{'sourceId': key, 'locators': value} for key, value in task['requiredCitations'].items()],
                'note': 'UNIT TEST FIXTURE ONLY. This is not a real observation or utility action.'}

    def test_equal_shared_evidence_without_answer_key(self):
        model = request_for(self.task, self.corpus, 'model', [])
        agent = request_for(self.task, self.corpus, 'agent', [])
        self.assertEqual(model['sharedEvidence'], agent['sharedEvidence'])
        self.assertNotIn('expected', model)
        self.assertNotIn('requiredCitations', model)
        self.assertEqual(model['tools'], [])
        self.assertEqual(len(agent['tools']), 3)

    def test_correct_fields_are_not_a_completed_saved_task(self):
        result = evaluate(self.task, self.answer(), self.corpus, False)
        self.assertEqual(result['factsCorrect'], 6)
        self.assertFalse(result['taskCompleted'])
        self.assertTrue(evaluate(self.task, self.answer(), self.corpus, True)['taskCompleted'])

    def test_missing_wrong_and_unknown_use_fixed_denominator(self):
        answer = self.answer()
        answer['fields']['care_limit'] = None
        answer['fields']['fera_limit'] = 12
        result = evaluate(self.task, answer, self.corpus, True)
        self.assertEqual(result['factsRequired'], 6)
        self.assertEqual(result['missingFields'], ['care_limit'])
        self.assertEqual(result['incorrectFields'], ['fera_limit'])

    def test_booleans_are_not_numbers_or_vice_versa(self):
        answer = self.answer()
        answer['fields']['official_decision'] = 0
        self.assertIn('official_decision', evaluate(self.task, answer, self.corpus, True)['incorrectFields'])

    def test_incomplete_or_invented_evidence_fails(self):
        answer = self.answer()
        answer['citations'][0]['locators'] = ['/effective_from']
        self.assertFalse(evaluate(self.task, answer, self.corpus, True)['evidenceComplete'])
        answer['citations'][0]['locators'] = ['/not_a_real_field']
        with self.assertRaisesRegex(ValueError, 'SOURCE_LOCATOR'):
            validate_answer(answer, self.task, self.corpus)

    def test_duplicate_source_cannot_inflate_evidence(self):
        answer = self.answer()
        answer['citations'].append(deepcopy(answer['citations'][0]))
        with self.assertRaisesRegex(ValueError, 'DUPLICATE_SOURCE'):
            validate_answer(answer, self.task, self.corpus)

    def test_only_task_documents_can_be_read(self):
        self.assertEqual(broker('read_file', {'id': 'assistance-rules'}, self.task, self.corpus)['id'], 'assistance-rules')
        for value in ('../../private', 'bill-text'):
            with self.assertRaisesRegex(ValueError, 'FILE_NOT_ALLOWED'):
                broker('read_file', {'id': value}, self.task, self.corpus)

    def test_generic_tool_cannot_invoke_skill_or_execute_code(self):
        with self.assertRaisesRegex(ValueError, 'TOOL_NOT_ALLOWED'):
            broker('screen_assistance', {}, self.task, self.corpus)
        with self.assertRaises(ValueError):
            broker('calculate', {'expression': '__import__("os")'}, self.task, self.corpus)
        self.assertEqual(broker('calculate', {'expression': '0.5+0.75+0.25+0.5'}, self.task, self.corpus)['value'], 2)

    def test_maintenance_is_explicit_and_does_not_mutate_baseline(self):
        original = digest(self.corpus)
        changed_tasks, changed = load_round(True)
        self.assertEqual(changed['maintenance'], 'SIMULATED_NOT_OFFICIAL')
        self.assertIsNone(changed['documents'][0]['url'])
        self.assertEqual(changed['documents'][0]['content']['care_income_upper_limit']['3'], 65000)
        self.assertEqual(len(changed_tasks['tasks']), 1)
        self.assertEqual(digest(load_round()[1]), original)

    def test_export_receipt_binds_bytes_and_answer(self):
        with tempfile.TemporaryDirectory(prefix='discovery-contract-') as temporary:
            directory = Path(temporary)
            row = {'taskId': self.task['id'], 'answer': self.answer()}
            row['artifact'] = save_artifact(directory, self.task, row['answer'])
            self.assertTrue(verify_artifact(directory, row))
            row['answer']['fields']['care_limit'] = 1
            with self.assertRaisesRegex(ValueError, 'ARTIFACT_CONTENT'):
                verify_artifact(directory, row)

    def test_export_cannot_be_overwritten_or_escape(self):
        with tempfile.TemporaryDirectory(prefix='discovery-contract-') as temporary:
            directory = Path(temporary)
            receipt = save_artifact(directory, self.task, self.answer())
            with self.assertRaises(FileExistsError):
                save_artifact(directory, self.task, self.answer())
            receipt['path'] = '../artifact.json'
            with self.assertRaisesRegex(ValueError, 'ARTIFACT_RECEIPT'):
                verify_artifact(directory, {'taskId': self.task['id'], 'answer': self.answer(), 'artifact': receipt})

    def test_unavailable_runtime_preserves_six_task_denominator(self):
        with tempfile.TemporaryDirectory(prefix='discovery-contract-') as temporary:
            directory = Path(temporary) / 'new-run'
            with patch('shared_evidence_benchmark.subprocess.run', return_value=subprocess.CompletedProcess([], 1, '', '')) as call:
                result = run('model', directory, ['unit-test-adapter'])
            self.assertEqual(call.call_count, 1)
            self.assertEqual(result['failed'], 1)
            self.assertEqual(result['notRunOrInterrupted'], 5)
            self.assertEqual(result['factsRequired'], 36)
            self.assertEqual(result['missingFields'], 36)
            self.assertIsNone(result['costUsd'])
            self.assertIsNone(result['usage']['totalTokens'])
            with self.assertRaises(FileExistsError):
                run('model', directory, ['unit-test-adapter'])

    def test_summary_rejects_catalog_change_and_task_omission(self):
        with tempfile.TemporaryDirectory(prefix='discovery-contract-') as temporary:
            directory = Path(temporary) / 'new-run'
            with patch('shared_evidence_benchmark.subprocess.run', return_value=subprocess.CompletedProcess([], 1, '', '')):
                run('model', directory, ['unit-test-adapter'])
            file = directory / 'run.json'
            report = json.loads(file.read_text())
            report['catalogHash'] = '0' * 64
            file.write_text(json.dumps(report))
            with self.assertRaisesRegex(ValueError, 'ROUND_IDENTITY'):
                read_summary(file)
            report['catalogHash'] = digest(self.catalog)
            report['results'].pop()
            file.write_text(json.dumps(report))
            with self.assertRaisesRegex(ValueError, 'TASK_DENOMINATOR'):
                read_summary(file)

    def test_agent_turn_limit_does_not_become_a_successful_retry(self):
        decision = {'tool': 'calculate', 'arguments': {'expression': '1+1'}, 'answer': None}
        envelope = json.dumps({'decision': decision, 'model': 'UNIT-TEST', 'provider': 'UNIT-TEST'})
        row = {'attempts': []}
        with patch('shared_evidence_benchmark.subprocess.run', return_value=subprocess.CompletedProcess([], 0, envelope, '')) as call:
            with self.assertRaisesRegex(ValueError, 'TURN_LIMIT'):
                model_answer(self.task, self.corpus, 'agent', ['unit-test-adapter'], row, self.catalog['limits'], lambda: None)
        self.assertEqual(call.call_count, 3)
        self.assertEqual(len(row['attempts']), 3)

    def test_model_cannot_obtain_an_agent_tool(self):
        envelope = json.dumps({'decision': {'tool': 'read_file', 'arguments': {'id': 'assistance-rules'}, 'answer': None}, 'model': 'UNIT-TEST', 'provider': 'UNIT-TEST'})
        row = {'attempts': []}
        with patch('shared_evidence_benchmark.subprocess.run', return_value=subprocess.CompletedProcess([], 0, envelope, '')):
            with self.assertRaisesRegex(ValueError, 'UNAUTHORIZED_TOOL'):
                model_answer(self.task, self.corpus, 'model', ['unit-test-adapter'], row, self.catalog['limits'], lambda: None)
        self.assertEqual(row['attempts'][0]['status'], 'FAILED')


if __name__ == '__main__':
    unittest.main()
