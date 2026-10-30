"""Recompute the dated pilot without model calls or changing original observations."""
import argparse
import hashlib
import json
from pathlib import Path

from shared_evidence_benchmark import read_summary
from shared_evidence_contract import ROUND

RUN_NAMES = ('model', 'agent', 'skill', 'maintenance-skill',
             'clarified-model', 'clarified-agent', 'clarified-skill',
             'clarified-maintenance-model', 'clarified-maintenance-agent',
             'clarified-maintenance-skill')


def build_report(root=ROUND):
    observations = {}
    receipts = {}
    total_calls = 0
    measured_api_calls = []
    for name in RUN_NAMES:
        file = root / 'results' / name / 'run.json'
        summary = read_summary(file)
        raw = json.loads(file.read_text(encoding='utf-8'))
        summary['exactFieldsMatched'] = summary.pop('factsCorrect')
        summary['exactFieldsRequired'] = summary.pop('factsRequired')
        for item in summary['evaluations']:
            item['exactFieldsMatched'] = item.pop('factsCorrect')
            item['exactFieldsRequired'] = item.pop('factsRequired')
        summary['interpretation'] = (
            'INCOMPLETE_SHARED_POLICY_NOT_FAIR_QUALITY_COMPARISON' if raw['maintenance'] else
            'POST_DISCOVERY_CALIBRATION_NOT_GENERALIZATION' if raw.get('clarified') else
            'FORMAT_AMBIGUOUS_NOT_FACTUAL_SCORE')
        summary['taskIds'] = [row['taskId'] for row in raw['results']]
        summary['billfitCommit'] = raw.get('billfitCommit')
        observations[name] = summary
        total_calls += summary['adapterCalls']
        if summary['adapterCalls']:
            measured_api_calls.append(summary['usage']['modelApiCalls'])
        for artifact in [file] + sorted(file.parent.glob('*.artifact.json')):
            content = artifact.read_bytes()
            receipts[artifact.relative_to(root).as_posix()] = {
                'bytes': len(content), 'sha256': hashlib.sha256(content).hexdigest()}
    if total_calls > 28:
        raise ValueError('FROZEN_CALL_BUDGET_EXCEEDED')
    for name in ('tasks.json', 'corpus.json', 'response-format.json'):
        content = (root / name).read_bytes()
        receipts[name] = {'bytes': len(content), 'sha256': hashlib.sha256(content).hexdigest()}
    return {
        'schema': 'SHARED_EVIDENCE_REPORT_V2',
        'protocolFreezeCommit': '28294c9aa2994d266acbc8f4a2af78134124e8e6',
        'formatFreezeCommit': 'f2a4962',
        'maximumAdapterCalls': 28, 'adapterCalls': total_calls,
        'measuredProviderApiCalls': sum(measured_api_calls) if all(value is not None for value in measured_api_calls) else None,
        'billingCostUsd': None, 'independentHumanReview': False,
        'maintenanceSourceReviewMs': None, 'maintenancePreparationMs': None,
        'maintenancePolicyGap': 'The shared corpus contains upper ceilings but no FERA lower-bound/CARE-precedence rule. BillFit has that rule in code. This variation cannot isolate reasoning or maintenance quality.',
        'observations': observations, 'receipts': receipts}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', type=Path)
    parser.add_argument('--check', type=Path)
    args = parser.parse_args()
    report = build_report()
    if args.check:
        if json.loads(args.check.read_text(encoding='utf-8')) != report:
            raise ValueError('PUBLISHED_REPORT_CHANGED_OR_OBSERVATION_DRIFT')
        print('Shared-evidence report, fixed denominators, budgets and artifact receipts verified; no model calls.')
    elif args.write:
        with args.write.open('x', encoding='utf-8', newline='\n') as handle:
            json.dump(report, handle, indent=2, allow_nan=False)
            handle.write('\n')
    else:
        print(json.dumps(report, indent=2, allow_nan=False))


if __name__ == '__main__':
    main()
