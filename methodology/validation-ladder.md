# Validation ladder

Use the highest fully evidenced level when describing a product. Do not skip levels in public claims.

| Level | Name | Required evidence |
|---:|---|---|
| V0 | Defined hypothesis | User, trigger, outcome, and falsifiable assumption are written down |
| V1 | Sourced problem | Relevant demand and supply evidence is recorded with caveats |
| V2 | Data feasibility | Authoritative data, access, versioning, and stale-data behavior are demonstrated |
| V3 | Working prototype | The narrow end-to-end path runs on representative fixtures |
| V4 | Engineering validation | Automated tests cover calculations, exclusions, and failure states |
| V5 | Distribution validation | An intended user can obtain and install or invoke the product through the target channel |
| V6 | Guided user validation | Target users complete the task with observed assistance and pass a pre-set threshold |
| V7 | Unassisted repeat use | Users return and complete the task without researcher intervention |
| V8 | Outcome validation | The product produces a verified real-world benefit without unacceptable harm |

## Separate status dimensions

A product can be V4 in engineering and still have no market validation. Also track:

- **authorization:** whether account access or external actions are allowed;
- **review:** whether a marketplace or regulator has reviewed it;
- **coverage:** which geographies, providers, and edge cases are supported;
- **freshness:** whether dynamic source data remains within its allowed age.

## BillFit as of 2026-08-18

BillFit has evidence through V4 and a public GitHub distribution path associated with V5. This case does not claim V6–V8. OpenAI marketplace review or public listing is not counted as complete validation here.

See the case-specific [validation status](../cases/billfit/validation-status.md).
