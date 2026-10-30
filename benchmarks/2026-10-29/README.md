# Run and inspect the shared-evidence study

Read [results and caveats](RESULTS.md) before interpreting a score. Python 3.11+ runs the offline checks without Hermes, BillFit or credentials:

```sh
python -m unittest discover -s tests
python scripts/check_repo.py
python scripts/shared_evidence_report.py --check benchmarks/2026-10-29/analysis.json
python scripts/shared_evidence_benchmark.py --summarize benchmarks/2026-10-29/results/clarified-model/run.json
```

Raw records are under `results/<arm>/run.json`; `clarified-*` identifies the separate format calibration and `maintenance-*` the explicitly hypothetical rule change. Requests are regenerated from the immutable catalog/corpus and hashed. Tool outputs and saved artifact bytes/content are independently recomputed. `analysis.json` renames exact-match counters so they are not presented as factual error rates. Missing, failed and interrupted cases stay in their original denominators.

Optional future execution uses **new absolute output directories** and existing authorized runtimes. The following is interface documentation, not a request to repeat this finished study:

```sh
python scripts/shared_evidence_benchmark.py --arm skill --billfit-root /path/to/clean/public/billfit --output-dir /absolute/new-skill-run
python scripts/shared_evidence_benchmark.py --arm model --adapter-json /absolute/existing-hermes-argv.json --clarified --output-dir /absolute/new-model-run
python scripts/shared_evidence_benchmark.py --arm agent --adapter-json /absolute/existing-hermes-argv.json --clarified --output-dir /absolute/new-agent-run
```

`--maintenance` loads the frozen isolated hypothetical change; it never edits BillFit data. The argv file uses the existing Hermes interpreter and an absolute path to `scripts/hermes_benchmark_adapter.py`, optionally through existing WSL. Keep it outside the public repository. No credentials or local account configuration belong in results. Do not install or reconfigure an Agent merely to run offline verification.

For a new case, retain dated originals, define complete shared policy and exact response semantics, remove expected answers from requests, freeze a new catalog and prospective budget, and adapt the pure contract/broker modules. The current loader intentionally fixes this round's six-task denominator. Use the [coverage and outcome template](../../templates/shared-evidence-protocol.md) before collecting new observations; do not edit this round to make another case fit.

No production migration, service, deployment or release is needed. A code rollback restores the earlier runner/adapter by a normal revert while keeping dated research observations and their limitations. It does not require rewriting Git history or deleting failed results.
