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
from datetime import date
from pathlib import Path

import jupyter_black
import polars as pl
import seaborn as sns

from highest_rated_year import save_plots

jupyter_black.load()
pl.Config.set_tbl_rows(100)
sns.set_style("dark")

# %%
seed = date.today().year

base_dir = Path(".").resolve()
data_dir = base_dir / "data"
plot_dir = base_dir / "plots"

seed, base_dir, data_dir, plot_dir

# %% [markdown]
# # Rankings

# %%
years_from_rankings = pl.read_csv(data_dir / "years_from_rankings.csv")
data_from_rankings = years_from_rankings.filter(pl.col("year") >= 1970)
years_from_rankings.shape, data_from_rankings.shape

# %%
save_plots(
    data=data_from_rankings,
    y_column="avg_rating",
    sizes_column="rel_num_games",
    title="Yearly average ratings from ranked games",
    plot_dir=plot_dir,
    file_name="avg_ratings_from_rankings",
    show=True,
    seed=seed,
)

# %%
save_plots(
    data=data_from_rankings,
    y_column="bayes_rating",
    sizes_column="rel_num_games",
    title="Yearly average geek score from ranked games",
    plot_dir=plot_dir,
    file_name="bayes_ratings_from_rankings",
    show=True,
    seed=seed,
)

# %% [markdown]
# # Ratings

# %%
years_from_ratings = pl.read_csv(data_dir / "years_from_ratings.csv")
data_from_ratings = years_from_ratings.filter(pl.col("year") >= 1970)
years_from_ratings.shape, data_from_ratings.shape

# %%
save_plots(
    data=data_from_ratings,
    y_column="avg_rating",
    sizes_column="rel_num_ratings",
    title="Yearly average ratings",
    plot_dir=plot_dir,
    file_name="avg_ratings_from_ratings",
    show=True,
    seed=seed,
)
