"""Stage 1: interrupted time series on national PBS PrEP dispensing.

Sanity-check step: fits a segmented (piecewise-linear) regression around the
1 April 2018 PBS listing date on the national monthly dispensing series, and
regenerates the two supporting charts in reports/figures/
(pbs_prep_dispensing_chart.png and pbs_epic_nsw_zoom_chart.png) before
moving to the harder outcome question in 02_diff_in_diff.py.

See docs/scope_and_rationale.md ("Causal question and design", Stage 1) for
the full design rationale, including why this national-level test needs the
staggered-adoption caveat addressed in 03_staggered_adoption.py. See
reports/stage1_interrupted_time_series.md for the write-up of these results.
"""

import os
import sys

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from src.utils.data_io import EPIC_NSW_START_DATE, PBS_LISTING_DATE, load_pbs_dispensing  # noqa: E402
from src.utils.plotting import NATIONAL_COLOR, STATE_COLORS, save_figure, set_style  # noqa: E402

STATE_ORDER = ["NSW", "VIC", "QLD", "WA", "SA", "OTHER"]


def state_label(state):
    return "Other" if state == "OTHER" else state


def fit_segmented_regression(national):
    national = national.copy()
    national["period_index"] = range(len(national))
    national["post_listing"] = (national["month"] >= PBS_LISTING_DATE).astype(int)
    national["months_since_listing_post"] = national["post_listing"] * (
        national["period_index"] - national.loc[national["post_listing"] == 1, "period_index"].min()
    )
    return smf.ols(
        "prep_dispensing_count ~ period_index + post_listing + months_since_listing_post",
        data=national,
    ).fit()


def plot_full_series(df, national):
    state_pivot = df.pivot(index="month", columns="state", values="prep_dispensing_count")

    fig, ax = plt.subplots()
    ax.plot(national["month"], national["prep_dispensing_count"], color=NATIONAL_COLOR, linewidth=3.5, label="National")
    for state in STATE_ORDER:
        ax.plot(state_pivot.index, state_pivot[state], color=STATE_COLORS[state], linewidth=2, label=state_label(state))

    top = ax.get_ylim()[1]
    ax.axvline(EPIC_NSW_START_DATE, color="grey", linestyle="--", linewidth=1.5)
    ax.text(EPIC_NSW_START_DATE, top * 0.85, "EPIC-NSW early\naccess (Mar 2016)",
            color="grey", ha="left", va="top")
    ax.axvline(PBS_LISTING_DATE, color="firebrick", linewidth=2)
    ax.text(PBS_LISTING_DATE, top * 0.72, "  PBS listing\n  (Apr 2018)",
            color="firebrick", ha="left", va="top")

    ax.set_title("PBS PrEP dispensing counts by state and nationally, Jan 2016 - Dec 2022")
    ax.set_ylabel("Dispensing count per month")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=7, frameon=False)
    return save_figure(fig, "pbs_prep_dispensing_chart.png")


def plot_nsw_pretrend(df):
    window = df[(df["month"] >= "2016-01-01") & (df["month"] <= "2018-05-01")]
    state_pivot = window.pivot(index="month", columns="state", values="prep_dispensing_count")

    fig, ax = plt.subplots()
    for state in STATE_ORDER:
        ax.plot(state_pivot.index, state_pivot[state], color=STATE_COLORS[state], linewidth=2.5, label=state_label(state))

    ax.axvline(EPIC_NSW_START_DATE, color="grey", linestyle="--", linewidth=1.5)
    ax.text(EPIC_NSW_START_DATE, 720, "EPIC-NSW early\naccess (Mar 2016)", color="grey", ha="left", va="top")
    ax.axvline(PBS_LISTING_DATE, color="firebrick", linewidth=2)
    ax.text(PBS_LISTING_DATE, 780, "PBS listing (Apr 2018)", color="firebrick", ha="right", va="top")

    ax.set_ylim(0, 800)
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    fig.autofmt_xdate(rotation=30, ha="right")

    ax.set_title("PBS PrEP dispensing: EPIC-NSW trial to PBS listing, Jan 2016 - Apr 2018")
    ax.set_ylabel("Dispensing count per month")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.25), ncol=6, frameon=False)
    return save_figure(fig, "pbs_epic_nsw_zoom_chart.png")


def main():
    set_style()
    df = load_pbs_dispensing()
    national = df.groupby("month", as_index=False)["prep_dispensing_count"].sum()

    model = fit_segmented_regression(national)
    print(model.summary())

    full_path = plot_full_series(df, national)
    zoom_path = plot_nsw_pretrend(df)
    print(f"\nFigures written:\n - {full_path}\n - {zoom_path}")


if __name__ == "__main__":
    main()
