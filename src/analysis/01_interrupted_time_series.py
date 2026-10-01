"""Stage 1: interrupted time series on national PBS PrEP dispensing.

Sanity-check step: fits a segmented (piecewise-linear) regression around the
1 April 2018 PBS listing date on the national monthly dispensing series,
fits OLS, Poisson, and NB as candidate families and runs the Empirical
comparison checklist from docs/model_family_concepts.md Section 6, and
regenerates the six supporting charts in reports/figures/
(pbs_prep_its_specification_chart.png, pbs_prep_family_distribution_chart.png,
pbs_prep_residuals_over_time_chart.png, pbs_prep_residuals_acf_chart.png,
pbs_prep_dispensing_chart.png, and pbs_epic_nsw_zoom_chart.png) before moving
to the harder outcome question in 02_diff_in_diff.py.

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
from scipy.stats import nbinom, norm, poisson
from statsmodels.graphics.tsaplots import plot_acf
from statsmodels.stats.diagnostic import het_breuschpagan
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
    bp_stat, bp_pvalue, _, _ = het_breuschpagan(ols_model.resid, ols_model.model.exog)

    rows = [
        {
            "Candidate": "OLS",
            "Coefficient (post_listing)": f"{ols_model.params['post_listing']:+.1f} (additive)",
            "AIC": ols_model.aic,
            "Assumption check": f"Breusch-Pagan LM = {bp_stat:.2f}, p = {bp_pvalue:.3f}",
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


def plot_family_distribution_comparison(national, ols_model, poisson_model, nb_model):
    """Compares OLS/Gaussian, Poisson, and NB's own fitted shape for one
    pre-listing and one post-listing month, using each model's real fitted
    mean (OLS's constant residual SD and NB's fitted alpha set the spread).
    See the Model family selection section of
    reports/stage1_interrupted_time_series.md for the numbers behind it.
    """
    ols_sd = np.sqrt(ols_model.mse_resid)
    alpha = nb_model.params["alpha"]

    def nb_pmf(k, mu):
        n = 1 / alpha
        p = n / (n + mu)
        return nbinom.pmf(k, n, p)

    pre_row = national.iloc[[0]]
    post_row = national[national["month"] == pd.Timestamp("2019-06-01")]
    cases = [
        (f"Pre-listing ({pre_row['month'].dt.strftime('%b %Y').iloc[0]})", pre_row),
        (f"Post-listing ({post_row['month'].dt.strftime('%b %Y').iloc[0]})", post_row),
    ]

    fig, axes = plt.subplots(1, 2, figsize=(12, 5.5))
    for ax, (label, row) in zip(axes, cases):
        ols_mu = ols_model.predict(row).iloc[0]
        poisson_mu = poisson_model.predict(row).iloc[0]
        nb_mu = nb_model.predict(row).iloc[0]
        poisson_sd = np.sqrt(poisson_mu)
        nb_sd = np.sqrt(nb_mu + alpha * nb_mu**2)

        lo = min(ols_mu - 4 * ols_sd, nb_mu - 4 * nb_sd, 0)
        hi = max(ols_mu + 4 * ols_sd, nb_mu + 4 * nb_sd)
        k = np.arange(int(np.floor(lo)), int(np.ceil(hi)) + 1)

        ax.bar(k, poisson.pmf(k, poisson_mu), width=1, alpha=0.5, color="#4C72B0",
               label=f"Poisson, μ={poisson_mu:.0f} (SD≈{poisson_sd:.0f})")
        ax.bar(k, nb_pmf(k, nb_mu), width=1, alpha=0.5, color="#C44E52",
               label=f"NB, μ={nb_mu:.0f} (SD≈{nb_sd:.0f})")
        xs = np.linspace(lo, hi, 1000)
        ax.plot(xs, norm.pdf(xs, ols_mu, ols_sd), color="#55A868", linewidth=2,
                label=f"OLS/Gaussian, μ={ols_mu:.0f} (SD≈{ols_sd:.0f})")
        ax.fill_between(xs, norm.pdf(xs, ols_mu, ols_sd), color="#55A868", alpha=0.25)
        ax.axvline(0, color="black", linewidth=0.8, linestyle=":")
        ax.set_title(label, fontsize=10)
        ax.set_xlabel("Monthly dispensing count")
        ax.legend(fontsize=8, loc="upper right")
    axes[0].set_ylabel("Probability (mass for Poisson/NB, density for OLS)")

    fig.suptitle("OLS, Poisson, and NB: each family's own fitted shape for the same month", fontsize=12)
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    return save_figure(fig, "pbs_prep_family_distribution_chart.png")


def _candidate_residuals(ols_model, poisson_model, nb_model):
    return {
        "OLS": ols_model.resid,
        "Poisson": poisson_model.resid_response,
        "NB": nb_model.resid,
    }


def plot_residuals_over_time(national, ols_model, poisson_model, nb_model):
    residuals = _candidate_residuals(ols_model, poisson_model, nb_model)
    colors = {"OLS": "#55A868", "Poisson": "#4C72B0", "NB": "#C44E52"}

    fig, axes = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
    for ax, (name, resid) in zip(axes, residuals.items()):
        ax.axhline(0, color="grey", linewidth=0.8)
        ax.plot(national["month"], resid, color=colors[name], marker="o", markersize=3, linewidth=1)
        ax.set_ylabel(f"{name} residual")
    axes[-1].set_xlabel("Month")
    fig.suptitle("Residuals over time: the wave pattern behind the low Durbin-Watson values", fontsize=12)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    return save_figure(fig, "pbs_prep_residuals_over_time_chart.png")


def plot_residuals_acf(ols_model, poisson_model, nb_model):
    residuals = _candidate_residuals(ols_model, poisson_model, nb_model)
    colors = {"OLS": "#55A868", "Poisson": "#4C72B0", "NB": "#C44E52"}

    fig, axes = plt.subplots(1, 3, figsize=(13, 4))
    for ax, (name, resid) in zip(axes, residuals.items()):
        plot_acf(resid, ax=ax, lags=20, color=colors[name], vlines_kwargs={"colors": colors[name]}, title=name)
        ax.set_xlabel("Lag (months)")
    axes[0].set_ylabel("Autocorrelation")
    fig.suptitle("Autocorrelation function (ACF) of residuals, by candidate", fontsize=12)
    fig.tight_layout(rect=[0, 0, 1, 0.92])
    return save_figure(fig, "pbs_prep_residuals_acf_chart.png")


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
    dist_path = plot_family_distribution_comparison(national_fit, ols_model, poisson_model, nb_model)
    resid_path = plot_residuals_over_time(national_fit, ols_model, poisson_model, nb_model)
    acf_path = plot_residuals_acf(ols_model, poisson_model, nb_model)
    print(
        f"\nFigures written:\n - {spec_path}\n - {dist_path}\n - {resid_path}\n - {acf_path}"
        f"\n - {full_path}\n - {zoom_path}"
    )


if __name__ == "__main__":
    main()
