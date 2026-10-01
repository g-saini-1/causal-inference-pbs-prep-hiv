# Did subsidising HIV prevention medication reduce diagnoses? A causal inference case study using synthetic data

**Methods & tools:** Python, pandas, statsmodels, synthetic data validation. *Implemented:* interrupted time series (OLS, Poisson, Negative Binomial). *Planned:* difference-in-differences, staggered-adoption analysis, causal forest heterogeneity analysis (EconML).

## Status

Portfolio project in progress: the data and reproducibility foundation are done, Stage 1 is nearly finalised, and Stages 2-4 (the actual causal claim) are still ahead.

| Status | Stage / activity | Key outcomes | Details |
|---|---|---|---|
| Complete | Data generation & QA | Synthetic PBS/HIV data built with a known, built-in ground truth; two QA issues found and fixed | [`reports/data_acquisition.md`](reports/data_acquisition.md) |
| In progress | Stage 1: Interrupted time series | Confirmed an unambiguous level shift in PrEP dispensing at the April 2018 listing; ran the full OLS/Poisson/NB comparison and traced its mixed signals to a shared specification gap, now the basis for refining the model | [`reports/stage1_interrupted_time_series.md`](reports/stage1_interrupted_time_series.md) |
| Not started | Stage 2: Difference-in-differences | Will compare MSM vs. other transmission categories to isolate the policy effect | [`docs/scope_and_rationale.md`](docs/scope_and_rationale.md) |
| Not started | Stage 3: Staggered-adoption analysis | Will use NSW's earlier EPIC-NSW trial as a staggered-treatment design | [`docs/scope_and_rationale.md`](docs/scope_and_rationale.md) |
| Not started | Stage 4 (optional): Causal forest heterogeneity | Will examine state-level heterogeneity in treatment effects | [`docs/scope_and_rationale.md`](docs/scope_and_rationale.md) |

## What this demonstrates

National PrEP dispensing jumps unmistakably at the April 2018 PBS listing, from under 750 a month to roughly 5,500 within six months, with a visible COVID-19 dip and recovery along the way.

![PBS PrEP dispensing counts by state and nationally, January 2016 to December 2022](reports/figures/pbs_prep_dispensing_chart.png)

Beyond fitting models, this project applies the reasoning causal inference requires: choosing an identification strategy and being explicit about what would threaten it, selecting a statistical model family with evidence, and documenting where the real data had genuine gaps and adjusting the design around them. Stage 1's causal design, shown below, ties the regression coefficients directly to the underlying causal concepts: treatment, counterfactual, treatment effect.

![Segmented regression: coefficients and causal concepts, both shown geometrically](reports/figures/pbs_prep_its_specification_chart.png)

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
| [`reports/data_acquisition.md`](reports/data_acquisition.md) | Data acquisition attempts, why synthetic data was used, and QA |
| [`reports/pbs_prep_dispensing_data_exploration.md`](reports/pbs_prep_dispensing_data_exploration.md) | Raw dispensing patterns and the NSW pre-trend, shared dataset-level evidence behind Stages 1 and 3 |
| [`reports/stage1_interrupted_time_series.md`](reports/stage1_interrupted_time_series.md) | Stage 1 model specification, model family selection, and charts |
| [`src/`](src/) | Synthetic data generator and analysis-stage scripts |

## Getting started

```bash
pip install -r requirements.txt
python src/generate.py                      # regenerate the synthetic data
python src/analysis/01_interrupted_time_series.py
```

## License

[MIT](LICENSE)
