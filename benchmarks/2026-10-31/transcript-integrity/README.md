# Execution-ledger integrity follow-up

Study date: October 31, 2026, America/New_York. This is an offline collector repair, not a new model study. The [original October 29 results](../../2026-10-29/RESULTS.md), 20 measured provider calls, failed answers, exact-match limitations and incomplete shared maintenance policy remain unchanged.

## Verified defect and change

The old reader counted any attempt containing `toolResult` as a tool call, including a final answer with a fabricated extra field. It also accepted a second turn after a final answer or failed/interrupted attempt, and some impossible combinations of result state and saved answer. Its request/artifact hashes and task denominator already caught other changes; these checks remain in place.

The new pure [replay module](../../../scripts/shared_evidence_replay.py) validates the collector's execution sequence before the existing evaluator computes outcomes:

- Only a received Agent tool request with a permitted operation, null answer and correctly recomputed result earns tool-use credit. Final answers cannot carry a tool result; failed and partial payloads retain no tool credit.
- A final response, failed call or interrupted call ends that task's transcript. Unknown attempt states and malformed received envelopes fail with a diagnostic.
- An unattempted row cannot contain model output or measured execution. An observed row requires a valid answer, its matching artifact and consistency with the received response and retained candidate.
- Numeric and boolean values remain distinct inside nested results. Execution identity flags must have the declared values and types.
- Legitimate transport failures, invalid final-answer contracts and interrupted checkpoints remain readable. Their missing work stays in the denominator; invalid output is not repaired.

This is internal consistency checking, not a cryptographic attestation of a provider. A consistently forged ledger cannot be authenticated by these checks. Free-text truth, independent review, billed costs, user effort and real-world task outcomes still require separate evidence. The code does not infer them from a valid transcript.

## Before and after

The original 27 tests, repository check and published-report recomputation passed at parent `a233a374eb36f7cd122462f8af1d9c25a0596425`. Thirteen new test methods were frozen at `89bde6c` before changing the implementation. They produced 19 failed assertions and three unhandled-type/key errors on the old reader; these are synthetic corruption probes, not 22 historical research failures.

| Check | Before | After |
|---|---|---|
| Frozen 13-method probe suite | 19 failures, 3 errors | All 13 pass |
| Two added compatibility tests | Added after the implementation | Every collector checkpoint replays; failed/partial payloads earn no tool credit |
| Complete local suite | 27 existing tests passed | 42 tests passed at runtime `85e3664` |
| Ten historical runs and published report | Recomputable | Identical recomputed outcomes, usage, receipts and limitations |
| New real provider calls | 0 | 0 |

The complete-suite run took 4.914 seconds on Python 3.11.3. Probe and full-suite times are test-harness observations, not model latency or a performance comparison. The synthetic adapter exercises the actual collector, atomic checkpoint writer, bounded arithmetic broker and artifact materializer; it does not contact a model or BillFit runtime. A mix of a valid tool trajectory, invalid final schema and transport failure retains six planned tasks, two completed tasks, two failures and two unattempted tasks.

The [verification receipt](verification.json) records source/artifact hashes, frozen revisions and local results. Public test logs replace only the workspace path with `<WORKSPACE>` and normalize line endings; original local log hashes are retained in the receipt. No recorded answer, answer key, historical score, original artifact or original receipt was edited. Hosted checks are reported separately in the draft PR after they finish.

## Reproduce without credentials

Use Python 3.11 or newer, from the repository root:

```sh
python -m unittest discover -s tests -v
python scripts/check_repo.py
python scripts/shared_evidence_report.py --check benchmarks/2026-10-29/analysis.json
python scripts/shared_evidence_benchmark.py --summarize benchmarks/2026-10-29/results/clarified-agent/run.json
```

To inspect the original failure, use an isolated checkout at `89bde6c` and run `python -m unittest discover -s tests -p test_shared_evidence_replay.py -v`. It is expected to fail there. Do not overwrite a research output directory or rerun the closed live campaign. No new configuration, dependency or service is required.

## Delivery and remaining work

This draft is stacked on the shared-evidence study branch. There is no database migration, production deployment, release, model switch or paid-service activation. A normal revert of the replay change restores the previous reader; keep the dated evidence and defect disclosure. No history deletion or observation rewrite is needed.

The repair does not complete the broader research goal. Complete equal-policy coverage, unseen tasks, repeated trials under a newly authorized frozen budget, independent content adjudication, user/edit measurements and prospective maintenance effort remain open. The calibrated Agent still used zero tools, so no tool advantage or overall Skill superiority follows from that study.
