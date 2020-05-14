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
red = "#E30613"
black = "#193F4A"

# %%
sdj_all = pd.read_csv("sdj.csv", index_col="bgg_id")
sdj_all.shape

# %%
ksdj_all = pd.read_csv("ksdj.csv", index_col="bgg_id")
ksdj_all.shape

# %%
with open("../../board-game-data/scraped/bgg_GameItem.jl") as f:
    records = map(json.loads, f)
    games = pd.DataFrame.from_records(records, index="bgg_id")
games.shape

# %%
sdj = (
    sdj_all[sdj_all.winner == 1]
    .drop(columns=["url", "winner"])
    .join(games, how="left")
    .sort_values("sdj")
)
sdj.shape

# %%
ksdj = (
    ksdj_all[ksdj_all.winner == 1]
    .drop(index=[203416, 203417])  # only keep one Exit game
    .drop(columns=["url", "winner"])
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
    "min_age",
]

# %%
sdj[["sdj"] + columns]

# %%
ksdj[["ksdj"] + columns]

# %%
plt.plot(ksdj.ksdj, ksdj.bayes_rating, color=black)
plt.plot(sdj.sdj, sdj.bayes_rating, color=red)
plt.savefig("bayes_rating.svg")
plt.show()

# %%
plt.plot(ksdj.ksdj, ksdj.complexity, color=black)
plt.plot(sdj.sdj, sdj.complexity, color=red)
plt.savefig("complexity.svg")
plt.show()

# %%
plt.fill_between(ksdj.ksdj, ksdj.min_time, ksdj.max_time, color=black, alpha=0.25)
plt.plot(
    ksdj.ksdj, (ksdj.min_time + ksdj.max_time) / 2, color=black, linestyle="dashed",
)
plt.fill_between(sdj.sdj, sdj.min_time, sdj.max_time, color=red, alpha=0.25)
plt.plot(sdj.sdj, (sdj.min_time + sdj.max_time) / 2, color=red, linestyle="dashed")
plt.savefig("time.svg")
plt.show()

# %%
plt.fill_between(ksdj.ksdj, ksdj.min_players, ksdj.max_players, color=black, alpha=0.5)
plt.fill_between(sdj.sdj, sdj.min_players, sdj.max_players, color=red, alpha=0.5)
plt.savefig("players.svg")
plt.show()

# %%
plt.plot(ksdj.ksdj, ksdj.min_age_rec, color=black, linestyle="dotted")
plt.plot(ksdj.ksdj, ksdj.min_age, color=black)
plt.plot(sdj.sdj, sdj.min_age_rec, color=red, linestyle="dotted")
plt.plot(sdj.sdj, sdj.min_age, color=red)
plt.savefig("age.svg")
plt.show()

# %%
games[
    (games.year >= 2019)
    & (games.year <= 2020)
    & (games.max_time <= 60)
    & (games.complexity <= 2)
    & (games.max_players >= 3)
    & ((games.min_age <= 12) | (games.min_age_rec <= 10))
][columns].sort_values("bayes_rating", ascending=False).head(50)

# %%
games[
    (games.year >= 2019)
    & (games.year <= 2020)
    & (games.max_time <= 120)
    & (games.complexity >= 1.5)
    & (games.complexity <= 3.5)
    & (games.max_players >= 3)
    & ((games.min_age <= 14) | (games.min_age_rec <= 12))
][columns].sort_values("bayes_rating", ascending=False).head(50)

# %%
ids_sdj = sdj_all[sdj_all.sdj >= 2011].index
ids_kdsj = ksdj_all[ksdj_all.ksdj >= 2011].index
ids_str = ",".join(map(str, sorted(tuple(ids_sdj) + tuple(ids_kdsj))))
print(ids_str)
