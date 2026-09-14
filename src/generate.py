"""
Synthetic data generator for the PBS PrEP listing -> HIV diagnoses project.

Produces three CSVs that mirror the real data sources described in the
project scope, with known ground-truth effects baked in so model output
can be checked against a known answer:

1. pbs_dispensing_monthly.csv
   State x month PBS PrEP dispensing counts, Jan 2016 - Dec 2022.
   - NSW gets an early ramp-up from 2016 (EPIC-NSW demonstration trial).
   - All states get a large level shift at 2018-04 (PBS listing).
   - A COVID dip appears 2020, worst and longest in VIC.

2. hiv_notifications_quarterly.csv
   State x quarter x transmission-category HIV notification counts,
   2013 Q1 - 2022 Q4.
   - MSM category declines much more after PrEP than other categories
     (which only carry a mild shared secular trend -> control group).
   - NSW's decline in MSM notifications starts earlier (2016) than other
     states (2018), reflecting EPIC-NSW staggered timing.
   - A shared testing-disruption dip appears in 2020 across all groups.
   - National annual MSM+other total is calibrated to roughly track the
     published 1,028 (2015) -> 838 (2018) figure.

3. state_covariates.csv
   Static-ish state-level covariates for heterogeneity analysis
   (population, MSM population proxy, socioeconomic index, baseline
   testing rate, urbanicity index, lockdown severity 2020 index).

All series include realistic noise (negative binomial / Poisson draws)
on top of deterministic trend components, so no two runs are identical
unless you fix the seed (done below).
"""

import os

import numpy as np
import pandas as pd
from datetime import date

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "synthetic")

MASTER_SEED = 20180401
_seed_seq = np.random.SeedSequence(MASTER_SEED)
rng_pbs, rng_hiv, rng_cov = (np.random.default_rng(s) for s in _seed_seq.spawn(3))
# Kept for any code below that still refers to the old shared name.
rng = rng_pbs

STATES = ["NSW", "VIC", "QLD", "WA", "SA", "OTHER"]
# rough relative population / MSM-population weights (not exact ABS figures,
# just plausible proportions for a synthetic exercise)
STATE_WEIGHTS = {"NSW": 0.32, "VIC": 0.26, "QLD": 0.20, "WA": 0.11, "SA": 0.07, "OTHER": 0.04}

# =============================================================
# 1. PBS DISPENSING (monthly, state x month), Jan 2016 - Dec 2022
# =============================================================
months = pd.date_range("2016-01-01", "2022-12-01", freq="MS")
PBS_LISTING = pd.Timestamp("2018-04-01")
EPIC_NSW_START = pd.Timestamp("2016-03-01")

rows = []
for state in STATES:
    w = STATE_WEIGHTS[state]
    base_national_scale = 5200  # approx national steady-state monthly dispensing count, post-ramp

    for m in months:
        months_since_listing = (m.year - PBS_LISTING.year) * 12 + (m.month - PBS_LISTING.month)
        months_since_epic = (m.year - EPIC_NSW_START.year) * 12 + (m.month - EPIC_NSW_START.month)

        # NSW-only early EPIC-NSW trial dispensing (small, trial-scale).
        # NOTE: this is *not* gated to "before listing" any more. EPIC-NSW
        # participants kept taking PrEP after the PBS listing too -- they
        # didn't stop the month the funding mechanism changed -- so this
        # term is treated as an ongoing floor, not a pre/post switch.
        epic_level = 0.0
        if state == "NSW" and months_since_epic >= 0:
            epic_level = min(700, 40 * months_since_epic)

        # National level shift + gradual growth after PBS listing
        post_level = 0.0
        if m >= PBS_LISTING:
            ramp = min(1.0, months_since_listing / 6)  # 6-month ramp to new steady state
            growth = 1 + 0.006 * months_since_listing  # slow ongoing growth
            post_level = base_national_scale * w * ramp * growth

        # Use max(), not sum: the EPIC-NSW trial cohort and the post-listing
        # PBS cohort overlap (same people, different funding mechanism), so
        # adding them would double-count. max() also removes the artificial
        # one-month drop to ~0 right at the listing month, since the trial
        # floor (~700/month by 2018) carries NSW through the transition
        # until the post-listing ramp naturally grows past it.
        level = max(epic_level, post_level)

        # COVID dip: strongest & longest in VIC (extended lockdowns), mild elsewhere
        if date(2020, 3, 1) <= m.date() <= date(2021, 10, 1):
            covid_month_idx = (m.year - 2020) * 12 + (m.month - 3)
            if state == "VIC":
                dip_frac = 0.55 * np.exp(-((covid_month_idx - 6) ** 2) / (2 * 6.5 ** 2))
            else:
                dip_frac = 0.30 * np.exp(-((covid_month_idx - 4) ** 2) / (2 * 4.0 ** 2))
            level *= (1 - dip_frac)

        level = max(level, 0)
        # negative-binomial-ish noise via Poisson with jittered mean (avoid zero mean issues)
        noisy = rng_pbs.poisson(max(level, 0.5))
        rows.append({"state": state, "month": m.strftime("%Y-%m-%d"), "prep_dispensing_count": int(noisy)})

pbs = pd.DataFrame(rows)
pbs.to_csv(os.path.join(OUT_DIR, "pbs_dispensing_monthly.csv"), index=False)

# =============================================================
# 2. HIV NOTIFICATIONS (quarterly, state x category), 2013Q1-2022Q4
# =============================================================
quarters = pd.period_range("2013Q1", "2022Q4", freq="Q")
CATEGORIES = ["MSM", "Heterosexual", "Other"]

# category shares of national notifications, pre-PrEP era (rough, plausible)
CAT_SHARE = {"MSM": 0.68, "Heterosexual": 0.22, "Other": 0.10}

# national baseline annual notification total (matches ~1,028 in 2015 anchor)
def national_annual_baseline(year):
    # mild pre-existing downward secular trend even before PrEP (testing/awareness campaigns)
    # Intercept/slope solved analytically so the noiseless expected annual
    # total hits the published anchor figures exactly: 1,028 in 2015 and
    # 838 in 2018 (accounting for the secular decline, PrEP effect ramp,
    # and 2020 testing-disruption dip already applied downstream).
    return 1089.37 - 24.44 * (year - 2013)

rows = []
for state in STATES:
    w = STATE_WEIGHTS[state]
    for cat in CATEGORIES:
        for q in quarters:
            qstart = q.start_time
            year = qstart.year

            quarterly_national_base = national_annual_baseline(year) / 4
            base = quarterly_national_base * CAT_SHARE[cat] * w

            # PrEP effect: only applies to MSM category, only from each state's own
            # "treatment start" (NSW: 2016Q2 via EPIC-NSW ramp; others: 2018Q2 PBS listing)
            treat_start = pd.Period("2016Q2", freq="Q") if state == "NSW" else pd.Period("2018Q2", freq="Q")
            if cat == "MSM" and q >= treat_start:
                quarters_since = (q.year - treat_start.year) * 4 + (q.quarter - treat_start.quarter)
                # effect ramps in over 2 years to ~42% relative reduction, then holds
                max_effect = 0.42
                effect_frac = max_effect * min(1.0, quarters_since / 8)
                base *= (1 - effect_frac)

            # shared mild secular decline applies to all categories (control-relevant)
            years_elapsed = year - 2013
            base *= (1 - 0.006 * years_elapsed)

            # 2020 testing-disruption dip, shared across categories, worst in VIC,
            # partially mechanical (fewer tests -> fewer diagnoses, not a real transmission drop)
            if q.year == 2020:
                dip = 0.18 if state == "VIC" else 0.10
                base *= (1 - dip)
            elif q.year == 2021 and q.quarter <= 2:
                dip = 0.08 if state == "VIC" else 0.04
                base *= (1 - dip)

            base = max(base, 0.2)
            noisy = rng_hiv.poisson(base)
            rows.append({
                "state": state,
                "quarter": str(q),
                "quarter_start": qstart.strftime("%Y-%m-%d"),
                "transmission_category": cat,
                "hiv_notifications": int(noisy),
            })

hiv = pd.DataFrame(rows)
hiv.to_csv(os.path.join(OUT_DIR, "hiv_notifications_quarterly.csv"), index=False)

# quick sanity check against the published anchor figures
nat_annual = (
    hiv.assign(year=pd.to_datetime(hiv["quarter_start"]).dt.year)
    .groupby("year")["hiv_notifications"].sum()
)
print("National annual total notifications (synthetic), sanity check vs 1028(2015)/838(2018):")
print(nat_annual.loc[[2015, 2018]])

# =============================================================
# 3. STATE COVARIATES (mostly static, a couple of time-varying fields)
# =============================================================
cov_rows = []
# plausible-ish synthetic covariates, not real ABS/Kirby figures
base_covs = {
    "NSW": dict(population=8_200_000, msm_pop_proxy=145_000, irsd_socio_index=1005, urbanicity_index=0.88),
    "VIC": dict(population=6_700_000, msm_pop_proxy=118_000, irsd_socio_index=1010, urbanicity_index=0.87),
    "QLD": dict(population=5_300_000, msm_pop_proxy=82_000, irsd_socio_index=985, urbanicity_index=0.71),
    "WA":  dict(population=2_700_000, msm_pop_proxy=44_000, irsd_socio_index=1000, urbanicity_index=0.79),
    "SA":  dict(population=1_800_000, msm_pop_proxy=27_000, irsd_socio_index=975, urbanicity_index=0.77),
    "OTHER": dict(population=1_100_000, msm_pop_proxy=14_000, irsd_socio_index=960, urbanicity_index=0.55),
}
covid_lockdown_severity_2020 = {"NSW": 0.45, "VIC": 0.85, "QLD": 0.25, "WA": 0.15, "SA": 0.20, "OTHER": 0.20}
baseline_testing_rate_2017 = {"NSW": 0.62, "VIC": 0.58, "QLD": 0.50, "WA": 0.47, "SA": 0.49, "OTHER": 0.40}

for state in STATES:
    row = {"state": state, **base_covs[state]}
    row["baseline_hiv_testing_rate_2017"] = baseline_testing_rate_2017[state]
    row["covid_lockdown_severity_2020"] = covid_lockdown_severity_2020[state]
    row["epic_nsw_early_access"] = 1 if state == "NSW" else 0
    cov_rows.append(row)

covariates = pd.DataFrame(cov_rows)
covariates.to_csv(os.path.join(OUT_DIR, "state_covariates.csv"), index=False)

print("\nFiles written:")
for f in ["pbs_dispensing_monthly.csv", "hiv_notifications_quarterly.csv", "state_covariates.csv"]:
    df = pd.read_csv(os.path.join(OUT_DIR, f))
    print(f" - {f}: {df.shape[0]} rows, {df.shape[1]} cols")
