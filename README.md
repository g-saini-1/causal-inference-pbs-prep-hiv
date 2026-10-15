# Did subsidising HIV prevention medication reduce diagnoses?
*A causal inference case study using synthetic data*

Full causal design and rationale: [`docs/scope_and_rationale.md`](docs/scope_and_rationale.md).

## PBS PrEP dispensing, 2016-2022

National PrEP dispensing rises sharply after the April 2018 PBS listing, climbing from about 2,100 in that first month to over 10,000 a month within a year, with a clear COVID-19 dip in 2020 and a partial, noisy recovery afterward. NSW is the exception: its EPIC-NSW trial gave it early access from 2016, so the analysis below tests the rest of the country separately.

![PBS PrEP dispensing counts by state and nationally, January 2016 to October 2022](reports/figures/pbs_prep_dispensing_chart.png)

## Did dispensing itself change sharply at the moment of the PBS listing?

The PBS listing is a natural experiment: interrupted time series compares dispensing immediately before and after it, with the pre-listing trend standing in for the counterfactual, what dispensing would have done without the listing. Since that pre-listing trend is essentially flat, the post-listing rise cannot be explained as a trend that was already underway.

![Segmented regression: full model specification](reports/figures/pbs_prep_its_specification_chart.png)

OLS provides the headline estimate, the only family that can use the data's verified zero pre-listing period directly: dispensing settles at roughly 9,452 more a month than the counterfactual once a 17-month, data-derived ramp completes. The discrete jump at the listing date is itself highly significant (p < 0.001), and the fuller picture, a sustained climb over the following year and a half, makes the case stronger still. This matters beyond what's visually obvious in the raw dispensing data above: it quantifies the effect with uncertainty, and it surfaces structure invisible by eye, a 17-month ramp rather than an instant step, and a long-run trend distinct from the COVID dip.


## Status

In progress: Stage 1 below is complete; Stages 2-4, the actual causal claim, are still ahead.

### Data readiness

| Dataset | Acquisition | Validation | Exploration |
|---|---|---|---|
| PBS dispensing | Complete | Complete | Complete |
| HIV notifications | In progress | In progress | In progress |
| State covariates | Not started | Not started | — |

Reports: [reports/data_acquisition.md](reports/data_acquisition.md),
[reports/data_validation.md](reports/data_validation.md),
[reports/data_exploration_pbs_prep_dispensing.md](reports/data_exploration_pbs_prep_dispensing.md),
[reports/data_exploration_hiv_notifications.md](reports/data_exploration_hiv_notifications.md).

### Causal stages

| Stage | Status | Depends on | Report |
|---|---|---|---|
| Stage 1: Interrupted time series | Complete | PBS dispensing data (see Data readiness above) | [reports/stage1_interrupted_time_series.md](reports/stage1_interrupted_time_series.md) |
| Stage 2: Difference-in-differences | Not started | HIV notifications data (see Data readiness above) | [reports/stage2_workflow.md](reports/stage2_workflow.md), [reports/stage2_diff_in_diff.md](reports/stage2_diff_in_diff.md) |
| Stage 3: Staggered-adoption analysis | Not started | HIV notifications data (see Data readiness above) | [reports/stage3_workflow.md](reports/stage3_workflow.md) |
| Stage 4 (optional): Causal forest heterogeneity | Not started | HIV notifications data, state covariates data (see Data readiness above) | [docs/scope_and_rationale.md](docs/scope_and_rationale.md) |

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

## Acknowledgments

Built with assistance from Claude (Anthropic), under the author's direction
and review.

## License

[MIT](LICENSE)
