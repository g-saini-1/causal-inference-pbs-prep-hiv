# Data validation

This document validates how each series in `data/synthetic/` was
actually built: whether the generator (`src/generate.py`) correctly
implements the construction described in
[`reports/data_acquisition.md`](data_acquisition.md), and, where an
independent real-world benchmark exists, how closely the result matches
that ground truth. Not every series here is synthetic in the sense of
randomly generated. The PBS dispensing series below is built from real
values and documented constructions with no random component; the HIV
notifications series is a calibrated simulation with noise. "Ground
truth" means different things for each: an exact match for the PBS
series' real segments, a closeness-of-fit comparison for the HIV series'
simulated one. Real-world source material used below is sourced and
licensed as described in `reports/data_acquisition.md`'s "Data sourcing
and licensing" note.

**Status.** The PBS dispensing data section below is complete.
The HIV notifications data section is still to be completed.

## PBS dispensing data

PrEP-specific PBS item codes are covered in
[`reports/data_acquisition.md`](data_acquisition.md). The generator does
not model item-code-level detail; it produces one aggregate monthly
dispensing count per state.

### Validation approach

This section checks:

- Whether the generator correctly implements the construction described
  in `reports/data_acquisition.md`'s "Data acquisition and construction"
  section.
- Whether the real-extract portion of the series matches an independent
  real-world benchmark, the Kirby Institute's published PrEP dispensing
  figures.
- Whether the EPIC-NSW-constructed portion matches the real enrolment
  milestones it is built from.
- Whether the series is continuous across its construction boundaries,
  with no unexplained artefact where one segment hands off to the next.

### Generator overview

`src/generate.py` builds this series deterministically, with no random
component: the real PBS extract is used directly from April 2018 onward,
NSW's March 2016 to March 2018 period is computed from EPIC-NSW's
published enrolment milestones, and every other cell is zero. See
`reports/data_acquisition.md` for the exact figures and sourcing behind
each segment.

### Validation tests

1. Post-April-2018 values match the real PBS Item Report extract exactly, for every state.
2. NSW's March 2016 to March 2018 values match the published EPIC-NSW enrolment milestones.
3. Rest-of-country values before April 2018 are exactly zero.
4. The series is continuous at the March-to-April 2018 construction boundary, for every state.

### Test results

1. **Confirmed.** Every state's post-April-2018 value equals the real PBS
   extract exactly; no scale, geography, or COVID-shape gap remains.
2. **Confirmed.** NSW's constructed values match the EPIC-NSW enrolment
   milestones they are built from.
3. **Confirmed.** Every rest-of-country value before April 2018 is zero.
4. **Failed: one artefact found, the EPIC-NSW transition cliff.** NSW
   drops from 9,375 in March 2018 (end of the constructed period) to 341
   in April 2018 (start of the real extract), a one-month fall of about
   96%. This is an artefact, not a real decline: EPIC-NSW participants did
   not stop taking PrEP, the real data's own gradual climb afterward (341,
   887, 1,198, 1,775 over the next three months) shows the actual
   trial-to-PBS-billing transition took several months, which the
   construction does not model. The other five states show no equivalent
   cliff, a genuine cold start from 0 to a small real value.
   **Project impact: none currently.** Stage 1 excludes NSW entirely, and
   no implemented or stubbed stage fits a model directly on NSW's PBS
   dispensing values; Stage 3's staggered-adoption design uses EPIC-NSW's
   timing only as a treatment-date anchor, not this series' values.

## HIV notifications data

### Validation approach

This section checks:

- Whether the generator correctly implements the construction described
  in `reports/data_acquisition.md`'s "Data acquisition and construction"
  section for this series.
- How closely the resulting simulation tracks real-world HIV notification
  patterns, at both an annual national level and a quarterly,
  category-level shape, since this series, unlike PBS dispensing, is
  genuinely simulated rather than built from real values.
- Whether mapping the real data's six exposure categories onto the
  synthetic data's three materially changes what the comparison group
  represents.

### Generator overview

`src/generate.py` builds this series from a calibrated formula with
Poisson noise, not real values: a secular decline anchored to two
published annual totals, a PrEP effect applied only to the MSM category
from each state's own treatment start, and a shared 2020
testing-disruption dip. See `reports/data_acquisition.md` for the full
construction detail.

### Validation tests

1. The generator's random-number handling does not let a change to one series silently change another.
2. Annual national totals, 2015-2018, closely match the published calibration anchors.
3. Annual national totals, 2019 onward, are checked against real figures for the size and cause of any divergence.
4. The quarterly MSM shape is compared against the real quarterly series.
5. The six-to-three exposure-category mapping is checked for whether it changes what the comparison group represents.

### Test results

1. **Failed, resolved.** A shared random-number stream between this
   series and PBS dispensing meant a PBS dispensing fix once silently
   changed these numbers too. Fixed by giving each dataset its own
   independent stream.
2. **Confirmed.** 2015-2018 annual national totals match the real totals
   within 5%, confirming the generator's 1,028/838 calibration anchors are
   accurate against the real 1,030/840 figures.

   | Year | Real total | Synthetic total | Difference |
   |---|---|---|---|
   | 2015 | 1,030 | 1,034 | +0.4% |
   | 2016 | 1,006 | 1,023 | +1.7% |
   | 2017 | 962 | 918 | -4.6% |
   | 2018 | 840 | 820 | -2.4% |

3. **Diverges, cause identified.** 2019 onward diverges by up to 21%:

   | Year | Real total | Synthetic total | Difference |
   |---|---|---|---|
   | 2019 | 895 | 706 | -21.1% |
   | 2020 | 626 | 557 | -11.0% |
   | 2021 | 542 | 590 | +8.9% |
   | 2022 | 553 | 612 | +10.7% |

   **The MSM timing finding.** Real MSM notifications stay essentially
   flat through all of 2019 (140-152 a quarter) and only drop sharply from
   2020 onward, the same year as COVID. The synthetic series' PrEP effect
   instead ramps immediately from 2018Q2, so it is already declining
   through 2019 (91-115) before the real data shows any comparable drop.
   In the real data, the post-listing MSM decline and the COVID
   testing-disruption dip land in the same narrow window and are hard to
   separate; the synthetic design deliberately keeps them as two distinct,
   separately-timed components. That is a known, deliberate
   simplification, not a defect: the project's synthetic data exists so
   each causal method can be validated against a clean, known effect, and
   a clean effect requires a clean, separable signal. It is still a real
   limit on how far this series' quarterly timing can be read as
   representative of the real world's, beyond its annual totals and
   overall direction.
4. **Descriptive, not a pass/fail test.** Quarterly shape, 2019Q1-2022Q4
   (MSM, mapped category, both sources):

   | Quarter | Real MSM | Synthetic MSM |
   |---|---|---|
   | 2019Q1 | 149 | 115 |
   | 2019Q2 | 148 | 111 |
   | 2019Q3 | 152 | 101 |
   | 2019Q4 | 140 | 91 |
   | 2020Q1 | 138 | 82 |
   | 2020Q2 | 90 | 75 |
   | 2020Q3 | 84 | 74 |
   | 2020Q4 | 100 | 74 |

   The full 16-quarter comparison gives a correlation of r=0.57 for MSM,
   against r=0.16 for Heterosexual and r=0.30 for Other, both of which are
   small, noise-dominated categories in both sources, so low correlation
   there is expected rather than a concern.
5. **Judged acceptable.** The Kirby quarterly report's underlying table
   reports six real-world categories: Male-to-male sex, Male-to-male sex
   and injecting drug use, Heterosexual sex, Injection drug use, Other
   exposure, and Vertical transmission. These map onto the synthetic
   data's three as: **MSM** = Male-to-male sex + Male-to-male sex and
   injecting drug use; **Heterosexual** = Heterosexual sex; **Other** =
   Injection drug use + Other exposure + Vertical transmission.
   Male-to-male sex and injecting drug use is folded into MSM rather than
   Other because it is still a male-to-male-sex exposure, the relevant
   criterion for Stage 2's identification argument (PrEP eligibility and
   uptake, not injecting drug use specifically, is what separates the
   treated and comparison groups). Injection drug use, Other exposure, and
   Vertical transmission are all small categories (each under 10% of the
   national total in every year checked above) not materially treated by
   PrEP, consistent with Stage 2's comparison group definition, so
   bucketing them together as "Other" does not meaningfully change what
   that comparison group represents.
