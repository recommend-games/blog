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
import dataclasses
import jupyter_black
import numpy as np
import polars as pl
import seaborn as sns
from elo.p_deterministic import p_deterministic_experiments
from tqdm import tqdm

jupyter_black.load()

seed = 13

# %%
num_players = (1000,)
num_matches = (1_000_000,)
players_per_match = (2, 3)
p_deterministic = np.linspace(start=0.00, stop=0.99, num=10)
elo_scale = (400,)
num_experiments = (
    len(num_players)
    * len(num_matches)
    * len(players_per_match)
    * len(p_deterministic)
    * len(elo_scale)
)
num_experiments

# %%
experiments = p_deterministic_experiments(
    seed=seed,
    num_players=num_players,
    num_matches=num_matches,
    players_per_match=players_per_match,
    p_deterministic=p_deterministic,
    elo_scale=elo_scale,
)
experiments = tqdm(experiments, desc="Running experiments", total=num_experiments)
results = (
    pl.LazyFrame(dataclasses.asdict(experiment) for experiment in experiments)
    .sort("num_players", "num_matches", "players_per_match", "p_deterministic")
    .collect()
)
results.shape

# %%
results.sample(10, seed=seed)

# %%
results.write_csv("results/p_deterministic.csv", float_precision=5)

# %%
sns.scatterplot(
    data=results,
    x="p_deterministic",
    y="elo_k",
    hue="players_per_match",
)

# %%
results_log = results.filter(pl.col("elo_k") > 0).select(
    "p_deterministic",
    pl.col("elo_k").log().alias("log(elo_k)"),
    "players_per_match",
)
sns.scatterplot(
    data=results_log,
    x="p_deterministic",
    y="log(elo_k)",
    hue="players_per_match",
)

# %%
sns.scatterplot(
    data=results,
    x="p_deterministic",
    y="std_dev",
    hue="players_per_match",
)

# %%
results_log = results.filter(pl.col("std_dev") > 0).select(
    "p_deterministic",
    pl.col("std_dev").log().alias("log(std_dev)"),
    "players_per_match",
)
sns.scatterplot(
    data=results_log,
    x="p_deterministic",
    y="log(std_dev)",
    hue="players_per_match",
)
