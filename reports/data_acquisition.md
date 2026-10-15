# Data acquisition and synthetic data

## Overview

This document covers how the data behind this project was sourced, why it
runs on a combination of synthetic and real PBS/NNDSS
extracts, and how each series was built, one dataset at a time. For QA and 
a deeper check of each series against real ground truth, see
[`reports/data_validation.md`](data_validation.md).

**Data sourcing and licensing.** Real third-party source files (PBS Item
Reports, Kirby Institute reports, Kirby's HIV dashboard exports) are kept
locally, not committed to git (see `.gitignore`), a project choice rather
than a uniform legal bar: the PBS Item Reports carry a Creative Commons
Attribution 3.0 Australia licence permitting redistribution with
attribution, while the Kirby Institute material carries no stated licence
and falls back to UNSW's general site policy, a genuine grey area on public
redistribution. Facts drawn from these sources are cited by their
real-world origin rather than a local path, so this document's claims stay
checkable without the files themselves.

**Status.** The PBS dispensing data section below is complete. The HIV
notifications data and State covariates data sections are still to be
completed.

## PBS dispensing data

### Data requirements

PrEP is the co-formulated antiretroviral tenofovir disoproxil + emtricitabine,
sold under the brand name Truvada and, since patent expiry, under several
generic brands. On the PBS, it is listed under several item codes, one per brand and pack size, with the indication *"Pre-exposure
prophylaxis (PrEP) against human immunodeficiency virus (HIV) infection"*,
for example item 11296M (tenofovir disoproxil 300 mg + emtricitabine
200 mg, 30 tablets, Viatris/Alphapharm brand). This PrEP-specific restriction
distinguishes these dispensings from the same drug prescribed to *treat*
existing HIV infection, which sits under a separate item and restriction.

The project's dispensing series must span January 2016 to October 2022,
so it covers both sides of the April 2018 PBS listing and supports a pre-
and post-treatment comparison (see
[`docs/scope_and_rationale.md`](../docs/scope_and_rationale.md)). Meeting
that requirement means identifying every PBS item code that carries the
PrEP restriction above, and establishing when each one started.

#### Identifying PrEP item codes
The item codes were identified through the following steps:

- The item codes currently listed were obtained from the PBS medicine
  search (https://www.pbs.gov.au/) for tenofovir disoproxil +
  emtricitabine.
- Older item codes that have since been deleted from the schedule were
  obtained by manually searching the historical archive of monthly
  Schedules of Pharmaceutical Benefits
  (https://www.pbs.gov.au/publication/schedule/archive).
- The resulting item codes were validated against the item codes listed
  in the **Kirby Institute** (UNSW Sydney) report series "Monitoring HIV
  pre-exposure prophylaxis (PrEP) uptake in Australia" [1].

These are the item codes found, and the month each has dispensing data.
Four of the eight codes, 14636H, 15366R, 15383P, and 15410C, list after the
project's October 2022 end date; they are recorded for completeness, not
because the ground-truth comparison needs them.

| Item code | Month listing starts | Sources |
|---|---|---|
| 11276L | April 2018 | Kirby Institute report series [1]; PBS Item Report extract |
| 11296M | April 2018 | Kirby Institute report series [1]; PBS Item Report extract |
| 11306C | April 2018 | Kirby Institute report series [1]; PBS Item Report extract |
| 12542D | April 2021 | Kirby Institute report series [1]; PBS Item Report extract |
| 14636H | October 2024 | PBS Item Report extract only (postdates Kirby Issues 1-10) |
| 15366R | July 2026 | PBS Item Report extract only (postdates Kirby Issues 1-10) |
| 15383P | July 2026 | PBS Item Report extract only (postdates Kirby Issues 1-10) |
| 15410C | July 2026 | PBS Item Report extract only (postdates Kirby Issues 1-10) |

### Data availability

Once the codes were confirmed, PBS dispensing data for those codes (by
item, scheme, state, and month, January 2016 to July 2026) was downloaded
from Services Australia's Medicare Statistics PBS Item Reports tool. The
exact URL used for that download cannot be confirmed: the downloaded
extract files carry no source link, only a Services Australia disclaimer,
and the tool does not appear to still be available at its expected
address.

### Data gaps

Two gaps affect the real-world data:

1. **No PBS dispensing data before April 2018.** The raw PBS Item Report
   extract has zero dispensing rows, for any state or any of the eight
   item codes above, before April 2018: these items did not exist on the
   PBS schedule earlier, so no PBS claims data can show pre-listing
   dispensing.
2. **NSW's EPIC-NSW trial left no PBS item code trail either.** From March
   2016, the EPIC-NSW trial [6] supplied PrEP to NSW (and a small number
   of ACT) participants entirely outside the PBS claims system, funded by
   the NSW Ministry of Health, with medication donated by Gilead and
   purchased from Mylan. NSW dispensing is a partial exception in
   substance during this period, just not in this data source.

The project's causal design (see
[`docs/scope_and_rationale.md`](../docs/scope_and_rationale.md)) needs a
dispensing series spanning both sides of the April 2018 listing; real PBS
data alone cannot supply the "before" half.

### Data acquisition and construction

Because of these gaps, the pre-listing period is constructed instead. No
value below is randomly generated, each segment is either a verified real
fact, a documented construction from real milestones, or the real extract
itself:

- **January 2016 to March 2018, rest of country (and NSW before March
  2016): zero**, the real value, since these item codes did not exist on
  the PBS schedule yet.
- **March 2016 to March 2018, NSW: constructed from EPIC-NSW's published
  enrolment milestones** [6], tracking cumulative enrolment (about 462
  new participants a month to 3,700 by October 2016, then about 334 a
  month to 9,709 by April 2018).
- **April 2018 to October 2022, all states: the real PBS Item Report
  extract**, used directly, unmodified. November and December 2022 are
  excluded: an isolated collapse in the raw extract
  for those two months, consistent with reporting lag rather than a real
  drop, left no reliable figure to use, so the series ends in October
  2022 instead.

## HIV notifications data

### Data requirements

The project design requires **quarterly** HIV notification counts by
state and transmission category, spanning both sides of the April 2018
treatment date, with several years of pre-treatment history (back to at
least 2013-2016, see
[`docs/scope_and_rationale.md`](../docs/scope_and_rationale.md)).

### Data availability

Three real-world sources were checked for HIV notification counts:

- The National Notifiable Diseases Surveillance System (NNDSS) extract on
  data.gov.au, available only from **Q1 2019** onward. This reflects a
  genuine feature of how the data is collected nationally, not a download
  or access fault.
- The project's own copy of a Kirby Institute National HIV Quarterly
  Report [2], whose tables run from **Q1 2019** to Q2 2023 with no earlier
  quarters present, consistent with the Kirby Institute's description of
  this report series [3] and a Health Equity Matters summary of it [4].
- Earlier years' exposure-category detail, available only at **annual**
  resolution: the Kirby Institute's interactive data dashboard [5]
  provides annual, machine-readable exposure-category figures back to at
  least 2015 (2013, at the time of this project's own download), and
  Kirby's Annual Surveillance Reports publish the same annual detail as
  PDF tables.

### Data gaps

Two gaps affect the real-world data:

1. **No quarterly resolution before 2019.** Neither real source above
   offers quarterly counts before 2019; the pre-period would have had to
   be annual while the post-period was quarterly, an asymmetry that would
   complicate the project's difference-in-differences designs.
2. **Manual extraction required even at annual resolution.** The annual
   PDF tables would still have required substantial manual extraction to
   assemble, even at that coarser resolution.

This left no way to build a genuinely quarterly, exposure-stratified series
spanning both sides of the April 2018 treatment date from public sources.

### Data acquisition and construction

With no quarterly pre-period available, the project generated synthetic
data with the same structure and a known, built-in effect, calibrated so
the national annual total tracks published anchor figures of 1,028
diagnoses in 2015 and 838 in 2018, close to, but not identical to, the real
totals in the Kirby Institute's interactive data dashboard [5], which sum
to 1,030 in 2015 and 840 in 2018.

Each state/category/quarter combines a mild shared secular decline, a
PrEP-driven reduction applied only to the MSM category from each state's
own treatment start date (2016 for NSW, 2018 for the rest), and a shared
2020 testing-disruption dip, calibrated to the anchor figures above.

## State covariates data

This dataset was never attempted from real-world sources; it holds static,
plausible state-level figures (population, MSM population proxy,
socioeconomic index, testing rates, lockdown severity, EPIC-NSW early-access
flag) built directly for the optional heterogeneity analysis, not
calibrated to any published figures.

## References

1. Kirby Institute. *Monitoring HIV pre-exposure prophylaxis (PrEP) uptake in
   Australia* [report series, Issues 1-10, 2019-2024]. Sydney: Kirby Institute,
   UNSW Sydney. Series page: https://www.kirby.unsw.edu.au/research/reports;
   Issue 10, used for item-code validation:
   https://www.kirby.unsw.edu.au/research/reports/monitoring-hiv-pre-exposure-prophylaxis-prep-uptake-australia-issue-10.
   Item codes stated explicitly from Issue 6 (May 2022) onward: 11276L,
   11296M, 11306C, 12542D.
2. Kirby Institute. *HIV summary Q2 2023* [National HIV Quarterly Report].
   Sydney: Kirby Institute, UNSW Sydney.
   https://www.kirby.unsw.edu.au/sites/default/files/documents/HIV%20summary%20Q2%202023.pdf.
   Table 2 (pages 1-2) covers Q1 2019 to Q2 2023.
3. Kirby Institute. *National HIV quarterly report* [report series page].
   https://www.kirby.unsw.edu.au/research/reports/national-hiv-quarterly-report.
4. Health Equity Matters. *National quarterly HIV reporting*.
   https://www.healthequitymatters.org.au/resources/national-quarterly-hiv-reporting.
   Summarises the same Kirby Institute series; its most recent edition states
   coverage of "quarter 1 (January to March) 2019 to quarter 2 (April to June)
   2023," corroborating the Q1 2019 starting point.
5. Kirby Institute. *HIV* [interactive data dashboard]. Sydney: Kirby Institute,
   UNSW Sydney. https://www.data.kirby.unsw.edu.au/hiv. Annual notifications by
   exposure category, jurisdiction, age, sex, and First Nations status.
6. Grulich AE, Jin F, Bavinton BR, et al (EPIC-NSW research group). Long-term
   protection from HIV infection with oral HIV pre-exposure prophylaxis in gay
   and bisexual men: findings from the expanded and extended EPIC-NSW
   prospective implementation study. *The Lancet HIV*. 2021. DOI:
   [10.1016/S2352-3018(21)00074-6](https://doi.org/10.1016/S2352-3018(21)00074-6).
