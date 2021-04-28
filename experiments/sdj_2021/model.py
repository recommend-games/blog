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

import joblib
import pandas as pd

from imblearn.metrics import classification_report_imbalanced
from sklearn.linear_model import LogisticRegressionCV
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from bg_utils import transform

SEED = 23

# %load_ext nb_black
# %load_ext lab_black

# %%
games = pd.read_csv(
    "../../../board-game-data/scraped/bgg_GameItem.csv",
    index_col="bgg_id",
)
games.shape

# %%
sdj = pd.read_csv(
    "../sdj.csv",
    dtype={"winner": bool, "nominated": bool, "recommended": bool, "sonderpreis": str},
)
sdj["award"] = "sdj"
ksdj = pd.read_csv(
    "../ksdj.csv",
    dtype={"winner": bool, "nominated": bool, "recommended": bool, "sonderpreis": str},
)
ksdj["award"] = "ksdj"
awards = pd.concat((sdj, ksdj))
awards.drop_duplicates("bgg_id", inplace=True)
awards.set_index("bgg_id", inplace=True)
awards.shape

# %%
games["award"] = awards["award"]
games["longlist"] = games["award"].notna()
games.longlist.sum(), games.award.value_counts()

# %%
alt_candidates = pd.read_csv("alt_candidates.csv", index_col="bgg_id")
games["kennerspiel_score"] = alt_candidates["kennerspiel_score"]
games["alt_candidate"] = games["kennerspiel_score"].notna()
alt_candidates.shape, games["alt_candidate"].sum()

# %%
games.sample(3).T

# %%
data_all = games[games.longlist ^ games.alt_candidate]
sdj_mask = (data_all.award == "sdj") | (
    data_all.award.isna() & (data_all.kennerspiel_score < 0.5)
)
data_sdj = data_all[sdj_mask].copy()
data_ksdj = data_all[~sdj_mask].copy()
data_all.shape, data_sdj.shape, data_ksdj.shape
