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
with open("features.json") as f:
    features = json.load(f)
len(features)

# %%
for feature in features:
    if feature not in data:
        print(feature)
        data[feature] = False

# %%
model = joblib.load("lr.joblib")
model

# %%
x = data[features]
x = x.fillna(x.mean())
data["sdj_prob"] = model.predict_proba(x)[:, 1]
results = data[["name", "year", "kennerspiel_score", "rec_rating", "sdj_prob"]].copy()
results["sdj_score"] = minmax_scale(results["rec_rating"]) * results["sdj_prob"]
results["sdj_score_add"] = minmax_scale(results["rec_rating"]) + results["sdj_prob"]
results["url"] = [
    f"<a href='https://recommend.games/#/game/{bgg_id}'>{name}</a>"
    for bgg_id, name in results.name.items()
]
sdj = results[results["kennerspiel_score"] < 0.5].copy()
sdj["name"] = sdj["url"]
sdj.drop(columns="url", inplace=True)
kdj = results[results["kennerspiel_score"] >= 0.5].copy()
kdj["name"] = kdj["url"]
kdj.drop(columns="url", inplace=True)
results.shape, sdj.shape, kdj.shape

# %%
results[["rec_rating", "sdj_prob", "sdj_score", "sdj_score_add"]].corr(
    method="spearman"
)

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
kdj.sort_values("sdj_prob", ascending=False)[:10].style

# %%
kdj.sort_values("rec_rating", ascending=False)[:10].style

# %%
kdj.sort_values("sdj_score", ascending=False)[:50].style

# %%
kdj.sort_values("sdj_score_add", ascending=False)[:50].style
