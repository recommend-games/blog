# -*- coding: utf-8 -*-
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
import seaborn as sns

from bokeh.plotting import figure, output_notebook, show
from sklearn.linear_model import LogisticRegressionCV
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.ensemble import RandomForestClassifier

output_notebook()

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
# there was no separate recommendation list for the two awards in 2011
games["sdj"] = games.index.isin(
    set(
        sdj.bgg_id[
            (sdj.jahrgang > 2011) | ((sdj.jahrgang == 2011) & (sdj.nominated == 1))
        ]
    )
)
games["ksdj"] = games.index.isin(
    set(ksdj.bgg_id)
    | set(sdj.bgg_id[sdj.sonderpreis.isin({"Complex Game", "Game of the Year Plus"})])
)
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
lr = LogisticRegressionCV(class_weight="balanced", max_iter=10_000)
lr.fit(data[features], data.ksdj)

# %%
dict(zip(features, lr.coef_[0, :]))

# %%
lr.score(data[features], data.ksdj)

# %%
data[features + ["ksdj"]].corr()

# %%
rfc = RandomForestClassifier(class_weight="balanced", n_jobs=-1)
rfc.fit(data[features], data.ksdj)
{
    feature: importance
    for importance, feature in sorted(
        zip(rfc.feature_importances_, features), reverse=True
    )
}

# %%
TOOLS = "hover,crosshair,pan,wheel_zoom,zoom_in,zoom_out,box_zoom,undo,redo,reset,tap,save,box_select,poly_select,lasso_select,"

plot = figure(
    tools=TOOLS,
    tooltips=[
        ("name", "@name"),
        ("year", "@year"),
        ("complexity", "@complexity"),
        ("time", "@min_time–@max_time"),
    ],
)

data["colors"] = ["#193F4A" if kennerspiel else "#E30613" for kennerspiel in data.ksdj]
plot.scatter(
    source=data,
    x="complexity",
    y="max_time",
    color="colors",
    # alpha=0.9,
    size=8,
)
show(plot)

# %%
data[lr.predict(data[features]) != data.ksdj][
    [
        "name",
        "year",
        "complexity",
        "min_players",
        "max_players",
        "min_time",
        "max_time",
        "min_age",
        "sdj",
        "ksdj",
    ]
]
