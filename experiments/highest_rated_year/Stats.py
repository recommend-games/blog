# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.4
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
from pathlib import Path

import jupyter_black
import polars as pl
import statsmodels.api as sm

from highest_rated_year import load_years_from_rankings, load_years_from_ratings

jupyter_black.load()
pl.Config.set_tbl_rows(100)

# %%
base_dir = Path(".").resolve()
project_dir = base_dir.parent.parent
rankings_dir = project_dir.parent / "bgg-ranking-historicals"
data_dir = project_dir.parent / "board-game-data"
base_dir, project_dir, rankings_dir, data_dir

# %% [markdown]
# # Rankings

# %%
years_from_rankings = load_years_from_rankings(rankings_dir)
years_from_rankings.shape

# %%
years_from_rankings.filter(pl.col("year") >= 1990)

# %%
data_from_rankings = years_from_rankings.filter(pl.col("year") >= 1970)
model_from_rankings = sm.OLS(
    data_from_rankings["avg_rating"].to_numpy(),
    sm.add_constant(data_from_rankings["year"].to_numpy()),
)
results_from_rankings = model_from_rankings.fit()
results_from_rankings.summary().tables[1]

# %% [markdown]
# # Ratings

# %%
years_from_ratings = load_years_from_ratings(data_dir)
years_from_ratings.shape

# %%
years_from_ratings.filter(pl.col("year") >= 1990)

# %%
data_from_ratings = years_from_ratings.filter(pl.col("year") >= 1970)
model_from_ratings = sm.OLS(
    data_from_ratings["avg_rating"].to_numpy(),
    sm.add_constant(data_from_ratings["year"].to_numpy()),
)
results_from_ratings = model_from_ratings.fit()
results_from_ratings.summary().tables[1]
