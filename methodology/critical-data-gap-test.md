# Critical-data gap test

This test distinguishes a defensible AI skill from a saved prompt.

## The seven checks

### 1. Necessity

Name the exact data without which the output becomes unreliable. Examples include a current tariff table, a model-specific compatibility mapping, a ZIP-code rule, an income threshold, or the user's interval history.

If no required data can be named, a general assistant may already be enough.

### 2. Authority

Identify which source controls when sources disagree. For regulated decisions, a current official tariff or agency rule should control over a blog, search snippet, or model memory.

### 3. Freshness and locality

Record effective date, geography, provider, customer class, and refresh trigger. “Current U.S. rule” is rarely precise enough.

### 4. Access

Confirm the data can be obtained legally, reliably, and at an MVP-compatible cost. A promising need with inaccessible or contract-restricted data is not yet a viable small skill.

### 5. Deterministic uplift

Define which output should be calculated or rule-evaluated rather than generated. The skill should improve accuracy in a way that can be tested with fixtures.

### 6. Maintenance

Assign an owner, check cadence, stale-data threshold, version identifier, and rollback path. Dynamic data without a maintenance plan is hidden product debt.

### 7. Safe failure

Specify what happens when data is missing, stale, conflicting, or outside scope. The correct output may be “needs confirmation,” not a guess.

## Decision rule

Proceed only if all of the following are true:

- at least one critical data item is necessary;
- an authoritative source and refresh path exist;
- deterministic handling materially improves the answer;
- unsupported cases can fail closed;
- the MVP does not require the skill to take over a sensitive account or irreversible action.

Otherwise reject, defer, or redesign the candidate.

## Data-gap patterns worth searching

| Pattern | Typical missing data | Example output |
|---|---|---|
| Exact qualification | Current thresholds plus household or account facts | Preliminary eligibility screen |
| Product compatibility | Model, part, version, and constraint mapping | Compatible/not compatible/needs confirmation |
| Local entitlements | Jurisdiction, provider, date, and user facts | Available benefit or next official route |
| Current official pricing | Versioned rates plus usage or quantity | Comparable cost estimate |

The useful product is not the database alone. It is the smallest trustworthy path from a user-owned input to a bounded decision.
