"""New dated preparation without changing historical corpus or request hashes."""
from copy import deepcopy
import json
from pathlib import Path

from shared_policy_coverage import validate_policy_coverage

ROUND = Path(__file__).resolve().parents[1] / 'benchmarks/2026-11-01'


def load_policy_round(maintenance=False, clarified=False):
    if clarified:
        raise ValueError('ROUND_FORMAT_ALREADY_DECLARED')
    catalog, corpus, formats = [json.loads((ROUND / name).read_text(encoding='utf-8'))
        for name in ('tasks.json', 'corpus.json', 'response-format.json')]
    tasks = catalog['tasks']
    if len(tasks) != 12 or len({t['id'] for t in tasks}) != 12:
        raise ValueError('TASK_DENOMINATOR')
    for task in tasks:
        if task['operation'] == 'assistance':
            if ('screening-policy' not in task['sourceIds'] or 'assistance-rules' not in task['sourceIds']
                    or task['input'].get('enrolled_public_programs', []) != []
                    or task['input'].get('medical_baseline_need') is not None):
                raise ValueError('POLICY_TASK_SCOPE')
        elif task['operation'] not in ('bill_fields', 'usage') or 'workflow-policy' not in task['sourceIds']:
            raise ValueError('POLICY_TASK_SCOPE')
        task['responseFormat'] = deepcopy(formats)
    if maintenance:
        task = deepcopy(next(t for t in tasks if t['id'] == catalog['maintenance']['taskId']))
        task['expected'] = deepcopy(catalog['maintenance']['expected'])
        task['prompt'] += ' This is a clearly simulated rules-change exercise, not an official update.'
        catalog['tasks'] = [task]
        doc = next(d for d in corpus['documents'] if d['id'] == 'assistance-rules')
        for pointer, value in catalog['maintenance']['patch'].items():
            table, key = pointer.split('/')
            doc['content'][table][key] = value
        doc.update(kind='SIMULATED_MAINTENANCE_NOT_OFFICIAL', title='Synthetic maintenance; not official policy', url=None)
        doc['content']['source'] = {'url': None, 'title': 'Synthetic maintenance; not official policy'}
        doc['content']['status'] = 'SIMULATED_NOT_OFFICIAL'
        policy = next(d for d in corpus['documents'] if d['id'] == 'screening-policy')['content']
        policy['officialFacts'].update(sourceUrl=None, checkedOn=None, status='SIMULATED_NOT_OFFICIAL')
        corpus['maintenance'] = 'SIMULATED_NOT_OFFICIAL'
    validate_policy_coverage(corpus)
    return catalog, corpus
