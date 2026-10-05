# Stage 1: diagnostics on the initial specification

Full results of the Empirical comparison checklist (`docs/model_family_concepts.md`,
Section 6) run on Stage 1's initial specification, before any revisions. Preserved
as the diagnostic trail that identified the need for those revisions; see
`reports/stage1_interrupted_time_series.md` for Stage 1's current specification and
results.

## Model family selection

The Decision checklist in `docs/model_family_concepts.md` identifies Poisson and NB
as the plausible candidates for a non-negative count outcome; OLS is included
alongside them as a baseline, not because the checklist selects it. Choosing among
the three requires the Empirical comparison checklist (Section 6): fit all three
on the same specification and work through its four items in turn.

**Table 1.** Empirical comparison checklist results (Section 6), for all three
candidates fitted on Stage 1's initial specification
(`reports/stage1_interrupted_time_series.md`).

| Candidate | Coefficients (β2) | AIC | Assumption check | Autocorrelation check |
|---|---|---|---|---|
| OLS | +2,877.9 (additive) | 1,375.0 | Breusch-Pagan LM = 37.29, p < 0.001 | Durbin-Watson = 0.255 |
| Poisson | ×3.57 (multiplicative) | 17,602.3 | Pearson chi-squared / df = 178.92 | Durbin-Watson = 0.250 |
| NB | ×2.13 (multiplicative) | 1,387.2 | α = 0.1823, 95% CI [0.1228, 0.2419] | Durbin-Watson = 0.190 |

**1. Coefficients and their interpretation.** The coefficient values aren't directly comparable, since OLS's β2 is additive and Poisson's and NB's are multiplicative.

**2. AIC.**

1. **OLS**: rank 1 (1,375.0).
2. **Poisson**: rank 3 (17,602.3, 16,227.3 points higher than OLS,
   decisively ruled out).
3. **NB**: rank 2 (1,387.2, 12.2 points higher than OLS).

The OLS-NB gap exceeds the ~2-point threshold usually considered meaningful, so
this item ranks OLS ahead of NB, with Poisson decisively ruled out.

**3. An assumption check specific to each candidate.**

1. **OLS**: fail (Breusch-Pagan LM = 37.29, p < 0.001).
2. **Poisson**: fail (Pearson chi-squared / df = 178.92).
3. **NB**: pass (α = 0.1823, 95% CI [0.1228, 0.2419]).

OLS's residual variance depends on `t`, `post_listing`, and
`months_since_post_listing` rather than staying constant (Breusch-Pagan
p < 0.001, well below the conventional 0.05 threshold), contradicting its
own assumption.

Poisson's dispersion ratio of 178.92 is far above the 1.0 expected if
variance genuinely equalled the mean, contradicting its own assumption just
as decisively.

NB's own assumption, that the extra dispersion its `α` term captures is real
rather than zero, is confirmed: its 95% confidence interval, [0.1228, 0.2419],
excludes zero.

![OLS, Poisson, and NB: each family's own fitted shape for the same month](figures/pbs_prep_family_distribution_chart.png)

The three numbers above are what this chart draws out: in June 2019, OLS's
fixed spread (SD≈848) sits far narrower than NB's own (SD≈1,922), while
Poisson's (SD≈67) is narrower still, visibly too tight for the real scatter
in the data.

**4. Residual autocorrelation over time.**

1. **OLS**: fail (Durbin-Watson = 0.255).
2. **Poisson**: fail (Durbin-Watson = 0.250).
3. **NB**: fail (Durbin-Watson = 0.190).

All three sit far from the 2 that would indicate independent residuals, and
close to 0, strong positive autocorrelation. Since every candidate fails,
the issue lies outside family choice: no choice among OLS, Poisson, and NB
fixes it, it needs its own remedy rather than a different family.

![Residuals over time: the wave pattern behind the low Durbin-Watson values](figures/pbs_prep_residuals_over_time_chart.png)

Figure 2 shows why: residuals from all three candidates trace nearly the
same wave, an undershoot at the April 2018 listing, a swing above zero
through 2019, a deep dip through the 2020 COVID period, and a partial
recovery after, not random scatter.

![Autocorrelation function (ACF) of residuals, by candidate](figures/pbs_prep_residuals_acf_chart.png)

Figure 3 breaks that wave down by lag. OLS's residuals, the other two look
the same, stay positively correlated out to about lag 5-6 (lag 1 = +0.87),
then swing to significant negative correlation from around lag 8, bottoming
out near −0.46 around lag 17. Durbin-Watson only reflects lag 1, so it
can't tell short-lived noise apart from a long, structural pattern, and
this is the latter: a trough at the April 2018 listing, a peak about 7
months later (November 2018), and the COVID trough about 20 months after
that (July 2020) are exactly what the shift to negative correlation at
longer lags is picking up. That's independent evidence the autocorrelation
reflects specific omitted structure, not a short-memory noise process any
family choice could fix.

**Family selection: deferred.** AIC currently favours OLS, but OLS fails its
own homoscedasticity assumption; NB passes its own assumption but loses
decisively on AIC; and all three fail the autocorrelation check identically,
for the same underlying reason. With the dominant signal across all four
items pointing at omitted structure in the specification rather than a
genuine difference between the candidates, selecting a family on this
specification would be premature. The next step is fixing the specification,
a COVID-period term and the non-linear post-listing growth are the leading
candidates, and re-running this checklist on the revised specification.
