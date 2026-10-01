# PBS PrEP dispensing: data exploration

A direct look at the national and state-level PrEP dispensing series, ahead of any
modelling. This is dataset-level evidence shared across stages, not specific to one
identification strategy: Stage 1 (`reports/stage1_interrupted_time_series.md`) relies
on the national-level patterns below, and Stage 3's staggered-adoption design relies
directly on the NSW pre-trend. See `docs/scope_and_rationale.md` for the full
four-stage causal design.

## National and state-level dispensing patterns

![PBS PrEP dispensing counts by state and nationally, January 2016 to December 2022](figures/pbs_prep_dispensing_chart.png)

Does the data actually show the large, obvious level shift the project's causal
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

Figure 2 zooms into January 2016 to April 2018, on a y-axis scaled to the
pre-listing range rather than the full national scale (where these numbers would be
flattened near zero). Two things stand out:

- **NSW's rise is not a fluke of the generator. It is the intended EPIC-NSW signal.**
  Dispensing climbs steadily from 0 to roughly 670-730 a month over two years,
  entirely before the national PBS listing, while every other state stays at
  essentially zero across the same period.
- **This is exactly why a single national break test needs a caveat, and why Stage 3
  exists.** A single national break test at April 2018 would attribute some of NSW's
  already-established upward trend to the listing itself. Treating NSW as an
  earlier-treated unit (from 2016) and the rest of the country as later-treated
  (from 2018), a staggered-adoption design, is the more defensible way to use this
  same data, and Figure 2 is the clearest single piece of evidence for why.
