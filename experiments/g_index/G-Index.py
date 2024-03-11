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
from g_index import h_and_g_index

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
game_indexes = h_and_g_index(
    counts=play_counts,
    count_col="bgg_user_play_count",
    target_col="bgg_id",
)

# %%
game_result = (
    game_data.join(game_indexes, on="bgg_id", how="inner")
    .sort(["h_index", "g_index", "bgg_id"], descending=[True, True, False])
    .collect()
)

# %%
game_result.head(10)

# %%
game_result.filter(pl.col("h_index") >= 10).write_csv("games.csv")

# %% [markdown]
# ## Players

# %%
player_result = h_and_g_index(
    counts=play_counts,
    count_col="bgg_user_play_count",
    target_col="bgg_user_name",
).collect()
player_result.shape

# %%
player_result.head(10)

# %%
player_result.filter(pl.col("h_index") >= 10).write_csv("players.csv")
