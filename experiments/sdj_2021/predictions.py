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
from tqdm import tqdm
from bg_utils import transform, recommend_games

pd.options.display.max_columns = 100
pd.options.display.max_rows = 500
pd.options.display.float_format = "{:.6g}".format

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
df["kennerspiel"] = df["kennerspiel_score"] >= 0.5
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
rel_features = [
    "avg_rating",
    "bayes_rating",
    "ksdj_prob",
    "num_votes",
    "rec_rating",
    "sdj_prob",
]
rel_columns = [f"{f}_rel" for f in rel_features]
len(rel_columns)

# %%
data[rel_columns] = data.groupby("kennerspiel")[rel_features].rank(pct=True)
data.shape

# %%
data[~data.kennerspiel][rel_columns].corr()

# %%
data[data.kennerspiel][rel_columns].corr()

# %%
prob_rel = 0.05
bayes_rating_rel = 0.1
avg_rating_rel = 0.05
rec_rating_rel = 1 - prob_rel - bayes_rating_rel - avg_rating_rel
rec_rating_rel, prob_rel, bayes_rating_rel, avg_rating_rel

# %%
data["sdj_score"] = (
    rec_rating_rel * data["rec_rating_rel"]
    + prob_rel * data["sdj_prob_rel"]
    + bayes_rating_rel * data["bayes_rating_rel"]
    + avg_rating_rel * data["avg_rating_rel"]
)
data["sdj_rank"] = data[~data["kennerspiel"]]["sdj_score"].rank(
    ascending=False, method="min"
)
data["ksdj_score"] = (
    rec_rating_rel * data["rec_rating_rel"]
    + prob_rel * data["ksdj_prob_rel"]
    + bayes_rating_rel * data["bayes_rating_rel"]
    + avg_rating_rel * data["avg_rating_rel"]
)
data["ksdj_rank"] = data[data["kennerspiel"]]["ksdj_score"].rank(
    ascending=False, method="min"
)

# %%
results = data[
    [
        "name",
        "year",
        "sdj_score",
        "sdj_rank",
        "ksdj_score",
        "ksdj_rank",
        "num_votes",
        "avg_rating",
        "avg_rating_rel",
        "bayes_rating",
        "bayes_rating_rel",
        "rec_rating",
        "rec_rating_rel",
        "sdj_prob",
        "sdj_prob_rel",
        "ksdj_prob",
        "ksdj_prob_rel",
        "kennerspiel_score",
    ]
].copy()
results["url"] = [
    f"<a href='https://recommend.games/#/game/{bgg_id}'>{name}</a>"
    for bgg_id, name in results.name.items()
]
results.shape

# %%
sdj = results[results["kennerspiel_score"] < 0.5].copy()
sdj["name_raw"] = sdj["name"]
sdj["name"] = sdj["url"]
sdj.drop(columns="url", inplace=True)
kdj = results[results["kennerspiel_score"] >= 0.5].copy()
kdj["name_raw"] = kdj["name"]
kdj["name"] = kdj["url"]
kdj.drop(columns="url", inplace=True)
results.shape, sdj.shape, kdj.shape

# %%
results.drop(columns="url", inplace=True)
results.sort_values(["sdj_rank", "ksdj_rank"], inplace=True)
results["sdj_rank"] = results["sdj_rank"].apply(
    lambda x: str(int(x)) if x and not pd.isna(x) else ""
)
results["ksdj_rank"] = results["ksdj_rank"].apply(
    lambda x: str(int(x)) if x and not pd.isna(x) else ""
)
results.to_csv("predictions.csv", header=True)

# %% [markdown]
# # SdJ candidates

# %%
sdj.sort_values("sdj_score", ascending=False)[:100].style

# %% [markdown]
# # KdJ candidates

# %%
kdj.sort_values("ksdj_score", ascending=False)[:100].style

# %%
for bgg_id, game in sdj.sort_values("sdj_score", ascending=False)[:12].iterrows():
    print(
        f"""
## {{{{% game {bgg_id} %}}}}{game["name_raw"]}{{{{% /game %}}}}



{{{{% game {bgg_id} %}}}}{game["name_raw"]}{{{{% /game %}}}}
"""
    )
    '<!-- {{{{< img src="{bgg_id}" size="x300" alt="{game["name_raw"]}" >}}}} -->'

# %%
for bgg_id, game in kdj.sort_values("ksdj_score", ascending=False)[:12].iterrows():
    print(
        f"""
## {{{{% game {bgg_id} %}}}}{game["name_raw"]}{{{{% /game %}}}}



{{{{% game {bgg_id} %}}}}{game["name_raw"]}{{{{% /game %}}}}
"""
    )
    '<!-- {{{{< img src="{bgg_id}" size="x300" alt="{game["name_raw"]}" >}}}} -->'
