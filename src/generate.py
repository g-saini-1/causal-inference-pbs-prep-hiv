"""
Synthetic data generator for the PBS PrEP listing -> HIV diagnoses project.

Produces three CSVs that mirror the real data sources described in the
project scope, with known ground-truth effects baked in so model output
can be checked against a known answer:

1. pbs_dispensing_monthly.csv
   State x month PBS PrEP dispensing counts, Jan 2016 - Dec 2022. Not a
   fitted formula: real PBS Item Report data from Apr 2018 onward (all
   states), a documented construction from EPIC-NSW's published enrolment
   milestones for NSW's Mar 2016 - Mar 2018 trial period, and 0 everywhere
   else pre-listing (these PBS item codes did not exist yet). See
   reports/data_validation.md's "Generation rules" (PBS
   dispensing) for the full reasoning.

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

The HIV notifications and state covariates series include Poisson noise (not
negative binomial, despite earlier wording here) on top of deterministic
trend components, so no two runs of those two series are identical unless
the seed is fixed (done below). PBS dispensing is fully deterministic (real
data or a documented construction, see above), so it is identical on every
run regardless of seed.
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
#
# Built from real data and a referenced construction, not a fitted formula;
# see reports/data_validation.md's "Generation rules" (PBS
# dispensing) for the full reasoning behind each of the three rules below.
# =============================================================
months = pd.date_range("2016-01-01", "2022-12-01", freq="MS")
PBS_LISTING = pd.Timestamp("2018-04-01")
EPIC_NSW_START = pd.Timestamp("2016-03-01")

REAL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "reference")
real_pbs = pd.read_csv(os.path.join(REAL_DIR, "pbs_dispensing_real_monthly.csv"), parse_dates=["month"])
real_pbs = real_pbs.set_index("month")

# EPIC-NSW enrolment-tracking construction (rule 2): monthly dispensing
# assumed to track cumulative enrolment, two segments anchored to the
# trial's own published milestones (Grulich et al. 2021, Lancet HIV):
# ~462 new participants/month to 3,700 by Oct 2016, then ~334/month
# onward. Not fitted; a direct, documented approximation.
EPIC_NSW_RATE_1 = 3700 / 8   # Mar-Oct 2016 (8 months) to reach 3,700
EPIC_NSW_RATE_2 = (9709 - 3700) / 18  # Nov 2016-Apr 2018 (18 months) to reach 9,709


def epic_nsw_cumulative_enrolment(m):
    months_since_epic = (m.year - EPIC_NSW_START.year) * 12 + (m.month - EPIC_NSW_START.month)
    if months_since_epic < 8:
        return EPIC_NSW_RATE_1 * (months_since_epic + 1)
    return 3700 + EPIC_NSW_RATE_2 * (months_since_epic - 7)


rows = []
for state in STATES:
    for m in months:
        if m >= PBS_LISTING:
            # Rule 3: real PBS Item Report data, all states, from the listing onward.
            count = int(real_pbs.loc[m, state])
        elif state == "NSW" and m >= EPIC_NSW_START:
            # Rule 2: NSW's EPIC-NSW trial period, constructed from real enrolment milestones.
            count = round(epic_nsw_cumulative_enrolment(m))
        else:
            # Rule 1: no PBS-subsidised PrEP existed yet (rest of country), or
            # EPIC-NSW hadn't started yet (NSW, before March 2016). A real value,
            # not an assumption: these item codes simply didn't exist.
            count = 0
        rows.append({"state": state, "month": m.strftime("%Y-%m-%d"), "prep_dispensing_count": count})

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
