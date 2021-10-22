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
import pandas as pd

# %load_ext nb_black
# %load_ext lab_black

# %%
games = pd.read_csv(
    "../../../board-game-data/scraped/bgg_GameItem.csv",
    index_col="bgg_id",
    low_memory=False,
)
games.shape

# %%
ratings1 = pd.read_csv(
    "../../../board-game-data/rankings/bgg/bgg/20211013-000000.csv",
    index_col="bgg_id",
)
ratings1.dropna(inplace=True)
ratings1.shape

# %%
ratings2 = pd.read_csv(
    "../../../board-game-data/rankings/bgg/bgg/20211020-000000.csv",
    index_col="bgg_id",
)
ratings2.dropna(inplace=True)
ratings2.shape

# %%
data = games[["name", "num_votes"]].join(
    ratings1.join(ratings2, lsuffix="_1", rsuffix="_2")
)
data["rank_increase"] = data["rank_1"] - data["rank_2"]
data["rank_increase_pct"] = 1 - data["rank_2"] / data["rank_1"]
data["score_increase"] = data["score_2"] - data["score_1"]
data["score_increase_pct"] = data["score_2"] / data["score_1"] - 1
data.shape

# %%
data.sort_values("rank_increase_pct", ascending=False)[:50]

# %%
data.sort_values("score_increase", ascending=False)[:50]
