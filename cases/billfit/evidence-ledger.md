# Evidence ledger

The machine-readable ledger is [`data/evidence-ledger.csv`](../../data/evidence-ledger.csv). This page highlights the sources that control the final product decision.

## Product-controlling evidence

| ID | Source | What it establishes | State |
|---|---|---|---|
| B01 | [PG&E company profile](https://www.pge.com/en/about/company-information/company-profile.html) | PG&E reports 5.5 million electric customer accounts, a reach proxy rather than a BillFit adoption estimate | Observed |
| B02 | [PG&E electric rates](https://www.pge.com/tariffs/en/rate-information/electric-rates.html) | Current and historic provider-specific residential rate workbooks exist; the page listed a March 1, 2026 current workbook when checked | Observed |
| B03 | [PG&E usage tools](https://www.pge.com/en/save-energy-and-money/energy-usage-and-tips/understand-my-usage.html) | Customers can download electric interval usage with Green Button after signing in | Observed |
| B04 | [CPUC CARE/FERA](https://www.cpuc.ca.gov/care/) | Income thresholds are program-specific and carry effective dates | Observed |
| B05 | [PG&E Medical Baseline](https://www.pge.com/en/account/billing-and-assistance/financial-assistance/medical-baseline-program.html) | Medical need must be certified and final enrollment remains with the program | Observed |
| B06 | [BillFit source](https://github.com/ValerianXXX/billfit) | Public implementation, scope, test command, privacy boundaries, and source notes | Observed |
| B07 | [BillFit v0.2.0](https://github.com/ValerianXXX/billfit/releases/tag/v0.2.0) | A public packaged release exists | Observed |

## Technology-supply research

The six-month GitHub scan used archived weekly Trending pages because GitHub does not provide an official historical Trending API. GitHub's own explanation says Trending is calculated in daily, weekly, and monthly buckets. The archive method therefore carries two important limitations:

- the collected 421 rows covered 81.0% of the theoretical 520 Top-20 positions;
- rule-based AI and category labels are analyst classifications, not GitHub metadata.

The derived summary is published in [`data/github-trend-summary.csv`](../../data/github-trend-summary.csv). It is evidence about visible developer supply, not consumer demand, code quality, or commercial value.

## Demand evidence and product hypothesis

The initial consumer scan used official data, recent surveys, industry research, and product pages. Those sources generated and eliminated concepts; they do not prove BillFit demand. The claim that target users will install, trust, or benefit from BillFit remains an untested product hypothesis.

## Refresh policy

| Source class | Refresh trigger |
|---|---|
| Tariffs and rate workbooks | Before release, when PG&E publishes a new effective period, and before acting on a snapshot older than the product's freshness threshold |
| CARE/FERA rules | At each stated effective-period boundary or earlier program change |
| Medical Baseline rules | Before material workflow changes and at least each release cycle |
| Product scope and release | Every BillFit version |
| Market and competitor sources | Before changing the product-selection conclusion |
