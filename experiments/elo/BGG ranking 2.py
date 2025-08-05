# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.17.2
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
import jupyter_black
import polars as pl
from elo.elo_ratings import TwoPlayerElo
from itertools import combinations

jupyter_black.load()

# %%
ratings = (
    pl.scan_ndjson("../../../board-game-data/scraped/bgg_RatingItem.jl")
    .select("bgg_id", "bgg_user_name", "bgg_user_rating", "updated_at")
    .drop_nulls()
    .sort("updated_at")
    .tail(1_000_000)
    # .collect()
)
self_join = ratings.join(
    ratings, on="bgg_user_name", how="left", suffix="_prev"
).filter(pl.col("updated_at_prev") < pl.col("updated_at"))
df_1 = self_join.filter(
    pl.col("bgg_user_rating") > pl.col("bgg_user_rating_prev")
).select(
    game_1="bgg_id",
    game_2="bgg_id_prev",
    updated_at="updated_at",
    updated_at_prev="updated_at_prev",
)
df_2 = self_join.filter(
    pl.col("bgg_user_rating") < pl.col("bgg_user_rating_prev")
).select(
    game_1="bgg_id_prev",
    game_2="bgg_id",
    updated_at="updated_at",
    updated_at_prev="updated_at_prev",
)
df = (
    pl.concat([df_1, df_2])
    .sort("updated_at", "updated_at_prev")
    .select("game_1", "game_2")
    .collect()
)
df.shape

# %%
elo = TwoPlayerElo(elo_k=1.0)
elo.update_elo_ratings_batch(
    df.iter_rows(), progress_bar=True, tqdm_kwargs={"total": len(df)}
)

# %%
sorted(elo.elo_ratings.items(), key=lambda x: -x[1])[:100]
