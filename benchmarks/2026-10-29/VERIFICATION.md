# Verification and delivery boundary

Local checks on October 29, 2026:

- Existing baseline: 10 offline tests passed before the new round.
- Final milestone: 27 offline tests passed; repository English/link/ledger checks and `git diff --check` passed.
- Recomputed ten stored run reports, all fixed task denominators, per-turn request identities, available tool results, saved-answer byte/content receipts and the 28-call ceiling. No model calls are made by this check.
- Actual pilot: 20 model adapter invocations and 20 measured provider calls, using the existing Hermes configuration. All model/Agent attempts and failures are retained; zero broker tools were used.
- Actual Skill runs: fixed clean BillFit commit `c8e9c305f048f66561a5312121bca22436417126`; isolated in-process evidence/date overrides restored after calls, repository unchanged at the final check.
- Official-source check: selected CPUC income ceilings/effective dates matched; FERA lower bounds present on the official page but absent from the shared corpus were explicitly disclosed.

Hosted run [40984681393](https://github.com/ValerianXXX/ai-skill-product-discovery/actions/runs/40984681393) passed repository checks and all 27 tests but failed report equality: local receipts hashed CRLF source files while Git stored LF. The [correction receipt](line-ending-correction.json) preserves old/new source byte hashes. Source JSON values, request hashes, raw observations, scores and every saved-artifact receipt are unchanged. The local source copies now match the repository's declared LF form; no integrity check was removed or softened.

The initial field-conformance counts are not factual accuracy estimates. The calibration is exposed and limited to three tasks. The maintenance comparison lacks complete shared policy and separate source-preparation timing. Independent content review, users, billing, maintenance effort, OCR and real bill/utility outcomes remain unverified.

This delivery is source/research work for a draft PR. It needs no production migration or deployment. Hosted CI reports its own status on the PR; this local record does not predeclare it passed. Roll back code by a normal revert while retaining the dated research and failures. Never remove a failed observation to obtain a passing report.
