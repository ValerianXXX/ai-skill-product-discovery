"""Offline execution-ledger probes, never model-quality observations."""
from contextlib import redirect_stdout
from copy import deepcopy
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from shared_evidence_benchmark import read_summary, run, save_artifact
from shared_evidence_broker import broker
from shared_evidence_contract import digest, load_round, request_for
from shared_evidence_report import build_report


class TranscriptReplayTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='discovery-replay-contract-')
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name) / 'synthetic-run'
        self.catalog, self.corpus = load_round()
        self.task = self.catalog['tasks'][0]
        answers = [self.answer(task) for task in self.catalog['tasks']]
        envelopes = [subprocess.CompletedProcess([], 0, json.dumps({
            'decision': {'tool': None, 'arguments': {}, 'answer': answer},
            'model': 'UNIT_TEST_ONLY', 'provider': 'UNIT_TEST_ONLY'}), '') for answer in answers]
        with patch('shared_evidence_benchmark.subprocess.run', side_effect=envelopes), redirect_stdout(io.StringIO()):
            run('agent', self.directory, ['unit-test-only-no-runtime'])
        self.file = self.directory / 'run.json'
        self.report = json.loads(self.file.read_text(encoding='utf-8'))

    def answer(self, task):
        return {'fields': deepcopy(task['expected']),
                'citations': [{'sourceId': key, 'locators': value} for key, value in task['requiredCitations'].items()],
                'note': 'UNIT TEST FIXTURE ONLY. No provider call, user outcome or utility action occurred.'}

    def summary(self, report=None):
        self.file.write_text(json.dumps(report or self.report), encoding='utf-8')
        return read_summary(self.file)

    def rejected(self, report=None):
        with self.assertRaises(ValueError):
            self.summary(report)

    def tool_turn(self, row, answer=None):
        decision = {'tool': 'calculate', 'arguments': {'expression': '1+0'}, 'answer': answer}
        result = broker(decision['tool'], decision['arguments'], self.task, self.corpus)
        first = deepcopy(row['attempts'][0])
        first['response'] = decision
        first['toolResult'] = result
        last = deepcopy(row['attempts'][0])
        last['requestHash'] = digest(request_for(self.task, self.corpus, 'agent', [
            {'request': decision, 'result': result}]))
        row['attempts'] = [first, last]

    def test_historical_report_and_all_original_receipts_stay_identical(self):
        published = Path(__file__).resolve().parents[1] / 'benchmarks/2026-10-29/analysis.json'
        self.assertEqual(build_report(), json.loads(published.read_text(encoding='utf-8')))

    def test_final_answer_cannot_claim_a_tool_result(self):
        self.report['results'][0]['attempts'][0]['toolResult'] = {'value': 1}
        self.rejected()

    def test_no_turn_may_follow_a_final_answer_failed_call_or_interrupted_call(self):
        for terminal in ('RECEIVED', 'FAILED', 'STARTED', 'UNRECOGNIZED'):
            with self.subTest(terminal=terminal):
                report = deepcopy(self.report)
                row = report['results'][0]
                first = deepcopy(row['attempts'][0])
                first['status'] = terminal
                if terminal in ('FAILED', 'STARTED'):
                    first['response'] = None
                if terminal == 'FAILED':
                    first['errorType'] = 'ConnectionError'
                row['attempts'].insert(0, first)
                self.rejected(report)

    def test_received_response_must_follow_the_actual_runner_contract(self):
        for mutation in ('arguments', 'extra', 'missing', 'array'):
            with self.subTest(mutation=mutation):
                report = deepcopy(self.report)
                attempt = report['results'][0]['attempts'][0]
                if mutation == 'arguments':
                    attempt['response']['arguments'] = {'unused': True}
                elif mutation == 'extra':
                    attempt['response']['extra'] = 'unrecorded-action'
                elif mutation == 'missing':
                    del attempt['response']['answer']
                else:
                    attempt['response'] = []
                self.rejected(report)

    def test_only_agent_tool_turns_can_produce_recomputed_tool_credit(self):
        row = self.report['results'][0]
        self.tool_turn(row)
        summary = self.summary()
        self.assertEqual(summary['toolCalls'], 1)
        self.assertEqual(summary['adapterCalls'], 7)
        self.assertEqual(summary['taskCompleted'], 6)
        row['attempts'][0]['toolResult']['value'] = True
        self.rejected()

    def test_tool_turn_cannot_also_return_an_answer(self):
        self.tool_turn(self.report['results'][0], self.answer(self.task))
        self.rejected()

    def test_model_record_cannot_claim_a_successful_agent_tool(self):
        self.report['arm'] = 'model'
        for task, row in zip(self.catalog['tasks'], self.report['results']):
            row['attempts'][0]['requestHash'] = digest(request_for(task, self.corpus, 'model', []))
        row = self.report['results'][0]
        row.update(status='FAILED', answer=None, artifact=None, errorType='ValueError')
        row.pop('candidateAnswer')
        row['attempts'][0].update(response={'tool': 'calculate', 'arguments': {'expression': '1+0'}, 'answer': None},
                                  toolResult={'value': 1})
        self.rejected()

    def test_unattempted_row_cannot_contain_measured_output(self):
        row = self.report['results'][0]
        row.update(status='NOT_RUN', answer=None, artifact=None)
        self.rejected()

    def test_observed_row_requires_a_valid_saved_answer_and_consistent_candidate(self):
        for mutation in ('no-artifact', 'candidate-changed', 'invalid-contract'):
            with self.subTest(mutation=mutation):
                report = deepcopy(self.report)
                row = report['results'][0]
                if mutation == 'no-artifact':
                    row['artifact'] = None
                elif mutation == 'candidate-changed':
                    row['candidateAnswer'] = self.answer(self.task)
                    row['candidateAnswer']['fields']['care_limit'] = 1
                else:
                    row['answer'] = {'fields': row['answer']['fields'], 'citations': [], 'note': 'short'}
                    row['candidateAnswer'] = deepcopy(row['answer'])
                    row['attempts'][0]['response']['answer'] = deepcopy(row['answer'])
                    # Replace only our temporary synthetic artifact, never a historical file.
                    (self.directory / row['artifact']['path']).unlink()
                    row['artifact'] = save_artifact(self.directory, self.task, row['answer'])
                self.rejected(report)

    def test_execution_identity_flags_are_not_truthy_aliases(self):
        for key, value in (('mode', 'SIMULATED'), ('syntheticInputs', False),
                           ('syntheticInputs', 1), ('maintenance', 0), ('clarified', 0)):
            with self.subTest(key=key, value=value):
                report = deepcopy(self.report)
                report[key] = value
                self.rejected(report)

    def test_malformed_attempt_collections_fail_with_a_diagnostic(self):
        for attempts in ({}, [None], 'not-a-call-ledger'):
            with self.subTest(attempts=attempts):
                report = deepcopy(self.report)
                report['results'][0]['attempts'] = attempts
                self.rejected(report)

    def test_failed_final_contract_remains_an_observation_without_completion(self):
        row = self.report['results'][0]
        invalid = {'fields': self.answer(self.task)['fields'], 'citations': [], 'note': 'short'}
        row.update(status='FAILED', answer=None, artifact=None, candidateAnswer=invalid, errorType='ValueError')
        row['attempts'][0]['response']['answer'] = invalid
        summary = self.summary()
        self.assertEqual(summary['failed'], 1)
        self.assertEqual(summary['taskCompleted'], 5)
        self.assertEqual(summary['factsCorrect'], 36)

    def test_failed_transport_and_received_but_unmaterialized_checkpoints_survive(self):
        for state in ('transport-failed', 'call-started', 'final-received', 'never-started'):
            with self.subTest(state=state):
                report = deepcopy(self.report)
                report['completedAt'] = None
                row = report['results'][0]
                row.update(status='STARTED', answer=None, artifact=None, durationMs=None)
                row.pop('candidateAnswer')
                attempt = row['attempts'][0]
                if state == 'transport-failed':
                    row.update(status='FAILED', errorType='ConnectionError', durationMs=1)
                    attempt.update(status='FAILED', response=None, errorType='ConnectionError')
                elif state == 'call-started':
                    attempt.update(status='STARTED', response=None, durationMs=None)
                elif state == 'never-started':
                    row.update(status='NOT_RUN', attempts=[], model=None, provider=None)
                summary = self.summary(report)
                self.assertEqual(summary['taskCompleted'], 5)
                self.assertEqual(summary['adapterCalls'], 5 if state == 'never-started' else 6)
                self.assertIsNone(summary['costUsd'])


if __name__ == '__main__':
    unittest.main()
