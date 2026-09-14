# Project scope and rationale: PBS-subsidised PrEP and HIV diagnoses

## Selection rationale

This case study was chosen ahead of other candidate ideas for the portfolio
because it offers a well-documented, real-world natural experiment with a
clear before-and-after story. It demonstrates a full two-stage causal chain,
from a policy change to a behavioural response to a downstream health
outcome, rather than a single isolated effect.

The expected effect is also well-established, which makes it possible to
validate the analysis against a known result rather than an unknown one:

- Published Australian HIV surveillance data shows new diagnoses declining
  substantially in the years following PrEP's PBS listing, particularly
  among the population PrEP targets. This gives the analysis an expected
  direction and rough magnitude to validate against, rather than an
  unconstrained result.
- PBS PrEP dispensing is expected to show a COVID-19-era disruption, based
  on Kirby Institute reporting on dispensing volumes through 2020, offering
  a second natural experiment as a possible stretch goal: whether the
  COVID-related interruption in PrEP shows up as an interruption in HIV
  prevention benefit, or whether the effect is too short to detect.

## Treatment date

1 April 2018: PrEP (Truvada or generic tenofovir-emtricitabine) was listed
on the PBS, dropping the cost from several hundred dollars a month to
around $40 a month, with further reductions for concession card holders.

## Causal question and design

Did PBS listing of PrEP cause a reduction in new HIV diagnoses in
Australia, beyond the trend already underway?

1. **Interrupted time series on dispensing** *(Stage 1)*. The level shift
   at April 2018 is large and unambiguous (dispensing moves from near-zero
   to thousands a month). This step mainly demonstrates a clean segmented
   regression; the effect size is large enough to serve as a sanity check
   before the harder question.
2. **Difference-in-differences on HIV notifications** *(Stage 2)*:
   diagnoses attributed to male-to-male sexual contact against other
   transmission categories. PrEP overwhelmingly targets gay and bisexual
   men, so notifications attributed to heterosexual transmission or other
   categories form a natural control group that was not materially treated
   by PrEP availability. Comparing trend breaks between groups around April
   2018 is a stronger identification strategy than a plain before/after
   comparison, since it nets out any general downward trend in HIV testing
   or awareness campaigns.
3. **State-level staggered-adoption design** *(Stage 3)*. NSW ran a large
   PrEP demonstration trial (EPIC-NSW) from 2016, ahead of the national PBS
   listing, so NSW was effectively treated earlier than other states. This
   staggered timing allows NSW's earlier decline to serve as a leading
   indicator against other states as a later comparison, similar in spirit
   to modern staggered-adoption difference-in-differences estimators such
   as Callaway and Sant'Anna, which also address the comparison problems
   that arise in classic two-way fixed-effects DiD when treatment timing
   varies across units.
4. **Causal forest heterogeneity analysis** *(Stage 4, optional)*. With
   state-level covariates, e.g. testing rates, population density of gay
   and bisexual populations, and socioeconomic indicators, a method such as
   EconML's CausalForestDML could estimate whether the PrEP effect varied
   by state.

## Outcome data

### A. Drug uptake data

The Kirby Institute's "Monitoring HIV PrEP Uptake in Australia" reports
publish monthly and quarterly PBS-derived dispensing counts as free
PDF/report tables at kirby.unsw.edu.au, which can be used to validate a PBS
data pull. Raw PBS Item Reports on data.gov.au, filtered to the PrEP item
code, provide monthly national and state-level dispensing volumes as
downloadable CSV files.

### B. Downstream health outcome data

The National Notifiable Diseases Surveillance System (NNDSS) on
data.gov.au publishes HIV notification counts by year and quarter,
nationally and by state. The Kirby Institute's Annual Surveillance Reports
(free PDFs) provide quarterly HIV diagnosis numbers by state and by
exposure category, e.g. male-to-male sexual contact, the population PrEP
targets. This makes it possible to construct a difference-in-differences
design comparing a heavily-exposed group against the general population,
rather than relying on a single time trend.
