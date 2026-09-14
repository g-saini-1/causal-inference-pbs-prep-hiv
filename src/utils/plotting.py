"""Shared matplotlib styling and a figure-save helper, for consistent charts
across the analysis scripts and notebook."""

import os

import matplotlib.pyplot as plt

FIGURES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "reports", "figures")

NATIONAL_COLOR = "#2a78d6"

STATE_COLORS = {
    "NSW": "#eb6e3c",
    "VIC": "#24b27f",
    "QLD": "#eda50a",
    "WA": "#e880a7",
    "SA": "#0a880a",
    "OTHER": "#6857d7",
}


def set_style():
    plt.rcParams.update({
        "figure.figsize": (10, 6),
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.alpha": 0.3,
        "font.size": 11,
    })


def save_figure(fig, filename):
    os.makedirs(FIGURES_DIR, exist_ok=True)
    path = os.path.join(FIGURES_DIR, filename)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    return path
