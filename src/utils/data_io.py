"""Shared data-loading helpers for the analysis scripts and notebook."""

import os

import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data", "synthetic")

PBS_LISTING_DATE = pd.Timestamp("2018-04-01")
EPIC_NSW_START_DATE = pd.Timestamp("2016-03-01")


def load_pbs_dispensing():
    df = pd.read_csv(os.path.join(DATA_DIR, "pbs_dispensing_monthly.csv"), parse_dates=["month"])
    return df


def load_hiv_notifications():
    df = pd.read_csv(os.path.join(DATA_DIR, "hiv_notifications_quarterly.csv"), parse_dates=["quarter_start"])
    return df


def load_state_covariates():
    return pd.read_csv(os.path.join(DATA_DIR, "state_covariates.csv"))
