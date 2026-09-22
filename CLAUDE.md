# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

A portfolio case study using PBS-subsidised PrEP as a natural experiment to test whether the
policy reduced new HIV diagnoses in Australia. Real PBS/NNDSS data pulls hit two genuine
availability gaps (pre-2019 NNDSS quarterly granularity, unresolved historical PBS item codes), so
the project runs against synthetic data with the same structure and known, built-in effects, so the
causal-inference workflow can be validated against a known ground truth. Full rationale in
`docs/scope_and_rationale.md`; what was tried with real data in `reports/data_acquisition.md`.

## Commands

```bash
pip install -r requirements.txt
python src/generate.py                                  # regenerate data/synthetic/*.csv (fixed seed)
python src/analysis/01_interrupted_time_series.py        # Stage 1, implemented
python src/analysis/02_diff_in_diff.py                    # Stage 2, currently a TODO stub
python src/analysis/03_staggered_adoption.py              # Stage 3, currently a TODO stub
python src/analysis/04_heterogeneity_causal_forest.py     # Stage 4 (optional), currently a TODO stub
```

There is no test suite or linter configured in this repo.

## Architecture

**Four-stage causal pipeline, not four independent scripts.** `src/analysis/01_interrupted_time_series.py`
-> `02_diff_in_diff.py` -> `03_staggered_adoption.py` -> `04_heterogeneity_causal_forest.py` (optional)
implement one methodology of increasing rigor. Each stage's causal question, chosen method, and
identification argument are decided up front in `docs/scope_and_rationale.md`; the scripts only
implement what that doc already committed to. Only Stage 1 is implemented. Stages 2–4 are TODO
stubs whose intended model spec is written in their module docstrings.

**Synthetic data with a known answer.** `src/generate.py` (fixed seed) builds the three CSVs in
`data/synthetic/` with deliberately baked-in effects (e.g. a national dispensing level-shift at the
2018-04 PBS listing, an earlier NSW-only ramp for the 2016 EPIC-NSW trial, a COVID-era dip),
documented column-by-column in `data/data_dictionary.md`. Because the ground truth is known, each
stage's fitted result can be checked against it rather than trusted blind. `data/raw/` holds the
real PBS/NNDSS/Kirby extracts from the abandoned real-data attempt, documented in
`data/raw/data-collection-notes.md`.

**`docs/` vs `reports/`.** `docs/` holds stage-agnostic reference material reused across stages:
`scope_and_rationale.md` (causal design), `causal_method_workflow_template.md` (the per-stage
9-step tracker), `model_family_concepts.md` (OLS/Poisson/NB selection reasoning). `reports/` holds
the dated, stage-specific write-ups of actual results (`data_acquisition.md`,
`stage1_interrupted_time_series.md`) plus generated charts in `reports/figures/`.

**Shared script plumbing.** Each `src/analysis/0N_*.py` script inserts the repo root onto
`sys.path` (there's no installed package) and pulls data loaders from `src/utils/data_io.py` and
chart styling/save helpers from `src/utils/plotting.py`, so state colors and figure output paths
stay consistent across stages.

## `docs/scope_and_rationale.md` is frozen

`docs/scope_and_rationale.md` records the project's upfront rationale and design as decided at the
start of the project. Do not edit it to reflect anything that happened afterward, e.g. results,
findings, model choices made along the way, or scope changes discovered mid-analysis. Findings and
results belong in `reports/`, not here. Only touch this file when the user explicitly asks for a
change to it in a prompt, or when the user has edited it manually themselves.
