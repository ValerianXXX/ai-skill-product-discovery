# Two-pass scoring model

Scoring supports comparison; it does not estimate market size or predict revenue.

## Pass A: broad opportunity screen

Use this pass to compare everyday problems before a product shape is fixed.

| Criterion | Weight |
|---|---:|
| Reach or base proxy | 20 |
| Trigger frequency | 15 |
| Pain or consequence | 15 |
| Unmet-workflow space | 15 |
| MVP ease | 15 |
| AI leverage | 10 |
| Acquisition path | 5 |
| Monetization path | 5 |
| Risk deduction | 0 to -15 |

Rate each positive criterion from 1 to 5, multiply by its weight, and divide by 5. Subtract the separately justified risk deduction.

This pass produced useful demand candidates in the BillFit project, but it overvalued concepts that a general assistant could already approximate.

## Mandatory substitute gate

Before Pass B, reject or reframe any candidate where:

- a capable general assistant can complete the task with the same input;
- differentiation is only tone, format, or a saved prompt;
- the concept requires broad integrations that contradict a small MVP;
- the proposed answer cannot name its authoritative source.

## Pass B: critical-data opportunity screen

Score only candidates that survive the substitute gate.

| Criterion | Weight |
|---|---:|
| Critical-data necessity | 20 |
| Authoritative data access | 15 |
| Deterministic reliability uplift | 15 |
| User-input availability | 10 |
| Narrow-scope feasibility | 10 |
| Freshness maintenance feasibility | 10 |
| Human-gate clarity | 10 |
| In-AI distribution fit | 5 |
| Economic or access value | 5 |

Again, score 1–5 and normalize to the weight. Record the reasoning beside every score. A high score cannot override a failed safety or data-access gate.

## Sensitivity check

Before selecting a winner:

1. reduce the two most subjective scores by one point;
2. increase maintenance difficulty by one point;
3. remove any unverified market-size assumption;
4. confirm the winner still has a coherent narrow MVP.

If the ranking changes easily, treat the candidates as tied and run a cheaper validation test before building.

The BillFit example scores are published in [`data/critical-data-opportunity-screen.csv`](../data/critical-data-opportunity-screen.csv).
