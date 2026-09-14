# PBS PrEP → HIV Notifications: Synthetic Panel Data

**This is fake data**, generated with `numpy`/`pandas` (seed=42) to have the same
structure and rough shape as the real story in `project-scope.md`. It exists so
you can build and test the whole analysis pipeline — segmented regression,
DiD, staggered-adoption DiD, causal forest — before swapping in the real pulls
from data.gov.au (PBS Item Reports, NNDSS) and the Kirby Institute reports.

## Files

### 1. `prep_dispensing_panel.csv` — the "first stage"
One row per state × quarter, 2013Q1–2022Q4.

| column | meaning |
|---|---|
| `state` | one of NSW, VIC, QLD, WA, SA, TAS, ACT, NT |
| `year`, `quarter`, `period`, `date` | time identifiers |
| `prep_dispensing_count` | synthetic PBS-derived PrEP dispensing count for that state-quarter |

Built-in patterns: near-zero everywhere before 2016; a NSW-only ramp from
2016Q1 (EPIC-NSW trial, plateauing ~8–9k); a sharp national jump at 2018Q2
(PBS listing) in every state; a COVID-19 dip 2020Q2–2021Q4, worst in VIC.

### 2. `hiv_notifications_panel.csv` — the "second stage"
One row per state × exposure category × quarter.

| column | meaning |
|---|---|
| `state` | as above |
| `exposure_category` | MSM, Heterosexual, Other |
| `hiv_notifications` | synthetic HIV notification count |

Built-in patterns: a slow secular decline in all groups (testing/awareness);
an *extra* decline in MSM notifications only, timed to EPIC-NSW (NSW, from
2016) and the PBS listing (all states, from 2018Q2, smaller incremental
effect in NSW since it was already partly treated); a partial stall in the
MSM decline during COVID, worst in VIC. Heterosexual/Other notifications get
no treatment effect — they're your control group.

### 3. `analysis_panel.csv` — merged, analysis-ready
One row per state × exposure category × quarter (960 rows). Combines both
panels above plus:

| column | meaning |
|---|---|
| `period_index` | 0-based quarter counter, useful for segmented regression |
| `post_pbs_listing` | 1 from 2018Q2 onward |
| `post_epic_nsw` | 1 for NSW from 2016Q1 onward, else 0 |
| `covid_period` | 1 for 2020Q2–2021Q4 |
| `is_msm` | 1 if `exposure_category == "MSM"` |
| `msm_x_post_pbs` | DiD interaction term (`is_msm * post_pbs_listing`) |
| `population_share`, `msm_population_weight` | illustrative state weights |
| `baseline_testing_rate_per_100k`, `seifa_irsad_index` | illustrative state covariates for the causal-forest heterogeneity step |

## Sanity check

National MSM notifications by year already echo the scope doc's reference
range (falling from the 2015 area toward the 2018 area and continuing down
post-listing) — check the printed table in `generate_panel.py`'s output, or
recompute with:

```python
import pandas as pd
d = pd.read_csv("hiv_notifications_panel.csv")
d[d.exposure_category == "MSM"].groupby("year")["hiv_notifications"].sum()
```

## Next step

Replace `prep_dispensing_panel.csv` and `hiv_notifications_panel.csv` with the
real pulls (PBS Item Reports / NNDSS from data.gov.au, Kirby Institute
Annual Surveillance Reports) and re-run the same merge/feature-engineering
logic in `generate_panel.py` (section 5) to reproduce `analysis_panel.csv`
on real data.
