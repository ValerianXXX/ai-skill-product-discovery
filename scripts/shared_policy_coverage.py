"""Fail closed on known policy-availability confounds before new observations.

This is a bounded structural/consistency check, not independent legal review or
proof that prose is complete for every BillFit account type.
"""
from datetime import date


def _require(condition, code):
    if not condition:
        raise ValueError(code)


def validate_policy_coverage(corpus):
    documents = corpus.get('documents')
    _require(isinstance(documents, list), 'POLICY_DOCUMENTS')
    ids = [d.get('id') for d in documents if isinstance(d, dict)]
    _require(len(ids) == len(documents) == len(set(ids)), 'POLICY_DOCUMENTS')
    docs = {d['id']: d for d in documents}
    _require({'assistance-rules', 'screening-policy', 'workflow-policy'} <= set(docs), 'POLICY_DOCUMENTS')
    rules = docs['assistance-rules']['content']
    keys = {str(i) for i in range(1, 9)} | {'additional_person'}
    tables = []
    for name in ('care_income_upper_limit', 'fera_income_lower_limit', 'fera_income_upper_limit'):
        table = rules.get(name)
        _require(isinstance(table, dict) and set(table) == keys, 'POLICY_FERA_RANGE')
        _require(all(type(v) is int and v > 0 for v in table.values()), 'POLICY_FERA_RANGE')
        tables.append(table)
    care, lower, upper = tables
    _require(all(lower[str(i)] == care[str(i)] + 1 < upper[str(i)] for i in range(1, 9)), 'POLICY_FERA_RANGE')
    _require(lower['additional_person'] == care['additional_person'] < upper['additional_person'], 'POLICY_FERA_RANGE')
    try:
        start, end, verified = (date.fromisoformat(rules[k]) for k in ('effective_from', 'effective_to', 'verified_on'))
    except (KeyError, TypeError, ValueError) as error:
        raise ValueError('POLICY_DATES') from error
    _require(start <= end and verified <= end, 'POLICY_DATES')

    policy_doc = docs['screening-policy']
    _require(policy_doc.get('kind') == 'DECLARED_BOUNDED_RESEARCH_POLICY' and policy_doc.get('url') is None,
             'POLICY_PROVENANCE')
    policy = policy_doc['content']
    for clause in ('inputValidation', 'householdsAboveEight', 'freshness', 'carePrecedence',
                   'fractionalIncome', 'officialFacts', 'output'):
        _require(isinstance(policy.get(clause), dict) and bool(policy[clause]), 'POLICY_CLAUSE')
    for clause in ('scope', 'missingIncome'):
        _require(isinstance(policy.get(clause), str) and bool(policy[clause]), 'POLICY_CLAUSE')
    ordered = [
        ('missing_income', 'needs_information', 'needs_information'),
        ('income_at_or_below_care_maximum', 'likely_eligible', 'not_primary_path'),
        ('income_above_care_maximum_below_fera_minimum', 'likely_not_eligible_by_income', 'needs_official_confirmation'),
        ('income_at_or_above_fera_minimum_at_or_below_fera_maximum', 'likely_not_eligible_by_income', 'likely_eligible'),
        ('income_above_fera_maximum', 'likely_not_eligible_by_income', 'likely_not_eligible_by_income')]
    _require(policy.get('incomeDecisionOrder') == [dict(zip(('when', 'care', 'fera'), values)) for values in ordered],
             'POLICY_DECISION_ORDER')
    _require(policy['carePrecedence'].get('feraStatus') == 'not_primary_path', 'POLICY_CARE_PRECEDENCE')
    _require(policy['fractionalIncome'].get('roundingPolicy') == 'unverified'
             and policy['fractionalIncome'].get('feraStatus') == 'needs_official_confirmation', 'POLICY_FRACTIONAL_GAP')
    freshness = policy['freshness']
    _require(type(freshness.get('maximumAgeDays')) is int and freshness['maximumAgeDays'] == 45
             and freshness.get('threshold') == 'strictly_greater'
             and freshness.get('effectiveDates') == 'inclusive'
             and freshness.get('outsideEffectiveWindow') == 'do_not_screen'
             and freshness.get('overdueWithinWindow') == 'screen_with_stale_warning'
             and freshness.get('rateChange') == 'unknown_not_inferred_from_age', 'POLICY_FRESHNESS')
    facts = policy['officialFacts']
    simulated = corpus.get('maintenance') == 'SIMULATED_NOT_OFFICIAL'
    if simulated:
        _require(docs['assistance-rules'].get('url') is None and rules['source'].get('url') is None
                 and facts.get('sourceUrl') is None and facts.get('checkedOn') is None,
                 'POLICY_SIMULATED_SOURCE')
    else:
        _require(facts.get('sourceUrl') == docs['assistance-rules'].get('url') == rules['source'].get('url')
                 == 'https://www.cpuc.ca.gov/care/' and facts.get('checkedOn') == '2026-11-01',
                 'POLICY_PROVENANCE')
    workflow = docs['workflow-policy']
    _require(workflow.get('kind') == 'DECLARED_BOUNDED_RESEARCH_POLICY' and workflow.get('url') is None
             and all(isinstance(workflow['content'].get(k), str) and workflow['content'][k]
                     for k in ('bill', 'usage', 'artifacts')), 'POLICY_WORKFLOW')
    return {'status': 'PASS', 'scope': 'BOUNDED_INCOME_AND_TWO_SYNTHETIC_FILE_TASKS',
            'rangeRowsChecked': 8, 'additionalPersonChecked': True, 'decisionBranchesChecked': len(ordered),
            'simulatedPolicy': simulated, 'independentPolicyReview': False}
