# Stage 2: Difference-in-differences on HIV notifications

Second step in the project's four-stage causal design: using
difference-in-differences as the identification strategy, did the population PrEP targets see a larger
drop in HIV notifications than other groups, beyond a trend they share?

*Pending.* `src/analysis/02_diff_in_diff.py` is currently a TODO stub; this
report fills in as that work happens, in step with
`reports/stage2_workflow.md`.

## Data exploration

See `reports/hiv_notifications_data_exploration.md` for the full write-up.
MSM notifications fall 44% (unconditional, before/after April 2018, all
states) against 19% for the Heterosexual/Other comparison group, the raw
signal this stage's model formalises. But the national MSM series is also
declining well before April 2018, an NSW/EPIC-NSW pre-trend rather than a
PBS-listing effect, the same issue Stage 1 found in dispensing. **NSW is
excluded from Stage 2** as a result, the same resolution Stage 1 used;
recomputed on the rest-of-country population, the gap is 42% vs. 20%, close
to the all-states figures.

## Model specification

*Pending.* Planned starting point, from the script's docstring: a two-way
fixed effects model, fit on the rest-of-country data (NSW excluded, per Data
exploration above),

```
hiv_notifications ~ is_msm * post_pbs_listing + C(state) + C(quarter)
```

with the `is_msm:post_pbs_listing` interaction as the DiD estimate, robust
or state-clustered standard errors, and a trend chart (MSM vs. the
comparison group around the April 2018 listing) saved to
`reports/figures/diff_in_diff_trends.png`.

## Model family selection

*Pending.*

## Conclusion

*Pending.*
