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
game_data = pl.scan_ndjson(DATA_DIR / "scraped" / "bgg_GameItem.jl").select(
    "bgg_id",
    "name",
)

# %%
play_counts = (
    pl.scan_ndjson(DATA_DIR / "scraped" / "bgg_RatingItem.jl")
    .select("bgg_id", "bgg_user_name", "bgg_user_play_count")
    .drop_nulls()
    .filter(pl.col("bgg_user_play_count") > 0)
)

# %%
game_counts = (
    play_counts.select(
        "bgg_id",
        "bgg_user_play_count",
        pl.col("bgg_user_play_count")
        .rank("ordinal", descending=True)
        .over("bgg_id")
        .alias("rank"),
    )
    .filter(pl.col("bgg_user_play_count") >= pl.col("rank"))
    .group_by("bgg_id")
    .agg(pl.col("rank").max().alias("ghi"))
)

# %%
game_result = (
    game_data.join(game_counts, on="bgg_id", how="inner")
    .sort("ghi", descending=True)
    .select(pl.col("ghi").rank("min", descending=True).alias("rank"), pl.all())
    .collect()
)

# %%
game_result.head(10)

# %%
game_result.filter(pl.col("ghi") >= 10).write_csv("games.csv")
