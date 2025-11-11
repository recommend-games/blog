# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.18.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
import jupyter_black
import polars as pl
import seaborn as sns
from pathlib import Path

jupyter_black.load()
sns.set_style("dark")

seed = 13

# %%
path = Path("../csv/p_deterministic.csv").resolve()
path

# %%
results = pl.read_csv(path)
results.shape

# %%
results.sample(10, seed=seed)

# %%
results.group_by("players_per_match").agg(pl.len()).sort("players_per_match")

# %%
plot_data = (
    results.filter(pl.col("p_deterministic") <= 0.9)
    .rename({"elo_k": "k*"})
    .with_columns(pl.col("players_per_match").cast(pl.String))
)
sns.scatterplot(
    data=plot_data,
    x="p_deterministic",
    y="k*",
    hue="players_per_match",
)

# %%
sns.scatterplot(
    data=plot_data,
    x="p_deterministic",
    y="std_dev",
    hue="players_per_match",
)

# %%
plot_data = (
    results.filter(pl.col("p_deterministic") <= 0.9)
    .filter(pl.col("elo_k") > 0)
    .select(
        "p_deterministic",
        pl.col("elo_k").log().alias("log(k*)"),
        pl.col("std_dev").log().alias("log(std_dev)"),
        pl.col("players_per_match").cast(pl.String),
    )
)
sns.scatterplot(
    data=plot_data,
    x="p_deterministic",
    y="log(k*)",
    hue="players_per_match",
)

# %%
sns.scatterplot(
    data=plot_data,
    x="p_deterministic",
    y="log(std_dev)",
    hue="players_per_match",
)
