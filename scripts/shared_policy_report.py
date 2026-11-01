"""Recompute the prepared round's reference outcomes without provider calls."""
import argparse
import hashlib
import json
from pathlib import Path

from shared_evidence_benchmark import read_summary
from shared_evidence_contract import digest, load_round, request_for

ROOT = Path(__file__).resolve().parents[1]
ROUND = ROOT / 'benchmarks/2026-11-01'


def verify(analysis_file=ROUND / 'analysis.json'):
    analysis = json.loads(analysis_file.read_text(encoding='utf-8'))
    for key, directory in (('skill', 'skill'), ('maintenanceSkill', 'maintenance-skill')):
        if digest(analysis[key]) != digest(read_summary(ROUND / 'results' / directory / 'run.json')):
            raise ValueError('REFERENCE_SUMMARY_CHANGED')
    if (type(analysis['newProviderCalls']) is not int or analysis['newProviderCalls'] != 0 or analysis['comparativeBenefit'] is not None
            or analysis['costUsd'] is not None or analysis['userOperations'] is not None
            or analysis['humanMaintenanceMs'] is not None or analysis['independentPolicyReview'] is not False):
        raise ValueError('UNOBSERVED_COMPARATIVE_CLAIM')
    for arm in ('generalModel', 'genericAgent'):
        if digest(analysis[arm]) != digest({'planned': 12, 'observed': 0, 'status': 'NOT_RUN_BUDGET_UNALLOCATED', 'quality': None}):
            raise ValueError('UNOBSERVED_MODEL_RESULT')
    receipt = json.loads((ROUND / 'verification.json').read_text(encoding='utf-8'))
    for item in receipt['historicalFiles']:
        if hashlib.sha256((ROOT / item['path']).read_bytes()).hexdigest() != item['gitBlobSha256']:
            raise ValueError('HISTORICAL_FILE_CHANGED')
    for item in receipt['testLogs']:
        if hashlib.sha256((ROUND / item['file']).read_bytes()).hexdigest() != item['publicSha256']:
            raise ValueError('TEST_LOG_CHANGED')
    catalog, corpus = load_round(round_id='2026-11-01')
    actual = []
    for task in catalog['tasks']:
        model, agent = [request_for(task, corpus, arm, []) for arm in ('model', 'agent')]
        if model['sharedEvidence'] != agent['sharedEvidence'] or model['responseContract'] != agent['responseContract']:
            raise ValueError('UNEQUAL_SHARED_INFORMATION')
        actual.append({'taskId': task['id'], 'evidenceHash': digest(model['sharedEvidence']),
            'responseContractHash': digest(model['responseContract']), 'modelRequestHash': digest(model),
            'agentRequestHash': digest(agent)})
    if actual != receipt['sameEvidenceAndFormat']:
        raise ValueError('PREPARED_REQUEST_CHANGED')
    return {'status': 'PASS', 'referenceTasks': 13, 'historicalFilesUnchanged': len(receipt['historicalFiles']),
        'newProviderCalls': 0, 'modelComparison': 'NOT_PRODUCED'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', type=Path, default=ROUND / 'analysis.json')
    args = parser.parse_args()
    print(json.dumps(verify(args.check)))


if __name__ == '__main__':
    main()
