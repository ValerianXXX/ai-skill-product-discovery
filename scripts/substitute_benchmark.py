"""Fixed synthetic substitute benchmark. Run adapters with argv, never a shell."""
from __future__ import annotations
import argparse
import ast
from datetime import datetime, timezone
import hashlib
import importlib
import json
import math
import operator
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "benchmarks" / "2026-10-27"
DATASET = json.loads((DATA / "tasks.json").read_text(encoding="utf-8"))
SOURCE = json.loads((DATA / "sources" / "cpuc-assistance.json").read_text(encoding="utf-8"))
ARMS = ("model", "agent", "skill")
EVALUATOR_VERSION = "required-facts-v2-abstentions"


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def calculate(expression):
    if not isinstance(expression, str) or len(expression) > 160:
        raise ValueError("EXPRESSION_LIMIT")
    tree = ast.parse(expression, mode="eval")
    if len(list(ast.walk(tree))) > 50:
        raise ValueError("EXPRESSION_LIMIT")
    operations = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv}

    def evaluate(node):
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            value = node.value
        elif isinstance(node, ast.BinOp) and type(node.op) in operations:
            value = operations[type(node.op)](evaluate(node.left), evaluate(node.right))
        elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            value = -evaluate(node.operand)
        else:
            raise ValueError("ARITHMETIC_ONLY")
        if not math.isfinite(value) or abs(value) > 10**12:
            raise ValueError("NUMBER_LIMIT")
        return value
    return evaluate(tree.body)


def broker(name, arguments):
    if not isinstance(arguments, dict):
        raise ValueError("TOOL_ARGUMENTS_REQUIRED")
    if name == "search_sources" and set(arguments) == {"query"}:
        query = arguments["query"]
        if not isinstance(query, str) or len(query) > 300:
            raise ValueError("QUERY_LIMIT")
        matches = any(word in query.lower() for word in ("care", "fera", "income", "pge", "pg&e", "cpuc"))
        return ({"index": "frozen-official-source-shelf", "documents": [SOURCE] if matches else []}, matches)
    if name == "read_file" and arguments == {"id": "cpuc-assistance"}:
        return (SOURCE, True)
    if name == "calculate" and set(arguments) == {"expression"}:
        return ({"value": calculate(arguments["expression"])}, False)
    raise ValueError("TOOL_NOT_ALLOWED")


def evaluate(task, answer, source_verified):
    if not isinstance(answer, dict):
        answer = {}
    correct = lambda key, expected: key in answer and answer[key] == expected and (type(answer[key]) is bool) == (type(expected) is bool)
    unmatched = [key for key, expected in task["expected"].items() if not correct(key, expected)]
    missing = [key for key in unmatched if key not in answer or answer[key] is None
               or (key.endswith("_status") and answer[key] == "needs_information")]
    wrong = [key for key in unmatched if key not in missing]
    extra = sorted(set(answer) - set(task["expected"]))
    return {"factsCorrect": len(task["expected"]) - len(unmatched), "factsChecked": len(task["expected"]), "wrongFields": wrong,
            "missingFields": missing, "unexpectedFields": extra,
            "taskCompleted": not unmatched and not extra and (source_verified or not task["requiresCurrentSource"])}


def request_for(task, arm, history):
    return {"protocol": "SUBSTITUTE_BENCHMARK_V1", "arm": arm, "asOf": DATASET["asOf"], "synthetic": True,
            "task": "Preliminarily screen this PG&E household for CARE/FERA using current verified rules. This is not official enrollment. Use the income path only; no categorical programs are reported. Reject negative income as INVALID_INCOME; missing income needs information.",
            "input": task["input"],
            "responseContract": {"tool": "null, or one allowed tool name", "arguments": "object (empty for final)",
                "answer": "null while calling tools; otherwise exactly {care_status,fera_status,care_limit,fera_limit,official_decision:false}, or {error:INVALID_INCOME} for invalid income. Use null for unknown numbers.",
                "statuses": ["likely_eligible", "likely_not_eligible_by_income", "not_primary_path", "needs_information"]},
            "tools": [] if arm == "model" else [
                {"name": "search_sources", "arguments": {"query": "string"}, "description": "Keyword search of frozen official public source files; returns source text and provenance, not live web search."},
                {"name": "read_file", "arguments": {"id": "cpuc-assistance"}, "description": "Read the complete official-fact transcription; no product code or expected answers."},
                {"name": "calculate", "arguments": {"expression": "numbers and + - * /"}}],
            "history": history}


def model_run(task, arm, command, row):
    history = []
    for _ in range(1 if arm == "model" else 4):
        row["providerCalls"] += 1
        started = time.perf_counter()
        attempt = {"status": "STARTED", "durationMs": None, "response": None}
        row["attempts"].append(attempt)
        try:
            process = subprocess.run(command, input=json.dumps(request_for(task, arm, history)), text=True,
                                     capture_output=True, timeout=90, check=False, shell=False, encoding="utf-8")
            if process.returncode or len(process.stdout) > 20000:
                raise ValueError("ADAPTER_FAILED")
            envelope = json.loads(process.stdout)
            row["model"] = envelope["model"]
            row["provider"] = envelope["provider"]
            decision = envelope["decision"]
            if not isinstance(decision, dict) or set(decision) != {"tool", "arguments", "answer"}:
                raise ValueError("RESPONSE_CONTRACT")
            attempt["response"] = decision
            attempt["status"] = "RECEIVED"
            if decision["tool"] is None:
                if decision["arguments"] != {}:
                    raise ValueError("FINAL_ARGUMENTS")
                return decision["answer"]
            if arm != "agent" or decision["answer"] is not None:
                raise ValueError("UNAUTHORIZED_TOOL")
            result, source_read = broker(decision["tool"], decision["arguments"])
            row["sourceVerified"] = row["sourceVerified"] or source_read
            row["toolCalls"] += 1
            history.append({"request": decision, "result": result})
        except Exception as error:
            attempt["status"] = "FAILED"
            attempt["errorType"] = type(error).__name__
            raise
        finally:
            attempt["durationMs"] = round((time.perf_counter() - started) * 1000)
    raise ValueError("TURN_LIMIT")


def skill_run(task, root, row):
    source_dir = root / "plugins" / "billfit" / "skills" / "billfit" / "scripts"
    if not (source_dir / "billfit_core.py").is_file():
        raise ValueError("BILLFIT_CHECKOUT_REQUIRED")
    sys.path.insert(0, str(source_dir))
    try:
        core = importlib.import_module("billfit_core")
        try:
            result = core.screen_assistance(**task["input"])
        except core.BillFitError as error:
            return {"error": error.as_dict()["code"]}
        data = core.assistance_data()
        if result["status"] != "screened" or result["rules_freshness"]["stale"]:
            raise ValueError("CURRENT_SKILL_DATA_REQUIRED")
        row["sourceVerified"] = data["verified_on"] == SOURCE["verifiedOn"] and data["source"]["url"] == SOURCE["url"]
        size = task["input"]["household_size"]
        return {"care_status": result["care"]["status"], "fera_status": result["fera"]["status"],
                "care_limit": core._income_limit(data["care_income_upper_limit"], size),
                "fera_limit": core._income_limit(data["fera_income_upper_limit"], size), "official_decision": False}
    finally:
        sys.path.pop(0)


def summarize(reports):
    result = []
    identities = set()
    for report in reports:
        if report["datasetHash"] != digest(DATASET) or report["sourceHash"] != digest(SOURCE) or report["arm"] not in ARMS:
            raise ValueError("DATASET_IDENTITY_MISMATCH")
        if report["arm"] in identities:
            raise ValueError("DUPLICATE_ARM")
        identities.add(report["arm"])
        rows = report["results"]
        if len(rows) != len(DATASET["tasks"]) or {row["taskId"] for row in rows} != {task["id"] for task in DATASET["tasks"]}:
            raise ValueError("INCOMPLETE_OR_DUPLICATE_TASKS")
        observed = [row for row in rows if row["status"] == "OBSERVED"]
        tasks = {task["id"]: task for task in DATASET["tasks"]}
        # Re-score immutable responses using one evaluator; stored run-time scores remain auditable.
        evaluations = [evaluate(tasks[row["taskId"]], row["answer"], row["sourceVerified"]) for row in observed]
        result.append({"arm": report["arm"], "observed": len(observed), "failedOrBlocked": len(rows)-len(observed),
            "taskCompleted": sum(item["taskCompleted"] for item in evaluations),
            "factsCorrect": sum(item["factsCorrect"] for item in evaluations), "factsChecked": sum(item["factsChecked"] for item in evaluations),
            "incorrectFields": sum(len(item["wrongFields"]) for item in evaluations),
            "missingOrAbstainedFields": sum(len(item["missingFields"]) for item in evaluations),
            "providerCalls": sum(row["providerCalls"] for row in rows), "toolCalls": sum(row["toolCalls"] for row in rows),
            "notRun": sum(row["status"] == "NOT_RUN" for row in rows),
            "durationMs": sum(row["durationMs"] for row in rows if row["durationMs"] is not None), "costUsd": None, "userOperations": None, "maintenanceHours": None})
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--arm", choices=ARMS)
    parser.add_argument("--adapter-json", type=Path)
    parser.add_argument("--billfit-root", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--summarize", nargs="+", type=Path)
    args = parser.parse_args()
    if args.summarize:
        analysis = {"evaluatorVersion": EVALUATOR_VERSION, "datasetHash": digest(DATASET), "sourceHash": digest(SOURCE),
                    "runFiles": [{"name": p.name, "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in args.summarize],
                    "summary": summarize([json.loads(p.read_text(encoding="utf-8")) for p in args.summarize])}
        if args.output:
            with args.output.open("x", encoding="utf-8") as handle:
                json.dump(analysis, handle, indent=2)
                handle.write("\n")
        print(json.dumps(analysis, indent=2)); return
    if not args.arm or not args.output or not args.output.is_absolute():
        parser.error("Choose --arm and a new absolute --output path")
    command = None
    if args.arm != "skill":
        command = json.loads(args.adapter_json.read_text(encoding="utf-8")) if args.adapter_json else None
        if not isinstance(command, list) or not command or not all(isinstance(part, str) and part for part in command):
            parser.error("An authorized argv-array --adapter-json is required")
    elif not args.billfit_root:
        parser.error("An existing --billfit-root checkout is required")
    report = {"datasetVersion": DATASET["version"], "datasetHash": digest(DATASET), "sourceHash": digest(SOURCE),
              "evaluatorVersion": EVALUATOR_VERSION,
              "arm": args.arm, "synthetic": True, "mode": "REAL_EXECUTION", "startedAt": datetime.now(timezone.utc).isoformat(),
              "pythonVersion": sys.version.split()[0], "billfitCommit": None, "results": []}
    if args.billfit_root:
        revision = subprocess.run(["git", "-C", str(args.billfit_root), "rev-parse", "HEAD"], capture_output=True, text=True, check=True, shell=False)
        report["billfitCommit"] = revision.stdout.strip()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)
    external_block = False
    for task in DATASET["tasks"]:
        row = {"taskId": task["id"], "status": "STARTED", "answer": None, "evaluation": None,
               "sourceVerified": False, "providerCalls": 0, "toolCalls": 0, "attempts": [], "model": None, "provider": None,
               "costUsd": None, "tokens": None, "userOperations": None, "maintenanceHours": None}
        start = time.perf_counter()
        if external_block:
            row.update(status="NOT_RUN", durationMs=None, blocker="EARLIER_ADAPTER_UNAVAILABLE")
            report["results"].append(row)
            continue
        try:
            row["answer"] = skill_run(task, args.billfit_root, row) if args.arm == "skill" else model_run(task, args.arm, command, row)
            row["evaluation"] = evaluate(task, row["answer"], row["sourceVerified"])
            row["status"] = "OBSERVED"
        except Exception as error:
            row["status"] = "FAILED_OR_BLOCKED"
            row["errorType"] = type(error).__name__
            external_block = isinstance(error, subprocess.TimeoutExpired) or str(error) == "ADAPTER_FAILED"
        row["durationMs"] = round((time.perf_counter()-start)*1000)
        report["results"].append(row)
        args.output.write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8")
        print(json.dumps({"taskId": task["id"], "status": row["status"], "providerCalls": row["providerCalls"]}), flush=True)
    report["completedAt"] = datetime.now(timezone.utc).isoformat()
    args.output.write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(summarize([report])))


if __name__ == "__main__":
    main()
