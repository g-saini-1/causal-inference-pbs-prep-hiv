"""Tests for src/generate.py's PBS dispensing series: the three generation
rules (rest of country zero pre-listing, NSW's EPIC-NSW construction, real
data from April 2018 onward) and the ground-truth checks that justify them.
See reports/data_validation.md's "Generation rules" (PBS
dispensing) for the full reasoning behind each rule tested here.

HIV notifications and state covariates are not covered yet.
"""

import importlib.util
import os

import pandas as pd
import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_spec = importlib.util.spec_from_file_location("generate", os.path.join(REPO_ROOT, "src", "generate.py"))
gen = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gen)  # runs the full generator; deterministic and idempotent, see module docstring

NON_NSW_STATES = [s for s in gen.STATES if s != "NSW"]


@pytest.fixture(scope="module")
def pbs():
    return gen.pbs


@pytest.fixture(scope="module")
def real_reference():
    path = os.path.join(REPO_ROOT, "data", "reference", "pbs_dispensing_real_monthly.csv")
    return pd.read_csv(path, parse_dates=["month"])


def test_full_series_covers_expected_window(pbs):
    # 84 months (Jan 2016 - Dec 2022) x 6 states
    assert pbs.shape == (504, 3)
    assert pbs["month"].nunique() == 84
    assert set(pbs["state"].unique()) == set(gen.STATES)


def test_no_negative_or_missing_counts(pbs):
    assert pbs["prep_dispensing_count"].notna().all()
    assert (pbs["prep_dispensing_count"] >= 0).all()


# --- Rule 1: rest of country (NSW excluded), before April 2018, is zero ---


def test_rest_of_country_zero_before_pbs_listing(pbs):
    pre = pbs[(pbs["state"].isin(NON_NSW_STATES)) & (pd.to_datetime(pbs["month"]) < gen.PBS_LISTING)]
    assert len(pre) == len(NON_NSW_STATES) * 27  # Jan 2016 - Mar 2018
    assert (pre["prep_dispensing_count"] == 0).all()


# --- Rule 2: NSW, March 2016 - March 2018, constructed from EPIC-NSW enrolment ---


def test_nsw_zero_before_epic_nsw_start(pbs):
    pre_epic = pbs[(pbs["state"] == "NSW") & (pd.to_datetime(pbs["month"]) < gen.EPIC_NSW_START)]
    assert len(pre_epic) == 2  # Jan, Feb 2016
    assert (pre_epic["prep_dispensing_count"] == 0).all()


def test_epic_nsw_enrolment_matches_first_milestone():
    # 3,700 participants by 31 Oct 2016, per Grulich et al. 2021 (Lancet HIV)
    assert gen.epic_nsw_cumulative_enrolment(pd.Timestamp("2016-10-01")) == pytest.approx(3700)


def test_epic_nsw_enrolment_rate_changes_after_first_milestone():
    oct_2016 = gen.epic_nsw_cumulative_enrolment(pd.Timestamp("2016-10-01"))
    nov_2016 = gen.epic_nsw_cumulative_enrolment(pd.Timestamp("2016-11-01"))
    dec_2016 = gen.epic_nsw_cumulative_enrolment(pd.Timestamp("2016-12-01"))
    assert nov_2016 - oct_2016 == pytest.approx(gen.EPIC_NSW_RATE_2)
    assert dec_2016 - nov_2016 == pytest.approx(gen.EPIC_NSW_RATE_2)
    assert gen.EPIC_NSW_RATE_2 < gen.EPIC_NSW_RATE_1  # recruitment slows after the initial target is hit


def test_nsw_construction_matches_function_in_generated_data(pbs):
    construction = pbs[
        (pbs["state"] == "NSW")
        & (pd.to_datetime(pbs["month"]) >= gen.EPIC_NSW_START)
        & (pd.to_datetime(pbs["month"]) < gen.PBS_LISTING)
    ].copy()
    assert len(construction) == 25  # Mar 2016 - Mar 2018
    expected = construction["month"].apply(lambda m: round(gen.epic_nsw_cumulative_enrolment(pd.Timestamp(m))))
    assert (construction["prep_dispensing_count"] == expected).all()


def test_nsw_construction_is_nondecreasing(pbs):
    construction = pbs[
        (pbs["state"] == "NSW")
        & (pd.to_datetime(pbs["month"]) >= gen.EPIC_NSW_START)
        & (pd.to_datetime(pbs["month"]) < gen.PBS_LISTING)
    ].sort_values("month")
    assert construction["prep_dispensing_count"].is_monotonic_increasing


# --- Rule 3: April 2018 onward, all states, real PBS Item Report data ---


def test_post_listing_matches_real_reference_exactly(pbs, real_reference):
    post = pbs[pd.to_datetime(pbs["month"]) >= gen.PBS_LISTING].copy()
    post["month"] = pd.to_datetime(post["month"])
    real_long = real_reference.melt(id_vars="month", var_name="state", value_name="real_count")
    merged = post.merge(real_long, on=["state", "month"], how="left")
    assert merged["real_count"].notna().all()  # every post-listing row has a real-data match
    assert (merged["prep_dispensing_count"] == merged["real_count"]).all()


def test_real_reference_file_covers_full_window_no_gaps(real_reference):
    assert real_reference.shape == (57, 7)  # Apr 2018 - Dec 2022, 6 state columns + month
    assert real_reference.drop(columns="month").notna().all().all()
    assert (real_reference.drop(columns="month") >= 0).all().all()
