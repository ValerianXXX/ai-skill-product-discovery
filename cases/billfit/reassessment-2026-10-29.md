# BillFit reassessment: October 29, 2026

The new [shared-evidence observations](../../benchmarks/2026-10-29/RESULTS.md) support a narrower product position: maintain auditable parsing, deterministic calculations and source updates while measuring how much these reduce user work. They do not demonstrate that a generic model cannot handle the selected tasks.

| Claim | Current evidence | Consequence |
|---|---|---|
| Exact current facts cannot safely be assumed from model memory | Official data and effective dates are still required; this round supplied them to both model arms | Preserve maintained sources, but do not call supplied-context lookup an exclusive Skill capability |
| Generic AI cannot interpret a bill conflict or deduplicate a short usage list | Both model arms returned the selected conflicting amounts and unique-usage arithmetic correctly | These small tasks are covered in this sample; OCR, large files and full tariff calculations remain untested comparisons |
| Tools caused the calibrated Agent to outperform the model | The Agent used zero broker tools in every new observation | No tool-benefit causal claim is supported |
| BillFit reliably accepts every common usage file | The frozen `kwh` CSV was rejected; a separate product repair is prepared in draft PR #5 | Retain the failed study baseline and verify the proposed parser against more file formats |
| A Skill handles changing rules better | BillFit retained a CARE/FERA precedence rule absent from the supplied corpus | Rule ownership is a maintenance responsibility; this experiment cannot isolate comparative reasoning or maintenance effort |
| Maintained deterministic rules, boundaries and evidence have value | Actual BillFit operations ran on a fixed commit; incomplete or conflicting inputs withhold action | Engineering capability is demonstrated within tested scope; user benefit and lower total cost still need measurement |
| BillFit has proven market demand or realized savings | No independent customers, utility actions or actual bill outcomes were observed | Validation remains V4 for the tested engineering scope; no market level is raised |

The official [CPUC CARE/FERA page](https://www.cpuc.ca.gov/care/), rechecked October 29, matches the selected packaged income ceilings and effective period. Its FERA table also contains lower bounds missing from the benchmark snapshot. This check does not newly certify every tariff, medical criterion or categorical program. The simulated maintenance ceilings are explicitly not official policy.

The correct next product test is a complete supported bill workflow with identical source access and rule semantics for the generic Agent, real-format authorized inputs or clearly synthetic equivalents, documented parser failures, user effort and blinded outcome review. For this study, elapsed machine time and tokens are available; actual billing, user edits and human maintenance work remain unknown.

Product follow-up: [BillFit draft PR #5](https://github.com/ValerianXXX/billfit/pull/5), commit `56874a26bea745d5c83fe9f5dd38cd305c1ae3d5`, accepts the explicit `kwh` header and rejects competing columns or conflicting units. Its separate [verification receipt](https://github.com/ValerianXXX/billfit/blob/56874a26bea745d5c83fe9f5dd38cd305c1ae3d5/plugins/billfit/skills/billfit/data/verification/csv-energy-verification-2026-10-29.json) records 14 frozen contracts improving from 3 passes to 14, 86 full-environment passes and actual CLI success on the original study CSV while withholding a short-sample recommendation. This is a draft engineering repair, not a rerun of the model comparison, a published release or a new market source.

This case, BillFit's own code and a NeedRadar handoff are internal engineering/research evidence. Circular project links do not add independent market sources. Historical August and October 27 decisions remain unchanged and dated.
