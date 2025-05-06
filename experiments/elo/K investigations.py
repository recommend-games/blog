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
    pl.scan_csv("results/p_deterministic.csv")
    .filter(pl.col("num_matches") > 1000)
    .with_columns(matches_per_player=pl.col("num_matches") / pl.col("num_players"))
    .collect()
)
data.shape


# %%
def power_law(x: np.ndarray, a: float) -> np.ndarray:
    return a / (x**0.5)


def fit_and_plot(data):
    x = data["matches_per_player"].to_numpy()
    y = data["elo_k"].to_numpy()
    popt, pcov = curve_fit(power_law, x, y, bounds=(0, np.inf))
    (a,) = popt
    print(f"Fitted parameters: a={a:.4f}, b={.5:.4f}, c={.0:.4f}")
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
fit_and_plot(data.filter(pl.col("p_deterministic") == 0.25))
plt.show()

# %%
fit_and_plot(data.filter(pl.col("p_deterministic") == 0.5))
plt.show()

# %%
fit_and_plot(data.filter(pl.col("p_deterministic") == 0.75))
plt.show()
