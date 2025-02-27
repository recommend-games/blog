# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.7
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
import warnings
from pathlib import Path

import jupyter_black
import numpy as np
import polars as pl
from board_game_recommender import LightGamesRecommender
from election.schulze import compute_pairwise_preferences, schulze_method
from election.trust import user_trust

jupyter_black.load()
rng = np.random.default_rng()

# %%
PROJECT_DIR = Path(".").resolve().parent.parent

DATA_DIR = PROJECT_DIR.parent / "board-game-data"
GAMES_FILE = DATA_DIR / "scraped" / "bgg_GameItem.jl"
RATINGS_FILE = DATA_DIR / "scraped" / "bgg_RatingItem.jl"

SERVER_DIR = PROJECT_DIR.parent / "recommend-games-server"
RECOMMENDER_FILE = SERVER_DIR / "data" / "recommender_light.npz"

PROJECT_DIR, DATA_DIR, GAMES_FILE, RATINGS_FILE, SERVER_DIR, RECOMMENDER_FILE

# %%
NUM_USERS = 10_000
NUM_GAMES = 1_000
NUM_USERS, NUM_GAMES

# %%
games = pl.scan_ndjson(GAMES_FILE).select("bgg_id", "name").collect()
len(games)

# %%
ratings_count = (
    pl.scan_ndjson(RATINGS_FILE)
    .filter(pl.col("bgg_user_rating").is_not_nan())
    .group_by("bgg_id")
    .agg(pl.len())
    .with_columns(p_games=pl.col("len") / pl.sum("len"))
    .sort("len", descending=True)
    .collect()
)
ratings_count.head()

# %%
# Sample or top NUM_GAMES?
# sampled_games = rng.choice(
#     ratings_count["bgg_id"],
#     size=NUM_GAMES,
#     replace=False,
#     p=ratings_count["p_games"],
#     shuffle=False,
# )
sampled_games = ratings_count["bgg_id"].head(NUM_GAMES)
len(sampled_games)

# %%
with warnings.catch_warnings(action="ignore"):
    trust = user_trust(str(RATINGS_FILE), progress_bar=True)
len(trust)

# %%
users, trust_scores = zip(*trust.items())
trust_scores = np.array(trust_scores)
p_users = trust_scores / trust_scores.sum()
trust_scores.shape

# %%
# Sample or top NUM_USERS?
sampled_users = rng.choice(
    users,
    size=NUM_USERS,
    replace=False,
    p=p_users,
    shuffle=False,
)
len(sampled_users)

# %%
recommender = LightGamesRecommender.from_npz(RECOMMENDER_FILE)
recommender.num_games, recommender.num_users

# %%
# The whole matrix at once might be too large
rating_matrix = recommender.recommend_as_numpy(
    users=sampled_users,
    games=sampled_games,
)
rating_matrix.shape

# %%
pairwise_preferences = compute_pairwise_preferences(
    rating_matrix,
    progress_bar=True,
)
pairwise_preferences.shape

# %%
ranking = np.array(
    schulze_method(
        pairwise_preferences,
        progress_bar=True,
    )
)
ranking.shape

# %%
ranked_games = pl.DataFrame(
    {
        "bgg_id": sampled_games[ranking],
        "rank": range(1, len(sampled_games) + 1),
    },
).join(games, on="bgg_id", how="left")
ranked_games.shape

# %%
ranked_games.head(10)
