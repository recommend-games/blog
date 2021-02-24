# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.8.2
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %%
from itertools import islice
import joblib
import pandas as pd
from utils import recommend_games

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
    "complexity__lte": 4,
    "min_players__lte": 3,
    "max_players__gte": 4,
    "min_time__lte": 120,
    "min_age__lte": 16,
}

candidates = list(islice(recommend_games(**params), 1000))

for game in candidates[:10]:
    print(
        f"{game['name'].upper()} by {', '.join(game['designer_name'])} ({game['bgg_id']})"
    )

# %%
df = pd.DataFrame.from_records(candidates)
df.shape

# %%
df.sample(3).T

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
]

# %%
model = joblib.load("lr.joblib")
model

# %%
df["sdj_prob"] = model.predict_proba(df[features])[:, 1]
df.sort_values("sdj_prob", ascending=False)[["name", "year", "bgg_id"]].head(50)
