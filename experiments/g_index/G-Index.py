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

BASE_DIR = Path().resolve().parent.parent
DATA_DIR = BASE_DIR.parent / "board-game-data"

jupyter_black.load()

# %%
g_index = (
    pl.scan_ndjson(DATA_DIR / "scraped" / "bgg_RatingItem.jl")
    .select("bgg_id", "bgg_user_name", "bgg_user_play_count")
    .drop_nulls()
    .filter(pl.col("bgg_user_play_count") > 0)
    .select(
        "bgg_id",
        "bgg_user_play_count",
        pl.col("bgg_user_play_count")
        .rank("ordinal", descending=True)
        .over("bgg_id")
        .alias("rank"),
    )
    .filter(pl.col("bgg_user_play_count") >= pl.col("rank"))
    .group_by("bgg_id")
    .agg(pl.col("rank").max().alias("g_index"))
)

# %%
games = pl.scan_ndjson(DATA_DIR / "scraped" / "bgg_GameItem.jl").select(
    "bgg_id",
    "name",
)

# %%
result = (
    games.join(g_index, on="bgg_id", how="inner")
    .sort("g_index", descending=True)
    .select(pl.col("g_index").rank("min", descending=True).alias("rank"), pl.all())
    .collect()
)

# %%
result.head(10)

# %%
result.filter(pl.col("g_index") >= 10).write_csv("g_index.csv")
