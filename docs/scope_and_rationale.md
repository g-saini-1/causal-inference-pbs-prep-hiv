# Project scope and rationale: PBS-subsidised PrEP and HIV diagnoses

## Selection rationale

This case study offers a well-documented, real-world natural experiment with
a clear before-and-after story. It demonstrates a full two-stage causal
chain, from a policy change to a behavioural response to a downstream health
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

## Causal question and methodology

**Did PBS listing of PrEP cause a reduction in new HIV diagnoses, beyond the trend already underway?**

This is answered using a methodology of four causal methods, applied in
increasing order of rigour:

1. **Stage 1: Did dispensing itself change sharply at the moment of the PBS
   listing?**
   *Causal method: interrupted time series on dispensing.*
   The level shift at April 2018 is large and unambiguous (dispensing
   moves from near-zero to thousands a month). This step mainly
   demonstrates a clean segmented regression; the effect size is large
   enough to serve as a sanity check before the harder question.
   *Threat to identification: dispensing shows no sharp shift at April
   2018, e.g. a gradual increase already underway beforehand, or no
   discernible change around that date.*
2. **Stage 2: Did the population PrEP targets see a larger drop in HIV
   notifications than other groups, beyond a trend they share?**
   *Causal method: difference-in-differences on HIV notifications,
   comparing diagnoses attributed to male-to-male sexual contact against
   other transmission categories.*
   PrEP overwhelmingly targets gay
   and bisexual men, so notifications attributed to heterosexual
   transmission or other categories form a natural control group that was
   not materially treated by PrEP availability. Comparing trend breaks
   between groups around April 2018 is a stronger causal method than a
   plain before/after comparison, since it nets out any general downward
   trend in HIV testing or awareness campaigns.
   *Threat to identification: the control group (heterosexual/other
   transmission) shows a drop of similar size to the MSM group after April
   2018, pointing to a shared secular trend rather than a PrEP-specific
   effect.*
3. **Stage 3: Does NSW's earlier access via EPIC-NSW show the same decline
   earlier than the rest of the country, consistent with PrEP access
   itself driving it rather than some other national factor?**
   *Causal method: staggered-adoption difference-in-differences, applied
   at the state level.*
   NSW ran a large PrEP
   demonstration trial (EPIC-NSW) from 2016, ahead of the national PBS
   listing, so NSW was effectively treated earlier than other states. This
   staggered timing allows NSW's earlier decline to serve as a leading
   indicator against other states as a later comparison, similar in spirit
   to modern staggered-adoption difference-in-differences estimators such
   as Callaway and Sant'Anna, which also address the comparison problems
   that arise in classic two-way fixed-effects DiD when treatment timing
   varies across units.
   *Threat to identification: NSW's MSM notification decline starts at
   the same time as other states' (2018) rather than earlier (2016), or
   other states already show a decline before their own 2018 access,
   suggesting some other national factor is driving the trend rather than
   PrEP access timing itself.*
4. **Stage 4 (optional): Did the size of the effect vary by state, and is
   that variation explained by state-level covariates?**
   *Causal method: causal forest (CausalForestDML) heterogeneity
   analysis.*
   With state-level covariates, e.g.
   testing rates, population density of gay and bisexual populations, and
   socioeconomic indicators, a method such as EconML's CausalForestDML
   could estimate whether the PrEP effect varied by state.
   *Threat to identification: effect size shows no meaningful relationship
   with these covariates. Note this is weaker than the other three: a null
   result here would only mean the heterogeneity isn't explained by the
   chosen covariates, not that Stages 1-3's core causal claim is wrong.*

Each stage answers a narrower question that the next stage builds on.
Together, they build up an answer to the main question by progressively
ruling out that something other than PrEP access was responsible.
