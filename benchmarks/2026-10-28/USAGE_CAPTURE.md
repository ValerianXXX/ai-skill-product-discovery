# Usage collection acceptance - October 28, 2026 (America/New_York)

The initial adapter always emitted null tokens/cost and the harness discarded any
usage metadata. A later actual Hermes client check established that the installed
runtime exposes session counters. The adapter and harness now preserve those
counters prospectively, including on a received response that subsequently fails
the answer contract. Missing responses remain unknown.

One additional real call used the existing `gpt-5.6-sol` / `openai-codex` setup and
the frozen invalid-income task from the October 27 dataset. It used `model_run`
with the model arm, no native or broker tools and a one-call limit. The returned
`INVALID_INCOME` answer passed the unchanged evaluator. This validates collection;
it is not another six-task round or evidence of improved answer quality.

- Actual model API calls: 1; tool calls: 0.
- Reported prompt/completion/total tokens: 760 / 21 / 781.
- Harness elapsed time: 4,586 ms, including adapter/WSL overhead.
- Hermes cost status/source: `included` / `none`; incremental estimate: `$0`.
- Independently measured billed cost: null. User operations and maintenance hours:
  null. No account enrollment, new service or purchase occurred.

The [raw receipt](usage-probe.json) retains the actual response, task/dataset
identity, Hermes revision and LF-normalized hashes of the tested adapter/harness.
Its UTC timestamp falls on October 29. The initial three-arm run files and their
checksums are unchanged; no historical token count is inferred from this probe.
The benchmark guide's existing commands collect usage on future authorized runs.

All ten offline tests and the repository checks pass. Added checks cover two-turn
aggregation, missing/failed-call coverage, preservation of unknown cost, invalid
counter types and keeping estimates separate from billing. The original immutable
run-file hash check still passes. No completion criterion or expected fact changed.

No production deployment or data migration is needed. Revert the collector change
to restore the prior adapter; older/newer run records remain readable and can be
re-evaluated without rewriting observations.
