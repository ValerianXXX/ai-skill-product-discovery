"""Generic tools over a common public/synthetic corpus, never product answers."""
from shared_evidence_contract import documents_for
from substitute_benchmark import calculate


def broker(name, arguments, task, corpus):
    if not isinstance(arguments, dict):
        raise ValueError('TOOL_ARGUMENTS')
    documents = documents_for(task, corpus)
    if name == 'read_file' and set(arguments) == {'id'}:
        matches = [d for d in documents if d['id'] == arguments['id']]
        if len(matches) != 1:
            raise ValueError('FILE_NOT_ALLOWED')
        return matches[0]
    if name == 'search_sources' and set(arguments) == {'query'}:
        query = arguments['query']
        if not isinstance(query, str) or not 1 <= len(query.strip()) <= 300:
            raise ValueError('QUERY_LIMIT')
        tokens = query.lower().split()
        return {'scope': 'SAME_SHARED_EVIDENCE', 'documents': [d for d in documents if any(token in (d['title'] + ' ' + str(d['content'])).lower() for token in tokens)]}
    if name == 'calculate' and set(arguments) == {'expression'}:
        return {'value': calculate(arguments['expression'])}
    raise ValueError('TOOL_NOT_ALLOWED')
