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
from sklearn.linear_model import LogisticRegressionCV
from sklearn.metrics import classification_report, plot_roc_curve
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MultiLabelBinarizer

SEED = 23

output_notebook()

# %matplotlib inline
# %load_ext nb_black
# %load_ext lab_black

# %%
with open("../game_types.json") as file:
    game_types = json.load(file)
with open("../categories.json") as file:
    categories = json.load(file)
with open("../mechanics.json") as file:
    mechanics = json.load(file)
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
all_categories = data.game_type.str.cat(
    data.mechanic.fillna(""), sep=",", na_rep=""
).str.cat(data.category.fillna(""), sep=",", na_rep="")
all_categories = all_categories.apply(
    lambda x: [c for c in x.split(",") if c] if isinstance(x, str) else []
)

# %%
mlb = MultiLabelBinarizer()
category_values = mlb.fit_transform(all_categories)
category_df = pd.DataFrame(data=category_values, columns=mlb.classes_, index=data.index)
category_df.rename(
    columns={k: f"Game type {v}" for k, v in game_types.items()}, inplace=True
)
category_df.rename(
    columns={k: f"Category {v}" for k, v in categories.items()}, inplace=True
)
category_df.rename(
    columns={k: f"Mechanic {v}" for k, v in mechanics.items()}, inplace=True
)
category_df.drop(columns=category_df.columns[category_df.mean() < 0.1], inplace=True)
category_df.shape

# %%
data[category_df.columns] = category_df
data.shape

# %%
data["complexity"].fillna(2, inplace=True)

# %%
data.sample(5, random_state=SEED).T

# %%
player_count_features = []
for player_count in range(1, 11):
    playable = (data.min_players <= player_count) & (data.max_players >= player_count)
    feature = f"playable_with_{player_count:02d}"
    data[feature] = playable
    player_count_features.append(feature)

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
features = num_features + list(category_df.columns) + player_count_features

# %%
data[num_features + ["ksdj"]].corr()

# %%
X_train, X_test, y_train, y_test = train_test_split(
    data[features],
    data.ksdj,
    test_size=0.2,
    random_state=SEED,
)
X_train.shape, X_test.shape, y_train.shape, y_test.shape

# %%
lr = LogisticRegressionCV(
    class_weight="balanced",
    scoring="f1",
    max_iter=10_000,
    random_state=SEED,
)
lr.fit(X_train, y_train)

# %%
print(classification_report(y_test, lr.predict(X_test)))
lr.score(X_train, y_train), lr.score(X_test, y_test)

# %%
plot_roc_curve(lr, X_test, y_test)

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
