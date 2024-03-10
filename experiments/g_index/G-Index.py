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

# %% [markdown]
# ## Games

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

# %% [markdown]
# ## Players

# %%
player_result = (
    play_counts.sort(
        ["bgg_user_name", "bgg_user_play_count"],
        descending=[False, True],
    )
    .select(
        pl.col("bgg_user_name"),
        pl.col("bgg_user_play_count"),
        pl.col("bgg_user_play_count")
        .cum_sum()
        .over("bgg_user_name")
        .alias("bgg_user_play_count_cum_sum"),
        pl.col("bgg_user_play_count")
        .rank("ordinal", descending=True)
        .over("bgg_user_name")
        .alias("rank"),
    )
    .with_columns(
        pl.when(pl.col("rank") <= pl.col("bgg_user_play_count"))
        .then(pl.col("rank"))
        .alias("h_index_rank"),
        pl.when(pl.col("rank") ** 2 <= pl.col("bgg_user_play_count_cum_sum"))
        .then(pl.col("rank"))
        .alias("g_index_rank"),
    )
    .group_by("bgg_user_name")
    .agg(
        pl.col("h_index_rank").max().alias("h_index"),
        pl.col("g_index_rank").max().alias("g_index"),
    )
    .sort(["h_index", "g_index", "bgg_user_name"], descending=[True, True, False])
    .select(
        pl.col("h_index").rank("min", descending=True).alias("rank_h_index"),
        pl.col("h_index"),
        pl.col("g_index").rank("min", descending=True).alias("rank_g_index"),
        pl.col("g_index"),
        pl.col("bgg_user_name"),
    )
    .collect()
)
player_result.shape

# %%
player_result.head(10)

# %%
player_result.filter(pl.col("h_index") >= 10).write_csv("players.csv")
