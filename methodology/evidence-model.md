# Evidence model

The method records both **source strength** and **claim state**. They answer different questions.

## Source strength

| Code | Source type | Appropriate use |
|---|---|---|
| S1 | Primary official rule, tariff, filing, standard, or raw first-party dataset | Exact rules, dates, definitions, and authoritative operational facts |
| S2 | Representative or well-documented independent research | Prevalence, behavior, and demand signals |
| S3 | Industry or vendor research with a disclosed sample | Directional demand evidence with an explicit commercial-bias caveat |
| S4 | Product documentation or product page | Existing capability and positioning, never market size by itself |
| S5 | Anecdote, forum post, interview note, or editorial test | Language, edge cases, and hypothesis generation |

Source strength is not a universal ranking. A product page is the strongest source for what that product claims to do, but a weak source for whether customers need it.

## Claim state

| State | Meaning |
|---|---|
| Observed | Directly present in a cited source or raw artifact |
| Derived | Reproducibly calculated from observed data |
| Inferred | A reasoned interpretation that could be wrong |
| Assumed | A planning input chosen before validation |
| Tested | Evaluated in a documented experiment |
| Validated | Passed the pre-registered threshold in the target context |
| Rejected | Failed a threshold or decision gate |

Every consequential statement should expose its state. “The official page lists a current tariff workbook” is observed. “Users will pay for an independent comparison” is assumed until tested.

## Evidence record

Each row should include:

- stable evidence ID;
- claim supported;
- source owner and title;
- source date and date checked;
- geography and population;
- URL or reproducible artifact path;
- source-strength code;
- claim state;
- caveat;
- refresh rule for dynamic sources.

Use [`templates/evidence-ledger.csv`](../templates/evidence-ledger.csv) as the starting schema.

## Evidence hygiene

- Cite the page that contains the fact, not a search-results page.
- Preserve the effective date of a rule separately from the date it was checked.
- Keep “no competitor found” as an inference, never an observed fact.
- Mark product performance numbers as vendor claims unless independently replicated.
- If a source disappears, retain the claim only when an archived copy or reproducible raw artifact exists.
- Do not publish private interview transcripts, bills, account identifiers, or research exports without explicit permission.
