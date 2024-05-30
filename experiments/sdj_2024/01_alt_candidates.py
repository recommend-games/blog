# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.2
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
from itertools import islice
import jupyter_black
import pandas as pd
from bg_utils import recommend_games

jupyter_black.load()

SEED = 23


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
    print(f"Processig {year}…")
    records = islice(sdj_candidates(year=year, **params), num)
    return pd.DataFrame.from_records(records, index="bgg_id")[
        [
            "name",
            "year",
            "kennerspiel_score",
        ]
    ]


# %%
jahrgang_2024 = pd.read_csv("include.csv")
jahrgang_2024["jahrgang"] = 2024
jahrgang_2024.shape

# %%
reviews = pd.read_csv("reviews.csv")
reviews["jahrgang"] = 2024
reviews.shape

# %%
sdj = pd.concat(
    [
        jahrgang_2024[["bgg_id", "jahrgang"]],
        reviews[["bgg_id", "jahrgang"]],
        pd.read_csv("sdj.csv"),
        pd.read_csv("ksdj.csv"),
    ],
    ignore_index=True,
)
sdj.sort_values("jahrgang", ascending=False, inplace=True)
bgg_ids = sdj[
    ((sdj.winner != 1) & (sdj.nominated != 1)) | (sdj.jahrgang >= 2020)
].bgg_id.unique()[:494]
exclude = ",".join(map(str, bgg_ids))
exclude[:100]

# %%
candidates = pd.concat(
    sdj_candidates_df(
        year=year,
        exclude=exclude,
        num=250,
        base_url="https://recommend.games",
    )
    for year in range(1979, 2023)
)

# %%
candidates.sample(10, random_state=SEED)

# %%
kennerspiel = candidates.kennerspiel_score >= 0.5
(~kennerspiel).sum(), kennerspiel.sum()

# %%
candidates.to_csv("alt_candidates.csv", header=True, float_format="%.5g")
