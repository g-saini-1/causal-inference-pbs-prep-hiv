"""Stage 3: staggered-adoption difference-in-differences across states.

NSW effectively received the PrEP "treatment" ~2 years earlier than other
states via the EPIC-NSW demonstration trial (from 2016), ahead of the
national PBS listing (April 2018). See docs/scope_and_rationale.md, Stage 3,
for why a naive two-way fixed-effects DiD is unreliable here (the classic
"bad comparisons" problem when treatment timing varies across units) and why
a modern staggered-adoption estimator (e.g. Callaway & Sant'Anna) is more
defensible.

TODO: implement a staggered-adoption estimator (e.g. via the `differences`
or `csdid`-style approach, or a manual group-time ATT calculation) using
each state's own treatment start (NSW: 2016Q2, all others: 2018Q2) on the
MSM notification series. Plot group-time treatment effects to
reports/figures/staggered_adoption_results.png.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from src.utils.data_io import load_hiv_notifications  # noqa: E402


def main():
    df = load_hiv_notifications()
    msm = df[df["transmission_category"] == "MSM"].copy()
    msm["treat_start"] = msm["state"].map(lambda s: "2016Q2" if s == "NSW" else "2018Q2")
    print(msm.groupby(["state", "treat_start"])["hiv_notifications"].sum())
    print("\nTODO: implement staggered-adoption DiD estimator and produce staggered_adoption_results.png")


if __name__ == "__main__":
    main()
