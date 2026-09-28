"""Stage 1: interrupted time series on national PBS PrEP dispensing.

Sanity-check step: fits a segmented (piecewise-linear) regression around the
1 April 2018 PBS listing date on the national monthly dispensing series, and
regenerates the four supporting charts in reports/figures/
(pbs_prep_dispensing_chart.png, pbs_epic_nsw_zoom_chart.png,
pbs_prep_its_specification_chart.png, and pbs_prep_fitted_model_chart.png)
before moving to the harder outcome question in 02_diff_in_diff.py.

See docs/scope_and_rationale.md ("Causal question and methodology", Stage 1) for
the full design rationale, including why this national-level test needs the
staggered-adoption caveat addressed in 03_staggered_adoption.py. See
reports/stage1_interrupted_time_series.md for the write-up of these results.
"""

import os
import sys

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.stattools import durbin_watson

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from src.utils.data_io import EPIC_NSW_START_DATE, PBS_LISTING_DATE, load_pbs_dispensing  # noqa: E402
from src.utils.plotting import NATIONAL_COLOR, STATE_COLORS, save_figure, set_style  # noqa: E402

STATE_ORDER = ["NSW", "VIC", "QLD", "WA", "SA", "OTHER"]


def state_label(state):
    return "Other" if state == "OTHER" else state


def fit_segmented_regression(national):
    national = national.copy()
    national["t"] = range(len(national))
    national["post_listing"] = (national["month"] >= PBS_LISTING_DATE).astype(int)
    national["months_since_post_listing"] = national["post_listing"] * (
        national["t"] - national.loc[national["post_listing"] == 1, "t"].min()
    )
    model = smf.ols(
        "prep_dispensing_count ~ t + post_listing + months_since_post_listing",
        data=national,
    ).fit()
    national["fitted"] = model.fittedvalues
    return model, national


FORMULA = "prep_dispensing_count ~ t + post_listing + months_since_post_listing"


def fit_candidate_families(national):
    """Fit OLS, Poisson, and Negative Binomial on the same specification, and
    compute the Empirical comparison checklist items from
    docs/model_family_concepts.md Section 6 for each candidate: coefficient,
    AIC, the family-specific assumption check, and residual autocorrelation.
    """
    ols_model = smf.ols(FORMULA, data=national).fit()
    poisson_model = smf.glm(FORMULA, data=national, family=sm.families.Poisson()).fit()
    nb_model = smf.negativebinomial(FORMULA, data=national).fit(disp=False)

    poisson_dispersion = poisson_model.pearson_chi2 / poisson_model.df_resid
    nb_alpha = nb_model.params["alpha"]
    nb_alpha_ci = nb_model.conf_int().loc["alpha"]

    rows = [
        {
            "Candidate": "OLS",
            "Coefficient (post_listing)": f"{ols_model.params['post_listing']:+.1f} (additive)",
            "AIC": ols_model.aic,
            "Assumption check": f"Durbin-Watson = {durbin_watson(ols_model.resid):.3f}",
            "Autocorrelation check": f"Durbin-Watson = {durbin_watson(ols_model.resid):.3f}",
        },
        {
            "Candidate": "Poisson",
            "Coefficient (post_listing)": f"x{np.exp(poisson_model.params['post_listing']):.2f} (multiplicative)",
            "AIC": poisson_model.aic,
            "Assumption check": f"Pearson chi-squared / df = {poisson_dispersion:.2f}",
            "Autocorrelation check": f"Durbin-Watson = {durbin_watson(poisson_model.resid_response):.3f}",
        },
        {
            "Candidate": "NB",
            "Coefficient (post_listing)": f"x{np.exp(nb_model.params['post_listing']):.2f} (multiplicative)",
            "AIC": nb_model.aic,
            "Assumption check": f"alpha = {nb_alpha:.4f}, 95% CI [{nb_alpha_ci[0]:.4f}, {nb_alpha_ci[1]:.4f}]",
            "Autocorrelation check": f"Durbin-Watson = {durbin_watson(nb_model.resid):.3f}",
        },
    ]
    return ols_model, poisson_model, nb_model, pd.DataFrame(rows)


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


def plot_fitted_model(national):
    fig, ax = plt.subplots()
    ax.scatter(national["month"], national["prep_dispensing_count"], color=NATIONAL_COLOR,
               s=18, alpha=0.5, label="Actual")

    pre = national[national["post_listing"] == 0]
    post = national[national["post_listing"] == 1]
    ax.plot(pre["month"], pre["fitted"], color="firebrick", linewidth=2.5, label="Fitted, pre-listing")
    ax.plot(post["month"], post["fitted"], color="firebrick", linewidth=2.5, linestyle="--",
            label="Fitted, post-listing")

    ax.axvline(PBS_LISTING_DATE, color="grey", linestyle=":", linewidth=1.5)
    top = ax.get_ylim()[1]
    ax.text(PBS_LISTING_DATE, top * 0.92, "  PBS listing (Apr 2018)", color="grey", ha="left", va="top")

    ax.set_title("Segmented regression fit vs. actual dispensing, national PBS PrEP, Jan 2016 - Dec 2022")
    ax.set_ylabel("Dispensing count per month")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=3, frameon=False)
    return save_figure(fig, "pbs_prep_fitted_model_chart.png")


def plot_its_specification(national, model):
    fig, ax = plt.subplots()

    beta0 = model.params["Intercept"]
    beta1 = model.params["t"]

    pre = national[national["post_listing"] == 0].reset_index(drop=True)
    post = national[national["post_listing"] == 1].reset_index(drop=True)
    listing_date = post["month"].iloc[0]
    t_listing = post["t"].iloc[0]
    pre_extrapolated = beta0 + beta1 * t_listing
    post_start = post["fitted"].iloc[0]

    ax.plot(pre["month"], pre["fitted"], color="firebrick", linewidth=2.5, label="Pre-listing fit")
    ax.plot(post["month"], post["fitted"], color="firebrick", linewidth=2.5, linestyle="--",
            label="Post-listing fit")

    # counterfactual: the pre-listing trend extended across the whole post period,
    # this doubles as the beta3 reference (gap vs. the actual post-listing fit) and
    # as the causal-inference counterfactual (gap vs. observed = the treatment effect)
    counterfactual = beta0 + beta1 * post["t"]
    ax.plot(post["month"], counterfactual, color="grey", linewidth=1.6, linestyle=":",
            label="Counterfactual (pre-trend continued)")
    ax.fill_between(post["month"], counterfactual, post["fitted"], color="firebrick", alpha=0.1)

    ax.axvline(listing_date, color="black", linewidth=1.2)
    top = ax.get_ylim()[1]
    ax.text(listing_date, top * 0.96, "  Treatment:\n  PBS listing (Apr 2018)", fontsize=9,
            ha="left", va="top")

    # beta2: the level shift at the listing date (also the treatment effect at t=0)
    ax.annotate("", xy=(listing_date, post_start), xytext=(listing_date, pre_extrapolated),
                arrowprops=dict(arrowstyle="<->", color="black", linewidth=1.3))
    ax.text(listing_date, (pre_extrapolated + post_start) / 2, "  β2\n  (level shift)",
            va="center", ha="left", fontsize=10)

    # beta0: the pre-listing intercept
    ax.annotate("β0 (intercept)", xy=(pre["month"].iloc[0], beta0),
                xytext=(pre["month"].iloc[5], 2200), fontsize=9.5, color="firebrick",
                arrowprops=dict(arrowstyle="->", color="firebrick", linewidth=1))

    # beta1: shown as an explicit rise-over-run triangle on the pre-listing line
    i1, i2 = len(pre) // 6, 5 * len(pre) // 6
    x1, y1 = pre["month"].iloc[i1], pre["fitted"].iloc[i1]
    x2, y2 = pre["month"].iloc[i2], pre["fitted"].iloc[i2]
    ax.plot([x1, x2], [y1, y1], color="grey", linewidth=1, linestyle="--")
    ax.plot([x2, x2], [y1, y2], color="grey", linewidth=1, linestyle="--")
    ax.annotate("β1 = rise ÷ run", xy=(x2, (y1 + y2) / 2), xytext=(18, 0),
                textcoords="offset points", fontsize=9.5, color="firebrick", va="center")

    # beta3: the gap between the counterfactual (beta1's slope) and the actual, steeper
    # post-listing fit a year on, this is also part of the shaded treatment effect
    ref_idx = min(12, len(post) - 1)
    ref_x = post["month"].iloc[ref_idx]
    ref_y = counterfactual.iloc[ref_idx]
    actual_y = post["fitted"].iloc[ref_idx]
    ax.annotate("", xy=(ref_x, actual_y), xytext=(ref_x, ref_y),
                arrowprops=dict(arrowstyle="->", color="firebrick", linewidth=1.3))
    ax.annotate("β3 (extra slope\nper month)", xy=(ref_x, (ref_y + actual_y) / 2), xytext=(18, 0),
                textcoords="offset points", fontsize=9.5, color="firebrick", va="center")

    ax.set_title("Segmented regression: coefficients and causal concepts, both geometrically")
    ax.set_ylabel("Dispensing count per month")
    ax.legend(loc="upper left", frameon=False, fontsize=9)
    return save_figure(fig, "pbs_prep_its_specification_chart.png")


def main():
    set_style()
    df = load_pbs_dispensing()
    national = df.groupby("month", as_index=False)["prep_dispensing_count"].sum()

    model, national_fit = fit_segmented_regression(national)
    print(model.summary())

    ols_model, poisson_model, nb_model, comparison = fit_candidate_families(national_fit)
    print("\nEmpirical comparison checklist (docs/model_family_concepts.md Section 6):")
    print(comparison.to_string(index=False))

    full_path = plot_full_series(df, national)
    zoom_path = plot_nsw_pretrend(df)
    spec_path = plot_its_specification(national_fit, model)
    fitted_path = plot_fitted_model(national_fit)
    print(f"\nFigures written:\n - {full_path}\n - {zoom_path}\n - {spec_path}\n - {fitted_path}")


if __name__ == "__main__":
    main()
