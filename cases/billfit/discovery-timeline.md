# Discovery timeline

This is a reconstructed decision log based on the project's research workbooks, implementation repository, and recorded product challenges. It summarizes decisions; it is not a verbatim conversation transcript.

## 1. Technology-supply scan

The project reviewed 26 complete weeks of archived GitHub Trending weekly results from 2026-02-16 through 2026-08-16. The archive contained 421 listed positions across 284 repositories, covering 81.0% of the theoretical Top-20 slots.

The rule-based classification marked 81.2% of appearances as AI-related and 57.7% as agent-related. Those figures describe the collected archive, not all open-source software and not consumer demand. The practical observation was a supply imbalance: developer agents and infrastructure were receiving intense attention while everyday consumer decisions still depended on fragmented official data.

See [`data/github-trend-summary.csv`](../../data/github-trend-summary.csv) and the [method note](evidence-ledger.md#technology-supply-research).

## 2. Broad consumer-pain scan

The U.S.-first scan combined recent surveys and complaint signals, existing-product research, and technical feasibility. Twelve candidates were scored for reach, frequency, pain, workflow whitespace, MVP ease, AI leverage, acquisition, monetization, and risk.

The first-ranked concept was a customer-service “context passport”: turn a failed chatbot transcript into a concise package for a human agent. The idea had a clear frustration signal and a fast text-only prototype.

## 3. First concept rejected

Two challenges changed the decision:

- **Substitutability:** a general assistant can already summarize a supplied transcript and draft an escalation message.
- **Integration burden:** collecting chat history and locating a live-agent channel across many brands would require browser permissions, site adapters, account context, or a separate application.

The idea was not rejected because the pain was false. It was rejected because the proposed small product lacked a strong capability gap and understated its workflow complexity.

## 4. Product form tightened

The target changed from a standalone web or mobile product to something invoked inside an AI environment: a skill, plugin, or package. That choice made the substitute question unavoidable. A skill had to add more than prompt wording or output formatting.

## 5. Critical-data filter introduced

The search narrowed to everyday decisions where ordinary AI lacks a required data layer:

- exact qualification;
- product compatibility;
- regional entitlements;
- current official rates or rules.

Candidates then had to pass authority, access, freshness, deterministic-uplift, maintenance, and safe-failure checks.

## 6. BillFit selected

Utility plan fit and assistance screening combined several useful properties:

- a concentrated but large provider footprint;
- user-accessible interval data;
- official current and historic tariffs;
- financially meaningful outputs;
- deterministic math;
- clear unsupported cases;
- an in-AI workflow that can stop before account login or submission.

PG&E was chosen before a national utility product because one provider made source versioning, rate fixtures, exclusions, and bill reconstruction testable.

## 7. MVP boundary defined

The first release was limited to individually metered PG&E residential bundled-electric accounts without solar/net export or CCA/Direct Access. It supported five plans and three assistance pathways. User credentials, sensitive proof documents, plan changes, applications, and practitioner certification remained outside the product.

## 8. Engineering and release

BillFit added:

- a deterministic Python calculator;
- Green Button parsing;
- versioned PG&E rate and CARE/FERA snapshots;
- explicit unknowns and fail-closed exclusions;
- a local CLI fallback and MCP interface;
- automated tests and public release materials.

The product was released publicly on GitHub as [v0.2.0](https://github.com/ValerianXXX/billfit/releases/tag/v0.2.0). This completes an engineering and availability milestone, not real-user outcome validation.
