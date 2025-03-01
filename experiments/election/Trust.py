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
from election.schulze import schulze_method
from election.trust import user_trust

jupyter_black.load()
rng = np.random.default_rng(seed=13)

# %%
BASE_DIR = Path(".").resolve()
RESULTS_DIR = BASE_DIR / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
PROJECT_DIR = BASE_DIR.parent.parent

DATA_DIR = PROJECT_DIR.parent / "board-game-data"
GAMES_FILE = DATA_DIR / "scraped" / "bgg_GameItem.jl"
RATINGS_FILE = DATA_DIR / "scraped" / "bgg_RatingItem.jl"

SERVER_DIR = PROJECT_DIR.parent / "recommend-games-server"
RECOMMENDER_FILE = SERVER_DIR / "data" / "recommender_light.npz"

BASE_DIR, RESULTS_DIR, PROJECT_DIR, DATA_DIR, GAMES_FILE, RATINGS_FILE, SERVER_DIR, RECOMMENDER_FILE

# %%
NUM_USERS = 100_000
NUM_GAMES = 100
NUM_USERS, NUM_GAMES

# %%
games = pl.scan_ndjson(GAMES_FILE).select("bgg_id", "name").collect()
len(games)

# %%
ratings_count_file = RESULTS_DIR / "ratings_count.csv"
if ratings_count_file.exists():
    ratings_count = pl.read_csv(ratings_count_file)
else:
    ratings_count = (
        pl.scan_ndjson(RATINGS_FILE)
        .filter(pl.col("bgg_user_rating").is_not_nan())
        .group_by("bgg_id")
        .agg(pl.len())
        .with_columns(p_games=pl.col("len") / pl.sum("len"))
        .sort("len", descending=True)
        .collect()
    )
    ratings_count.write_csv(ratings_count_file, float_precision=12)
ratings_count.head()

# %%
sampled_games = ratings_count["bgg_id"].head(NUM_GAMES)
len(sampled_games)

# %%
trust_file = RESULTS_DIR / "trust.csv"
if trust_file.exists():
    trust_df = pl.read_csv(trust_file)
else:
    with warnings.catch_warnings(action="ignore"):
        trust = user_trust(str(RATINGS_FILE), progress_bar=True)
    trust_df = (
        pl.DataFrame(
            {
                "bgg_user_name": trust.keys(),
                "trust": trust.values(),
            }
        )
        .filter(pl.col("trust") > 0)
        .sort("trust", descending=True)
        .with_columns(p_users=pl.col("trust") / pl.sum("trust"))
    )
    trust_df.write_csv(trust_file, float_precision=12)
trust_df.shape

# %%
# Sample or top NUM_USERS?
sampled_users = rng.choice(
    trust_df["bgg_user_name"],
    size=NUM_USERS,
    replace=False,
    p=trust_df["p_users"],
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
ranked_games = schulze_method(
    rating_matrix=rating_matrix,
    bgg_ids=sampled_games,
    bgg_user_names=sampled_users,
).join(games, on="bgg_id", how="left")
ranked_games.select("rank", "bgg_id", "name").write_csv(
    RESULTS_DIR / "ranked_games.csv",
)
ranked_games.shape

# %%
ranked_games.head(10)
