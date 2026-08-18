# Contributing

Contributions that improve the method, correct evidence, or add a fully sourced case are welcome.

## Evidence corrections

Open an **Evidence correction** issue and include:

- the affected file and evidence ID;
- the exact statement that needs correction;
- a primary or stronger source;
- the date you checked it;
- whether the change affects a score or decision.

## New cases

Use the [case template](templates/case-study-template.md) and the blank ledgers in [`templates/`](templates/README.md). A case must:

- record rejected alternatives and decision changes;
- distinguish observation, inference, assumption, and test result;
- disclose stale, dynamic, and unavailable sources;
- separate engineering completion from real-user validation;
- avoid sensitive personal data and proprietary research exports.

## Pull requests

Run the repository check before opening a pull request:

```shell
python scripts/check_repo.py
```

Keep changes focused. Do not add market-size claims without a reproducible source and a clearly stated denominator.
