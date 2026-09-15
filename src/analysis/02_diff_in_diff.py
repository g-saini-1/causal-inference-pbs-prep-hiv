"""Stage 2: difference-in-differences on HIV notifications.

Compares MSM notifications (the population PrEP overwhelmingly targets)
against Heterosexual/Other notifications (the control group, unaffected by
PrEP availability but exposed to the same secular trends) around the 1 April
2018 PBS listing date. See docs/scope_and_rationale.md, Stage 2, for the
identification argument.

TODO: fit the two-way fixed effects DiD model
    hiv_notifications ~ is_msm * post_pbs_listing + C(state) + C(quarter)
and report the interaction coefficient (the DiD estimate) with robust /
clustered (by state) standard errors. Plot MSM vs. control group trends
around the listing date to reports/figures/diff_in_diff_trends.png.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from src.utils.data_io import PBS_LISTING_DATE, load_hiv_notifications  # noqa: E402


def main():
    df = load_hiv_notifications()
    df["is_msm"] = (df["transmission_category"] == "MSM").astype(int)
    df["post_pbs_listing"] = (df["quarter_start"] >= PBS_LISTING_DATE).astype(int)
    print(df.groupby(["is_msm", "post_pbs_listing"])["hiv_notifications"].mean())
    print("\nTODO: fit two-way fixed effects DiD model and produce diff_in_diff_trends.png")


if __name__ == "__main__":
    main()
