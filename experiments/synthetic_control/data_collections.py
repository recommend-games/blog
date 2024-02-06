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
)
pivoted.shape

# %%
pivoted.head(10)

# %%
game_columns = sorted(pivoted.select(pl.exclude("day")).columns, key=int)
df = (
    pivoted.lazy()
    .sort("day")
    .select(
        "day",
        pl.col(*game_columns)
        .interpolate()
        .fill_null(strategy="forward")
        .cast(pl.Int64),
    )
    .collect()
)
df.write_csv("num_collections.csv")
df.shape
