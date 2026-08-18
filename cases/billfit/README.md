# BillFit: from broad consumer pain to a data-backed AI skill

BillFit is the first case produced with this repository's discovery method. It compares supported PG&E residential electricity plans from user-provided interval data and screens common assistance pathways using versioned official-source rules.

- Product repository: [ValerianXXX/billfit](https://github.com/ValerianXXX/billfit)
- Public release: [BillFit v0.2.0](https://github.com/ValerianXXX/billfit/releases/tag/v0.2.0)
- Case date: 2026-08-18
- Primary market: U.S. consumers; MVP scope: supported PG&E residential bundled-electric accounts
- Highest fully evidenced validation level: V4, engineering validation

## Executive summary

The project did not begin with utility rates. A six-month technology-supply scan and a U.S. consumer-pain scan produced twelve lightweight AI concepts. A customer-service context tool ranked first under the initial scorecard.

That concept failed two product challenges:

1. a capable general assistant could already summarize a conversation; and
2. automatic collection and handoff would require site-specific integrations, turning a small skill into a broader application.

The discovery method was tightened. New candidates had to depend on critical data a general model could not safely supply from memory: exact qualification rules, compatibility mappings, local entitlements, or current official rates.

BillFit survived because its useful output requires five things at once:

- a user-owned interval-usage file;
- current provider-specific tariff data;
- exact time and baseline calculations;
- account-scope and technology facts that may remain unknown;
- official assistance thresholds and human certification boundaries.

The resulting MVP is deliberately narrow. It performs deterministic analysis inside an AI workflow and leaves account login, plan changes, applications, and medical certification to people.

## The user decision

> When a supported PG&E residential customer wants to know whether another rate plan or assistance path may fit, the customer needs a source-dated comparison, but a general model lacks the current tariff tables, interval-usage calculation, and confirmed account facts.

This is a decision-support problem, not a bill-summary problem.

## Why general AI is insufficient

| Missing element | Why it matters | BillFit response |
|---|---|---|
| Current tariff version | Rates and fixed charges change over time | Versioned official-source data with effective and verification dates |
| Interval usage | Time-of-use plans depend on when energy is consumed | Local parsing of Green Button CSV or XML data |
| Exact arithmetic | Small rule or time-bucket errors can reverse a ranking | Deterministic standard-library calculator |
| Account scope | Solar, CCA, baseline territory, and technology eligibility change validity | Explicit inputs, exclusions, and human gates |
| Assistance rules | Income thresholds and certification requirements are dated and program-specific | Separate source-dated screening; never a final approval claim |

PG&E lists current and historic residential rate workbooks on its [electric rates page](https://www.pge.com/tariffs/en/rate-information/electric-rates.html). Its usage guidance says electric interval data can be downloaded through Green Button after the customer signs in to their own account. The [CPUC CARE/FERA page](https://www.cpuc.ca.gov/care/) publishes date-bounded income rules, while [PG&E Medical Baseline guidance](https://www.pge.com/en/account/billing-and-assistance/financial-assistance/medical-baseline-program.html) retains practitioner certification and utility approval.

## What the MVP does

- parses user-provided Green Button CSV or XML usage;
- compares E-1, E-TOU-C, E-TOU-D, EV2-A, and E-ELEC where inputs are sufficient;
- reconstructs comparable energy and base-service components;
- screens CARE, FERA, and Medical Baseline pathways;
- reports source dates, exclusions, data-quality warnings, and human gates.

## What it intentionally does not do

- collect utility credentials or sign in to an account;
- support solar, net export, CCA, Direct Access, gas, or every bill component;
- change a rate plan;
- submit an assistance application;
- accept tax returns, pay stubs, Social Security numbers, or medical records;
- certify eligibility or guarantee savings.

## Case files

- [Discovery timeline](discovery-timeline.md)
- [Opportunity matrix](opportunity-matrix.md)
- [Product decisions](product-decisions.md)
- [Evidence ledger](evidence-ledger.md)
- [Validation status](validation-status.md)

## Honest status

The product is implemented, tested on fixtures, publicly released on GitHub, and packaged as a skill/plugin. The case does not yet contain observed target-user adoption, unassisted repeat use, verified real-bill savings, or product-market fit. Marketplace review and public listing are not treated as completed merely because submission materials exist.
