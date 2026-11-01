"""Validate collector state transitions before deriving research outcomes.

This checks internal consistency, not provider authenticity or answer semantics.
Failed model payloads remain evidence; only received, authorized tool turns earn
tool-use credit. No adapters, network calls or record rewrites occur here.
"""
from dataclasses import dataclass

from shared_evidence_broker import broker
from shared_evidence_contract import digest, request_for, validate_answer


@dataclass(frozen=True)
class ReplayedRow:
    candidate: object
    tool_calls: int


def validate_run_metadata(report):
    if (not isinstance(report, dict) or report.get('mode') != 'REAL_EXECUTION'
            or report.get('syntheticInputs') is not True
            or type(report.get('maintenance')) is not bool
            or type(report.get('clarified', False)) is not bool):
        raise ValueError('EXECUTION_IDENTITY')


def _same_json(first, second):
    # Python equality treats True as 1, including inside nested tool results.
    return digest(first) == digest(second)


def _duration(value):
    if value is not None and (type(value) is not int or value < 0):
        raise ValueError('DURATION')


def replay_row(row, task, corpus, arm, limits, artifact_verified):
    status = row.get('status')
    if status not in {'OBSERVED', 'FAILED', 'NOT_RUN', 'STARTED'}:
        raise ValueError('RESULT_STATUS')
    attempts = row.get('attempts')
    if not isinstance(attempts, list):
        raise ValueError('ATTEMPTS_CONTRACT')
    limit = limits['modelTurns'] if arm == 'model' else limits['agentTurns'] if arm == 'agent' else 0
    if len(attempts) > limit:
        raise ValueError('CALL_LIMIT')
    _duration(row.get('durationMs'))
    if status == 'NOT_RUN' and (attempts or row.get('candidateAnswer') is not None
                                or row.get('durationMs') is not None
                                or row.get('model') is not None or row.get('provider') is not None):
        raise ValueError('UNATTEMPTED_OUTCOME')

    history = []
    terminal = False
    final_received = False
    final = None
    tool_calls = 0
    for attempt in attempts:
        if terminal:
            raise ValueError('TURN_AFTER_TERMINAL')
        if not isinstance(attempt, dict) or attempt.get('status') not in {'STARTED', 'RECEIVED', 'FAILED'}:
            raise ValueError('ATTEMPT_STATUS')
        if attempt.get('requestHash') != digest(request_for(task, corpus, arm, history)):
            raise ValueError('REQUEST_IDENTITY')
        _duration(attempt.get('durationMs'))
        if attempt['status'] != 'RECEIVED':
            # A transport/parser failure or interrupted checkpoint may retain an
            # incomplete payload. It earns no tool credit and permits no retry.
            terminal = True
            continue

        decision = attempt.get('response')
        if not isinstance(decision, dict) or set(decision) != {'tool', 'arguments', 'answer'}:
            raise ValueError('RESPONSE_CONTRACT')
        if decision['tool'] is None:
            if decision['arguments'] != {}:
                raise ValueError('FINAL_ARGUMENTS')
            if 'toolResult' in attempt:
                raise ValueError('FINAL_HAS_TOOL_RESULT')
            # Receiving an invalid answer is still a real attempt. Validation
            # failure belongs to the row and is not retroactively repaired.
            final = decision['answer']
            final_received = True
            terminal = True
        else:
            if arm != 'agent' or decision['answer'] is not None:
                raise ValueError('UNAUTHORIZED_TOOL')
            result = broker(decision['tool'], decision['arguments'], task, corpus)
            if 'toolResult' not in attempt or not _same_json(result, attempt['toolResult']):
                raise ValueError('TOOL_RESULT_CHANGED')
            history.append({'request': decision, 'result': result})
            tool_calls += 1

    candidate = row.get('answer') if status == 'OBSERVED' else row.get('candidateAnswer')
    if arm != 'skill' and (status == 'OBSERVED' or candidate is not None):
        if not final_received or not _same_json(final, candidate):
            raise ValueError('FINAL_RESPONSE_CHANGED')
    if status == 'OBSERVED':
        if not artifact_verified:
            raise ValueError('OBSERVED_ARTIFACT_REQUIRED')
        validate_answer(candidate, task, corpus)
        if 'candidateAnswer' in row and not _same_json(row['candidateAnswer'], candidate):
            raise ValueError('CANDIDATE_RESPONSE_CHANGED')
    elif row.get('answer') is not None or artifact_verified:
        raise ValueError('UNAVAILABLE_OUTCOME')
    return ReplayedRow(candidate, tool_calls)
