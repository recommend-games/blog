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

import pandas as pd

from bg_utils import recommend_games

SEED = 23

# %load_ext nb_black
# %load_ext lab_black

# %%
def sdj_candidates(year, **params):
    params["year__gte"] = year
    params["year__lte"] = year
    params.setdefault("user", "S_d_J")
    params.setdefault("exclude_clusters", True)
    params.setdefault("exclude_known", True)
    params.setdefault("exclude_owned", False)
    params.setdefault("page", 1)

    yield from recommend_games(**params)


def sdj_candidates_df(year, num=100, **params):
    print(f"Processig {year}...")
    records = islice(sdj_candidates(year, **params), num)
    return pd.DataFrame.from_records(records, index="bgg_id")[["name", "year"]]


# %%
jahrgang_2021 = pd.read_csv("include.csv")
jahrgang_2021["jahrgang"] = 2021

# %%
sdj = pd.concat(
    [pd.read_csv("../sdj.csv"), pd.read_csv("../ksdj.csv"), jahrgang_2021],
    ignore_index=True,
)
sdj.sort_values("jahrgang", ascending=False, inplace=True)
bgg_ids = sdj[
    ((sdj.winner != 1) & (sdj.nominated != 1)) | (sdj.jahrgang >= 2019)
].bgg_id.unique()[:500]
exclude = ",".join(map(str, bgg_ids))

# %%
candidates = pd.concat(
    sdj_candidates_df(year=year, exclude=exclude) for year in range(1979, 2020)
)

# %%
candidates.sample(10, random_state=SEED)

# %%
candidates.to_csv("alt_candidates.csv", header=True)
