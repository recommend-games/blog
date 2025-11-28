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
users = (
    pl.scan_ndjson("../../../board-game-data/scraped/bgg_RatingItem.jl")
    .select("bgg_id", "bgg_user_name", "bgg_user_rating")
    .drop_nulls()
    .group_by("bgg_user_name")
    .agg(
        num_rated_games=pl.len(),
        ratings=pl.struct("bgg_id", "bgg_user_rating").shuffle(),
    )
    .filter(pl.col("num_rated_games") > 1)
    .select(pl.col("ratings").shuffle())
    .collect()["ratings"]
)
len(users)

# %%
users.sample(10)


# %%
def matches_from_ratings(users):
    for user in users:
        for game_1, game_2 in combinations(user, 2):
            if game_1["bgg_user_rating"] > game_2["bgg_user_rating"]:
                yield game_1["bgg_id"], game_2["bgg_id"]
            elif game_1["bgg_user_rating"] < game_2["bgg_user_rating"]:
                yield game_2["bgg_id"], game_1["bgg_id"]


# %%
elo = TwoPlayerElo()
elo.update_elo_ratings_batch(matches_from_ratings(users), progress_bar=True)

# %%
sorted(elo.elo_ratings.items(), key=lambda x: -x[1])[:100]
