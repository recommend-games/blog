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

SEED = 23

# %load_ext nb_black
# %load_ext lab_black

# %%
def sdj_candidates(year):
    print(f"Processig {year}...")
    url = "https://recommend.games/api/games/recommend/"
    params = {
        "user": "S_d_J",
        "year__gte": year,
        "year__lte": year,
        "exclude_clusters": False,
        "exclude_known": True,
        "exclude_owned": False,
    }
    response = requests.get(url, params)
    return pd.DataFrame.from_records(response.json()["results"], index="bgg_id")[
        ["name", "year"]
    ]


# %%
candidates = pd.concat(sdj_candidates(year).head(25) for year in range(1979, 2019))

# %%
candidates.sample(10, random_state=SEED)

# %%
candidates.to_csv("alt_candidates.csv", header=True)
