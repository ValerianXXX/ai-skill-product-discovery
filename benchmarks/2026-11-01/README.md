# Complete shared policy: prepared comparison, executed reference

The [protocol](PROTOCOL.md), [tasks](tasks.json), [corpus](corpus.json) and [response format](response-format.json) were frozen at `e6082ad` before new reference execution. Runtime `beec2f4` executed the clean public BillFit commit `d9d2a079312cf9948b4f5fe4084629ebf41f5cf2`. No model or Agent observation was made.

The [CPUC income table](https://www.cpuc.ca.gov/care/) was checked November 1. For example, the four-person CARE maximum is 66,000 and the FERA range starts at 66,001 and ends at 82,500 during the stated June 2026-May 2027 window. The separate policy document labels product conventions and unverified fractional-income handling explicitly; it is not presented as official eligibility guidance. The packaged October 27 verification date is retained.

| Observation | Completion | Selected fields | Persisted artifacts | Measured task time |
| --- | --- | --- | --- | --- |
| Actual BillFit, twelve synthetic tasks | 12/12 | 95/95 | 12 verified | 155 ms total |
| Actual BillFit, isolated synthetic policy change | 1/1 | 9/9 | 1 verified | 88 ms |
| General model | Not run | Unknown | None | Unknown |
| Generic Agent | Not run | Unknown | None | Unknown |

These are deterministic reference results against assistant-authored expected fields, not independent ground-truth review, actual households, model latency or comparative quality. Machine time includes bridge work on a shared Windows/Python 3.11.3 host; it excludes prospectively unmeasured human preparation and review. Costs, user actions and human maintenance effort remain null. The Agent's future tools cover the same evidence already supplied; tool-use benefit needs observation, not assumption.

The [analysis](analysis.json) is recomputed from [primary records](results/skill/run.json) and [maintenance records](results/maintenance-skill/run.json). The [verification receipt](verification.json) binds shared requests, 59 unchanged historical files and redacted test logs. Baseline: 42 tests passed; the frozen new contract initially could not import its unimplemented module. After implementation: eight new fairness tests and 50 total tests passed. A missing module is an implementation baseline, not a factual-quality score. The first evidence-packaging script incorrectly normalized preserved historical CRLF bytes; its raw-byte comparison was corrected before recording the receipt. No historical file changed.

## Run without credentials

Python 3.11+ is enough for preparation, tests and report verification. No provider configuration is needed:

```sh
python scripts/prepare_shared_policy.py
python scripts/prepare_shared_policy.py --output-dir /absolute/new-request-directory
python scripts/shared_policy_report.py
python scripts/shared_evidence_report.py --check benchmarks/2026-10-29/analysis.json
python -m unittest discover -s tests -v
python scripts/check_repo.py
```

The optional export writes 24 first-turn requests and a preparation receipt into a new directory. It excludes answer keys and launches no adapter. Existing output directories are rejected. `--maintenance` prepares the separately labeled one-task hypothetical variation.

The [delivery probes](report-negative-probes.json) also rejected five altered summaries, including invented completion, boolean counts and unknown cost relabeled zero. Request export preserved an existing directory and exposed no answer keys. These are offline integrity checks, not additional study observations.

To reproduce the reference, use a clean checkout of the exact public BillFit commit above and its documented Python dependencies, including timezone data on Windows. Use new absolute output directories; never overwrite the retained observations:

```sh
python scripts/shared_evidence_benchmark.py --round 2026-11-01 --arm skill --billfit-root /absolute/billfit --output-dir /absolute/new-reference-run
python scripts/shared_evidence_benchmark.py --round 2026-11-01 --maintenance --arm skill --billfit-root /absolute/billfit --output-dir /absolute/new-maintenance-run
python scripts/shared_evidence_benchmark.py --summarize /absolute/new-reference-run/run.json /absolute/new-maintenance-run/run.json
```

The new round refuses model/Agent execution with `NEW_ROUND_MODEL_BUDGET_UNALLOCATED` before creating output or spawning an adapter. A later real comparison requires a separately approved, frozen campaign budget and corresponding collector work; this is not unlocked by changing a data-file approval boolean. The proposed ceiling in the protocol grants no authority. No Hermes installation or account changes were performed.

## Remaining acceptance and rollback

Independent policy review, balanced repeated model trials, independent users, native tool/export capability, human modification/maintenance effort, OCR and full annual bill comparisons remain unverified. The earlier Agent used zero tools; these prepared requests do not change that finding. Historical studies have different tasks, code and information conditions and cannot form an accuracy trend.

This branch requires no production deployment, schema migration or paid service. A reviewed revert can remove the new preparation and round-selection code. Keep historical observations and any later collected raw failures intact. The actual BillFit checkout and official data are read-only throughout this study.
