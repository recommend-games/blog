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

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# %matplotlib inline
# %load_ext nb_black
# %load_ext lab_black

# %%
sdj = pd.read_csv("sdj.csv", index_col="bgg_id")
sdj.shape

# %%
ksdj = pd.read_csv("ksdj.csv", index_col="bgg_id")
ksdj.shape

# %%
with open("../../board-game-data/scraped/bgg_GameItem.jl") as f:
    records = map(json.loads, f)
    games = pd.DataFrame.from_records(records, index="bgg_id")
games.shape

# %%
sdj = sdj.drop(columns="url").join(games, how="left").sort_values("sdj")
sdj.shape

# %%
ksdj = (
    ksdj.drop(index=[203416, 203417])  # only keep on Exit game
    .drop(columns="url")
    .join(games, how="left")
    .sort_values("ksdj")
)
ksdj.shape

# %%
columns = [
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

# %%
sdj[["sdj"] + columns]

# %%
ksdj[["ksdj"] + columns]

# %%
# sns.lineplot(data=sdj, x="sdj", y="bayes_rating")
plt.plot(sdj.sdj, sdj.bayes_rating, "red")
plt.plot(ksdj.ksdj, ksdj.bayes_rating, "black")
plt.show()

# %%
# sns.lineplot(data=sdj, x="sdj", y="complexity")
plt.plot(sdj.sdj, sdj.complexity, "red")
plt.plot(ksdj.ksdj, ksdj.complexity, "black")
plt.show()

# %%
# sns.lineplot(data=sdj, x="sdj", y="max_time")
# plt.plot(sdj.sdj, sdj.min_time, "red")
# plt.plot(sdj.sdj, sdj.max_time, "red")
plt.fill_between(sdj.sdj, sdj.min_time, sdj.max_time, color="red", alpha=0.25)
plt.plot(sdj.sdj, (sdj.min_time + sdj.max_time) / 2, "r--")
# plt.plot(ksdj.ksdj, ksdj.min_time, "black")
# plt.plot(ksdj.ksdj, ksdj.max_time, "black")
plt.fill_between(ksdj.ksdj, ksdj.min_time, ksdj.max_time, color="black", alpha=0.25)
plt.plot(
    ksdj.ksdj, (ksdj.min_time + ksdj.max_time) / 2, color="black", linestyle="dashed",
)
plt.show()

# %%
# sns.lineplot(data=sdj, x="sdj", y="max_players")
plt.fill_between(
    ksdj.ksdj, ksdj.min_players, ksdj.max_players, color="black", alpha=0.5
)
plt.fill_between(sdj.sdj, sdj.min_players, sdj.max_players, color="red", alpha=0.5)

# %%
games[
    (games.year >= 2019)
    & (games.year <= 2020)
    & (games.max_time <= 60)
    & (games.complexity <= 2)
    & (games.max_players >= 3)
][columns].sort_values("bayes_rating", ascending=False).head(50)

# %%
games[
    (games.year >= 2019)
    & (games.year <= 2020)
    & (games.max_time <= 120)
    & (games.complexity >= 1.5)
    & (games.complexity <= 3.5)
    & (games.max_players >= 3)
][columns].sort_values("bayes_rating", ascending=False).head(50)
