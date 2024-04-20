# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
from pathlib import Path
import jupyter_black
import polars as pl

jupyter_black.load()

PROJECT_DIR = Path(".").resolve()
BASE_DIR = PROJECT_DIR.parent.parent
DATA_DIR = BASE_DIR.parent / "board-game-data"
PROJECT_DIR, BASE_DIR, DATA_DIR

# %%
ratings = (
    pl.scan_ndjson(DATA_DIR / "scraped" / "bgg_RatingItem.jl")
    .select("bgg_id", "bgg_user_name", "bgg_user_rating")
    .drop_nulls()
)
users = (
    pl.scan_ndjson(DATA_DIR / "scraped" / "bgg_UserItem.jl")
    .select("bgg_user_name", "country")
    .drop_nulls()
)
data = ratings.join(other=users, on="bgg_user_name", how="inner")

# %%
data.select(pl.n_unique("bgg_id", "bgg_user_name", "country")).collect()

# %%
bayes = (
    data.with_columns(num_ratings_per_country=pl.len().over("country"))
    .filter(pl.col("num_ratings_per_country") >= 10_000)
    .with_columns(num_dummies=pl.col("num_ratings_per_country") / 10_000)
    .filter(
        pl.len().over("country", "bgg_id")
        >= pl.min_horizontal(3 * pl.col("num_dummies"), 30)
    )
    .group_by("country", "bgg_id")
    .agg(
        pl.col("num_dummies").first(),
        num_ratings=pl.len(),
        avg_rating=pl.col("bgg_user_rating").mean(),
    )
    .with_columns(
        bayes_rating=(
            pl.col("avg_rating") * pl.col("num_ratings") + 5.5 * pl.col("num_dummies")
        )
        / (pl.col("num_ratings") + pl.col("num_dummies"))
    )
    .with_columns(
        rank=pl.col("bayes_rating").rank(method="min", descending=True).over("country")
    )
    .sort(
        "num_dummies",
        "country",
        "rank",
        "bgg_id",
        descending=[True, False, False, False],
    )
    .collect()
)
bayes.shape

# %%
bayes.filter(pl.col("rank") == 1).head(10)

# %%
bayes.filter(pl.col("rank") == 1)["bgg_id"].value_counts(sort=True).head(10)

# %%
round(
    bayes.group_by("country").agg(pl.col("num_dummies").first())["num_dummies"].sum()
    * 10_000
)

# %%
bayes.select(
    "country",
    "rank",
    "bgg_id",
    "avg_rating",
    "bayes_rating",
    "num_ratings",
).write_csv("rankings.csv", float_precision=5)
