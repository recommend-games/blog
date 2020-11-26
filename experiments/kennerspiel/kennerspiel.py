# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.7.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %%
import json

import numpy as np
import pandas as pd

from sklearn.linear_model import LogisticRegressionCV
from sklearn.preprocessing import MultiLabelBinarizer

# %load_ext nb_black
# %load_ext lab_black

# %%
with open("../game_types.json") as file:
    game_types = json.load(file)
game_types

# %%
sdj = pd.read_csv("../sdj.csv")
ksdj = pd.read_csv("../ksdj.csv")
games = pd.read_csv(
    "../../../board-game-data/scraped/bgg_GameItem.csv", index_col="bgg_id"
)
sdj.shape, ksdj.shape, games.shape

# %%
games["sdj"] = games.index.isin(set(sdj.bgg_id[sdj.jahrgang >= 2011]))
games["ksdj"] = games.index.isin(set(ksdj.bgg_id))
games.sdj.sum(), games.ksdj.sum()

# %%
data = games[games.sdj | games.ksdj].copy()
data.shape

# %%
mlb = MultiLabelBinarizer()
data[mlb.classes_] = mlb.fit_transform(
    data.game_type.apply(lambda x: x.split(",") if isinstance(x, str) else []).apply(
        lambda l: [game_types.get(x) for x in l]
    )
)
data.shape

# %%
data["complexity"][data.complexity.isna()] = 2

# %%
data.sample(5).T

# %%
features = [
    "min_players",
    "max_players",
    "min_players_rec",
    "max_players_rec",
    "min_players_best",
    "max_players_best",
    "min_age",
    # "min_age_rec",
    "min_time",
    "max_time",
    "cooperative",
    "complexity",
] + list(mlb.classes_)

# %%
model = LogisticRegressionCV(class_weight="balanced", max_iter=10_000)
model.fit(data[features], data.ksdj)

# %%
dict(zip(features, model.coef_[0, :]))

# %%
model.score(data[features], data.ksdj)

# %%
data[features + ["ksdj"]].corr()
