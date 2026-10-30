# Shared-evidence pilot and format calibration

Study date: October 29, 2026, America/New_York. Some UTC timestamps are October 30. These are real runtime calls on explicitly synthetic inputs, not real household outcomes or an independent user study.

The trial found an actual BillFit input-compatibility defect and two evaluation-design defects. It does **not** establish overall Skill superiority. Read the preserved [original protocol](PROTOCOL.md), [format correction](CALIBRATION.md) and recomputable [analysis](analysis.json).

## What ran

The six new tasks cover current income screening, conflicting two-page extracted bill text, duplicate CSV usage, missing income, a simulated future expiry and invalid income. All arms received the same selected document content. The model received it inline; the Agent also had bounded search, file-read and arithmetic tools over the same content. Actual BillFit code supplied the Skill arm, with an additional common-format adapter. There was no OCR, live web search by an arm, unrestricted file access, enrollment or rate change.

Before calls, protocol/data/runner were committed at `28294c9aa2994d266acbc8f4a2af78134124e8e6`. The separately selected format calibration was frozen at `f2a4962ab4d334227f9d1b24055d91c2aa7c8136`. Every Skill observation used the clean, unchanged BillFit commit `c8e9c305f048f66561a5312121bca22436417126`.

Runtime: existing Hermes revision `afe53708ee7400919ae3e17a6dde9b02629e5c87`, Python 3.11.15, configured `gpt-5.6-sol` through `openai-codex`. This is an observed configuration, not a claim that it is the newest available model. Native tools, history, memory and fallback were disabled in this bounded adapter. There were 20 adapter calls and 20 measured provider API calls, within the frozen 28-call ceiling. No further calls or retries were made to improve these results.

## Original six-task results are format conformance, not factual accuracy

| Arm | Completed exact contract | Exact fields matched | Retained artifacts | Measured elapsed time | Tokens |
|---|---:|---:|---:|---:|---:|
| General model | 1/6 | 23/36 | 5 | 40.445 s | 8,699 |
| General Agent | 1/6 | 16/36 | 3 | 39.595 s | 9,298 |
| Actual BillFit Skill | 5/6 | 30/36 | 5 | 0.130 s | No model calls |

The evaluator demanded status strings, numeric-string formatting and grouped citations that the original request did not fully define. The Skill adapter already used these conventions. Consequently these counts cannot establish comparative factual quality. The exact evaluator and all raw outputs remain unchanged; no synonym remapping retroactively repairs the first attempts.

Reading the retained answers shows that both model arms returned the selected income ceilings and duplicate-usage arithmetic correctly and kept bill confirmation with the user. The Agent's usage and missing-income answers placed fields directly under `answer`, violating the explicitly requested nested `fields` contract. Repeated source entries invalidated the bill response contract. These are distinct from factual mistakes. This inspection was by the implementing coding assistant, not an independent adjudicator.

BillFit rejected the frozen `start,duration minutes,kwh` CSV with `CSV_HEADER_NOT_FOUND`. The [separate diagnostic](skill-usage-diagnostic.json) identifies the actual error; it does not replace the failed observation. Its supported CSV column list omitted `kwh`. Later product repairs must remain separate from this dated baseline.

## Separately frozen three-task calibration

Accepted vocabulary, numeric-string conventions, conflict field IDs and citation grouping were then stated explicitly. The selected tasks were current-income, conflicting-bill and duplicate-usage. This is post-discovery calibration on exposed tasks, not a held-out benchmark or model upgrade comparison.

| Arm | Completed exact contract | Exact fields matched | Actual broker calls | Elapsed time | Tokens |
|---|---:|---:|---:|---:|---:|
| General model | 2/3 | 14/20 | 0 | 21.272 s | 5,473 |
| General Agent | 3/3 | 20/20 | 0 | 19.622 s | 5,621 |
| Actual BillFit Skill | 2/3 | 14/20 | 0 | 0.101 s | No model calls |

The model's usage arithmetic was correct but its response again omitted the nested `fields` object, so no completed artifact was credited. BillFit still rejected the same CSV. The Agent returned three conforming answers without using any offered broker tool. The difference cannot be attributed to tool use; this small single-observation design also cannot isolate sampling variability or the extra tool descriptions in the prompt. All three retained the conflicting bill values and confirmation boundary where they returned a bill answer.

## Simulated maintenance exposed an incomplete shared policy

The isolated variation changed only the three-person CARE and FERA ceilings to 65,000 and 70,000. It was labeled synthetic and its official-source URL removed. The actual corpus and BillFit files stayed unchanged. Both model arms used the new numeric ceilings. BillFit selected CARE as the primary path; both model answers reported likely eligibility under both upper ceilings. The Agent additionally returned a flat answer contract.

The shared snapshot contains upper ceilings but omits the FERA lower bound and CARE-precedence rule that BillFit has in code. The [official CPUC table](https://www.cpuc.ca.gov/care/), rechecked October 29, supplies a FERA lower bound above the CARE ceiling; the supplied snapshot did not. Thus the observed status difference is confounded by policy availability and cannot fairly isolate reasoning or maintenance quality. The hypothetical thresholds are not official rules.

Exact maintenance conformance was model 0/1 (5/6 fields), Agent 0/1 (0/6 nested fields), Skill 1/1 (6/6). Model/Agent used one call each, 2,239/2,450 tokens and 11.817/11.758 seconds. The calibrated Skill took 0.089 seconds. An earlier deterministic maintenance check is also retained at 0.088 seconds; it is not an additional independent sample. Original unclarified model/Agent maintenance runs were not performed.

Machine task time was captured; separate source-preparation time and human source-review/maintenance effort were not prospectively captured and remain unknown. This is a protocol coverage gap, not a zero-cost update. A future study must publish complete rule semantics to both general arms before freezing new held-out tasks.

## Interpretation and remaining work

- Every persisted answer is saved by the **common harness**, with byte/hash and content checks. This is not native model/Agent export capability. Invalid answers remain in raw runs but receive no successful artifact.
- Timing includes adapter startup and orchestration on a shared host. Skill timings include local setup. Neither is isolated model latency or production throughput.
- Provider counters report included-cost estimates; attributable billing, subscription allocation, user operations, user edits and human maintenance effort remain unknown. No dollar-saving claim is made.
- Source locators and frozen selected fields are checked. Free-text note semantics have no independent review. Correct selected fields do not establish that every note claim is correct.
- No independent users, customer demand, market validation, unrestricted generic Agent, OCR quality, complete annual rate comparison or real bill savings were measured.
- Next research needs independently reviewed complete policy coverage, a response-schema preflight, unseen cases and repeated trials within a new frozen budget. Do not spend unused calls from this finished protocol on selective repairs.

The reusable outcome is a bounded collector, transparent failure record, source/contract audit and concrete product defect. Historical August/October 27 conclusions and their different information conditions remain dated records.
