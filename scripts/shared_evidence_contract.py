"""Pure contracts for the new equal-evidence pilot; historical scores are untouched."""
from __future__ import annotations
from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROUND = ROOT / 'benchmarks' / '2026-10-29'
ARMS = ('model', 'agent', 'skill')


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def load_round(maintenance=False):
    catalog = json.loads((ROUND / 'tasks.json').read_text(encoding='utf-8'))
    corpus = json.loads((ROUND / 'corpus.json').read_text(encoding='utf-8'))
    if len(catalog['tasks']) != 6 or len({t['id'] for t in catalog['tasks']}) != 6:
        raise ValueError('TASK_DENOMINATOR')
    if maintenance:
        task = deepcopy(next(t for t in catalog['tasks'] if t['id'] == catalog['maintenance']['taskId']))
        task['expected'] = deepcopy(catalog['maintenance']['expected'])
        task['prompt'] += ' This is a clearly simulated rules-change exercise, not an official update.'
        catalog['tasks'] = [task]
        document = next(d for d in corpus['documents'] if d['id'] == 'assistance-rules')
        document['kind'] = 'SIMULATED_MAINTENANCE_NOT_OFFICIAL'
        document['title'] = 'Synthetic threshold change for maintenance testing; not official policy'
        document['url'] = None
        for pointer, value in catalog['maintenance']['patch'].items():
            table, key = pointer.split('/')
            document['content'][table][key] = value
        corpus['maintenance'] = 'SIMULATED_NOT_OFFICIAL'
    return catalog, corpus


def documents_for(task, corpus):
    return [deepcopy(d) for d in corpus['documents'] if d['id'] in task['sourceIds']]


def pointer_value(value, pointer):
    if not isinstance(pointer, str) or not pointer.startswith('/') or len(pointer) > 160:
        raise ValueError('SOURCE_LOCATOR')
    for component in pointer[1:].split('/'):
        if '~' in component:
            raise ValueError('SOURCE_LOCATOR')
        value = value[int(component)] if isinstance(value, list) and component.isdecimal() else value[component]
    return value


def validate_answer(answer, task, corpus):
    if not isinstance(answer, dict) or set(answer) != {'fields', 'citations', 'note'}:
        raise ValueError('ANSWER_CONTRACT')
    if not isinstance(answer['fields'], dict) or len(answer['fields']) > 30:
        raise ValueError('FIELDS_CONTRACT')
    if not isinstance(answer['note'], str) or not 20 <= len(answer['note']) <= 1800:
        raise ValueError('NOTE_CONTRACT')
    citations = answer['citations']
    if not isinstance(citations, list) or len(citations) > 8:
        raise ValueError('CITATION_CONTRACT')
    documents = {d['id']: d for d in documents_for(task, corpus)}
    ids = []
    for citation in citations:
        if not isinstance(citation, dict) or set(citation) != {'sourceId', 'locators'} or citation['sourceId'] not in documents:
            raise ValueError('UNKNOWN_SOURCE')
        ids.append(citation['sourceId'])
        locations = citation['locators']
        if not isinstance(locations, list) or not locations or len(locations) > 30 or len(set(locations)) != len(locations):
            raise ValueError('SOURCE_LOCATOR')
        for location in locations:
            try:
                pointer_value(documents[citation['sourceId']]['content'], location)
            except (ValueError, KeyError, IndexError, TypeError) as error:
                raise ValueError('SOURCE_LOCATOR') from error
    if len(set(ids)) != len(ids):
        raise ValueError('DUPLICATE_SOURCE')
    digest(answer)
    return answer


def exact(actual, expected):
    if type(expected) is bool:
        return type(actual) is bool and actual == expected
    if type(expected) in (int, float):
        return type(actual) in (int, float) and math.isfinite(actual) and actual == expected
    return type(actual) is type(expected) and actual == expected


def evaluate(task, answer, corpus, artifact_verified):
    fields = answer.get('fields', {}) if isinstance(answer, dict) else {}
    if not isinstance(fields, dict):
        fields = {}
    missing = [key for key in task['expected'] if key not in fields or fields[key] is None]
    wrong = [key for key, value in task['expected'].items() if key not in missing and not exact(fields[key], value)]
    extra = sorted(set(fields) - set(task['expected']))
    contract = False
    evidence = False
    try:
        validate_answer(answer, task, corpus)
        contract = True
        retained = {c['sourceId']: set(c['locators']) for c in answer['citations']}
        evidence = all(set(locations) <= retained.get(source, set()) for source, locations in task['requiredCitations'].items())
    except (ValueError, TypeError):
        pass
    return {'factsRequired': len(task['expected']), 'factsCorrect': len(task['expected']) - len(missing) - len(wrong),
            'missingFields': missing, 'incorrectFields': wrong, 'extraFields': extra, 'contractValid': contract,
            'evidenceComplete': evidence, 'artifactVerified': artifact_verified,
            'taskCompleted': not missing and not wrong and not extra and contract and evidence and artifact_verified,
            'noteSemanticallyReviewed': False}


def request_for(task, corpus, arm, history):
    return {'protocol': 'SUBSTITUTE_SHARED_EVIDENCE_V2', 'arm': arm, 'synthetic': True,
            'taskId': task['id'], 'asOf': task['asOf'], 'task': task['prompt'], 'input': task['input'],
            'sharedEvidence': documents_for(task, corpus),
            'responseContract': {
                'tool': 'null for final, otherwise one allowed broker tool', 'arguments': 'empty object for final',
                'answer': {'fields': task['responseFields'], 'citations': [{'sourceId': 'one supplied document ID', 'locators': ['JSON pointer relative to that document content, such as /care_income_upper_limit/3 or /1/text']}],
                           'note': '20..1800 characters: a compact decision note with uncertainty and no invented completed actions'},
                'rules': 'Return exactly tool, arguments and answer. Answer is null during tool use. Final fields use exactly the requested names, null when genuinely unknown. Cite source pointers for all requested facts. A shared harness saves every valid final answer as a JSON artifact; do not claim a native save or utility action.'},
            'tools': [] if arm == 'model' else [
                {'name': 'search_sources', 'arguments': {'query': 'nonempty text'}, 'description': 'Search the same evidence already supplied, without live web or hidden facts.'},
                {'name': 'read_file', 'arguments': {'id': 'one supplied document ID'}, 'description': 'Read the same bounded document; no arbitrary filesystem access.'},
                {'name': 'calculate', 'arguments': {'expression': 'numbers and + - * /'}, 'description': 'Bounded generic arithmetic, no domain functions.'}],
            'history': history}
