# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.6.0
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %%
import pandas as pd
import requests

# %load_ext nb_black
# %load_ext lab_black

# %%
include = list(pd.read_csv("include.csv").bgg_id)
exclude = list(pd.read_csv("exclude.csv").bgg_id)
len(include), len(exclude)

# %%
url = "https://recommend.games/api/games/recommend/"
params = {
    "user": "S_d_J",
    "year__gte": 2020,
    "year__lte": 2021,
    "include": include,
    "exclude": exclude,
    "exclude_clusters": False,
    "exclude_known": False,
    "exclude_owned": False,
    "complexity__lte": 3.5,
    "max_players__gte": 3,
    "max_time__lte": 120,
    "min_age__lte": 16,
}

response = requests.get(url, params).json()
results = response["results"]
for game in results:
    print(
        f"{game['name'].upper()} by {', '.join(game['designer_name'])} ({game['bgg_id']})"
    )
