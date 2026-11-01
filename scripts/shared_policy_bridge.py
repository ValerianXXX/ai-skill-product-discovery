"""Common-format bridge to actual BillFit; no expected-answer access."""
from copy import deepcopy
from datetime import date


def execute_assistance(core, task, evidence):
    snapshot = deepcopy(evidence['assistance-rules'])
    inputs = task['input']
    try:
        result = core._screen_assistance_snapshot(snapshot, **inputs, as_of=date.fromisoformat(task['asOf']))
    except core.BillFitError as error:
        fields = {'error': error.code, 'official_decision': False, 'can_act': False}
    else:
        if result['status'] == 'rules_outside_effective_window':
            fields = {'status': result['status'], 'stale': result['rules_freshness']['stale'],
                'outside_effective_window': result['rules_freshness']['outside_effective_window'],
                'care_status': result['care']['status'], 'fera_status': result['fera']['status'], 'can_act': False}
        else:
            size = inputs['household_size']
            fields = {'status': result['status'], 'care_status': result['care']['status'], 'fera_status': result['fera']['status'],
                'care_limit': core._income_limit(snapshot['care_income_upper_limit'], size),
                'fera_lower': core._income_limit(snapshot['fera_income_lower_limit'], size),
                'fera_limit': core._income_limit(snapshot['fera_income_upper_limit'], size),
                'stale': result['rules_freshness']['stale'], 'outside_effective_window': result['rules_freshness']['outside_effective_window'],
                'official_decision': False}
    row = str(min(inputs['household_size'], 8))
    locators = [f'/care_income_upper_limit/{row}', f'/fera_income_lower_limit/{row}',
        f'/fera_income_upper_limit/{row}', '/verified_on', '/effective_from', '/effective_to']
    if inputs['household_size'] > 8:
        locators += ['/care_income_upper_limit/additional_person', '/fera_income_lower_limit/additional_person', '/fera_income_upper_limit/additional_person']
    return {'fields': fields, 'citations': [
        {'sourceId': 'assistance-rules', 'locators': locators},
        {'sourceId': 'screening-policy', 'locators': ['/inputValidation', '/freshness', '/output', '/incomeDecisionOrder', '/fractionalIncome', '/householdsAboveEight']}],
        'note': 'Actual BillFit income-only screening on the equally supplied snapshot and declared decision semantics. This is preliminary; no enrollment, official decision or utility action occurs. Unknown precision and stale evidence require confirmation.'}
