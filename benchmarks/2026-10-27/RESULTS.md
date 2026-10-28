# October 27, 2026 substitute pilot

Six original synthetic tasks were fixed before execution. All three arms actually ran; no responses below are mock observations. The local date was October 27 (America/New_York), with UTC timestamps on October 28. This is one pass over assistance screening, not a tariff comparison or user study.

| Arm | Completed tasks | Correct required fields | Incorrect claims | Missing/abstained fields | Model calls | Tool calls | Total wall time |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| General model | 1/6 | 17/26 | 0 | 9 | 6 | 0 | 83.361 s |
| General Agent | 6/6 | 26/26 | 0 | 0 | 11 | 5 | 63.434 s |
| BillFit Skill | 6/6 | 26/26 | 0 | 0 | 0 | 0 | 0.117 s |

The model's unanswered ceilings/statuses were conservative abstentions, not fabricated facts. Some correct remembered facts still lacked a verified current-source read; the task explicitly required current verification. The invalid-income case required no source lookup and completed. The Agent read the supplied official-source transcription for five valid tasks and returned correct results. Its negative-income case needed no tool. The Skill used the actual separately checked-out BillFit calculator and dated rules.

The tool Agent matches the specialized Skill for this bounded lookup. This weakens an undifferentiated claim that assistance rules require a dedicated product. BillFit removes provider calls from this deterministic slice; the measured wall times are descriptive, not a stable speed ratio. Source preparation and review time are excluded from all arms and remain unmeasured. Actual dollar cost, token use, user operations and maintenance hours are null; subscription access is not evidence of zero cost.

## Environment and evidence

- Same configured `gpt-5.6-sol` through the existing `openai-codex` Hermes provider for model and Agent; actual model build was not exposed. No provider switch, account signup or OpenClaw installation.
- Windows Python 3.11.3 harness; existing WSL Ubuntu Hermes interpreter invoked through a bounded subprocess. Hermes source revision was `afe53708ee7400919ae3e17a6dde9b02629e5c87`. Native Agent tools, memory, session history and trajectories were disabled; the explicit harness broker supplied generic source/file/arithmetic capabilities.
- Agent search uses a frozen, human-reviewed official-source shelf, not live web search. The source transcription includes rule interpretation. This tests the value of accessible context plus tools, not whether domain knowledge is impossible for a model to learn.
- BillFit commit: `8ad0b6ff65e9bbe7937e26b240b0b209d7e4660a`, task version `substitute-assistance-2026-10-27-v1`. Full dataset/source hashes and immutable run-file hashes are in [analysis.json](results/analysis.json).
- [Model](results/model.json), [Agent](results/agent.json) and [Skill](results/skill.json) records retain every actual attempt, normalized answer, runtime and evidence-read status. No failed attempts were selectively rerun. No real customer information was used.

After the first model run, evaluator v2 split the original unmatched-field category into explicit incorrect claims and missing/abstained fields. Completion requirements and exact-match denominators did not change. All raw records were preserved; the summary re-scores all arms with the same evaluator and tests this distinction. This refinement was not a model retry or performance improvement.

Seven offline contract/evidence tests and repository checks pass. The tests enforce source-required completion, immutable task identity and run-file hashes, bounded arithmetic/file access, excluded answer keys, strict booleans and abstention accounting. Git preserves the original run-file bytes, including their Windows line endings. Real provider execution is separate from these offline checks.

## Scope, remaining work and rollback

No customer enrollment, bill reconstruction, interval rate ranking, live browser search or user study occurred. A single small sample and fixed execution order cannot establish general accuracy or latency superiority. Independent fact review, broader tasks, repeat runs and observed user/maintenance metrics are still needed.

Run commands and authorization/call limits are in [the benchmark guide](../README.md). The adapter uses an existing Hermes installation and a local argv JSON file; no credentials belong in this repository. CI performs offline checks only. No production deployment, migration or service purchase is needed. Revert the reviewed code commit to roll back the harness while preserving dated results as research evidence.
