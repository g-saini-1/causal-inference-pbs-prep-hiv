"""Tests for the data-construction logic in src/analysis/01_interrupted_time_series.py:
rest-of-country aggregation and the ramp/COVID segment terms. These encode exact,
hand-verified behaviour (NSW excluded, a 6-month ramp cap, a data-derived COVID
trough) rather than being self-evidently correct from the code alone, so a silent
regression here would be easy to miss without a test catching it.
"""

import importlib.util
import os

import pandas as pd
import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_spec = importlib.util.spec_from_file_location(
    "stage1_its", os.path.join(REPO_ROOT, "src", "analysis", "01_interrupted_time_series.py")
)
stage1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(stage1)


@pytest.fixture(scope="module")
def dispensing():
    return stage1.load_pbs_dispensing()


@pytest.fixture(scope="module")
def rest_of_country(dispensing):
    return stage1.build_rest_of_country_series(dispensing)


@pytest.fixture(scope="module")
def v2_fit(rest_of_country):
    model, national = stage1.fit_v2_specification(rest_of_country)
    return model, national


def test_rest_of_country_excludes_nsw(dispensing, rest_of_country):
    non_nsw_total = dispensing.loc[dispensing["state"] != "NSW", "prep_dispensing_count"].sum()
    assert rest_of_country["prep_dispensing_count"].sum() == non_nsw_total


def test_rest_of_country_matches_manual_sum_for_one_month(dispensing, rest_of_country):
    month = pd.Timestamp("2019-06-01")
    expected = dispensing.loc[
        (dispensing["month"] == month) & (dispensing["state"] != "NSW"), "prep_dispensing_count"
    ].sum()
    actual = rest_of_country.loc[rest_of_country["month"] == month, "prep_dispensing_count"].iloc[0]
    assert actual == expected


def test_post_listing_indicator_flips_at_listing_date(v2_fit):
    _, national = v2_fit
    before = national[national["month"] < stage1.PBS_LISTING_DATE]
    on_or_after = national[national["month"] >= stage1.PBS_LISTING_DATE]
    assert (before["post_listing"] == 0).all()
    assert (on_or_after["post_listing"] == 1).all()


def test_early_ramp_is_zero_pre_listing_and_capped_post_listing(v2_fit):
    _, national = v2_fit
    pre = national[national["post_listing"] == 0]
    post = national[national["post_listing"] == 1].reset_index(drop=True)
    assert (pre["early_ramp"] == 0).all()
    # Rises 0, 1, 2, ..., RAMP_MONTHS over the first RAMP_MONTHS + 1 post-listing rows.
    expected_rise = list(range(stage1.RAMP_MONTHS + 1))
    assert post["early_ramp"].iloc[: stage1.RAMP_MONTHS + 1].tolist() == expected_rise
    # Holds at the cap for every month after that, never exceeds it.
    assert (post["early_ramp"].iloc[stage1.RAMP_MONTHS :] == stage1.RAMP_MONTHS).all()


def test_covid_decline_and_recovery_are_zero_outside_the_window(v2_fit):
    _, national = v2_fit
    outside = national[national["covid_period"] == 0]
    assert (outside["covid_decline"] == 0).all()
    assert (outside["covid_recovery"] == 0).all()


def test_covid_decline_and_recovery_form_a_continuous_hinge_at_the_trough(v2_fit):
    _, national = v2_fit
    covid_rows = national[national["covid_period"] == 1].reset_index(drop=True)
    trough_idx = covid_rows["prep_dispensing_count"].idxmin()
    trough_offset = covid_rows["covid_decline"].iloc[trough_idx]

    # Before the trough: decline is still rising, recovery hasn't started.
    assert (covid_rows["covid_recovery"].iloc[:trough_idx] == 0).all()
    # From the trough onward: decline has capped out, recovery is what's moving.
    assert (covid_rows["covid_decline"].iloc[trough_idx:] == trough_offset).all()
    # The two terms meet at the trough with no gap or overlap.
    assert covid_rows["covid_recovery"].iloc[trough_idx] == 0


def test_fit_candidate_families_returns_one_row_per_family(v2_fit):
    _, national = v2_fit
    _, _, _, comparison = stage1.fit_candidate_families(national, stage1.FORMULA_V2)
    assert list(comparison["Candidate"]) == ["OLS", "Poisson", "NB"]
    for col in ["Coefficient (post_listing)", "AIC", "Assumption check", "Autocorrelation check"]:
        assert col in comparison.columns
        assert comparison[col].notna().all()
