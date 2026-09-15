# Stage 1 results: interrupted time series on PrEP dispensing

Sanity-check step in the four-stage design: does national PBS PrEP dispensing show
the level shift the project's causal argument depends on, and is a naive national
break test even valid here? See
[`docs/scope_and_rationale.md`](../docs/scope_and_rationale.md#causal-question-and-design)
for the full design rationale and how this stage fits the other three.

## Regression results

A segmented (piecewise-linear) regression of national monthly dispensing around the
1 April 2018 listing date, produced by
[`src/analysis/01_interrupted_time_series.py`](../src/analysis/01_interrupted_time_series.py):

| Term | Coefficient | Std. error | p-value |
|---|---|---|---|
| Intercept | -7.2 | 317.4 | 0.982 |
| Pre-period trend (per month) | 32.1 | 20.9 | 0.130 |
| **Level shift at listing** | **2,877.9** | 402.1 | **< 0.001** |
| Post-period trend change (per month) | 25.8 | 22.0 | 0.244 |

N = 84 months, R² = 0.897. The level shift at the listing date is large and highly
significant: national dispensing jumps by around 2,878 a month at April 2018, holding
the pre-existing trend constant. The pre- and post-period trend terms are not
significant on their own, consistent with the shift being a genuine step change
rather than a gradual acceleration.

## Visual check: does the dispensing data show the expected level shift?

![PBS PrEP dispensing counts by state and nationally, January 2016 to December 2022](figures/pbs_prep_dispensing_chart.png)

Before trusting the regression, it's worth just looking at the raw dispensing series:
does the data actually show the large, obvious level shift the project's causal
argument depends on? It does. National dispensing sits below 750 a month through
2016-17, then rises roughly eightfold in the first six months after the April 2018
listing, settling around 5,500-6,000 a month by 2019. Two further patterns are visible
without any modelling:

- **A clear COVID-19 dip.** National dispensing falls from ~5,900 to ~3,800 a month
  during 2020, with the slowest recovery in Victoria, consistent with that state's
  extended lockdowns, and a useful secondary natural experiment also discussed in
  [`docs/scope_and_rationale.md`](../docs/scope_and_rationale.md).
- **NSW is already elevated before the national listing.** Its line separates from
  the other states well before April 2018, which is the first visual hint that the
  "before" period isn't as flat as a simple before/after comparison would assume,
  addressed below.

## NSW pre-trend and the case for Stage 3

![PBS PrEP dispensing, EPIC-NSW trial to PBS listing, January 2016 to April 2018](figures/pbs_epic_nsw_zoom_chart.png)

The chart above zooms into January 2016 to April 2018, on a y-axis scaled to the
pre-listing range rather than the full national scale (where these numbers would be
flattened near zero). Two things stand out:

- **NSW's rise is not a fluke of the generator. It is the intended EPIC-NSW signal.**
  Dispensing climbs steadily from 0 to roughly 670-730 a month over two years,
  entirely before the national PBS listing, while every other state stays at
  essentially zero across the same period.
- **This is exactly why Stage 1's naive interrupted time series needs a caveat, and
  why Stage 3 exists.** A single national break test at April 2018 would attribute
  some of NSW's already-established upward trend to the listing itself. Treating NSW
  as an earlier-treated unit (from 2016) and the rest of the country as later-treated
  (from 2018), a staggered-adoption design, is the more defensible way to use this
  same data, and this chart is the clearest single piece of evidence for why.
