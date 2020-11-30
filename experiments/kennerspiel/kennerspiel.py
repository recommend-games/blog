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

from itertools import combinations

import numpy as np
import pandas as pd
import seaborn as sns

from bokeh.models import Slope
from bokeh.plotting import figure, output_notebook, show
from bokeh.transform import jitter
from sklearn.linear_model import LogisticRegressionCV
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.ensemble import RandomForestClassifier

SEED = 23

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
data.sample(5, random_state=SEED).T

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
data[features + ["ksdj"]].corr()

# %%
lr = LogisticRegressionCV(class_weight="balanced", max_iter=10_000, random_state=SEED)
lr.fit(data[features], data.ksdj)

# %%
dict(zip(features, lr.coef_[0, :]))

# %%
lr.score(data[features], data.ksdj)

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

# %%
rfc = RandomForestClassifier(class_weight="balanced", n_jobs=-1, random_state=SEED)
rfc.fit(data[features], data.ksdj)
{
    feature: importance
    for importance, feature in sorted(
        zip(rfc.feature_importances_, features), reverse=True
    )
}


# %%
def test_feature_pairs(data=data, features=features, target="ksdj"):
    for pair in combinations(features, 2):
        pair = sorted(pair)  # Pandas column selection requires lists
        model = LogisticRegressionCV(
            class_weight="balanced",
            scoring="f1",
            max_iter=10_000,
            random_state=SEED,
        )
        model.fit(data[pair], data[target])
        score = model.score(data[pair], data[target])
        print(f"{score:.5f}: {pair[0]} & {pair[1]}")
        yield pair, model, score


# %%
pair, model, score = max(
    test_feature_pairs(features=set(features) - set(mlb.classes_)), key=lambda x: x[-1]
)
print(f"Best score: {score:.5f} for features {pair[0]} & {pair[1]}")

# %%
TOOLS = "hover,crosshair,pan,wheel_zoom,zoom_in,zoom_out,box_zoom,undo,redo,reset,tap,save,box_select,poly_select,lasso_select"

plot = figure(
    tools=TOOLS,
    tooltips=[
        ("name", "@name"),
        ("year", "@year"),
        ("complexity", "@complexity"),
        ("time", "@min_time–@max_time minutes"),
        ("age", "@min_age+"),
    ],
)

data["color"] = ["#193F4A" if kennerspiel else "#E30613" for kennerspiel in data.ksdj]
data["marker"] = np.where(model.predict(data[pair]) == data.ksdj, "circle", "square")

plot.scatter(
    source=data,
    x=pair[0],
    y=jitter(pair[1], 0.5),
    color="color",
    marker="marker",
    # alpha=0.9,
    size=8,
)

# sigmoid(w*x+b) = 0.5
# w*x+b = 0
# w1*x1 + w2*x2 = -b
# x2 = (-w1*x1-b)/w2
w1 = model.coef_[0, 0]
w2 = model.coef_[0, 1]
b = model.intercept_[0]
slope = Slope(
    gradient=-w1 / w2,
    y_intercept=-b / w2,
    line_color="black",
    line_dash="dashed",
    line_width=2,
)
plot.add_layout(slope)

show(plot)
