# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.4.2
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %%
import json
import pandas as pd
import seaborn as sns

# %matplotlib inline
# %load_ext nb_black
# %load_ext lab_black

# %%
sdj = pd.read_csv("sdj.csv", index_col="bgg_id")
sdj.shape

# %%
with open("../../board-game-data/scraped/bgg_GameItem.jl") as f:
    records = map(json.loads, f)
    games = pd.DataFrame.from_records(records, index="bgg_id")
games.shape

# %%
sdj = sdj.drop(columns="url").join(games, how="left").sort_values("sdj")
sdj.shape

# %%
sdj[
    [
        "sdj",
        "name",
        # "year",
        # "designer",
        # "artist",
        # "publisher",
        "complexity",
        "avg_rating",
        "bayes_rating",
        "rank",
        "num_votes",
        "min_players",
        "max_players",
        "min_time",
        "max_time",
    ]
]

# %%
sns.lineplot(data=sdj, x="sdj", y="bayes_rating")

# %%
sns.lineplot(data=sdj, x="sdj", y="complexity")

# %%
sns.lineplot(data=sdj, x="sdj", y="max_time")
