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
from datetime import date
from pathlib import Path
import polars as pl

try:
    import jupyter_black

    jupyter_black.load()
except:
    pass

# %%
rankings_file = (
    Path().resolve().parent.parent.parent
    / "board-game-data"
    / "scraped"
    / "bgg_RatingItem.jl"
)
rankings_file

# %%
max_games = 50_000
min_date = date(2021, 1, 1)

# %%
schema = {
    "bgg_id": pl.Int64,
    # "bgg_user_owned": pl.Boolean,
    # "bgg_user_rating": pl.Float64,
    # "bgg_user_want_to_play": pl.Boolean,
    "updated_at": pl.Datetime,
    # "bgg_user_play_count": pl.Int64,
    # "bgg_user_wishlist": pl.Int64,
}

# %%
collection_counts = (
    pl.scan_ndjson(rankings_file, schema=schema)
    .drop_nulls(["bgg_id", "updated_at"])
    .sort("bgg_id", "updated_at")
    .group_by_dynamic("updated_at", every="1d", by="bgg_id", check_sorted=False)
    .agg(pl.len().alias("num_collections"))
    .with_columns(
        pl.col("updated_at").dt.date().alias("day"),
        pl.col("num_collections").cum_sum().over("bgg_id"),
    )
    .collect()
)
collection_counts.shape

# %%
collection_counts.filter(pl.col("bgg_id") == 13).tail(20)

# %%
pivoted = collection_counts.pivot(
    values="num_collections",
    index="day",
    columns="bgg_id",
).sort("day")
pivoted.shape

# %%
pivoted.head(10)

# %%
top_games = (
    pivoted.select(pl.exclude("day").max())
    .transpose(
        include_header=True,
        header_name="bgg_id",
        column_names=("max_count",),
    )
    .cast(pl.Int32)
    .sort("max_count", descending=True)["bgg_id"][:max_games]
    .sort()
    .cast(pl.String)
)
len(top_games)

# %%
df = pivoted.lazy().select(
    "day",
    pl.col(*top_games).interpolate().fill_null(strategy="forward").cast(pl.Int64),
)
if min_date:
    df = df.filter(pl.col("day") >= min_date)
df = df.collect()
df.write_csv("num_collections.csv")
df.shape
