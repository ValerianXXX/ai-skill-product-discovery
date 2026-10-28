import importlib.util
import hashlib
import json
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("benchmark", Path(__file__).resolve().parents[1] / "scripts" / "substitute_benchmark.py")
benchmark = importlib.util.module_from_spec(spec)
spec.loader.exec_module(benchmark)


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
        with self.assertRaisesRegex(ValueError, "DATASET_IDENTITY_MISMATCH"):
            benchmark.summarize([{**report, "datasetHash": "changed"}])
        with self.assertRaisesRegex(ValueError, "DUPLICATE_ARM"):
            benchmark.summarize([report, report])


if __name__ == "__main__":
    unittest.main()
