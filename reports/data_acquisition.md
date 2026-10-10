# Data acquisition and synthetic data: PBS-subsidised PrEP and HIV diagnoses

*A causal inference case study using Australian PrEP listing and HIV surveillance data*

## Overview

This document covers how the data behind this project was sourced, why most
of it currently runs on synthetic data rather than the real PBS/NNDSS
extracts, and how each series was built, one dataset at a time. For QA of the
generator and a deeper check of each series against real ground truth, see
[`reports/synthetic_data_validation.md`](synthetic_data_validation.md). For
the causal question and the four-stage design, see
[`docs/scope_and_rationale.md`](../docs/scope_and_rationale.md). For Stage 1's
results, see
[`reports/stage1_interrupted_time_series.md`](stage1_interrupted_time_series.md).

Both datasets below were generated synthetically for the same two reasons:
it lets each stage's fitted result be checked against a **known ground
truth** rather than an unknown real effect, and it avoids reconciling
multiple incomplete public extracts before modelling could start. Each
dataset's section below sets out the specific difficulty that made this
necessary.

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

## PBS dispensing data

### What was found in the real world

PrEP is the co-formulated antiretroviral tenofovir disoproxil + emtricitabine,
sold under the brand name Truvada and, since patent expiry, under several
generic brands. On the PBS, it is listed under several **Restricted Benefit**
items, one per brand and pack size, with the indication *"Pre-exposure
prophylaxis (PrEP) against human immunodeficiency virus (HIV) infection"*,
for example item **11296M** (tenofovir disoproxil 300 mg + emtricitabine
200 mg, 30 tablets, Viatris/Alphapharm brand). This PrEP-specific restriction
distinguishes these dispensings from the same drug prescribed to *treat*
existing HIV infection, which sits under a separate item and restriction.
Each candidate code was identified via a PBS item drug map search, then
checked against PBS Schedule history (monthly schedule snapshots, searched
across January 2017 to June 2026) to confirm the restriction and establish
its listing date.

The **Kirby Institute** (UNSW Sydney) publishes its own "Monitoring HIV
pre-exposure prophylaxis (PrEP) uptake in Australia" report series [1] using
the same item codes, drawing on every PBS-subsidised PrEP prescription
dispensed since 1 April 2018. It provides an external check against the raw
PBS Item Reports (data.gov.au) extracted directly for this project, which
shows about 59,600 PrEP dispensing services nationally in the first nine
months after listing (April to December 2018), rising from a standing start.

These are the item codes found, and the month each has dispensing data,
since the project's dispensing series spans January 2016 to December 2022.
Four of the eight codes, 14636H, 15366R, 15383P, and 15410C, list after that
period ends; they are recorded for completeness, not because the
ground-truth comparison needs them.

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

### The difficulty

The raw PBS Item Report extract has zero dispensing rows, for any state or
any of the eight item codes above, before April 2018: these items did not
exist on the PBS schedule earlier, so no PBS claims data can show
pre-listing dispensing. NSW is a partial exception in substance, not in
this data source: the EPIC-NSW trial supplied PrEP to NSW (and a small
number of ACT) participants from March 2016, entirely outside the PBS
claims system, funded by the NSW Ministry of Health, with medication
donated by Gilead and purchased from Mylan, so it left no PBS item code
trail either. The project's causal design (see
[`docs/scope_and_rationale.md`](../docs/scope_and_rationale.md)) needs a
dispensing series spanning both sides of the April 2018 listing; real PBS
data alone cannot supply the "before" half.

### Why synthetic

With no real pre-listing dispensing data of any kind, the project generated
synthetic data with the same structure and a known, built-in effect, giving
the full pre/post series the causal design needs. A revision bringing most
of this series back to real data is proposed in
[`reports/synthetic_data_validation.md`](synthetic_data_validation.md), now
that the extent of the pre-period gap is this well established.

### How this series was built

A single generator script produces this series, along with the other two
synthetic files, from a fixed random seed, so the data is reproducible.
Each state's monthly dispensing count combines an early ramp for NSW from
2016 (EPIC-NSW), a large level shift and ramp-up for all states from April
2018, and a COVID-era dip in 2020 that is deepest and longest in Victoria,
then adds realistic Poisson noise.

## HIV notifications data

### What was found in the real world

The National Notifiable Diseases Surveillance System (NNDSS) extract on
data.gov.au was the first port of call for HIV notification counts, but it
was only available from **Q1 2019** onward. This reflects a genuine feature
of how the data is collected nationally, not a download or access fault.
The project's own copy of a Kirby Institute National HIV Quarterly Report
[2] is itself evidence of this: its tables run from **Q1 2019** to Q2 2023,
with no earlier quarters present, consistent with the Kirby Institute's
description of this report series [3] and a Health Equity Matters summary
of it [4]. Earlier years' exposure-category detail is available, but only
at **annual** resolution: the Kirby Institute's interactive data dashboard
[5] provides annual, machine-readable exposure-category figures back to at
least 2015 (2013, at the time of this project's own download), and Kirby's
Annual Surveillance Reports publish the same annual detail as PDF tables.

### The difficulty

The project design requires **quarterly** notification counts by state and
transmission category, with several years of pre-treatment history (back to
at least 2013-2016, see
[`docs/scope_and_rationale.md`](../docs/scope_and_rationale.md)). Neither
real source above offers quarterly resolution before 2019; the pre-period
would have had to be annual while the post-period was quarterly, an
asymmetry that would complicate the project's difference-in-differences
designs, and the annual PDF tables would still have required substantial
manual extraction to assemble even at that coarser resolution. This left no
way to build a genuinely quarterly, exposure-stratified series spanning
both sides of the April 2018 treatment date from public sources.

### Why synthetic

With no quarterly pre-period available, the project generated synthetic
data with the same structure and a known, built-in effect, calibrated so
the national annual total tracks published anchor figures of 1,028
diagnoses in 2015 and 838 in 2018, close to, but not identical to, the real
totals in the Kirby Institute's interactive data dashboard [5], which sum
to 1,030 in 2015 and 840 in 2018.

### How this series was built

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
   UNSW Sydney. https://www.kirby.unsw.edu.au/research/reports. Item codes
   stated explicitly from Issue 6 (May 2022) onward: 11276L, 11296M, 11306C,
   12542D.
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
