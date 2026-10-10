"""Stage 2: difference-in-differences on HIV notifications.

Compares MSM notifications (the population PrEP overwhelmingly targets, see
docs/scope_and_rationale.md, Stage 2, references 1-2) against
Heterosexual/Other notifications (the comparison group, unaffected by PrEP
availability but exposed to the same secular trends) around the 1 April 2018
PBS listing date. See docs/scope_and_rationale.md, Stage 2, for the full
identification argument. Data exploration write-up:
reports/hiv_notifications_data_exploration.md.

NSW excluded, same as Stage 1. Its EPIC-NSW trial gives NSW's own MSM
notifications an early, separately-timed decline from 2016, which a single
April 2018 cutoff would misattribute to the national PBS listing; rest of
country only isolates that listing's own effect, leaving NSW's earlier start
to Stage 3.

TODO: fit the two-way fixed effects DiD model, on the rest-of-country data,
    hiv_notifications ~ is_msm * post_pbs_listing + C(state) + C(quarter)
and report the interaction coefficient (the DiD estimate) with robust /
clustered (by state) standard errors.

TODO: reconsider "control group" terminology when writing this stage up.
Stage 1's report settled on "comparison group" as the more accurate term
for a non-randomised design ("control group" implies random assignment,
which nothing in this project has). Heterosexual/Other notifications here
are a comparison group in that same sense; decide whether to rename this
docstring and any write-up to match, or keep "control group" if there's a
reason to treat Stage 2 differently.
"""

import os
import sys

import matplotlib.pyplot as plt

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from src.utils.data_io import PBS_LISTING_DATE, load_hiv_notifications  # noqa: E402
from src.utils.plotting import save_figure, set_style  # noqa: E402

CATEGORY_COLORS = {
    "MSM": "#2a78d6",
    "Heterosexual": "#eb6e3c",
    "Other": "#6857d7",
}
CATEGORY_ORDER = ["MSM", "Heterosexual", "Other"]


def plot_notifications_by_category(national_by_category):
    pivot = national_by_category.pivot(index="quarter_start", columns="transmission_category", values="hiv_notifications")

    fig, ax = plt.subplots()
    for category in CATEGORY_ORDER:
        ax.plot(pivot.index, pivot[category], color=CATEGORY_COLORS[category], linewidth=2.5, label=category)

    top = ax.get_ylim()[1]
    ax.axvline(PBS_LISTING_DATE, color="firebrick", linewidth=2)
    ax.text(PBS_LISTING_DATE, top * 0.95, "  PBS listing\n  (Apr 2018)", color="firebrick", ha="left", va="top")

    ax.set_title("National HIV notifications by transmission category, 2013Q1 - 2022Q4")
    ax.set_ylabel("Notifications per quarter (all states)")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=3, frameon=False)
    return save_figure(fig, "hiv_notifications_by_category_chart.png")


def main():
    set_style()
    df = load_hiv_notifications()
    df["is_msm"] = (df["transmission_category"] == "MSM").astype(int)
    df["post_pbs_listing"] = (df["quarter_start"] >= PBS_LISTING_DATE).astype(int)

    national_by_category = df.groupby(["quarter_start", "transmission_category"], as_index=False)["hiv_notifications"].sum()
    chart_path = plot_notifications_by_category(national_by_category)
    print(f"Figures written:\n - {chart_path}")

    rest_of_country = df[df["state"] != "NSW"]
    print("\nGroup means, rest of country (NSW excluded):")
    print(rest_of_country.groupby(["is_msm", "post_pbs_listing"])["hiv_notifications"].mean())
    print("\nTODO: fit two-way fixed effects DiD model on rest_of_country")


if __name__ == "__main__":
    main()
