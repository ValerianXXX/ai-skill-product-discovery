# Validation status

Status date: 2026-08-18.

October 27 addendum: [six synthetic three-arm tasks](../../benchmarks/2026-10-27/RESULTS.md) were actually executed using the existing configured model and BillFit commit `8ad0b6ff65e9bbe7937e26b240b0b209d7e4660a`. This adds engineering/substitute evidence, not customer adoption or outcome validation. V5 remains partial and V6-V8 remain uncompleted. The original ladder and proposed user tests below are preserved.

October 28 addendum: the [two-stage model-selected BillFit workflow](workflow-evidence-2026-10-28.md) passed fixed synthetic acceptance after an initial file-boundary failure and path-guidance repair. Its fixture confirmation, returned tool results and deliberately withheld switching action are not third-party installation, customer consent or completed utility enrollment. V4 remains the highest fully evidenced level; the ledger below is unchanged.

## Validation ladder

| Level | Status | Evidence | What remains |
|---:|---|---|---|
| V0 Defined hypothesis | Complete | Decision moment, target scope, and falsifiable assumptions are documented | Revisit if scope changes |
| V1 Sourced problem | Complete for opportunity selection | Evidence ledger and rejected alternatives are published | BillFit-specific demand prevalence remains uncertain |
| V2 Data feasibility | Complete for MVP sources | Official rate, usage, CARE/FERA, and Medical Baseline paths; versioned snapshots | Operational refresh run after each source change |
| V3 Working prototype | Complete on fixtures | End-to-end parser, comparison, validation, and assistance operations | More real-format and edge-case files |
| V4 Engineering validation | Complete for the tested MVP | Automated unit suite covers supported calculations and exclusions | Independent review and larger fixture corpus |
| V5 Distribution validation | Partial | Public GitHub repository, release, and install instructions | Observe a clean third-party install and invocation; do not count marketplace listing until public |
| V6 Guided user validation | Not started | None | Moderated target-user sessions with pre-set thresholds |
| V7 Unassisted repeat use | Not started | None | Cohort retention and repeat-task evidence |
| V8 Outcome validation | Not started | None | Verified real-bill comparisons, realized benefit, and harm monitoring |

The highest fully evidenced level is V4.

## Engineering, authorization, and external review

| Dimension | Status |
|---|---|
| Code and fixture tests | Complete for the current repository test suite |
| Real utility account login | Intentionally not implemented or authorized |
| Real plan change | Intentionally not implemented or authorized |
| Assistance submission | Intentionally not implemented or authorized |
| Medical certification | Remains with a qualified practitioner |
| Public GitHub availability | Complete |
| OpenAI public listing/review | Not counted as complete in this case |
| Real-user acceptance | Not completed |

## Pre-registered next tests

| Hypothesis | Minimum test | Pass threshold | Failure response |
|---|---|---|---|
| A target customer can obtain usable input | 5 supported PG&E customers attempt Green Button export with written instructions | At least 4 provide a parseable file without sharing credentials | Improve instructions or add a safer manual-input fallback |
| The output is understandable | 10 guided users interpret one comparison and name its main limitation | At least 8 identify the lowest modeled plan and one exclusion correctly | Redesign result hierarchy and language |
| Reconstruction is credible | 15 anonymized supported bills plus matching usage | At least 12 comparable-component reconstructions fall within the documented tolerance | Withhold switching guidance and expand bill-component diagnostics |
| The in-AI surface is preferable | Compare skill workflow with a general-assistant baseline for 10 users | At least 7 prefer BillFit for trust, speed, or clarity | Reassess whether the maintained skill adds enough value |
| Users will return when rates or usage change | 30-day follow-up with users who completed a comparison | At least 30% voluntarily run a second valid task | Treat as an occasional utility, not a recurring product |

Thresholds are planning assumptions. They become evidence only after the tests run and raw results are retained.
