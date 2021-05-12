# -*- coding: utf-8 -*-
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
from itertools import islice
import joblib
import pandas as pd
from tqdm import tqdm
from bg_utils import transform, recommend_games

pd.options.display.max_columns = 100
pd.options.display.max_rows = 500
pd.options.display.float_format = "{:.6g}".format

# %load_ext nb_black
# %load_ext lab_black

# %%
include = list(pd.read_csv("include.csv").bgg_id)
exclude = list(pd.read_csv("exclude.csv").bgg_id)
len(include), len(exclude)

# %%
params = {
    "user": "S_d_J",
    "year__gte": 2020,
    "year__lte": 2021,
    "include": ",".join(map(str, include)),
    "exclude": ",".join(map(str, exclude)),
    "exclude_clusters": True,
    "exclude_known": True,
    "exclude_owned": False,
    # "complexity__lte": 4,
    # "min_players__lte": 3,
    # "max_players__gte": 4,
    # "min_time__lte": 120,
    # "min_age__lte": 16,
}

candidates = list(tqdm(recommend_games(**params)))

for game in candidates[:10]:
    print(
        f"{game['name'].upper()} by {', '.join(game['designer_name'])} ({game['bgg_id']})"
    )

# %%
df = pd.DataFrame.from_records(candidates, index="bgg_id")
df["kennerspiel"] = df["kennerspiel_score"] >= 0.5
df.shape

# %%
df.sample(3).T

# %%
data = transform(
    data=df,
    list_columns=("game_type", "category", "mechanic"),
    min_df=0,
)
data.shape

# %%
with open("features.json") as f:
    features = json.load(f)
len(features)

# %%
for feature in features:
    if feature not in data:
        print(feature)
        data[feature] = False

# %%
model = joblib.load("lr.joblib")
model

# %%
x = data[features]
x = x.fillna(x.mean())
data["sdj_prob"] = model.predict_proba(x)[:, 1]

# %%
rel_features = [
    "avg_rating",
    "bayes_rating",
    "num_votes",
    "rec_rating",
    "sdj_prob",
]
rel_columns = [f"{f}_rel" for f in rel_features]
len(rel_columns)

# %%
data[rel_columns] = data.groupby("kennerspiel")[rel_features].rank(pct=True)
data.shape

# %%
data[~data.kennerspiel][rel_columns].corr()

# %%
data[data.kennerspiel][rel_columns].corr()

# %%
sdj_prob = 0.05
bayes_rating_rel = 0.025
avg_rating_rel = 0.025
rec_rating_rel = 1 - sdj_prob - bayes_rating_rel - avg_rating_rel
rec_rating_rel, sdj_prob, bayes_rating_rel, avg_rating_rel

# %%
data["sdj_score"] = (
    rec_rating_rel * data["rec_rating_rel"]
    + sdj_prob * data["sdj_prob"]
    + bayes_rating_rel * data["bayes_rating_rel"]
    + avg_rating_rel * data["avg_rating_rel"]
)
data["sdj_rank"] = (
    data.groupby("kennerspiel")["sdj_score"]
    .rank(
        ascending=False,
        method="min",
        na_option="bottom",
    )
    .astype(int)
)

# %%
results = data[
    [
        "name",
        "year",
        "sdj_score",
        "sdj_rank",
        "num_votes",
        "avg_rating",
        "avg_rating_rel",
        "bayes_rating",
        "bayes_rating_rel",
        "rec_rating",
        "rec_rating_rel",
        "sdj_prob",
        "sdj_prob_rel",
        "kennerspiel",
        "kennerspiel_score",
        "min_age",
        "min_time",
        "max_time",
        "complexity",
    ]
].copy()
results[["min_players", "max_players"]] = df[["min_players", "max_players"]]
results["url"] = [
    f"<a href='https://recommend.games/#/game/{bgg_id}'>{name}</a>"
    for bgg_id, name in results.name.items()
]
results.sort_values("sdj_score", ascending=False, inplace=True)
results.shape

# %%
sdj = results[~results["kennerspiel"]].copy()
sdj["name_raw"] = sdj["name"]
sdj["name"] = sdj["url"]
sdj.drop(columns="url", inplace=True)
kdj = results[results["kennerspiel"]].copy()
kdj["name_raw"] = kdj["name"]
kdj["name"] = kdj["url"]
kdj.drop(columns="url", inplace=True)
results.shape, sdj.shape, kdj.shape

# %%
results.drop(columns="url", inplace=True)
results.sort_values(["kennerspiel", "sdj_rank"], inplace=True)
results.to_csv("predictions.csv", header=True)

# %% [markdown]
# # SdJ candidates

# %%
sdj[:100].style

# %% [markdown]
# # KdJ candidates

# %%
kdj[:100].style

# %% [markdown]
# # Outputs

# %%
sdj.columns

# %%
COMPLEXITIES = (None, "light", "medium light", "medium", "medium heavy", "heavy")


def game_str(game, bgg_id=None, position=None):
    bgg_id = game["bgg_id"] if bgg_id is None else bgg_id
    position_str = f"#{int(position)}: " if position is not None else ""
    name = game.get("name_raw") or game.get("name")
    min_players = int(min_players) if (min_players := game["min_players"]) else None
    max_players = int(max_players) if (max_players := game["max_players"]) else None
    player_count = (
        f"{min_players:d}–{max_players:d} players"
        if max_players > min_players
        else f"{min_players:d} players"
        if min_players > 1
        else "Solo game"
    )
    min_time = int(min_time) if (min_time := game["min_time"]) else None
    max_time = int(max_time) if (max_time := game["max_time"]) else None
    play_time = (
        f"{min_time:d}–{max_time:d} minutes"
        if max_time > min_time
        else f"{min_time:d} minutes"
    )
    player_age = f"{int(min_age)}+ years" if (min_age := game["min_age"]) else ""
    complexity = complexity if (complexity := game["complexity"]) else 0
    complexity_str = f"{COMPLEXITIES[round(complexity)]}" if complexity > 0 else ""
    kennerspiel_score = (
        round(100 * kennerspiel_score)
        if (kennerspiel_score := game["kennerspiel_score"])
        else None
    )
    kennerspiel = (
        ""
        if kennerspiel_score is None
        else f"{kennerspiel_score}% {{{{% kdj %}}}}Kennerspiel{{{{% /kdj %}}}}"
        if kennerspiel_score >= 50
        else f"{100 - kennerspiel_score}% {{{{% sdj %}}}}Spiel{{{{% /sdj %}}}}"
    )

    # TODO data for each game: designers, player count, play time, age, complexity, Kennerspiel score

    return f"""## {position_str}{{{{% game {bgg_id} %}}}}{name}{{{{% /game %}}}}

*{player_count}, {play_time}, {player_age}, {complexity_str} ({complexity:.1f}), {kennerspiel}*

{{{{< img src="{bgg_id}" size="x300" alt="{name}" >}}}}

{{{{% game {bgg_id} %}}}}{name}{{{{% /game %}}}}"""


# %%
for pos, (bgg_id, game) in enumerate(sdj[:12].iterrows()):
    print(game_str(game, bgg_id, pos + 1))
    print("\n")

# %%
for pos, (bgg_id, game) in enumerate(kdj[:12].iterrows()):
    print(game_str(game, bgg_id, pos + 1))
    print("\n")
