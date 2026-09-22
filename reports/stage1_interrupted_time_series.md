# Stage 1: Interrupted time series on PrEP dispensing

Sanity-check step in the four-stage design: does national PBS PrEP dispensing show
the level shift the project's causal argument depends on, and is a simple national
break test even valid here?

## Model specification

Stage 1 fits a segmented (piecewise-linear) regression, the standard design for an
interrupted time series:

```
dispensing[t] = β0 + β1 * t + β2 * post_listing[t] + β3 * months_since_post_listing[t] + ε[t]
```

where:
- `dispensing[t]`: national PrEP dispensing count in month t.
- `t`: a running month index, 0, 1, 2, ..., 83 (January 2016 = 0).
- `post_listing[t]`: 1 if month t falls on or after April 2018, 0 otherwise.
- `months_since_post_listing[t]`: `post_listing[t] * (t - t at the first post-listing month)`,
  so it counts 0, 1, 2, ... after listing and stays at 0 throughout the pre-period.
- `ε[t]`: the error term

Coefficients:

- `β0`: fitted dispensing level at the start of the series (January 2016).
- `β1`: pre-existing linear trend: the change in dispensing per month before the listing.
- `β2`: level shift: the immediate jump in dispensing at treatment (April 2018)
- `β3`: change in slope after treatment, so the post-period trend equals β1 + β3.

## Model fitting

The coefficients are estimated by ordinary least squares
(`smf.ols(...).fit()` in
[`src/analysis/01_interrupted_time_series.py`](../src/analysis/01_interrupted_time_series.py)),
minimising the sum of squared residuals. Standard errors use the classical
(nonrobust) formula, and each p-value comes from comparing the coefficient's
t-statistic against a t-distribution with 80 degrees of freedom (84 months minus 4
parameters). Note that this assumes independent errors; the regression's own
Durbin-Watson statistic (0.255) indicates strong positive autocorrelation in monthly
residuals, so these p-values are likely optimistic and would tighten under
autocorrelation-robust (HAC) standard errors.

## Regression results

| Term | Coefficient | Std. error | p-value |
|---|---|---|---|
| Intercept (β0) | -7.2 | 317.4 | 0.982 |
| Pre-period trend (β1, per month) | 32.1 | 20.9 | 0.130 |
| **Level shift at listing (β2)** | **2,877.9** | 402.1 | **< 0.001** |
| Post-period trend change (β3, per month) | 25.8 | 22.0 | 0.244 |

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
  extended lockdowns.
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
