# Equal-evidence pilot protocol, October 29, 2026

Freeze this protocol, task file and corpus before real model observations. Preserve the six-task October 27 study and October 28 usage/workflow records. This pilot changes both tasks and source access, so it cannot demonstrate a model improvement over the historical scores.

## Question and common inputs

Can a general model, a generic tool Agent and actual deterministic BillFit code produce the same bounded, sourced handoff when all three receive the same input evidence? The six tasks cover current income rules, conflicting two-page bill text, arithmetic over duplicate usage rows, missing income, an explicitly simulated expired date and invalid input. Every task requests structured fields, source locators and a compact note. No account, enrollment, rate change or actual savings is involved.

All arms receive the same selected public/synthetic documents. The general model receives their content inline, avoiding a retrieval-availability disadvantage. The Agent receives that same content plus generic search/read/arithmetic over those same documents. There is no hidden source shelf, live web, expected answer, dedicated BillFit tool or unrestricted filesystem in the Agent arm. The Skill calls the actual separately checked-out public BillFit code and maps its outputs to the common response format. This adapter and its evidence mapping are additional maintenance work, not a native product capability.

The income/effective-date fields were rechecked against [CPUC](https://www.cpuc.ca.gov/care/) on October 29: the June 1, 2026-May 31, 2027 table matches the packaged selected thresholds. The corpus retains BillFit's actual October 27 verification date and full public data structure; untested categorical-program and medical claims are outside this pilot. Bill text, duplicate usage and the future evaluation date are explicitly synthetic. Text extraction is supplied; no PDF/image OCR capability is measured.

## Frozen budgets and stopping

- Six primary tasks per arm, one initial attempt each; no prompt repairs or selective reruns.
- Model: at most one adapter call per task. Agent: at most three adapter turns per task, each returning one tool request or final answer. The primary ceiling is 24 adapter calls. Skill has zero model calls.
- A separately labeled maintenance variation repeats only current-income under a simulated threshold change, adding at most four adapter calls. Total ceiling: 28 adapter invocations. Provider API counters are measured separately; if a returned counter shows more than one provider call for an invocation, stop that arm after retaining the observation. Runtime transport behavior is not inferred from adapter counts.
- At most 90 seconds per adapter invocation and 180 seconds per task. Runtime unavailability/timeout stops the affected arm; remaining tasks stay unavailable in the denominator. No new service, purchase, credential export, native model tool or fallback model.
- Use the existing Hermes runtime and active configured model/provider. Record runtime commit, Python and model selection. Do not label the configured model as the newest model or change account settings.

## Outcome and file integrity

The evaluator checks all 36 required primary fields, including failed and unrun tasks. Missing/abstained and incorrect fields are separate. Completion requires exact requested fields, the cited source locations and a valid persisted artifact. Extra fields, invalid locators, malformed contracts and missing artifacts withhold completion. A syntactically valid artifact can still contain incorrect facts.

A common harness writes the structured answer for every arm and checks its bytes/hash and answer identity. This deliberately equalizes file plumbing: it is **harness materialization**, not evidence of native model or Agent file saving. The compact free-text note receives contract checks, but independent semantic review is unavailable; completion is explicitly limited to the frozen facts, evidence and artifact contract.

Record every model turn, response, permitted tool result, elapsed time and optional usage. Recompute tool results and request hashes when summarizing. Never trust hand-entered completion counters. Output directories/files are exclusive, progress uses atomic replacement and interrupted rows remain visible. This is local research storage, not a tamper-proof identity system; preserve Git history and original run files.

## Maintenance variation

After the primary run, change only the synthetic three-person CARE/FERA ceilings to 65,000 and 70,000 in an isolated evidence copy. Label it SIMULATED_NOT_OFFICIAL and remove the official-source URL from that altered document. Re-run current-income in all three arms. The 62,000 input changes from the FERA screening range to CARE under the hypothetical rule. Keep the original corpus and actual BillFit files unchanged.

Record changed source fields, adapter turns, machine preparation/evaluation time and regression results. Human source verification, review effort, user modifications and operational maintenance cost remain unknown unless prospectively measured by a person. A successful hypothetical update is not a tariff activation or an official rule change. Other five model/Agent cases are not silently re-run or claimed to have passed a new regression.

## Interpretation and delivery

Separate task completion, critical facts, source preservation, artifact integrity, machine calls, elapsed time, tokens, attributable billing and human effort. Null cost is not zero subscription cost. No user study or independent second coder is available. The case is internal engineering evidence, not a second market source when linked from NeedRadar. Publish the dated run records and an honest reassessment through a draft PR; no production deployment or release is required. Rollback restores the prior runner while retaining this dated research history.
