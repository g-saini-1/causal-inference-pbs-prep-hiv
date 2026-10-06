# Stage 1: Interrupted time series on PrEP dispensing

Sanity-check step in the project's four-stage causal design: using interrupted time
series as the identification strategy (see `docs/scope_and_rationale.md`), does PBS
PrEP dispensing show the level shift the project's causal argument depends on?

**NSW excluded.** Its EPIC-NSW trial ramp predates and dominates the national
pre-trend (see `reports/pbs_prep_dispensing_data_exploration.md` for why); this
report tests the rest-of-country aggregate instead.

## Data exploration

![PBS PrEP dispensing counts by state and nationally, January 2016 to December 2022](figures/pbs_prep_dispensing_chart.png)

Three patterns in the raw series, set out in full in
`reports/pbs_prep_dispensing_data_exploration.md`, motivate this specification
directly: post-listing growth is not a straight line, there is a clear COVID-19 dip
in 2020 followed by a full recovery, and NSW's EPIC-NSW early access dominates the
national pre-trend before the listing even happens. The early ramp and long-run
growth terms, the COVID decline-and-recovery terms, and rest-of-country aggregation
in Model specification below address each of these in turn.

## Model specification

Stage 1's initial specification (preserved in
`reports/stage1_initial_specification_diagnostics.md`) modelled the trajectory
as two segments, a pre-listing trend and a single post-listing trend, a 4-term
linear specification. Its own diagnostics showed this led to mixed,
inconclusive results, because the trajectory actually has more structure than
two segments can represent: the post-listing transition plays out over several
months rather than in one step, the 2020 COVID disruption has no term at all,
and NSW's EPIC-NSW ramp dominates the national pre-trend (see
`reports/pbs_prep_dispensing_data_exploration.md`).

**NSW excluded throughout** (see Table 1 below). This revised specification
models the trajectory as five segments instead of two, a 7-term linear
specification:

1. **Pre-listing trend** (January 2016 to March 2018): the baseline trend before the listing.
2. **Early ramp** (April 2018 to October 2018): a level shift at the listing
   date, then a steep slope while dispensing climbs to its new level.
3. **Long-run growth** (November 2018 to February 2020): the shallower slope
   dispensing settles into once the ramp is complete.
4. **COVID decline** (March 2020 to June 2020): a sharp fall to the observed
   trough, layered on top of the ongoing long-run growth.
5. **COVID recovery** (June 2020 to October 2021): the climb back, also layered
   on top of the ongoing long-run growth; growth continues at the long-run
   rate once the window ends.

Its linear predictor is:

```
η[t] = β0 + β1 * t + β2 * post_listing[t] + β3 * months_since_post_listing[t]
     + β4 * early_ramp[t] + β5 * covid_decline[t] + β6 * covid_recovery[t]
```

where:
- `η[t]`: the linear predictor for month t; how it maps to the actual predicted
  dispensing count depends on which family's link function is used.
- `t`: a running month index, 0, 1, 2, ..., 83 (January 2016 = 0).
- `post_listing[t]`: 1 if month t falls on or after April 2018, 0 otherwise.
- `months_since_post_listing[t]`: `post_listing[t] * (t - t at the first post-listing month)`,
  so it counts 0, 1, 2, ... after listing and stays at 0 throughout the pre-period.
- `early_ramp[t]`: `months_since_post_listing[t]` capped at 6, chosen because
  dispensing visibly settles into its new plateau by around then (see Data
  exploration above); it keeps rising for the first 6 months after listing, then
  holds constant, giving that early transition its own, steeper slope.
- `months_since_covid_start[t]`: zero outside the COVID window (March 2020 to
  October 2021); inside it, counts 0, 1, 2, ... from the window's start.
- `covid_decline[t]`: `months_since_covid_start[t]` capped at 3, the point
  dispensing bottoms out in the rest-of-country series (June 2020, see Data
  exploration above); it rises for the first 3 months of the window, then holds
  constant for the rest of it.
- `covid_recovery[t]`: zero until that same month, then counts the months
  elapsed since it, capturing the climb back over the remainder of the window.

Coefficients:

- `β0`: fitted level at the start of the series (January 2016).
- `β1`: pre-existing linear trend: the change in dispensing per month before the listing.
- `β2`: level shift measured exactly at the listing date (April 2018).
- `β3`: the long-run linear trend dispensing settles into once the ramp is complete.
- `β4`: the extra slope during the ramp, on top of β3, while dispensing is still
  settling into its new level.
- `β5`: the decline's slope, the fall in dispensing over the three months
  leading up to the observed trough.
- `β6`: the recovery's slope, the climb back over the rest of the COVID window.

**Table 1.** Causal concepts mapped to this design's specification.

| Causal concept | What it is in this design |
|---|---|
| Treatment | The 1 April 2018 PBS listing |
| Treated unit | The rest-of-country dispensing series (NSW excluded, see above) |
| Comparison group | Not used in this design; ITS relies on the treated unit's own extrapolated pre-trend instead. Stage 2 uses one |
| Counterfactual | The pre-listing trend extrapolated forward: what dispensing would have been without the listing |
| Treatment effect | The gap between observed post-listing dispensing and the counterfactual: phased in via β2 and β4 over the ramp, then growing at the shallower β3 rate once settled; narrowed sharply by the COVID decline (β5) and partly closed again by the recovery (β6) |
| Estimand | The steady-state level shift, `β2 + 6 * β4`: the gap between the counterfactual and the level dispensing settles at once the post-listing transition is complete |

![Segmented regression: full model specification](figures/pbs_prep_its_specification_chart.png)

Each coefficient corresponds to a distinct visual feature of the segmented
regression: `β0` is where the pre-listing line meets t=0; `β1` is that line's
slope, near zero here, since the rest-of-country series is essentially flat
before the listing; `β2` is the vertical jump at the listing date. The
post-listing line then has two distinct slopes either side of the "ramp ends"
marker: `β4` is the steeper slope during the early ramp, and `β3` is the
shallower slope dispensing settles into once the ramp is complete. The grey
dotted line is the counterfactual from Table 1, the pre-listing trend extended
forward as if the listing had not happened; the shaded gap between it and the
post-listing line is the treatment effect. The solid fitted line layers in the
remaining controls, dropping sharply to the observed trough (`β5`) before
climbing back through the rest of the shaded COVID-19 window (`β6`).

**The estimand: the steady-state level shift.** The identification strategy
(interrupted time series) argues that a comparison of dispensing before and
after the listing supports a causal claim, provided nothing else plausibly
changed over that period (see the "Threat to identification" for this stage in
`docs/scope_and_rationale.md`). An estimand is the specific causal quantity
such a comparison is meant to recover, defined independently of which
coefficients or statistical family eventually estimate it.

Because dispensing climbs over several months before settling, rather than
jumping in one step (see Data exploration above), that quantity cannot be read
off `post_listing` alone: a discrete term at the listing date only captures
whichever fraction of the transition happens to land exactly on that month.
The estimand here is the steady-state level shift, the gap between the
counterfactual and the level dispensing settles at once the post-listing
transition is complete: `β2 + 6 * β4`. `β2` alone still has a reading, the
level shift measured exactly at the listing date, but it is not the estimand;
the steady-state level shift is, and it is what the empirical comparison in
Model family selection is run on.

## Model family selection

The Decision checklist in `docs/model_family_concepts.md` identifies Poisson and NB
as the plausible candidates for a non-negative count outcome; OLS is included
alongside them as a baseline, not because the checklist selects it. Family selection
on this revised specification is pending; see Model specification above for why the
initial specification's comparison was inconclusive rather than decided.
