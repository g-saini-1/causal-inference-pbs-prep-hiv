"""Stage 4 (optional/advanced): treatment-effect heterogeneity via causal forest.

Uses state-level covariates (testing rates, socioeconomic index, COVID
lockdown severity, EPIC-NSW early-access flag) with EconML's CausalForestDML
to estimate whether the PrEP effect on MSM HIV notifications varied by
state. See docs/scope_and_rationale.md, Stage 4, for the motivating
observation that COVID-19 disrupted PrEP uptake unevenly across states.

TODO: merge data/synthetic/hiv_notifications_quarterly.csv (MSM category)
with data/synthetic/state_covariates.csv, fit econml.dml.CausalForestDML
with state covariates as effect modifiers, and report/plot heterogeneous
treatment effect estimates by state.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from src.utils.data_io import load_hiv_notifications, load_state_covariates  # noqa: E402


def main():
    hiv = load_hiv_notifications()
    covariates = load_state_covariates()
    merged = hiv[hiv["transmission_category"] == "MSM"].merge(covariates, on="state")
    print(merged.head())
    print("\nTODO: fit CausalForestDML for heterogeneous treatment effects by state")


if __name__ == "__main__":
    main()
