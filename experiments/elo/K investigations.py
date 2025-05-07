# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.17.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
import jupyter_black
import numpy as np
import polars as pl
import seaborn as sns
from matplotlib import pyplot as plt
from scipy.optimize import curve_fit

jupyter_black.load()

# %%
data = (
    pl.scan_csv("results/p_deterministic*.csv")
    # .filter(pl.col("num_matches") > 1000)
    .with_columns(matches_per_player=pl.col("num_matches") / pl.col("num_players"))
    .sort("p_deterministic")
    .collect()
)
data.shape


# %%
def power_law(x: np.ndarray, a: float, b: float, c: float) -> np.ndarray:
    return a / (x**b) + c


def fit_and_plot(data):
    data = data.filter(pl.col("matches_per_player") > 10)

    if len(data) < 10:
        print(f"Only {len(data)} row(s) provided, skipping…")
        return

    x = data["matches_per_player"].to_numpy()
    y = data["elo_k"].to_numpy()
    popt, pcov = curve_fit(power_law, x, y, bounds=(0, np.inf))
    a, b, c = popt
    print(f"Fitted parameters: a={a:.4f}, b={b:.4f}, c={c:.4f}")
    x_fit = np.linspace(x.min(), x.max(), 100)
    y_fit = power_law(x_fit, *popt)

    _, ax = plt.subplots()
    sns.scatterplot(
        data=data,
        x="matches_per_player",
        y="elo_k",
        hue="players_per_match",
        size="num_players",
        ax=ax,
    )
    sns.lineplot(x=x_fit, y=y_fit, ax=ax)

    return ax


# %%
for (p_deterministic,), group in data.group_by("p_deterministic", maintain_order=True):
    print(f"{p_deterministic=}")
    fit_and_plot(group)
    plt.show()

# %%
