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
experiments = p_deterministic_experiments(
    seed=seed,
    num_players=1000,
    num_matches=1_000_000,
    players_per_match=2,
    p_deterministic=np.linspace(start=0.01, stop=0.99, num=99),
    elo_scale=400,
)
results = (
    pl.LazyFrame(dataclasses.asdict(experiment) for experiment in tqdm(experiments))
    .sort("num_players", "num_matches", "players_per_match", "p_deterministic")
    .collect()
)
results.shape

# %%
results.sample(10, seed=seed)

# %%
results.write_csv("results/p_deterministic.csv", float_precision=5)

# %%
sns.scatterplot(data=results, x="p_deterministic", y="elo_k")

# %%
sns.scatterplot(x=results["p_deterministic"], y=np.log(results["elo_k"]))

# %%
sns.scatterplot(data=results, x="p_deterministic", y="std_dev")

# %%
sns.scatterplot(x=results["p_deterministic"], y=np.log(results["std_dev"]))
