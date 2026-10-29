import importlib.util
import hashlib
import json
from pathlib import Path
from subprocess import CompletedProcess
from types import SimpleNamespace
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("benchmark", Path(__file__).resolve().parents[1] / "scripts" / "substitute_benchmark.py")
benchmark = importlib.util.module_from_spec(spec)
spec.loader.exec_module(benchmark)
adapter_spec = importlib.util.spec_from_file_location("hermes_adapter", Path(__file__).resolve().parents[1] / "scripts" / "hermes_benchmark_adapter.py")
adapter = importlib.util.module_from_spec(adapter_spec)
adapter_spec.loader.exec_module(adapter)

USAGE = {"source": "HERMES_SESSION_COUNTERS", "modelApiCalls": 1, "promptTokens": 180,
         "completionTokens": 20, "totalTokens": 200, "estimatedCostUsd": 0.0,
         "costStatus": "included", "costSource": "none"}


class SubstituteTests(unittest.TestCase):
    def test_published_run_hashes_preserve_original_evidence(self):
        analysis = json.loads((benchmark.DATA / "results" / "analysis.json").read_text(encoding="utf-8"))
        for record in analysis["runFiles"]:
            actual = hashlib.sha256((benchmark.DATA / "results" / record["name"]).read_bytes()).hexdigest()
            self.assertEqual(actual, record["sha256"])

    def test_guessed_facts_without_current_evidence_are_not_task_completion(self):
        task = benchmark.DATASET["tasks"][0]
        self.assertEqual(benchmark.evaluate(task, task["expected"], False)["factsCorrect"], 5)
        self.assertFalse(benchmark.evaluate(task, task["expected"], False)["taskCompleted"])
        self.assertTrue(benchmark.evaluate(task, task["expected"], True)["taskCompleted"])

    def test_broker_cannot_execute_code_or_read_arbitrary_files(self):
        self.assertEqual(benchmark.calculate("111440 + 11360 * (9 - 8)"), 122800)
        for expression in ["__import__('os')", "2**1000", "True", "1/0"]:
            with self.assertRaises((ValueError, ZeroDivisionError)):
                benchmark.calculate(expression)
        with self.assertRaises(ValueError):
            benchmark.broker("read_file", {"id": "../../private"})

    def test_answer_key_is_excluded_and_agent_capabilities_are_explicit(self):
        task = benchmark.DATASET["tasks"][0]
        request = benchmark.request_for(task, "agent", [])
        self.assertNotIn("expected", request)
        self.assertNotIn("43280", str(request))
        self.assertEqual(len(request["tools"]), 3)
        self.assertEqual(benchmark.request_for(task, "model", [])["tools"], [])

    def test_wrong_fields_and_boolean_type_are_not_softened(self):
        task = benchmark.DATASET["tasks"][0]
        wrong = {**task["expected"], "official_decision": 0, "care_limit": 1}
        self.assertEqual(benchmark.evaluate(task, wrong, True)["wrongFields"], ["care_limit", "official_decision"])
        self.assertFalse(benchmark.evaluate(task, {**task["expected"], "invented": True}, True)["taskCompleted"])

    def test_abstention_is_incomplete_without_being_an_incorrect_claim(self):
        task = benchmark.DATASET["tasks"][0]
        answer = {**task["expected"], "care_limit": None, "care_status": "needs_information"}
        result = benchmark.evaluate(task, answer, True)
        self.assertEqual(result["factsCorrect"], 3)
        self.assertEqual(result["wrongFields"], [])
        self.assertEqual(result["missingFields"], ["care_status", "care_limit"])
        self.assertFalse(result["taskCompleted"])

    def test_summary_rejects_changed_identity_and_does_not_trust_stored_scores(self):
        report = {"datasetHash": benchmark.digest(benchmark.DATASET), "sourceHash": benchmark.digest(benchmark.SOURCE),
                  "arm": "model", "results": [{"taskId": task["id"], "status": "OBSERVED", "answer": {},
                  "sourceVerified": False, "evaluation": {"taskCompleted": True}, "providerCalls": 1,
                  "toolCalls": 0, "durationMs": 10} for task in benchmark.DATASET["tasks"]]}
        self.assertEqual(benchmark.summarize([report])[0]["taskCompleted"], 0)
        self.assertIsNone(benchmark.summarize([report])[0]["tokens"])
        with self.assertRaisesRegex(ValueError, "DATASET_IDENTITY_MISMATCH"):
            benchmark.summarize([{**report, "datasetHash": "changed"}])
        with self.assertRaisesRegex(ValueError, "DUPLICATE_ARM"):
            benchmark.summarize([report, report])

    def test_all_agent_turns_are_counted_without_promoting_estimate_to_billing(self):
        task = benchmark.DATASET["tasks"][0]
        decisions = [{"tool": "read_file", "arguments": {"id": "cpuc-assistance"}, "answer": None},
                     {"tool": None, "arguments": {}, "answer": task["expected"]}]
        responses = [CompletedProcess([], 0, json.dumps({"model": "synthetic-test", "provider": "unit-fixture",
                     "decision": decision, "usage": USAGE}), "") for decision in decisions]
        row = {"providerCalls": 0, "toolCalls": 0, "sourceVerified": False, "attempts": [], "costUsd": None}
        with patch.object(benchmark.subprocess, "run", side_effect=responses):
            self.assertEqual(benchmark.model_run(task, "agent", ["unused"], row), task["expected"])
        self.assertEqual(row["tokens"], 400)
        self.assertEqual(row["usage"]["modelApiCalls"], 2)
        self.assertEqual(row["usage"]["callsWithUsage"], 2)
        self.assertEqual(row["usage"]["estimatedCostUsd"], 0)
        self.assertFalse(row["usage"]["billingVerified"])
        self.assertIsNone(row["costUsd"])

    def test_missing_or_failed_attempt_does_not_make_a_partial_token_total_complete(self):
        measured = {"usage": USAGE}
        for unmeasured in [{}, {"usage": None, "status": "FAILED"}]:
            total = benchmark.summarize_usage([measured, unmeasured], 2)
            self.assertEqual(total["callsWithUsage"], 1)
            self.assertIsNone(total["totalTokens"])
            self.assertIsNone(total["estimatedCostUsd"])
        self.assertIsNone(benchmark.summarize_usage([measured], 2)["totalTokens"])
        self.assertIsNone(benchmark.summarize_usage([], 0)["totalTokens"])

    def test_invalid_usage_and_unknown_cost_do_not_become_free_or_zero(self):
        for update in [{"totalTokens": True}, {"totalTokens": -1}, {"totalTokens": 10**400},
                       {"estimatedCostUsd": float("nan")}, {"estimatedCostUsd": float("inf")},
                       {"costStatus": "unknown"}, {"costSource": "private path/credential"}]:
            with self.assertRaises(ValueError):
                benchmark.validate_usage({**USAGE, **update})
        observed = adapter.session_usage(SimpleNamespace(session_api_calls=1, session_prompt_tokens=180,
            session_completion_tokens=20, session_total_tokens=200, session_cost_status="unknown",
            session_estimated_cost_usd=0.0))
        self.assertEqual(observed["totalTokens"], 200)
        self.assertIsNone(observed["estimatedCostUsd"])
        self.assertIsNone(adapter.session_usage(SimpleNamespace())["totalTokens"])


if __name__ == "__main__":
    unittest.main()
