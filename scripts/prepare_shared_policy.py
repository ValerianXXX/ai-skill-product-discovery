"""Inspect or export the new common requests; never launch a model adapter."""
import argparse
import json
from pathlib import Path

from shared_evidence_contract import digest, load_round, request_for
from shared_policy_coverage import validate_policy_coverage


def prepare(directory=None, maintenance=False):
    catalog, corpus = load_round(maintenance=maintenance, round_id='2026-11-01')
    coverage = validate_policy_coverage(corpus)
    requests = {}
    for task in catalog['tasks']:
        for arm in ('model', 'agent'):
            request = request_for(task, corpus, arm, [])
            if len(json.dumps(request, allow_nan=False).encode()) > 39000:
                raise ValueError('INPUT_LIMIT')
            requests[f'{task["id"]}.{arm}.json'] = request
    receipt = {'schema': 'SHARED_POLICY_PREPARATION_V1', 'roundId': '2026-11-01',
        'status': 'PREPARED_NOT_MODEL_OBSERVED', 'maintenance': maintenance,
        'catalogHash': digest(catalog), 'corpusHash': digest(corpus),
        'coverage': coverage, 'tasks': len(catalog['tasks']),
        'requests': [{'file': name, 'requestHash': digest(value)} for name, value in requests.items()],
        'providerCalls': 0, 'modelResults': None, 'agentResults': None,
        'modelBudgetStatus': 'NOT_ALLOCATED', 'independentPolicyReview': False}
    if directory is not None:
        directory.mkdir(parents=True, exist_ok=False)
        for name, value in {**requests, 'preparation.json': receipt}.items():
            with (directory / name).open('x', encoding='utf-8', newline='\n') as handle:
                json.dump(value, handle, indent=2, allow_nan=False)
                handle.write('\n')
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path)
    parser.add_argument('--maintenance', action='store_true')
    args = parser.parse_args()
    print(json.dumps(prepare(args.output_dir, args.maintenance), indent=2))


if __name__ == '__main__':
    main()
