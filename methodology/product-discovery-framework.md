# Product-discovery framework

## Objective

Find a small consumer decision where AI becomes meaningfully better only after adding a maintainable data source, deterministic logic, or both.

The unit of discovery is a **decision moment**, not a demographic and not a broad topic. “Household finance” is too broad. “Which supported electricity plan best fits this interval-usage file?” is testable.

## Stage 1: Set the research boundary

Write down:

- primary geography;
- trend window;
- target user;
- maximum MVP scope;
- prohibited or high-risk actions;
- the evidence date after which dynamic sources must be refreshed.

BillFit used U.S. consumers as the primary market and a six-month trend window ending 2026-08-18. Older figures were allowed only as structural population or market context.

## Stage 2: Scan demand, supply, and enabling technology

Use three separate signal layers:

1. **Demand:** complaints, representative surveys, official program data, repeated workarounds, and costly errors.
2. **Supply:** direct products, adjacent products, free official alternatives, and the general AI baseline.
3. **Enablers:** newly accessible data, file formats, APIs, local execution, deterministic libraries, or distribution surfaces such as skills.

Do not use product pages to prove market size. Do not use GitHub stars to prove consumer demand.

## Stage 3: Describe the decision moment

For each candidate, complete this sentence:

> When **[trigger]** happens, **[user]** needs to decide or do **[action]**, but cannot because **[missing fact or workflow]**.

Reject candidates whose value proposition is only “summarize this,” “explain this image,” or “write a nicer message” unless the output also depends on a nontrivial data or rule layer.

## Stage 4: Run the substitute test

Give a capable general assistant the same user-provided material. Ask:

- Can it produce a sufficiently reliable answer without a dedicated data source?
- Is the proposed product merely a saved prompt or preferred format?
- Can the user obtain the same result in one normal conversation?
- Does the product require an integration that makes the “small MVP” assumption false?

If the baseline is good enough, reject or reframe the candidate. BillFit's first concept, a customer-service context summary, failed this test.

## Stage 5: Run the critical-data gap test

Identify the facts that a general model does not safely know: current official rates, local eligibility thresholds, exact compatibility tables, user-specific usage, or account-scope facts. Apply the [critical-data gap test](critical-data-gap-test.md).

## Stage 6: Draw the deterministic boundary

Separate responsibilities:

- **Model:** understand the request, collect minimal inputs, explain results, and preserve unknowns.
- **Calculator or rules engine:** parse structured data, apply exact arithmetic or rules, and return auditable outputs.
- **Human:** authenticate, confirm ambiguous facts, approve irreversible actions, and submit regulated forms.

If the model must improvise exact values, the design is not ready.

## Stage 7: Narrow the first release

A useful MVP should have:

- one geography or provider;
- one user-owned input path;
- a small supported rule set;
- explicit exclusions;
- no unnecessary account access;
- a safe answer when required information is unknown.

Narrow scope is a testing instrument. It makes false confidence visible and source maintenance possible.

## Stage 8: Pre-register validation

Before coding, record:

- what must be true;
- the smallest test that could disprove it;
- a numeric or binary pass threshold;
- what will be changed or stopped after failure.

Track each claim on the [validation ladder](validation-ladder.md). Never promote a claim because the product looks finished.

## Required outputs

Every case should publish:

- research boundary;
- evidence ledger;
- initial opportunity screen;
- rejected concepts;
- critical-data screen;
- product decision record;
- source and maintenance plan;
- validation status and untested claims.
