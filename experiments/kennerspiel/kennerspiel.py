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

from bokeh.embed import json_item
from bokeh.models import Slope
from bokeh.plotting import figure, output_notebook, show
from bokeh.transform import jitter
from games import transform
from sklearn.linear_model import LogisticRegressionCV
from sklearn.metrics import classification_report, plot_roc_curve

pd.options.display.max_columns = 100
pd.options.display.max_rows = 100

SEED = 23

output_notebook()

# %matplotlib inline
# %load_ext nb_black
# %load_ext lab_black

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
data = transform(
    data=data, list_columns=("game_type", "mechanic", "category"), min_df=0.1
)
data.shape

# %%
data["complexity"].fillna(2, inplace=True)

# %%
data.sample(5, random_state=SEED).T

# %%
num_features = [
    # "min_players",
    # "max_players",
    # "min_players_rec",
    # "max_players_rec",
    # "min_players_best",
    # "max_players_best",
    "min_age",
    # "min_age_rec",
    "min_time",
    "max_time",
    "cooperative",
    "complexity",
]
features = num_features + [
    col for col in data.columns if (":" in col) or col.startswith("playable_")
]
features

# %%
data[num_features + ["ksdj"]].corr()

# %%
lr = LogisticRegressionCV(
    class_weight="balanced",
    scoring="f1",
    max_iter=10_000,
    random_state=SEED,
)
lr.fit(data[features], data.ksdj)

# %%
print(classification_report(data.ksdj, lr.predict(data[features])))
lr.score(data[features], data.ksdj)

# %%
plot_roc_curve(lr, data[features], data.ksdj)

# %%
dict(zip(features, lr.coef_[0, :]))

# %%
for feature, score in zip(features, np.exp(lr.coef_[0]) - 1):
    print(f"{score:+10.3%} change in odds ratio for one unit increase in {feature}")

# %%
data[lr.predict(data[features]) != data.ksdj][
    [
        "name",
        "year",
        "complexity",
        # "min_players",
        # "max_players",
        "min_time",
        "max_time",
        "min_age",
        "sdj",
        "ksdj",
    ]
]


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
pair, model, score = max(test_feature_pairs(features=num_features), key=lambda x: x[-1])
print(f"Best score: {score:.5f} for features {pair[0]} & {pair[1]}")

# %%
TOOLS = "hover,crosshair,pan,wheel_zoom,zoom_in,zoom_out,box_zoom,reset,save,box_select"

plot = figure(
    title="Kennerspiel des Jahres",
    x_axis_label=pair[0],
    y_axis_label=pair[1],
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
    y=jitter(pair[1], width=0.25, distribution="normal"),
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

# %%
with open("complexity_vs_min_age.json", "w") as out_file:
    json.dump(json_item(plot), out_file, indent=4)

# %% [markdown]
# # Old Spiel des Jahres winners

# %%
sdj_ids = sdj[((sdj.winner == 1) | (sdj.nominated == 1)) & (sdj.jahrgang < 2011)].bgg_id
sdj_winners = games[games.index.isin(sdj_ids)]
sdj_winners.shape

# %%
sdj_data = transform(
    sdj_winners, list_columns=("game_type", "mechanic", "category"), min_df=0
)
for feature in features:
    if feature not in sdj_data:
        sdj_data[feature] = 0
sdj_data.shape

# %%
sdj_data["kennerspiel"] = lr.predict(sdj_data[features])
sdj_data["kennerspiel_prob"] = lr.predict_proba(sdj_data[features])[:, 1]

# %%
sdj_data[["name", "kennerspiel", "kennerspiel_prob"]].sort_values(
    "kennerspiel_prob",
    ascending=False,
)
