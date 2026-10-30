"""Bounded real runs and independently recomputed artifacts; no default model calls."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

from shared_evidence_contract import ARMS, digest, evaluate, load_round, request_for, validate_answer
from shared_evidence_broker import broker
from substitute_benchmark import summarize_usage, validate_usage


def now():
    return datetime.now(timezone.utc).isoformat()


def atomic_report(file, report):
    temporary = file.with_suffix('.pending')
    with temporary.open('x', encoding='utf-8', newline='\n') as handle:
        json.dump(report, handle, indent=2, allow_nan=False)
        handle.write('\n')
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, file)


def save_artifact(directory, task, answer):
    content = (json.dumps({'provenance': 'COMMON_HARNESS_MATERIALIZATION', 'taskId': task['id'], 'answer': answer}, indent=2, allow_nan=False) + '\n').encode()
    file = directory / (task['id'] + '.artifact.json')
    with file.open('xb') as handle:
        handle.write(content)
        handle.flush()
        os.fsync(handle.fileno())
    return {'path': file.name, 'bytes': len(content), 'sha256': hashlib.sha256(content).hexdigest(),
            'provenance': 'COMMON_HARNESS_MATERIALIZATION'}


def verify_artifact(directory, row):
    receipt = row.get('artifact')
    if receipt is None:
        return False
    expected_name = row['taskId'] + '.artifact.json'
    if not isinstance(receipt, dict) or receipt.get('path') != expected_name or receipt.get('provenance') != 'COMMON_HARNESS_MATERIALIZATION':
        raise ValueError('ARTIFACT_RECEIPT')
    file = directory / expected_name
    if file.is_symlink() or not file.is_file() or file.stat().st_size > 30000:
        raise ValueError('ARTIFACT_FILE')
    content = file.read_bytes()
    if receipt['bytes'] != len(content) or receipt['sha256'] != hashlib.sha256(content).hexdigest():
        raise ValueError('ARTIFACT_HASH')
    value = json.loads(content)
    if value != {'provenance': 'COMMON_HARNESS_MATERIALIZATION', 'taskId': row['taskId'], 'answer': row['answer']}:
        raise ValueError('ARTIFACT_CONTENT')
    return True


def model_answer(task, corpus, arm, command, row, limits, checkpoint):
    history = []
    deadline = time.monotonic() + limits['secondsPerTask']
    for _ in range(limits['modelTurns'] if arm == 'model' else limits['agentTurns']):
        timeout = min(limits['secondsPerCall'], deadline - time.monotonic())
        if timeout <= 0:
            raise TimeoutError('TASK_DEADLINE')
        request = request_for(task, corpus, arm, history)
        encoded = json.dumps(request, allow_nan=False)
        if len(encoded.encode()) > 39000:
            raise ValueError('INPUT_LIMIT')
        attempt = {'status': 'STARTED', 'requestHash': digest(request), 'startedAt': now(), 'durationMs': None, 'response': None, 'usage': None}
        row['attempts'].append(attempt)
        checkpoint()
        started = time.perf_counter()
        try:
            response = subprocess.run(command, input=encoded, text=True, encoding='utf-8', capture_output=True,
                                      timeout=timeout, shell=False, check=False)
            if response.returncode or len(response.stdout) > 20000:
                raise ConnectionError('ADAPTER_UNAVAILABLE')
            envelope = json.loads(response.stdout)
            decision = envelope['decision']
            attempt['usage'] = validate_usage(envelope.get('usage'))
            row['model'], row['provider'] = envelope['model'], envelope['provider']
            attempt['response'] = decision
            if not isinstance(decision, dict) or set(decision) != {'tool', 'arguments', 'answer'}:
                raise ValueError('RESPONSE_CONTRACT')
            if decision['tool'] is None:
                if decision['arguments'] != {}:
                    raise ValueError('FINAL_ARGUMENTS')
                attempt['status'] = 'RECEIVED'
                return decision['answer']
            if arm != 'agent' or decision['answer'] is not None:
                raise ValueError('UNAUTHORIZED_TOOL')
            result = broker(decision['tool'], decision['arguments'], task, corpus)
            attempt['toolResult'] = result
            attempt['status'] = 'RECEIVED'
            history.append({'request': decision, 'result': result})
        except Exception as error:
            attempt['status'] = 'FAILED'
            attempt['errorType'] = type(error).__name__
            raise
        finally:
            attempt['durationMs'] = round((time.perf_counter() - started) * 1000)
            checkpoint()
    raise ValueError('TURN_LIMIT')


def read_summary(file):
    report = json.loads(file.read_text(encoding='utf-8'))
    catalog, corpus = load_round(report['maintenance'])
    if report['schema'] != 'SHARED_EVIDENCE_RUN_V2' or report['arm'] not in ARMS or report['catalogHash'] != digest(catalog) or report['corpusHash'] != digest(corpus):
        raise ValueError('ROUND_IDENTITY')
    tasks = {t['id']: t for t in catalog['tasks']}
    rows = report['results']
    if len(rows) != len(tasks) or {r['taskId'] for r in rows} != set(tasks):
        raise ValueError('TASK_DENOMINATOR')
    evaluations, attempts = [], []
    measured_duration = []
    for row in rows:
        if row['status'] not in {'OBSERVED', 'FAILED', 'NOT_RUN', 'STARTED'}:
            raise ValueError('RESULT_STATUS')
        verified = verify_artifact(file.parent, row)
        history = []
        task = tasks[row['taskId']]
        if len(row['attempts']) > (catalog['limits']['modelTurns'] if report['arm'] == 'model' else catalog['limits']['agentTurns'] if report['arm'] == 'agent' else 0):
            raise ValueError('CALL_LIMIT')
        final = None
        for attempt in row['attempts']:
            if attempt['requestHash'] != digest(request_for(task, corpus, report['arm'], history)):
                raise ValueError('REQUEST_IDENTITY')
            decision = attempt.get('response')
            if attempt['status'] == 'RECEIVED' and decision is not None:
                if decision['tool'] is None:
                    final = decision['answer']
                else:
                    result = broker(decision['tool'], decision['arguments'], task, corpus)
                    if result != attempt.get('toolResult'):
                        raise ValueError('TOOL_RESULT_CHANGED')
                    history.append({'request': decision, 'result': result})
        candidate = row['answer'] if row['status'] == 'OBSERVED' else row.get('candidateAnswer')
        if report['arm'] != 'skill' and candidate is not None and final != candidate:
            raise ValueError('FINAL_RESPONSE_CHANGED')
        if row['status'] != 'OBSERVED' and (row['answer'] is not None or verified):
            raise ValueError('UNAVAILABLE_OUTCOME')
        evaluations.append(evaluate(task, candidate, corpus, verified))
        attempts.extend(row['attempts'])
        if row['durationMs'] is not None:
            if type(row['durationMs']) is not int or row['durationMs'] < 0:
                raise ValueError('DURATION')
            measured_duration.append(row['durationMs'])
    usage = summarize_usage(attempts, len(attempts))
    return {'arm': report['arm'], 'maintenance': report['maintenance'], 'planned': len(tasks),
            'observed': sum(r['status'] == 'OBSERVED' for r in rows),
            'failed': sum(r['status'] == 'FAILED' for r in rows), 'notRunOrInterrupted': sum(r['status'] in {'STARTED', 'NOT_RUN'} for r in rows),
            'taskCompleted': sum(e['taskCompleted'] for e in evaluations),
            'factsCorrect': sum(e['factsCorrect'] for e in evaluations), 'factsRequired': sum(e['factsRequired'] for e in evaluations),
            'incorrectFields': sum(len(e['incorrectFields']) for e in evaluations), 'missingFields': sum(len(e['missingFields']) for e in evaluations),
            'evidenceComplete': sum(e['evidenceComplete'] for e in evaluations), 'artifactsVerified': sum(e['artifactVerified'] for e in evaluations),
            'adapterCalls': len(attempts), 'toolCalls': sum('toolResult' in a for a in attempts),
            'usage': usage, 'costUsd': None, 'userOperations': None, 'humanMaintenanceMs': None,
            'durationMs': sum(measured_duration), 'timedTasks': len(measured_duration), 'evaluations': evaluations,
            'noteSemanticsIndependentlyReviewed': False}


def run(arm, directory, command=None, billfit_root=None, maintenance=False):
    catalog, corpus = load_round(maintenance)
    directory.mkdir(parents=True, exist_ok=False)
    file = directory / 'run.json'
    report = {'schema': 'SHARED_EVIDENCE_RUN_V2', 'mode': 'REAL_EXECUTION', 'syntheticInputs': True,
              'arm': arm, 'maintenance': maintenance, 'catalogHash': digest(catalog), 'corpusHash': digest(corpus),
              'startedAt': now(), 'completedAt': None, 'billfitCommit': None, 'results': []}
    if arm == 'skill':
        revision = subprocess.run(['git', '-C', str(billfit_root), 'rev-parse', 'HEAD'], capture_output=True, text=True, check=True)
        dirty = subprocess.run(['git', '-C', str(billfit_root), 'status', '--porcelain'], capture_output=True, text=True, check=True)
        if dirty.stdout.strip():
            raise ValueError('BILLFIT_DIRTY_CHECKOUT')
        report['billfitCommit'] = revision.stdout.strip()
    for task in catalog['tasks']:
        report['results'].append({'taskId': task['id'], 'status': 'NOT_RUN', 'answer': None, 'attempts': [], 'artifact': None,
                                  'durationMs': None, 'model': None, 'provider': None})
    checkpoint = lambda: atomic_report(file, report)
    checkpoint()
    unavailable = False
    for task, row in zip(catalog['tasks'], report['results']):
        if unavailable:
            row['blocker'] = 'EARLIER_RUNTIME_UNAVAILABLE_OR_EXTRA_PROVIDER_CALLS'
            continue
        started = time.perf_counter()
        row['status'] = 'STARTED'
        checkpoint()
        try:
            if arm == 'skill':
                from billfit_benchmark_bridge import execute
                answer = execute(task, corpus, billfit_root)
            else:
                answer = model_answer(task, corpus, arm, command, row, catalog['limits'], checkpoint)
            row['candidateAnswer'] = answer
            row['answer'] = validate_answer(answer, task, corpus)
            row['artifact'] = save_artifact(directory, task, answer)
            row['status'] = 'OBSERVED'
        except Exception as error:
            row['status'] = 'FAILED'
            row['answer'] = None
            row['errorType'] = type(error).__name__
            unavailable = isinstance(error, (ConnectionError, TimeoutError, subprocess.TimeoutExpired))
        finally:
            row['durationMs'] = round((time.perf_counter() - started) * 1000)
            # Adapter invocations and provider calls are different budget units.
            # Stop the arm if measured provider retries exceeded the one-call expectation.
            if any((a.get('usage') or {}).get('modelApiCalls', 0) not in (None, 0, 1) for a in row['attempts']):
                unavailable = True
            checkpoint()
            print(json.dumps({'taskId': task['id'], 'status': row['status'], 'adapterCalls': len(row['attempts'])}), flush=True)
    report['completedAt'] = now()
    checkpoint()
    return read_summary(file)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--arm', choices=ARMS)
    parser.add_argument('--output-dir', type=Path)
    parser.add_argument('--adapter-json', type=Path)
    parser.add_argument('--billfit-root', type=Path)
    parser.add_argument('--maintenance', action='store_true')
    parser.add_argument('--summarize', type=Path, nargs='+')
    args = parser.parse_args()
    if args.summarize:
        print(json.dumps([read_summary(file) for file in args.summarize], indent=2)); return
    if not args.arm or not args.output_dir or not args.output_dir.is_absolute():
        parser.error('Choose an arm and a new absolute output directory')
    command = json.loads(args.adapter_json.read_text()) if args.adapter_json else None
    if args.arm != 'skill' and (not isinstance(command, list) or not command or not all(isinstance(s, str) and s for s in command)):
        parser.error('An existing authorized argv adapter is required')
    if args.arm == 'skill' and not args.billfit_root:
        parser.error('Provide the existing public BillFit checkout')
    print(json.dumps(run(args.arm, args.output_dir, command, args.billfit_root, args.maintenance), indent=2))


if __name__ == '__main__':
    main()
