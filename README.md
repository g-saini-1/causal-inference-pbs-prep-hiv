# Did PBS-subsidised PrEP reduce new HIV diagnoses in Australia?

*A causal inference case study using Australian PrEP listing and HIV surveillance data*

## Status

**Where things stand:** Data generation and QA are complete against a known,
built-in effect. The interrupted time series sanity check (Stage 1) is in
progress and has so far confirmed an unambiguous shift in PrEP dispensing at
the April 2018 subsidy date. The core analysis, isolating the policy's
effect on HIV diagnoses, is next.

- [x] Data generation and QA: synthetic PBS/HIV data built with a known ground
  truth and validated before use (see
  [`reports/data_acquisition.md`](reports/data_acquisition.md))
- [ ] Interrupted time series *(Stage 1, in progress)*: confirms an unambiguous
  level shift in PrEP dispensing at the April 2018 subsidy date (results so far in
  [`reports/stage1_interrupted_time_series.md`](reports/stage1_interrupted_time_series.md))
- [ ] Difference-in-differences *(Stage 2)*: compares HIV diagnoses attributed to
  male-to-male sexual contact against other transmission categories to isolate the
  policy effect
- [ ] Staggered-adoption analysis *(Stage 3)*: exploits NSW's earlier EPIC-NSW
  trial (2016) as a natural staggered-treatment design
- [ ] Causal forest heterogeneity analysis *(Stage 4, optional)*: examines
  state-level heterogeneity in treatment effects

## Approach

This project uses PBS-subsidised PrEP as a natural experiment to test
whether the policy caused a measurable reduction in new HIV diagnoses,
using a full causal-inference workflow:

1. **Interrupted time series** on PrEP dispensing.
2. **Difference-in-differences** on HIV notifications.
3. **Staggered-adoption analysis** across states.
4. **Causal forest heterogeneity analysis** *(optional)*.

Real PBS/NNDSS data pulls were attempted first; two genuine data-availability
gaps (pre-2019 NNDSS quarterly granularity, and unresolved historical PBS
item codes) led to using **synthetic data with the same structure and known,
built-in effects** instead, so the workflow can be validated against a known
ground truth. The full design rationale is in
[`docs/scope_and_rationale.md`](docs/scope_and_rationale.md); what was tried
with real data, why it didn't work, and the QA performed on the synthetic
data are in
[`reports/data_acquisition.md`](reports/data_acquisition.md).

## Repository layout

| Path | Contents |
|---|---|
| [`data/synthetic/`](data/synthetic/) | The three analysis-ready synthetic CSVs (see [`data/data_dictionary.md`](data/data_dictionary.md)) |
| [`data/raw/`](data/raw/) | Real PBS/NNDSS/Kirby extracts pulled during the initial data-acquisition phase |
| [`src/generate.py`](src/generate.py) | Synthetic data generator (fixed seed, reproducible) |
| [`src/analysis/`](src/analysis/) | The four analysis stages |
| [`notebooks/exploratory_analysis.ipynb`](notebooks/exploratory_analysis.ipynb) | Reproducible, top-to-bottom walkthrough of the whole analysis |
| [`reports/data_acquisition.md`](reports/data_acquisition.md) | Data acquisition attempts, why synthetic data was used, and QA |
| [`reports/stage1_interrupted_time_series.md`](reports/stage1_interrupted_time_series.md) | Stage 1 regression results and charts |
| [`reports/figures/`](reports/figures/) | Generated charts |
| [`docs/scope_and_rationale.md`](docs/scope_and_rationale.md) | Upfront selection rationale, causal design, and data provenance |

## Getting started

```bash
pip install -r requirements.txt
python src/generate.py                      # regenerate the synthetic data
python src/analysis/01_interrupted_time_series.py
```

## License

[MIT](LICENSE)
