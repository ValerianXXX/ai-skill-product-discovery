# BillFit workflow evidence - October 28, 2026

This is an internal engineering follow-up to the [October 27 reassessment](reassessment-2026-10-27.md). It does not replace the historical discovery record or the [six-task three-arm benchmark](../../benchmarks/2026-10-27/RESULTS.md). BillFit's reviewed source is commit [`6e476b2`](https://github.com/ValerianXXX/billfit/commit/6e476b2ae1b38e0c0c9359842fba71ef32d41292), still on [draft PR #3](https://github.com/ValerianXXX/billfit/pull/3), not a released upgrade.

## What was actually exercised

Existing Hermes `afe53708ee7400919ae3e17a6dde9b02629e5c87`, its configured `gpt-5.6-sol` / `openai-codex` model, and the real BillFit MCP SDK server executed two separately initialized model stages on fixed synthetic inputs:

1. Read an original synthetic PDF, preserve five unconfirmed fields and exact page/line/quote/hash evidence, screen a declared household, and report missing interval usage and pending human actions.
2. Use explicit **synthetic fixture confirmation** and a separate one-day usage file; parse 24 intervals, compare two plans with the deterministic calculator, identify the intentional bill mismatch and withhold switching action.

The model selected tools and explained their results. Local PDF text extraction and the existing deterministic engine produced the fields and numbers. This was not a model-only arithmetic or multimodal OCR benchmark. The exposed tool set contains no utility login, plan-change or enrollment action.

The first actual observation failed because an extraction argument did not match the supplied exact filename. The boundary rejected it before reading a file; the model later corrected the argument and produced the correct final answer. The exact rejected argument was not retained, so its value and the model's reason are unknown. Overall failure status remains unchanged. The product's skill and MCP parameter descriptions were clarified to preserve supplied paths. With identical prompts, fixtures, evaluator, model and pass criteria, a second observation passed all 23 fixed checks.

| Recorded measure | Before path guidance | After path guidance |
| --- | --- | --- |
| Stage acceptance | First failed; second passed | Both passed |
| Rejected file calls | 1, then recovery | 0 |
| Successful real tool calls | 6 | 6 |
| Reported model API calls | 6 | 5 |
| Reported tokens | 40,690 | 34,489 |
| Whole runner elapsed | 70.490 s | 45.782 s |
| Actual billing | Unknown | Unknown |

One observation per revision does not establish a general completion rate or causal latency/cost improvement. Model/service variation and cache effects were not controlled. The provider-labelled estimate was zero with status `included` and source `none`; this is not an independent billing receipt. No model service was purchased or installed.

## What changes in the product assessment

| Question | Evidence-supported conclusion | Still unproven |
| --- | --- | --- |
| Can a compatible model host perform the bounded analytical flow? | Yes, in the fixed two-stage synthetic scenario after path guidance. The earlier host test exercised direct tool dispatch only. | Clean third-party installation, real customer files and unassisted reuse. |
| Does the Skill preserve source and user-control boundaries? | The tested scenario retained unconfirmed fields, missing inputs, source dates and a bill mismatch; it did not claim a submitted application. | Robustness across noisy documents, models and unanticipated user requests. |
| Is generic assistance lookup still substitutable? | The original generic Agent and Skill both completed 6/6 assistance cases. This result is unchanged. | Generalization beyond those six frozen tasks. |
| Is the full interval workflow better than a general Agent? | It now has a reproducible successful Skill-side workflow observation. | An equal-source, equal-tool-budget general-Agent comparator has not run this workflow. |
| Has the customer's business task finished? | The analytical handoff reported why no switching action should follow. | Utility enrollment, a completed plan change, verified real-bill savings or customer satisfaction. |
| Has maintenance or user effort improved? | The runner records technical calls, tokens, elapsed time and boundary failures. | User operations/corrections and operational maintenance effort were not measured. Scripted fixture confirmation is not a counted real-user action. |

V4 remains the highest fully evidenced validation level. The [validation ladder](validation-status.md) is unchanged. The engineering lesson is that tool input contracts and bounded execution can expose and recover a real integration failure. This is an inference about implementation practice, not proof that general-purpose agents cannot do the task.

## Provenance and reproduction

- [Frozen protocol, setup and limits at the reviewed commit](https://github.com/ValerianXXX/billfit/blob/6e476b2ae1b38e0c0c9359842fba71ef32d41292/docs/hermes-workflow-2026-10-28.md).
- [Original failed model observation](https://github.com/ValerianXXX/billfit/blob/6e476b2ae1b38e0c0c9359842fba71ef32d41292/plugins/billfit/skills/billfit/data/verification/hermes-workflow-attempt-1.json), bound to source `7392a56814e35065ad9e5ad2b44c7238afd5c845`.
- [Original passing model observation](https://github.com/ValerianXXX/billfit/blob/6e476b2ae1b38e0c0c9359842fba71ef32d41292/plugins/billfit/skills/billfit/data/verification/hermes-workflow-attempt-2.json), bound to source `90ffa2bf2bc54d990c05572f462b4be2bcec9c49`.
- [GitHub CI 40809138034](https://github.com/ValerianXXX/billfit/actions/runs/40809138034): tested merge `9eb6fcf221e2f3874f4bcd85d1760967ae1dc62f` has the same tree as the reviewed head. Local Windows passed 34 tests. CI first ran 34 cases with two optional-profile skips, then installed the profiles and passed all eight integration/freshness cases, including the two optional checks.

The protocol requires an already authorized Hermes environment, uses an opt-in live flag, refuses to overwrite observations and exposes only fixed synthetic files. Original files are parsed locally; the configured model receives returned synthetic facts and evidence snippets. Actual billing remains unknown. Historical results are not backfilled with later measurements.

Evidence ID `B09` in the [ledger](../../data/evidence-ledger.csv) is first-party product engineering evidence with the same source owner as BillFit. NeedRadar, this case, the product documentation and copied result summaries are not independent demand sources. No market score, adoption count or validation level is increased by adding this link.
