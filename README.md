# Did subsidising HIV prevention medication reduce diagnoses? A causal inference case study using synthetic data

**Methods & tools:** Python, pandas, statsmodels, synthetic data validation. *Implemented:* interrupted time series (OLS, Poisson, Negative Binomial). *Planned:* difference-in-differences, staggered-adoption analysis, causal forest heterogeneity analysis (EconML).

## Status

Portfolio project in progress: the data and reproducibility foundation are done, Stage 1 is complete, and Stages 2-4 (the actual causal claim) are still ahead.

| Status | Stage / activity | Key outcomes | Details |
|---|---|---|---|
| Complete | Data generation & QA | Synthetic PBS/HIV data built with a known, built-in ground truth; two QA issues found and fixed | [`reports/data_acquisition.md`](reports/data_acquisition.md) |
| Complete | Data exploration | Confirmed the expected level shift visually; identified NSW's early EPIC-NSW ramp, motivating Stage 3's design | [`reports/pbs_prep_dispensing_data_exploration.md`](reports/pbs_prep_dispensing_data_exploration.md) |
| Complete | Stage 1: Interrupted time series | Found the national aggregate's pre-listing trend was dominated by NSW's EPIC-NSW ramp; refitted on the rest-of-country aggregate with a five-segment specification (ramp, long-run growth, COVID decline and recovery); selected Negative Binomial with evidence and concluded dispensing rose to a precisely-estimated, durably higher level (~3,934 a month) within six months of the listing, not instantly | [`reports/stage1_interrupted_time_series.md`](reports/stage1_interrupted_time_series.md) |
| Not started | Stage 2: Difference-in-differences | Will compare MSM vs. other transmission categories to isolate the policy effect | [`docs/scope_and_rationale.md`](docs/scope_and_rationale.md) |
| Not started | Stage 3: Staggered-adoption analysis | Will use NSW's earlier EPIC-NSW trial as a staggered-treatment design | [`docs/scope_and_rationale.md`](docs/scope_and_rationale.md) |
| Not started | Stage 4 (optional): Causal forest heterogeneity | Will examine state-level heterogeneity in treatment effects | [`docs/scope_and_rationale.md`](docs/scope_and_rationale.md) |

## What this demonstrates

National PrEP dispensing ramps up to a new steady state over the six months following the April 2018 PBS listing, from under 750 a month to roughly 5,500, not an instant jump, with a clear COVID-19 dip and full recovery along the way.

![PBS PrEP dispensing counts by state and nationally, January 2016 to December 2022](reports/figures/pbs_prep_dispensing_chart.png)

Beyond fitting models, this project applies the reasoning causal inference requires: choosing an identification strategy and being explicit about what would threaten it, selecting a statistical model family with evidence, and documenting where the real data had genuine gaps and adjusting the design around them. Stage 1's causal design, shown below, ties the regression coefficients directly to the underlying causal concepts: treatment, counterfactual, treatment effect.

![Segmented regression: full model specification](reports/figures/pbs_prep_its_specification_chart.png)

Family selection confirmed Negative Binomial as the best-supported model (evidence: AIC, residual diagnostics), and the resulting estimate is precise: dispensing settles at roughly 3,934 more a month than the counterfactual once the ramp completes. That answers Stage 1's question affirmatively, even though the change unfolds over six months rather than instantly.

See [Methodology tooling](#methodology-tooling) below for the reusable frameworks this produced.

## Approach

This project uses PBS-subsidised PrEP as a natural experiment to test whether the policy caused a measurable reduction in new HIV diagnoses, using four causal methods of increasing rigour: interrupted time series, difference-in-differences, staggered-adoption analysis, and (optionally) causal forest heterogeneity analysis. Stages 1 and 2 are fit using the generalized linear model (GLM) class; see [`docs/model_family_concepts.md`](docs/model_family_concepts.md) for how the specific family (e.g. OLS vs. Poisson vs. Negative Binomial) is chosen with evidence. The full causal design and rationale are in [`docs/scope_and_rationale.md`](docs/scope_and_rationale.md).

The analysis runs on synthetic data with known, built-in effects rather than the real PBS/NNDSS extracts; why, and how that data was validated, is covered in [`reports/data_acquisition.md`](reports/data_acquisition.md).

## Methodology tooling

Beyond running the causal experiments, this project identified a need for reusable tooling to support consistent, evidence-based decisions, and built two references:

- [`docs/model_family_concepts.md`](docs/model_family_concepts.md): a framework for choosing a regression family (OLS, Poisson, Negative Binomial, and beyond) using evidence, e.g. AIC, residual diagnostics.
- [`docs/causal_method_workflow_template.md`](docs/causal_method_workflow_template.md): a tracker for applying the same nine-step workflow consistently across all four stages, from framing the question to interpreting the result.

## Repository layout

| Path | Contents |
|---|---|
| [`data/`](data/) | Synthetic (analysis-ready) and raw (real-world) data files; see [`data/data_dictionary.md`](data/data_dictionary.md) for column definitions |
| [`docs/causal_method_workflow_template.md`](docs/causal_method_workflow_template.md) | Reusable per-stage workflow tracker; see [Methodology tooling](#methodology-tooling) |
| [`docs/model_family_concepts.md`](docs/model_family_concepts.md) | Framework for choosing a regression family; see [Methodology tooling](#methodology-tooling) |
| [`docs/scope_and_rationale.md`](docs/scope_and_rationale.md) | Upfront selection rationale, causal design, and data provenance |
| [`notebooks/`](notebooks/) | Reproducible, top-to-bottom walkthrough of the whole analysis |
| [`reports/`](reports/) | Per-stage results and write-ups; see Status above for each stage's current report |
| [`src/`](src/) | Synthetic data generator and analysis-stage scripts |
| [`tests/`](tests/) | Automated tests for the analysis scripts |

## Getting started

```bash
pip install -r requirements.txt
python src/generate.py                      # regenerate the synthetic data
python src/analysis/01_interrupted_time_series.py
python -m src.utils.distribution_shapes     # regenerate the illustrative distribution-shapes chart
python -m pytest tests/                     # run the test suite
```

## License

[MIT](LICENSE)
