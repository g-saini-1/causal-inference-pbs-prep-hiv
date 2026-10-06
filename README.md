# Did subsidising HIV prevention medication reduce diagnoses?
*A causal inference case study using synthetic data*

Full causal design and rationale: [`docs/scope_and_rationale.md`](docs/scope_and_rationale.md).

## PBS PrEP dispensing, 2016-2022

National PrEP dispensing rises sharply after the April 2018 PBS listing, from under 750 a month to roughly 5,500 within about six months, with a clear COVID-19 dip and recovery along the way. NSW is the exception: its EPIC-NSW trial gave it early access from 2016, so the analysis below tests the rest of the country separately.

![PBS PrEP dispensing counts by state and nationally, January 2016 to December 2022](reports/figures/pbs_prep_dispensing_chart.png)

## Did dispensing itself change sharply at the moment of the PBS listing?

The PBS listing is a natural experiment: interrupted time series tests this directly, comparing dispensing before and after it. Since the pre-listing trend is essentially flat, the post-listing rise cannot be explained as a trend that was already underway.

![Segmented regression: full model specification](reports/figures/pbs_prep_its_specification_chart.png)

Negative Binomial was selected with evidence, producing a precise estimate: dispensing settles at roughly 3,934 more a month than the counterfactual once the six-month ramp completes. The discrete jump at the listing date alone isn't statistically significant, but interrupted time series doesn't need an instant jump, just a change large and well-timed enough to rule out coincidence, and by that standard the answer is affirmative.

See [Methodology tooling](#methodology-tooling) below for the reusable frameworks this produced.

## Status

In progress: Stage 1 below is complete; Stages 2-4, the actual causal claim, are still ahead.

| Status | Stage / activity | Details |
|---|---|---|
| Complete | Data generation & QA | [Report](reports/data_acquisition.md): Synthetic PBS/HIV data with known ground truth, two QA issues found and fixed |
| Complete | Data exploration | [Report](reports/pbs_prep_dispensing_data_exploration.md): NSW's early EPIC-NSW access dominates the national pre-trend |
| Complete | Stage 1: Interrupted time series | [Report](reports/stage1_interrupted_time_series.md) |
| Not started | Stage 2: Difference-in-differences | [Scope](docs/scope_and_rationale.md): will compare MSM vs. other transmission categories to isolate the policy effect |
| Not started | Stage 3: Staggered-adoption analysis | [Scope](docs/scope_and_rationale.md): will use NSW's earlier EPIC-NSW trial as a staggered-treatment design |
| Not started | Stage 4 (optional): Causal forest heterogeneity | [Scope](docs/scope_and_rationale.md): will examine state-level heterogeneity in treatment effects |

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
