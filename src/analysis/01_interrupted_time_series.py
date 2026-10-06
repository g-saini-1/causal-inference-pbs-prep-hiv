"""Stage 1: interrupted time series on national PBS PrEP dispensing.

Sanity-check step: fits a segmented (piecewise-linear) regression around the
1 April 2018 PBS listing date. Regenerates Stage 1's current specification chart
(pbs_prep_its_specification_chart.png, rest-of-country series, every fitted term
including the COVID-period and quadratic growth controls drawn, see
reports/stage1_interrupted_time_series.md) plus the initial specification's
preserved charts (pbs_prep_its_specification_initial_chart.png,
pbs_prep_family_distribution_initial_chart.png,
pbs_prep_residuals_over_time_initial_chart.png, pbs_prep_residuals_acf_initial_chart.png,
pbs_prep_dispensing_initial_chart.png, see
reports/stage1_initial_specification_diagnostics.md) and the two current raw-data
charts (pbs_prep_dispensing_chart.png, pbs_epic_nsw_zoom_chart.png) before moving
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

# Stage 1 v2: the initial specification's own diagnostics (see
# reports/stage1_initial_specification_diagnostics.md) identified two omitted-structure
# gaps and a confound, addressed here: an early ramp term and a COVID dip-and-recovery
# term (both checked against src/generate.py's actual functional forms, not just the
# chart), and switching from the full national aggregate to a rest-of-country
# aggregate (NSW excluded, since its EPIC-NSW ramp otherwise dominates the pre-trend).
#
# The data-generating process (src/generate.py) ramps post-listing growth linearly
# over 6 months to a steady state, then grows linearly (not curved) indefinitely; a
# single quadratic term across the whole post-period can't represent two distinct
# straight-line slopes, and was found to force a spurious late decline. `early_ramp`
# is a linear spline (capped at RAMP_MONTHS) that gives the first 6 months their own,
# much steeper slope, matching that generator exactly.
#
# The generator's COVID effect is a bell-shaped multiplicative dip, but its peak sits
# well before the window's midpoint (the rest-of-country trough lands around three
# months in, not ten); a single term symmetric about the window's centre put the
# modelled trough roughly six months later than the data actually shows. `covid_decline`
# and `covid_recovery` are a hinge pair, the same construction as `early_ramp`, split at
# the observed trough, so the sharp decline and the much longer recovery each get their
# own slope instead of being forced into one symmetric shape.
COVID_START = pd.Timestamp("2020-03-01")
COVID_END = pd.Timestamp("2021-10-01")
RAMP_MONTHS = 6
FORMULA_V2 = (
    "prep_dispensing_count ~ t + post_listing + months_since_post_listing "
    "+ early_ramp + covid_decline + covid_recovery"
)


def build_rest_of_country_series(df):
    rest = df[df["state"] != "NSW"]
    return rest.groupby("month", as_index=False)["prep_dispensing_count"].sum()


def fit_v2_specification(rest_of_country):
    national = rest_of_country.copy()
    national["t"] = range(len(national))
    national["post_listing"] = (national["month"] >= PBS_LISTING_DATE).astype(int)
    national["months_since_post_listing"] = national["post_listing"] * (
        national["t"] - national.loc[national["post_listing"] == 1, "t"].min()
    )
    national["early_ramp"] = national["months_since_post_listing"].clip(upper=RAMP_MONTHS)
    national["covid_period"] = (
        (national["month"] >= COVID_START) & (national["month"] <= COVID_END)
    ).astype(int)
    months_since_covid_start = national["covid_period"] * (
        national["t"] - national.loc[national["covid_period"] == 1, "t"].min()
    )
    # Observed trough within the COVID window (data-derived, not assumed), the hinge
    # point between the decline and recovery segments.
    covid_window = national[national["covid_period"] == 1]
    trough_t = covid_window.loc[covid_window["prep_dispensing_count"].idxmin(), "t"]
    trough_offset = trough_t - covid_window["t"].min()
    national["covid_decline"] = months_since_covid_start.clip(upper=trough_offset)
    national["covid_recovery"] = (months_since_covid_start - trough_offset).clip(lower=0)

    model = smf.ols(FORMULA_V2, data=national).fit()
    national["fitted"] = model.fittedvalues
    # The core causal trajectory (pre-trend, level shift, ramp, and long-run growth),
    # excluding only the COVID control, used for the geometric chart so it shows the
    # treatment's own shape rather than the COVID dip partialled out on top of it.
    national["structural"] = (
        model.params["Intercept"]
        + model.params["t"] * national["t"]
        + model.params["post_listing"] * national["post_listing"]
        + model.params["months_since_post_listing"] * national["months_since_post_listing"]
        + model.params["early_ramp"] * national["early_ramp"]
    )
    return model, national


def fit_candidate_families(national, formula=FORMULA):
    """Fit OLS, Poisson, and Negative Binomial on the same specification, and
    compute the Empirical comparison checklist items from
    docs/model_family_concepts.md Section 6 for each candidate: coefficient,
    AIC, the family-specific assumption check, and residual autocorrelation.
    """
    ols_model = smf.ols(formula, data=national).fit()
    poisson_model = smf.glm(formula, data=national, family=sm.families.Poisson()).fit()
    nb_model = smf.negativebinomial(formula, data=national).fit(disp=False)

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
    return save_figure(fig, "pbs_prep_dispensing_initial_chart.png")


def plot_dispensing_overview_annotated(df, national):
    """Same chart as plot_full_series, with the distinct segments a specification
    needs to account for marked out and dated directly: the post-listing ramp to
    a steady state, the steady linear growth after it, the COVID dip and its
    trough, and the continued growth once COVID ends.
    """
    state_pivot = df.pivot(index="month", columns="state", values="prep_dispensing_count")
    ramp_end_date = PBS_LISTING_DATE + pd.DateOffset(months=RAMP_MONTHS)
    covid_window = national[(national["month"] >= COVID_START) & (national["month"] <= COVID_END)]
    trough = covid_window.loc[covid_window["prep_dispensing_count"].idxmin()]
    trough_date = trough["month"]

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

    ax.axvline(ramp_end_date, color=NATIONAL_COLOR, linewidth=1, linestyle="--")
    ax.text(ramp_end_date, top * 0.38, "  Ramp to steady\n  state ends ({})".format(ramp_end_date.strftime("%b %Y")),
            color=NATIONAL_COLOR, fontsize=8, ha="left", va="top")

    ax.axvspan(COVID_START, COVID_END, color="grey", alpha=0.12, zorder=0)
    ax.text(COVID_START, top * 0.62, "  COVID-19\n  restrictions\n  (Mar 2020 - Oct 2021)",
            color="grey", ha="left", va="center", fontsize=8.5)
    ax.annotate("Trough: {}".format(trough_date.strftime("%b %Y")),
                xy=(trough_date, trough["prep_dispensing_count"]), xytext=(trough_date, top * 0.1),
                fontsize=8, color="grey", ha="center",
                arrowprops=dict(arrowstyle="->", color="grey", linewidth=1))

    recovery_point = national[national["month"] == pd.Timestamp("2022-06-01")]
    if not recovery_point.empty:
        rec_x = recovery_point["month"].iloc[0]
        rec_y = recovery_point["prep_dispensing_count"].iloc[0]
        ax.annotate("Growth continues after COVID,\nno decline in the raw data",
                    xy=(rec_x, rec_y), xytext=(rec_x, top * 0.74),
                    fontsize=8.5, color=NATIONAL_COLOR, ha="center",
                    arrowprops=dict(arrowstyle="->", color=NATIONAL_COLOR, linewidth=1))

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
    return save_figure(fig, "pbs_prep_its_specification_initial_chart.png")


def plot_v2_specification(national, model):
    """Geometric story for the revised specification: a pre-listing line (β0, β1),
    a level shift at the listing (β2), a steep early ramp for the first
    RAMP_MONTHS (β4), the shallower long-run growth after it (β3), and a COVID
    decline (β5) and recovery (β6), hinged at the observed trough rather than
    drawn as one symmetric dip, added as a control layer rather than into the
    core trajectory. See Model specification in reports/stage1_interrupted_time_series.md.
    """
    fig, ax = plt.subplots()

    beta0 = model.params["Intercept"]
    beta1 = model.params["t"]

    pre = national[national["post_listing"] == 0].reset_index(drop=True)
    post = national[national["post_listing"] == 1].reset_index(drop=True)
    listing_date = post["month"].iloc[0]
    t_listing = post["t"].iloc[0]
    pre_extrapolated = beta0 + beta1 * t_listing
    post_start = post["structural"].iloc[0]
    ramp_end_date = post["month"].iloc[RAMP_MONTHS]

    ax.axvspan(COVID_START, COVID_END, color="grey", alpha=0.12, zorder=0)

    # Pre-listing and fitted are the same line in substance (no post-listing terms
    # apply before the listing), so they share one continuous "Fitted" line and
    # legend entry rather than two identically-styled entries for the same curve.
    ax.plot(national["month"], national["fitted"], color="firebrick", linewidth=2.5, label="Fitted")
    ax.plot(post["month"], post["structural"], color="firebrick", linewidth=2, linestyle="--",
            label="Post-listing core trajectory (no COVID)")

    counterfactual = beta0 + beta1 * post["t"]
    ax.plot(post["month"], counterfactual, color="grey", linewidth=1.6, linestyle=":",
            label="Counterfactual (pre-trend continued)")
    ax.fill_between(post["month"], counterfactual, post["structural"], color="firebrick", alpha=0.1)

    ax.axvline(listing_date, color="black", linewidth=1.2)
    ax.axvline(ramp_end_date, color="grey", linewidth=1, linestyle="--")
    top = ax.get_ylim()[1]
    ax.text(listing_date, top * 0.74, "Treatment:\nPBS listing (Apr 2018)  ", fontsize=9,
            ha="right", va="top")
    ax.text(ramp_end_date, top * 0.92, "  Ramp ends\n  ({})".format(ramp_end_date.strftime("%b %Y")),
            fontsize=8, color="grey", ha="left", va="top")
    covid_mid = COVID_START + (COVID_END - COVID_START) / 2
    ax.text(covid_mid, top * 0.28, "COVID-19\nrestrictions", color="grey",
            ha="center", va="center", fontsize=8)

    ax.annotate("", xy=(listing_date, post_start), xytext=(listing_date, pre_extrapolated),
                arrowprops=dict(arrowstyle="<->", color="black", linewidth=1.3))
    ax.text(listing_date, (pre_extrapolated + post_start) / 2, "  β2\n  (level shift)",
            va="center", ha="left", fontsize=10)

    ax.annotate("β0 (intercept)", xy=(pre["month"].iloc[0], beta0),
                xytext=(pre["month"].iloc[8], top * 0.1), fontsize=9.5,
                color="firebrick", arrowprops=dict(arrowstyle="->", color="firebrick", linewidth=1))

    # beta1: the pre-listing line's own slope is too close to zero to show as a
    # visible rise/run triangle at this scale, so point directly at the line instead
    i2 = 5 * len(pre) // 6
    x2, y2 = pre["month"].iloc[i2], pre["structural"].iloc[i2]
    ax.annotate("β1 = rise ÷ run\n(near zero, since pre-2018\nuptake was NSW-only)",
                xy=(x2, y2), xytext=(pre["month"].iloc[2 * len(pre) // 3], top * 0.22),
                fontsize=9.5, color="firebrick", ha="center", va="bottom",
                arrowprops=dict(arrowstyle="->", color="firebrick", linewidth=1))

    # beta4: the ramp's own steep slope, read as a triangle between the listing
    # date and the point where early_ramp stops growing (RAMP_MONTHS later)
    ramp_y0 = post["structural"].iloc[0]
    ramp_y1 = post["structural"].iloc[RAMP_MONTHS]
    ax.plot([listing_date, ramp_end_date], [ramp_y0, ramp_y0], color="darkorange", linewidth=1, linestyle="--")
    ax.plot([ramp_end_date, ramp_end_date], [ramp_y0, ramp_y1], color="darkorange", linewidth=1, linestyle="--")
    ax.annotate("β4 (ramp slope,\nfirst {} months)".format(RAMP_MONTHS),
                xy=(ramp_end_date, (ramp_y0 + ramp_y1) / 2), xytext=(10, -65),
                textcoords="offset points", fontsize=9.5, color="darkorange", va="center")

    # beta3: the shallower long-run slope, read a year past the ramp so it isn't
    # blended with the ramp's much steeper early slope
    ref_idx = min(RAMP_MONTHS + 12, len(post) - 1)
    ref_x = post["month"].iloc[ref_idx]
    ref_y = counterfactual.iloc[ref_idx]
    actual_y = post["structural"].iloc[ref_idx]
    ax.annotate("", xy=(ref_x, actual_y), xytext=(ref_x, ref_y),
                arrowprops=dict(arrowstyle="->", color="firebrick", linewidth=1.3))
    ax.annotate("β3 (long-run extra\nslope per month)\n{}".format(ref_x.strftime("%b %Y")),
                xy=(ref_x, (ref_y + actual_y) / 2), xytext=(18, 0),
                textcoords="offset points", fontsize=9.5, color="firebrick", va="center")

    # beta5: the gap between the core trajectory and the fully fitted line, read
    # exactly at the observed trough, where covid_recovery is still 0, so the gap
    # reflects the decline alone
    covid_rows = post[post["covid_period"] == 1]
    trough_row = covid_rows.loc[covid_rows["prep_dispensing_count"].idxmin()]
    trough_date = trough_row["month"]
    core_at_trough = trough_row["structural"]
    fitted_at_trough = trough_row["fitted"]
    ax.annotate("", xy=(trough_date, fitted_at_trough), xytext=(trough_date, core_at_trough),
                arrowprops=dict(arrowstyle="->", color="firebrick", linewidth=1.3))
    ax.annotate("β5 (decline):\ngap opens by {}".format(trough_date.strftime("%b %Y")),
                xy=(trough_date, (core_at_trough + fitted_at_trough) / 2),
                xytext=(-110, 0), textcoords="offset points", fontsize=9.5, color="firebrick", va="center")

    # beta6: the gap at the end of the COVID window, where covid_decline has
    # capped out and covid_recovery has reached its maximum; the narrowing
    # relative to the trough's gap is the recovery's own contribution
    window_end_row = covid_rows.iloc[-1]
    end_x = window_end_row["month"]
    core_at_end = window_end_row["structural"]
    fitted_at_end = window_end_row["fitted"]
    ax.annotate("", xy=(end_x, fitted_at_end), xytext=(end_x, core_at_end),
                arrowprops=dict(arrowstyle="->", color="firebrick", linewidth=1.3))
    ax.annotate("β6 (recovery): gap\nnarrows vs. trough\nby {}".format(end_x.strftime("%b %Y")),
                xy=(end_x, (core_at_end + fitted_at_end) / 2),
                xytext=(post["month"].iloc[int(len(post) * 0.62)], top * 0.55),
                fontsize=9.5, color="firebrick", ha="center", va="center",
                arrowprops=dict(arrowstyle="->", color="firebrick", linewidth=1))

    ax.set_title("Segmented regression: full model specification")
    ax.set_ylabel("Dispensing count per month (rest of country)")
    ax.legend(loc="upper left", frameon=False, fontsize=8.5)
    return save_figure(fig, "pbs_prep_its_specification_chart.png")


def main():
    set_style()
    df = load_pbs_dispensing()
    national = df.groupby("month", as_index=False)["prep_dispensing_count"].sum()

    model, national_fit = fit_segmented_regression(national)
    print(model.summary())

    rest_of_country = build_rest_of_country_series(df)
    v2_model, v2_fit = fit_v2_specification(rest_of_country)
    print(v2_model.summary())

    ols_model, poisson_model, nb_model, comparison = fit_candidate_families(v2_fit, FORMULA_V2)
    print("\nEmpirical comparison checklist (docs/model_family_concepts.md Section 6), v2 specification:")
    print(comparison.to_string(index=False))

    dispensing_initial_path = plot_full_series(df, national)
    dispensing_path = plot_dispensing_overview_annotated(df, national)
    zoom_path = plot_nsw_pretrend(df)
    initial_spec_path = plot_its_specification(national_fit, model)
    v2_spec_path = plot_v2_specification(v2_fit, v2_model)
    dist_path = plot_family_distribution_comparison(v2_fit, ols_model, poisson_model, nb_model)
    resid_path = plot_residuals_over_time(v2_fit, ols_model, poisson_model, nb_model)
    acf_path = plot_residuals_acf(ols_model, poisson_model, nb_model)
    print(
        f"\nFigures written:\n - {v2_spec_path}\n - {initial_spec_path}"
        f"\n - {dist_path}\n - {resid_path}\n - {acf_path}\n - {dispensing_initial_path}\n - {dispensing_path}"
        f"\n - {zoom_path}"
    )


if __name__ == "__main__":
    main()
