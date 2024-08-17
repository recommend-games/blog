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

jupyter_black.load()
pl.Config.set_tbl_rows(100)

# %%
base_dir = Path(".").resolve()
data_dir = base_dir / "data"
base_dir, data_dir

# %% [markdown]
# # Rankings

# %%
years_from_rankings = pl.read_csv(data_dir / "years_from_rankings.csv")
years_from_rankings.shape

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
years_from_ratings = pl.read_csv(data_dir / "years_from_ratings.csv")
years_from_ratings.shape

# %%
data_from_ratings = years_from_ratings.filter(pl.col("year") >= 1970)
model_from_ratings = sm.OLS(
    data_from_ratings["avg_rating"].to_numpy(),
    sm.add_constant(data_from_ratings["year"].to_numpy()),
)
results_from_ratings = model_from_ratings.fit()
results_from_ratings.summary().tables[1]
