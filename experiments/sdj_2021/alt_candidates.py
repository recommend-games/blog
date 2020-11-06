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
from itertools import islice

import pandas as pd
import requests

SEED = 23

# %load_ext nb_black
# %load_ext lab_black

# %%
def sdj_candidates(year, **params):
    url = "https://recommend.games/api/games/recommend/"
    params["year__gte"] = year
    params["year__lte"] = year
    params.setdefault("user", "S_d_J")
    params.setdefault("exclude_clusters", False)
    params.setdefault("exclude_known", True)
    params.setdefault("exclude_owned", False)
    params.setdefault("page", 1)

    while True:
        print(f"Requesting page {params['page']}")
        response = requests.get(url, params).json()
        if not response.get("results"):
            return
        yield from response["results"]
        if not response.get("next"):
            return
        params["page"] += 1


def sdj_candidates_df(year, num=100, **params):
    print(f"Processig {year}...")
    records = islice(sdj_candidates(year, **params), num)
    return pd.DataFrame.from_records(records, index="bgg_id")[["name", "year"]]


# %%
candidates = pd.concat(sdj_candidates_df(year) for year in range(1979, 2019))

# %%
candidates.sample(10, random_state=SEED)

# %%
candidates.to_csv("alt_candidates.csv", header=True)
