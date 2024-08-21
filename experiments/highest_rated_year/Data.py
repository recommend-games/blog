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

from highest_rated_year import load_years_from_rankings, load_years_from_ratings

jupyter_black.load()
pl.Config.set_tbl_rows(100)

# %%
base_dir = Path(".").resolve()
save_dir = base_dir / "data"
save_dir.mkdir(parents=True, exist_ok=True)
project_dir = base_dir.parent.parent
rankings_dir = project_dir.parent / "bgg-ranking-historicals"
data_dir = project_dir.parent / "board-game-data"
base_dir, save_dir, project_dir, rankings_dir, data_dir

# %% [markdown]
# # Rankings

# %%
years_from_rankings = load_years_from_rankings(rankings_dir)
years_from_rankings.shape

# %%
years_from_rankings.filter(pl.col("year") >= 1990)

# %%
years_from_rankings.write_csv(save_dir / "years_from_rankings.csv", float_precision=5)

# %% [markdown]
# # Ratings

# %%
years_from_ratings = load_years_from_ratings(data_dir)
years_from_ratings.shape

# %%
years_from_ratings.filter(pl.col("year") >= 1990)

# %%
years_from_ratings.write_csv(save_dir / "years_from_ratings.csv", float_precision=5)
