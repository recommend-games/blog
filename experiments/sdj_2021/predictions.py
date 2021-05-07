# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.11.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %%
import json
from itertools import islice
import joblib
import pandas as pd
from sklearn.preprocessing import minmax_scale
from tqdm import tqdm
from bg_utils import transform, recommend_games

# %load_ext nb_black
# %load_ext lab_black

# %%
include = list(pd.read_csv("include.csv").bgg_id)
exclude = list(pd.read_csv("exclude.csv").bgg_id)
len(include), len(exclude)

# %%
params = {
    "user": "S_d_J",
    "year__gte": 2020,
    "year__lte": 2021,
    "include": ",".join(map(str, include)),
    "exclude": ",".join(map(str, exclude)),
    "exclude_clusters": True,
    "exclude_known": True,
    "exclude_owned": False,
    # "complexity__lte": 4,
    # "min_players__lte": 3,
    # "max_players__gte": 4,
    # "min_time__lte": 120,
    # "min_age__lte": 16,
}

candidates = list(tqdm(recommend_games(**params)))

for game in candidates[:10]:
    print(
        f"{game['name'].upper()} by {', '.join(game['designer_name'])} ({game['bgg_id']})"
    )

# %%
df = pd.DataFrame.from_records(candidates, index="bgg_id")
df.shape

# %%
df.sample(3).T

# %%
data = transform(
    data=df,
    list_columns=("game_type", "category", "mechanic"),
    min_df=0,
)
data.shape

# %%
with open("features_sdj.json") as f:
    features_sdj = json.load(f)
with open("features_ksdj.json") as f:
    features_ksdj = json.load(f)
len(features_sdj), len(features_ksdj)

# %%
for feature in features_sdj + features_ksdj:
    if feature not in data:
        print(feature)
        data[feature] = False

# %%
model_sdj = joblib.load("lr_sdj.joblib")
model_sdj

# %%
x = data[features_sdj]
x = x.fillna(x.mean())
data["sdj_prob"] = model_sdj.predict_proba(x)[:, 1]

# %%
model_ksdj = joblib.load("lr_ksdj.joblib")
model_ksdj

# %%
x = data[features_ksdj]
x = x.fillna(x.mean())
data["ksdj_prob"] = model_ksdj.predict_proba(x)[:, 1]

# %%
results = data[
    ["name", "year", "kennerspiel_score", "rec_rating", "sdj_prob", "ksdj_prob"]
].copy()
results["url"] = [
    f"<a href='https://recommend.games/#/game/{bgg_id}'>{name}</a>"
    for bgg_id, name in results.name.items()
]
results.shape

# %%
results["sdj_score"] = minmax_scale(results["rec_rating"]) * results["sdj_prob"]
results["sdj_score_add"] = minmax_scale(results["rec_rating"]) + results["sdj_prob"]
results["ksdj_score"] = minmax_scale(results["rec_rating"]) * results["ksdj_prob"]
results["ksdj_score_add"] = minmax_scale(results["rec_rating"]) + results["ksdj_prob"]

# %%
sdj = results[results["kennerspiel_score"] < 0.5].copy()
sdj["name"] = sdj["url"]
sdj.drop(columns="url", inplace=True)
kdj = results[results["kennerspiel_score"] >= 0.5].copy()
kdj["name"] = kdj["url"]
kdj.drop(columns="url", inplace=True)
results.shape, sdj.shape, kdj.shape

# %%
results[
    [
        "rec_rating",
        "sdj_prob",
        "sdj_score",
        "sdj_score_add",
        "ksdj_prob",
        "ksdj_score",
        "ksdj_score_add",
    ]
].corr(method="spearman")

# %%
results.drop(columns="url").sort_values("sdj_score", ascending=False).to_csv(
    "predictions.csv", header=True
)

# %% [markdown]
# # SdJ candidates

# %%
sdj.sort_values("sdj_prob", ascending=False)[:10].style

# %%
sdj.sort_values("rec_rating", ascending=False)[:10].style

# %%
sdj.sort_values("sdj_score", ascending=False)[:50].style

# %%
sdj.sort_values("sdj_score_add", ascending=False)[:50].style

# %% [markdown]
# # KdJ candidates

# %%
kdj.sort_values("ksdj_prob", ascending=False)[:10].style

# %%
kdj.sort_values("rec_rating", ascending=False)[:10].style

# %%
kdj.sort_values("ksdj_score", ascending=False)[:50].style

# %%
kdj.sort_values("ksdj_score_add", ascending=False)[:50].style
