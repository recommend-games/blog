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

jupyter_black.load()

pl.Config.set_tbl_rows(100)

# %% [markdown]
# # Rankings

# %%
base_dir = Path("/Users/markus/Recommend.Games/bgg-ranking-historicals/").resolve()
file_path = max(base_dir.glob("*.csv"))
file_path

# %%
data = (
    pl.scan_csv(file_path)
    .select(
        bgg_id="ID",
        name="Name",
        year="Year",
        avg_rating="Average",
        bayes_rating="Bayes average",
        num_ratings="Users rated",
    )
    .filter(1900 <= pl.col("year"))
    .filter(pl.col("year") <= 2023)
    .group_by("year")
    .agg(
        num_games=pl.len(),
        avg_rating=pl.mean("avg_rating"),
        bayes_rating=pl.mean("bayes_rating"),
    )
    .sort("year")
    .collect()
)
data.shape

# %%
data.tail(100)

# %% [markdown]
# # Ratings

# %%
games = (
    pl.scan_ndjson("../../../board-game-data/scraped/bgg_GameItem.jl")
    .select("bgg_id", "name", "year")
    .filter(pl.col("year") >= 1900)
    .filter(pl.col("year") <= 2023)
)
ratings = (
    pl.scan_ndjson("../../../board-game-data/scraped/bgg_RatingItem.jl")
    .select("bgg_id", "bgg_user_rating")
    .drop_nulls()
)
joined = (
    games.join(ratings, on="bgg_id", how="inner")
    .select(
        "year",
        rating="bgg_user_rating",
    )
    .collect()
)
data = (
    joined.group_by("year")
    .agg(
        num_ratings=pl.len(),
        avg_rating=pl.mean("rating"),
    )
    .sort("year")
)
joined.shape, data.shape

# %%
data.tail(100)

# %%
sns.barplot(data=joined.filter(pl.col("year") >= 2014), x="year", y="rating")
