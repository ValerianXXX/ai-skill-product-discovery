"""Call the real public BillFit implementation with isolated dates and evidence."""
from copy import deepcopy
from datetime import date
import importlib
from pathlib import Path
import sys
import tempfile

from shared_evidence_contract import digest, documents_for


def execute(task, corpus, root):
    directory = Path(root) / 'plugins/billfit/skills/billfit/scripts'
    if not (directory / 'billfit_core.py').is_file():
        raise ValueError('BILLFIT_CHECKOUT_REQUIRED')
    sys.path.insert(0, str(directory))
    try:
        core = importlib.import_module('billfit_core')
        bill_input = importlib.import_module('bill_input')
    finally:
        sys.path.pop(0)
    if Path(core.__file__).resolve().parent != directory.resolve():
        raise ValueError('BILLFIT_MODULE_ORIGIN')
    original_date, original_data = core.date, core.assistance_data
    evidence = {d['id']: d['content'] for d in documents_for(task, corpus)}
    fixed_date = date.fromisoformat(task['asOf'])

    class FrozenDate(date):
        @classmethod
        def today(cls):
            return fixed_date

    core.date = FrozenDate
    if 'assistance-rules' in evidence:
        core.assistance_data = lambda: deepcopy(evidence['assistance-rules'])
    try:
        if task['operation'] == 'assistance':
            try:
                result = core.screen_assistance(**task['input'])
            except core.BillFitError as error:
                fields = {'error': error.code, 'official_decision': False, 'can_act': False}
            else:
                if result['status'] == 'rules_outside_effective_window':
                    fields = {'status': result['status'], 'stale': result['rules_freshness']['stale'],
                              'outside_effective_window': result['rules_freshness']['outside_effective_window'],
                              'care_status': result['care']['status'], 'fera_status': result['fera']['status'], 'can_act': False}
                else:
                    data = core.assistance_data()
                    fields = {'status': result['status'], 'care_status': result['care']['status'], 'fera_status': result['fera']['status'],
                              'care_limit': core._income_limit(data['care_income_upper_limit'], task['input']['household_size']),
                              'fera_limit': core._income_limit(data['fera_income_upper_limit'], task['input']['household_size']), 'official_decision': False}
                    if task['input'].get('gross_annual_household_income') is None:
                        fields['missing'] = ['gross_annual_household_income']
            note = 'Actual BillFit screening on the supplied dated snapshot. This is preliminary and cannot enroll an account; missing, invalid or expired information must be resolved before action.'
        elif task['operation'] == 'bill_fields':
            result = bill_input.extract_spans(evidence['bill-text'], digest(evidence['bill-text']), 'SYNTHETIC_EXTRACTED_TEXT')
            values = lambda field: [c['value'] for c in result['candidates'] if c['field'] == field]
            fields = {'status': result['status'], 'current_plan': values('current_plan')[0],
                      'energy_charge_values': values('reported_energy_charge'), 'base_services_charge': values('reported_base_services_charge')[0],
                      'total_kwh': values('total_kwh')[0], 'conflicting_fields': result['conflicting_fields'],
                      'automatic_calculation': result['automatic_calculation'], 'automatic_confirmation': result['automatic_confirmation']}
            note = 'Actual BillFit span extraction retains the conflicting page values and excludes amount due. This text-only fixture does not measure OCR; the user must confirm every field.'
        elif task['operation'] == 'usage':
            with tempfile.TemporaryDirectory(prefix='shared-evidence-usage-') as temporary:
                file = Path(temporary) / 'synthetic.csv'
                file.write_text('\n'.join(evidence['usage-csv']) + '\n', encoding='utf-8')
                result = core.parse_usage_file(str(file))
                comparison = core.compare_rate_plans(usage_file=str(file), candidate_plans=['E-1'], baseline_territory='X', service_type='basic', qualifying_technologies=[])
            summary = result['summary']
            fields = {'status': result['status'], 'unique_intervals': summary['interval_count'],
                      'duplicate_intervals_removed': len(evidence['usage-csv']) - 1 - summary['interval_count'],
                      'total_kwh': summary['total_kwh'], 'hours_covered': summary['elapsed_minutes'] / 60,
                      'recommendation_ready': not comparison['recommendation']['status'].startswith('withheld')}
            note = 'Actual BillFit interval parsing removes duplicate readings and totals unique energy. The four-hour sample withholds switching guidance; no annual saving or rate-plan change is established.'
        else:
            raise ValueError('UNSUPPORTED_OPERATION')
    finally:
        core.date, core.assistance_data = original_date, original_data
    # The bridge adds a common-format evidence mapping, not a new product-native export.
    # Mapping is tied to the public operation and input, never to expected answers.
    citations = []
    if 'assistance-rules' in evidence:
        size = str(task['input']['household_size'])
        locations = ['/verified_on', '/effective_to'] if fields.get('status') == 'rules_outside_effective_window' else [f'/care_income_upper_limit/{size}', f'/fera_income_upper_limit/{size}']
        citations = [{'sourceId': 'assistance-rules', 'locators': locations}]
    if 'bill-text' in evidence:
        citations = [{'sourceId': 'bill-text', 'locators': [f'/{i}/text' for i in range(len(evidence['bill-text']))]}]
    if 'usage-csv' in evidence:
        citations = [{'sourceId': 'usage-csv', 'locators': [f'/{i}' for i in range(1, len(evidence['usage-csv']))]}]
    return {'fields': fields, 'citations': citations, 'note': note}
