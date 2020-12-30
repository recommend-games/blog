# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.8.0
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %%
import numpy as np
import pandas as pd
from board_game_recommender import BGGRecommender
from sklearn.linear_model import ElasticNetCV

SEED = 23

# %matplotlib inline
# %load_ext nb_black
# %load_ext lab_black

# %%
games = pd.read_csv(
    "../../../board-game-data/scraped/bgg_GameItem.csv", index_col="bgg_id"
)
games.shape

# %%
games.sample(5, random_state=SEED).T

# %%
recommender = BGGRecommender.load(
    "../../../recommend-games-server/data/recommender_bgg"
)

# %%
ratings = recommender.recommend(
    "markus shepherd",
    exclude_known=False,
    exclude_clusters=False,
    exclude_compilations=False,
)
ratings

# %%
games = ratings.to_dataframe().join(games, on="bgg_id", how="inner", lsuffix="_rg")
games.shape

# %%
games[:3].T

# %%
model = ElasticNetCV()

# %%
features = [
    "min_players",
    "max_players",
    "min_age",
    "min_time",
    "max_time",
    "cooperative",
    "complexity",
]
data = games.dropna(subset=features)
data.shape

# %%
model.fit(data[features], data["score"])

# %%
model.coef_
