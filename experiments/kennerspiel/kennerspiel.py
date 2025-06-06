# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.15.2
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # What makes a Kennerspiel?

# %%
import json

from itertools import combinations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
import shap

from bokeh.embed import json_item
from bokeh.models import Slope
from bokeh.plotting import figure, output_notebook, show
from bokeh.transform import jitter
from bg_utils import transform
from sklearn.linear_model import LogisticRegressionCV
from sklearn.metrics import classification_report, plot_roc_curve

pd.options.display.max_columns = 150
pd.options.display.max_rows = 150

SEED = 23

output_notebook()
shap.initjs()

# %matplotlib inline
# %load_ext nb_black
# %load_ext lab_black

# %% [markdown]
# ## Data

# %%
sdj = pd.read_csv("../sdj.csv")
ksdj = pd.read_csv("../ksdj.csv")
games = pd.read_csv(
    "../../../board-game-data/scraped/bgg_GameItem.csv", index_col="bgg_id"
)
sdj.shape, ksdj.shape, games.shape

# %%
with open("../game_types.json") as f:
    game_types = json.load(f)
with open("../categories.json") as f:
    categories = json.load(f)
with open("../mechanics.json") as f:
    mechanics = json.load(f)
rename = {"game_type": game_types, "category": categories, "mechanic": mechanics}
game_types

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
    data=data,
    list_columns=("game_type", "mechanic", "category"),
    min_df=0.1,
    rename=rename,
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


# %% [markdown]
# ## Simple model in two variables

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


def plot_games(data, model, features, **plot_kwargs):
    plot_kwargs.setdefault("x_axis_label", features[0])
    plot_kwargs.setdefault("y_axis_label", features[1])
    plot_kwargs.setdefault("tools", TOOLS)
    plot_kwargs.setdefault(
        "tooltips",
        [
            ("name", "@name"),
            ("year", "@year"),
            ("complexity", "@complexity"),
            ("time", "@min_time–@max_time minutes"),
            ("age", "@min_age+"),
        ],
    )

    plot = figure(**plot_kwargs)

    data["color"] = [
        "#193F4A" if kennerspiel else "#E30613" for kennerspiel in data.ksdj
    ]
    data["marker"] = np.where(
        model.predict(data[features]) == data.ksdj, "circle", "square"
    )

    plot.scatter(
        source=data,
        x=features[0],
        y=jitter(features[1], width=0.25, distribution="normal"),
        color="color",
        marker="marker",
        # alpha=0.9,
        size=8,
    )

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

    return plot


# %%
plot = plot_games(data=data, model=model, features=pair, title="Kennerspiel des Jahres")
show(plot)

# %%
with open("complexity_vs_min_age.json", "w") as out_file:
    json.dump(json_item(plot), out_file, indent=4)

# %% [markdown]
# ## Complex model in many variables

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
    print(f"{score:+10.3%} change in odds for one unit increase in {feature}")

# %%
data["predict"] = lr.predict(data[features])
data["predict_proba"] = lr.predict_proba(data[features])[:, 1]

# %%
csv_features = [
    "name",
    "year",
    "complexity",
    "min_age",
    "min_time",
    "max_time",
    "cooperative",
    "sdj",
    "ksdj",
    "predict",
    "predict_proba",
]
data[csv_features].sort_values("predict_proba", ascending=False).to_csv(
    "results_post_2011.csv"
)

# %%
correct = data.predict == data.ksdj
print(
    f"{correct.sum()} out of {len(correct)} classified correctly, that's {correct.mean()*100:.1f}% accurate"
)

# %%
data[~correct][
    [
        "name",
        "year",
        "complexity",
        "min_time",
        "max_time",
        "min_age",
        "ksdj",
        "predict",
        "predict_proba",
    ]
]

# %%
wrong = data[model.predict(data[pair]) != data.ksdj][
    ["name", "year", "complexity", "min_age", "sdj", "predict", "predict_proba"]
].sort_values(["year", "sdj"])
wrong["name"] = [
    "{{% game " + str(i) + " %}}" + n + "{{% /game %}}" for i, n in wrong.name.items()
]
wrong["complexity"] = wrong["complexity"].apply(lambda c: f"{c:.1f}")
wrong["confidence"] = wrong["predict_proba"].apply(lambda p: f"{p*100:.1f}%")
print(wrong.to_markdown())

# %% [markdown]
# ### SHAP values

# %%
explainer = shap.LinearExplainer(lr, data[features])
# feature_perturbation="interventional"
X_test_array = data[features].values
shap_values = explainer.shap_values(X_test_array)

# %%
shap.summary_plot(
    shap_values.astype(float),
    X_test_array,
    feature_names=features,
    plot_type="dot",
    max_display=10,
    show=False,
)
plt.tight_layout()
plt.savefig("shap_summary.svg")

# %%
shap.summary_plot(
    shap_values.astype(float),
    X_test_array,
    feature_names=features,
    plot_type="dot",
    max_display=100,
    show=False,
)
plt.tight_layout()
plt.savefig("shap_summary_full.svg")

# %%
to_test = [
    171668,  # The Grizzled
    244521,  # The Quacks of Quedlinburg
    244522,  # That's Pretty Clever!
    284083,  # The Crew
    295486,  # My City
    223953,  # Kitchen Rush
]

# %%
for bgg_id in to_test:
    ind = data.index.get_loc(bgg_id)
    name = data.name.iloc[ind]
    print(f"{name} ({bgg_id})")
    shap.force_plot(
        base_value=explainer.expected_value,
        shap_values=shap_values[ind, :],
        features=X_test_array[ind, :],
        feature_names=features,
        matplotlib=True,
        show=False,
    )
    plt.tight_layout()
    plt.title(name, loc="left", y=1.3, fontdict={"fontsize": 20})
    plt.savefig(f"shap_{bgg_id}.svg")

# %%
shap.force_plot(
    base_value=explainer.expected_value,
    shap_values=shap_values,
    features=X_test_array,
    feature_names=features,
)

# %% [markdown]
# ## Old Spiel des Jahres winners

# %%
sdj_ids = sdj[((sdj.winner == 1) | (sdj.nominated == 1)) & (sdj.jahrgang < 2011)].bgg_id
sdj_winners = games[games.index.isin(sdj_ids)]
sdj_winners.shape

# %%
sdj_data = transform(
    sdj_winners,
    list_columns=("game_type", "mechanic", "category"),
    min_df=0,
    rename=rename,
)
for feature in features:
    if feature not in sdj_data:
        sdj_data[feature] = 0
sdj_data.shape

# %%
sdj_data["kennerspiel"] = lr.predict(sdj_data[features])
sdj_data["kennerspiel_prob"] = lr.predict_proba(sdj_data[features])[:, 1]

# %%
csv_features.remove("sdj")
csv_features.remove("ksdj")
sdj_data.rename(
    columns={"kennerspiel": "predict", "kennerspiel_prob": "predict_proba"}
)[csv_features].sort_values("predict_proba", ascending=False).to_csv(
    "results_pre_2011.csv"
)

# %%
old_sdj = sdj_data[
    ["name", "year", "complexity", "min_age", "min_time", "kennerspiel_prob"]
].sort_values(
    "kennerspiel_prob",
    ascending=False,
)
old_sdj

# %%
old_sdj["link"] = [
    "{{% game " + str(i) + " %}}" + n + "{{% /game %}}" for i, n in old_sdj.name.items()
]
old_sdj["confidence"] = old_sdj.kennerspiel_prob.apply(lambda c: f"{c*100:.1f}%")
print(old_sdj.reset_index()[["link", "year", "confidence"]].to_markdown())

# %%
sdj_data["ksdj"] = model.predict(sdj_data[pair])
plot = plot_games(
    data=sdj_data, model=model, features=pair, title="Spiel des Jahres before 2011"
)
show(plot)

# %%
with open("complexity_vs_min_age_before_2011.json", "w") as out_file:
    json.dump(json_item(plot), out_file, indent=4)

# %%
X_test_array = sdj_data[features].values
shap_values = explainer.shap_values(X_test_array)

# %%
to_test = [
    13,  # Catan
    478,  # Citadels
    21790,  # Thurn and Taxis
    30549,  # Pandemic
    6249,  # Alhambra
    9209,  # Ticket to Ride
]

# %%
for bgg_id in to_test:
    ind = sdj_data.index.get_loc(bgg_id)
    name = sdj_data.name.iloc[ind]
    print(f"{name} ({bgg_id})")
    shap.force_plot(
        base_value=explainer.expected_value,
        shap_values=shap_values[ind, :],
        features=X_test_array[ind, :],
        feature_names=features,
        matplotlib=True,
        show=False,
    )
    plt.tight_layout()
    plt.title(name, loc="left", y=1.3, fontdict={"fontsize": 20})
    plt.savefig(f"shap_{bgg_id}.svg")

# %% [markdown]
# ## Candidates for SdJ 2021

# %%
url = "https://recommend.games/api/games/recommend/"
params = {
    "user": "S_d_J",
    "year__gte": 2020,
    "year__lte": 2021,
    "min_players__lte": 3,
    "max_players__gte": 4,
    "max_time__lte": 120,
    "min_age__lte": 16,
    "exclude_clusters": True,
    "exclude_known": True,
    "exclude_owned": False,
}
response = requests.get(url, params)

# %%
results = response.json()["results"][:10]
candidates = pd.DataFrame.from_records(results, index="bgg_id")
candidates.shape

# %%
candidates = transform(
    data=candidates,
    list_columns=("game_type", "mechanic", "category"),
    min_df=0,
)
candidates.shape

# %%
for feature in features:
    if feature not in candidates:
        candidates[feature] = 0
candidates.fillna(0, inplace=True)
candidates.shape

# %%
candidates["kennerspiel"] = lr.predict(candidates[features])
candidates["kennerspiel_prob"] = lr.predict_proba(candidates[features])[:, 1]

# %%
sdj2021 = candidates[["name", "kennerspiel", "kennerspiel_prob"]].sort_values(
    "kennerspiel_prob",
    ascending=False,
)
sdj2021

# %%
sdj2021["link"] = [
    "{{% game " + str(i) + " %}}" + n + "{{% /game %}}" for i, n in sdj2021.name.items()
]
sdj2021["confidence"] = sdj2021.kennerspiel_prob.apply(lambda c: f"{c*100:.1f}%")
print(sdj2021.reset_index()[["link", "confidence"]].to_markdown())
