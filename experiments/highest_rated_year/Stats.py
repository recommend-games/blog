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

from highest_rated_year import t_test

jupyter_black.load()
pl.Config.set_tbl_rows(100)

# %%
base_dir = Path(".").resolve()
data_dir = base_dir / "data"
base_dir, data_dir

# %% [markdown]
# # Rankings

# %%
data_from_rankings = (
    pl.scan_csv(data_dir / "years_from_rankings.csv")
    .filter(pl.col("year") >= 1970)
    .collect()
)
data_from_rankings.shape

# %%
data_from_rankings = t_test(data_from_rankings, y_column="avg_rating")
data_from_rankings.shape

# %%
data_from_rankings.sort(pl.col("avg_rating_p_value")).head(10)

# %%
data_from_rankings = t_test(data_from_rankings, y_column="bayes_rating")
data_from_rankings.shape

# %%
data_from_rankings.sort(pl.col("bayes_rating_p_value")).head(10)

# %%
# TODO: Write results back to CSV

# %% [markdown]
# # Ratings

# %%
data_from_ratings = (
    pl.scan_csv(data_dir / "years_from_ratings.csv")
    .filter(pl.col("year") >= 1970)
    .collect()
)
data_from_ratings.shape

# %%
data_from_ratings = t_test(data_from_ratings, y_column="avg_rating")
data_from_ratings.shape

# %%
data_from_ratings.sort(pl.col("avg_rating_p_value")).head(10)

# %%
# TODO: Write results back to CSV
