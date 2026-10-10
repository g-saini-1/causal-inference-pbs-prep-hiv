# Synthetic data validation against ground truth

This document checks the project's synthetic data (see
[`reports/data_acquisition.md`](data_acquisition.md) for why it is
synthetic) against real-world ground truth: the
generation rule behind each series, how closely the result tracks the real pattern where one
exists, and any specific handling decision worth recording. Real-world
source material used below is sourced and licensed as described in
`reports/data_acquisition.md`'s "Data sourcing and licensing" note.

## PBS dispensing data

PrEP-specific PBS codes identification are covered in
`reports/data_acquisition.md`. The generator does not model item-code-level
detail; it produces one aggregate monthly dispensing count per state.

### Generation rules

1. **Rest of country (NSW excluded), January 2016 to March 2018: set to 0.**
   The real value, not an assumption: these item codes did not exist
   before April 2018 (zero rows in the raw extract for every state), and
   no equivalent pre-2018 program is documented outside NSW.
2. **NSW, March 2016 to March 2018: constructed from EPIC-NSW's published
   enrolment figures [1].** Dispensing tracks cumulative enrolment: about
   462 new participants a month to October 2016 (3,700 total), then about
   334 a month to April 2018 (9,709 total), not plateauing. Simplifies
   away the adherence decline the source paper reports, and folds
   EPIC-NSW's small ACT presence into NSW.
3. **April 2018 onward, all states: use the real PBS Item Report extract
   directly**, resolving the scale, geography, and COVID-shape findings
   below at the source. November and December 2022 are excluded or
   substituted, an isolated collapse in the raw extract consistent with
   reporting lag, not a real drop (see QA below).


### QA

This QA checks two things: whether the generator correctly implements its
own intended logic, and how closely the resulting series matches
real-world patterns where real data exists.

**Ground truth comparison.** Checks performed:

- April 2018 onward, every state: the series equals the real PBS Item
  Report extract exactly, no scale, geography, or COVID-shape gap remains.
- NSW, March 2016 to March 2018: matches the EPIC-NSW enrolment milestones
  it is constructed from (462/month to 3,700, then 334/month to 9,709).
- Rest of country, before April 2018: zero, the real value, no PBS item
  codes existed yet.
- Continuity at the March-to-April 2018 boundary, checked for every state.

That last check found one issue. **EPIC-NSW transition cliff.** NSW drops
from 9,375 in March 2018 (end of the constructed cohort-tracking period) to
341 in April 2018 (start of real PBS billing data), a one-month fall of
about 96%. This is an artefact: EPIC-NSW participants did not stop taking
PrEP, the real data's own gradual climb afterward (341, 887, 1,198, 1,775
over the next three months) shows the actual trial-to-PBS-billing
transition took several months, which the construction does not model. The
other five states show no equivalent cliff, a genuine cold start from 0 to
a small real value.

**Project impact: none currently.** Stage 1 excludes NSW entirely
(rest-of-country only), and no implemented or stubbed stage fits a model
directly on NSW's PBS dispensing series. Stage 3's staggered-adoption
design works from HIV notifications, using EPIC-NSW's timing only as a
treatment-date anchor, not this series' values. Worth a note, not a
blocker.

## HIV notifications data

### Generation rules

The notifications series combines a straight-line secular decline, with
intercept and slope solved so the noiseless expected national annual total
hits two published anchor figures exactly, 1,028 in 2015 and 838 in 2018;
fixed category shares of that national baseline (MSM 68%, Heterosexual 22%,
Other 10%); the same state population weights used by the PBS dispensing
series; a PrEP effect applied only to the MSM category, from each state's
own treatment start (NSW from 2016Q2, every other state from 2018Q2),
ramping linearly over 8 quarters to a 42% relative reduction then holding;
a further shared secular decline applied to every category and state; a
2020 COVID testing-disruption dip, worst in Victoria and milder elsewhere,
explicitly intended to represent fewer tests producing fewer diagnoses
rather than a real transmission drop; and Poisson noise throughout.

A generator-level QA fix affected this series too: a shared random-number
stream between the two datasets meant a PBS dispensing fix once silently
changed these numbers as well. See "Fixes found during development" under
PBS dispensing data's QA section above for the full fix and the
recalibrated totals.

### Ground truth comparison

Two real sources exist, both described in `reports/data_acquisition.md`: an
annual series by exposure category back to 2015, from the Kirby Institute's
interactive dashboard, and a quarterly series from Q1 2019 to Q2 2023, from
a Kirby Institute National HIV Quarterly Report. Both comparisons below are
descriptive, not a pass/fail test, since the synthetic data is deliberately
a simplified version of a noisier real process.

**Annual national totals, 2015-2022 (the years both sources cover):**

| Year | Real total | Synthetic total | Difference |
|---|---|---|---|
| 2015 | 1,030 | 1,034 | +0.4% |
| 2016 | 1,006 | 1,023 | +1.7% |
| 2017 | 962 | 918 | -4.6% |
| 2018 | 840 | 820 | -2.4% |
| 2019 | 895 | 706 | -21.1% |
| 2020 | 626 | 557 | -11.0% |
| 2021 | 542 | 590 | +8.9% |
| 2022 | 553 | 612 | +10.7% |

2015-2018 matches closely (within 5%), confirming the generator's 1,028/838
calibration anchors are accurate against the real 1,030/840 figures. 2019
onward diverges more (up to 21%), for a specific, identifiable reason below.

**Quarterly shape, 2019Q1-2022Q4 (MSM, mapped category, both sources):**

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

Full 16-quarter comparison gives a correlation of r=0.57 for MSM, against
r=0.16 for Heterosexual and r=0.30 for Other, both of which are small,
noise-dominated categories in both sources, so low correlation there is
expected rather than a concern.

**The MSM timing finding.** Real MSM notifications stay essentially flat
through all of 2019 (140-152 a quarter) and only drop sharply from 2020
onward, the same year as COVID. The synthetic series' PrEP effect instead
ramps immediately from 2018Q2, so it is already declining through 2019
(91-115) before the real data shows any comparable drop. This is why the
annual comparison above tracks well through 2018 and diverges from 2019: in
the real data, the post-listing MSM decline and the COVID
testing-disruption dip land in the same narrow window and are hard to
separate, while the synthetic design deliberately keeps them as two
distinct, separately-timed components. That is a known, deliberate
simplification, not a defect: the project's synthetic data exists so each
causal method can be validated against a clean, known effect, and a clean
effect requires a clean, separable signal. It is still worth recording here
as a real limit on how far the synthetic series' quarterly timing can be
read as representative of the real world's, beyond its annual totals and
overall direction.

### Exposure category handling

The real data carries more exposure categories than the synthetic data's
three. The Kirby quarterly report's underlying table reports six:
Male-to-male sex, Male-to-male sex and injecting drug use, Heterosexual
sex, Injection drug use, Other exposure, and Vertical transmission. The
comparison above used this mapping onto the synthetic data's three
categories:

- **MSM**: Male-to-male sex + Male-to-male sex and injecting drug use.
- **Heterosexual**: Heterosexual sex.
- **Other**: Injection drug use + Other exposure + Vertical transmission.

This mapping is judged acceptable for this project's purposes. Male-to-male
sex and injecting drug use is folded into MSM rather than Other because it
is still a male-to-male-sex exposure, the relevant criterion for Stage 2's
identification argument (PrEP eligibility and uptake, not injecting drug
use specifically, is what separates the treated and comparison groups).
Injection drug use, Other exposure, and Vertical transmission are all small
categories (each under 10% of the national total in every year checked
above) not materially treated by PrEP, consistent with Stage 2's comparison
group definition, so bucketing them together as "Other" does not
meaningfully change what that comparison group represents.

## References

1. Grulich AE, Jin F, Bavinton BR, et al (EPIC-NSW research group). Long-term
   protection from HIV infection with oral HIV pre-exposure prophylaxis in
   gay and bisexual men: findings from the expanded and extended EPIC-NSW
   prospective implementation study. *The Lancet HIV*. 2021. DOI:
   [10.1016/S2352-3018(21)00074-6](https://doi.org/10.1016/S2352-3018(21)00074-6).
