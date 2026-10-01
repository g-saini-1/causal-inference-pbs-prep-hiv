"""Generates docs/figures/distribution_shapes_general_chart.png: an
illustrative, non-project-specific comparison of how OLS/Gaussian, Poisson,
and NB look as their mean grows, referenced from docs/model_family_concepts.md
(Section 4).

Unlike src/analysis/*.py, this script doesn't depend on the project's data.
The three means and NB's alpha are chosen purely to make the shapes visible,
not fitted from data; see reports/stage1_interrupted_time_series.md (Model
family selection) for this project's own fitted values plotted the same way.
"""

import os

import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import nbinom, norm, poisson

from src.utils.plotting import set_style

DOCS_FIGURES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "docs", "figures")

MEANS = [2, 10, 50]
OLS_SD = 1.5
NB_ALPHA = 0.5  # illustrative, not this project's fitted value


def nb_pmf(k, mu, alpha):
    n = 1 / alpha
    p = n / (n + mu)
    return nbinom.pmf(k, n, p)


def plot_general_shapes():
    fig, axes = plt.subplots(3, 3, figsize=(12, 9))

    for col, mu in enumerate(MEANS):
        ax = axes[0][col]
        xs = np.linspace(mu - 4 * OLS_SD, mu + 4 * OLS_SD, 400)
        ax.plot(xs, norm.pdf(xs, mu, OLS_SD), color="#55A868", linewidth=2)
        ax.fill_between(xs, norm.pdf(xs, mu, OLS_SD), color="#55A868", alpha=0.3)
        ax.set_xlim(mu - 4 * 7, mu + 4 * 7)
        ax.set_title(f"mean = {mu}", fontsize=10)
        if col == 0:
            ax.set_ylabel("OLS / Gaussian\n(SD fixed at 1.5)")

        ax = axes[1][col]
        sd = np.sqrt(mu)
        lo, hi = max(0, mu - 4 * sd), mu + 4 * sd + 1
        k = np.arange(int(np.floor(lo)), int(np.ceil(hi)) + 1)
        ax.bar(k, poisson.pmf(k, mu), width=1, color="#4C72B0")
        if col == 0:
            ax.set_ylabel("Poisson\n(SD = √mean)")

        ax = axes[2][col]
        nb_sd = np.sqrt(mu + NB_ALPHA * mu**2)
        lo, hi = max(0, mu - 4 * nb_sd), mu + 4 * nb_sd + 1
        k = np.arange(int(np.floor(lo)), int(np.ceil(hi)) + 1)
        ax.bar(k, nb_pmf(k, mu, NB_ALPHA), width=1, color="#C44E52")
        if col == 0:
            ax.set_ylabel(f"NB (α={NB_ALPHA}, illustrative)\n(SD = √(mean+α·mean²))")
        ax.set_xlabel("Count")

    fig.suptitle("General shape by family, as the mean grows (illustrative, not project-specific)", fontsize=13)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    return fig


def main():
    set_style()
    os.makedirs(DOCS_FIGURES_DIR, exist_ok=True)
    fig = plot_general_shapes()
    path = os.path.join(DOCS_FIGURES_DIR, "distribution_shapes_general_chart.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    print(f"Figure written: {path}")


if __name__ == "__main__":
    main()
